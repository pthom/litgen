from __future__ import annotations
import copy
from typing import List, Optional

from srcmlcpp.cpp_scope import CppScope, CppScopePart, CppScopeType
from srcmlcpp.cpp_types.base.cpp_element_visitor import (
    CppElementsVisitorEvent,
    CppElementsVisitorFunction,
)
from srcmlcpp.srcml_wrapper import SrcmlWrapper


__all__ = ["CppElement"]


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
        from srcmlcpp.cpp_types.classes.cpp_struct import CppStruct
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
