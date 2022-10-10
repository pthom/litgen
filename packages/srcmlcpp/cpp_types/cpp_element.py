from __future__ import annotations
import copy
from dataclasses import dataclass
from enum import Enum
from typing import Callable, List, Optional

from srcmlcpp.cpp_scope import CppScope, CppScopePart, CppScopeType
from srcmlcpp.srcml_wrapper import SrcmlWrapper


class CppElement(SrcmlWrapper):
    """Base class of all the cpp types"""

    # the parent of this element (will be None for the root, which is a CppUnit)
    # at construction time, this field is absent (hasattr return False)!
    # It will be filled later by CppBlock.fill_parents() (with a tree traversal)
    parent: Optional[CppElement]

    # members that are always copied as shallow members (this is intentionally a static list)
    CppElement__deep_copy_force_shallow_ = ["parent"]

    def __init__(self, element: SrcmlWrapper) -> None:
        super().__init__(element.options, element.srcml_xml, element.filename)
        # self.parent is intentionally not filled!

    def __deepcopy__(self, memo=None):
        """CppElement.__deepcopy__: force shallow copy of the parent
        This improves the performance a lot.
        Reason: when we deepcopy, we only intend to modify children.
        """

        # __deepcopy___ "manual":
        #   See https://stackoverflow.com/questions/1500718/how-to-override-the-copy-deepcopy-operations-for-a-python-object
        #   (Antony Hatchkins's answer here)

        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            if k not in CppElement.CppElement__deep_copy_force_shallow_:
                setattr(result, k, copy.deepcopy(v, memo))
            else:
                setattr(result, k, v)
        return result

    def str_code(self) -> str:
        """Returns a C++ textual representation of the contained code element.
        By default, it returns an exact copy of the original code.

        Derived classes override this implementation and str_code will return a string that differs
         a little from the original code, because it is based on information stored in these derived classes.
        """
        return self.str_code_verbatim()

    def depth(self) -> int:
        """The depth of this node, i.e how many parents it has"""
        depth = 0
        current = self
        if not hasattr(current, "parent"):
            return 0
        while current.parent is not None:
            depth += 1
            current = current.parent
        return depth

    def visit_cpp_breadth_first(self, cpp_visitor_function: CppElementsVisitorFunction, depth: int = 0) -> None:
        """Visits all the cpp children, and run the given function on them.
        Runs the visitor on this element first, then on its children

        This method is overriden in classes that have children!
        """
        # For an element without children, simply run the visitor
        cpp_visitor_function(self, CppElementsVisitorEvent.OnElement, depth)

    def short_cpp_element_info(self, include_scope: bool = True) -> str:
        r = type(self).__name__
        if self.has_name():
            r += f" name={self.name_code()}"
        if include_scope:
            scope_str = self.cpp_scope().str_cpp()
            if len(scope_str) > 0:
                r += f" scope={scope_str}"
        return r

    def cpp_scope(self, include_self: bool = False) -> CppScope:
        """Return this element cpp scope

        For example
        namespace Foo {
            struct S {
                void dummy();  // Will have a scope equal to ["Foo", "S"]
            }
        }
        """
        from srcmlcpp.cpp_types.cpp_class import CppStruct
        from srcmlcpp.cpp_types.cpp_namespace import CppNamespace
        from srcmlcpp.cpp_types.cpp_enum import CppEnum

        ancestors = self.ancestors_list(include_self)
        ancestors.reverse()

        scope = CppScope()
        for ancestor in ancestors:
            if isinstance(ancestor, CppStruct):  # this also tests for CppClass
                scope.scope_parts.append(CppScopePart(CppScopeType.ClassOrStruct, ancestor.class_name))
            elif isinstance(ancestor, CppNamespace):
                scope.scope_parts.append(CppScopePart(CppScopeType.Namespace, ancestor.ns_name))
            elif isinstance(ancestor, CppEnum):
                scope.scope_parts.append(CppScopePart(CppScopeType.Enum, ancestor.enum_name))

        return scope

    def ancestors_list(self, include_self: bool = False) -> List[CppElement]:
        """
        Returns the list of ancestors, up to the root unit

        This list does not include this element, and is in the order parent, grand-parent, grand-grand-parent, ...
        :return:
        """
        assert hasattr(self, "parent")  # parent should have been filled by parse_unit & CppBlock
        ancestors = []

        current_parent = self if include_self else self.parent
        while current_parent is not None:
            ancestors.append(current_parent)
            current_parent = current_parent.parent
        return ancestors

    def hierarchy_overview(self) -> str:
        log = ""

        def visitor_log_info(cpp_element: CppElement, event: CppElementsVisitorEvent, depth: int) -> None:
            nonlocal log
            if event == CppElementsVisitorEvent.OnElement:
                log += "  " * depth + cpp_element.short_cpp_element_info() + "\n"

        self.visit_cpp_breadth_first(visitor_log_info)
        return log

    def __str__(self) -> str:
        return self._str_simplified_yaml()


@dataclass
class CppElementAndComment(CppElement):
    """A CppElement to which we add comments"""

    cpp_element_comments: CppElementComments

    def __init__(self, element: SrcmlWrapper, cpp_element_comments: CppElementComments) -> None:
        super().__init__(element)
        self.cpp_element_comments = cpp_element_comments

    def str_commented(self, is_enum: bool = False, is_decl_stmt: bool = False) -> str:
        result = self.cpp_element_comments.top_comment_code()
        result += self.str_code()
        if is_enum:
            result += ","
        if is_decl_stmt:
            result += ";"
        result += self.cpp_element_comments.eol_comment_code()
        return result

    def __str__(self) -> str:
        return self.str_commented()


@dataclass
class CppElementComments:
    """Gathers the C++ comments about functions, declarations, etc. : each CppElement can store
     comment on previous lines, and a single line comment next to its declaration.

    Lonely comments are stored as `CppComment`

     Example:
         `````cpp
         /*
         A multiline C comment
         about Foo1
         */
         void Foo1();

         // First line of comment on Foo2()
         // Second line of comment on Foo2()
         void Foo2();

         // A lonely comment

         //
         // Another lonely comment, on two lines
         // which ends on this second line, but has surrounding empty lines
         //

         // A comment on top of Foo3() & Foo4(), which should be kept as a standalone comment
         // since Foo3 and Foo4 have eol comments
         Void Foo3(); // Comment on end of line for Foo3()
         Void Foo4(); // Comment on end of line for Foo4()
         // A comment that shall not be grouped to the previous (which was an EOL comment for Foo4())
         ````
    """

    comment_on_previous_lines: str
    comment_end_of_line: str
    is_c_style_comment: bool  # Will be True if comment_on_previous_lines was a /* */ comment

    def __init__(self) -> None:
        self.comment_on_previous_lines = ""
        self.comment_end_of_line = ""
        self.is_c_style_comment = False

    def comment(self) -> str:
        if len(self.comment_on_previous_lines) > 0 and len(self.comment_end_of_line) > 0:
            return self.comment_on_previous_lines + "\n" + self.comment_end_of_line
        else:
            return self.comment_on_previous_lines + self.comment_end_of_line

    def top_comment_code(self, add_eol: bool = True, preserve_c_style_comment: bool = True) -> str:

        if preserve_c_style_comment and self.is_c_style_comment:
            r = "/*" + self.comment_on_previous_lines + "*/"
            return r

        top_comments = map(lambda comment: "//" + comment, self.comment_on_previous_lines.splitlines())
        top_comment = "\n".join(top_comments)
        if add_eol:
            if len(top_comment) > 0:
                if not top_comment.endswith("\n"):
                    top_comment += "\n"
        else:
            while top_comment.endswith("\n"):
                top_comment = top_comment[:-1]
        return top_comment

    def eol_comment_code(self) -> str:
        if len(self.comment_end_of_line) == 0:
            return ""
        else:
            if self.comment_end_of_line.startswith("//"):
                return self.comment_end_of_line
            else:
                return " //" + self.comment_end_of_line

    def add_eol_comment(self, comment: str) -> None:
        if len(self.comment_end_of_line) == 0:
            self.comment_end_of_line = comment
        else:
            self.comment_end_of_line += " - " + comment

    def full_comment(self) -> str:
        if len(self.comment_on_previous_lines) > 0 and len(self.comment_end_of_line) > 0:
            return self.comment_on_previous_lines + "\n\n" + self.comment_end_of_line
        else:
            return self.comment_on_previous_lines + self.comment_end_of_line


class CppElementsVisitorEvent(Enum):
    OnElement = 1  # We are visiting this element (will be raised for all elements, incl Blocks)
    OnBeforeChildren = 2  # We are about to visit a block's children
    OnAfterChildren = 3  # We finished visiting a block's children


# This defines the type of function that will visit all the Cpp Elements
# - First param: element being visited. A same element can be visited up to three times with different events
# - Second param: event (see CppElementsVisitorEvent doc)
# - Third param: depth in the source tree
CppElementsVisitorFunction = Callable[[CppElement, CppElementsVisitorEvent, int], None]
