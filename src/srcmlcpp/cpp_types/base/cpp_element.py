from __future__ import annotations
import copy
from enum import Enum
from typing import TYPE_CHECKING, Callable

from srcmlcpp.cpp_types.scope.cpp_scope import CppScope, CppScopePart, CppScopeType
from srcmlcpp.srcml_wrapper import SrcmlWrapper


if TYPE_CHECKING:
    from srcmlcpp.cpp_types.blocks.cpp_unit import CppUnit


__all__ = ["CppElement", "CppElementsVisitorFunction", "CppElementsVisitorEvent"]


# members that are always copied as shallow members (this is intentionally a static list)
_CppElement__deep_copy_force_shallow_ = ["parent"]


class CppElement(SrcmlWrapper):
    """Base class of all the cpp types"""

    # the parent of this element (will be None for the root, which is a CppUnit)
    # at construction time, this field is absent (hasattr return False)!
    # It will be filled later by CppBlock.fill_parents() (with a tree traversal)
    parent: CppElement | None

    # The scope of this element (i.e. the namespace or class it belongs to)
    # This is a cached value, and is filled by self.cpp_scope()
    # (it may be absent if not yet filled)
    _cached_cpp_scope: CppScope
    _cached_cpp_scope_include_self: CppScope

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
        memo[id(self)] = result  # type: ignore
        for k, v in self.__dict__.items():
            if k not in _CppElement__deep_copy_force_shallow_:
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
        if self.has_xml_name():
            r += f" name={self.extract_name_from_xml()}"
        if include_scope:
            scope_str = self.cpp_scope_str(include_self=False)
            if len(scope_str) > 0:
                r += f" scope={scope_str}"
        return r

    def self_scope(self) -> CppScopePart | None:
        from srcmlcpp.cpp_types.classes.cpp_struct import CppStruct
        from srcmlcpp.cpp_types.cpp_namespace import CppNamespace
        from srcmlcpp.cpp_types.cpp_enum import CppEnum

        if isinstance(self, CppStruct):  # this also tests for CppClass
            return CppScopePart(CppScopeType.ClassOrStruct, self.class_name)
        elif isinstance(self, CppNamespace):
            return CppScopePart(CppScopeType.Namespace, self.ns_name)
        elif isinstance(self, CppEnum):
            return CppScopePart(CppScopeType.Enum, self.enum_name)

        return None

    def _clear_scope_cache(self) -> None:
        if hasattr(self, "_cached_cpp_scope"):
            del self._cached_cpp_scope
        if hasattr(self, "_cached_cpp_scope_include_self"):
            del self._cached_cpp_scope_include_self
        if hasattr(self, "_cached_cpp_scope_str"):
            del self._cached_cpp_scope_str
        if hasattr(self, "_cached_cpp_scope_include_self_str"):
            del self._cached_cpp_scope_include_self_str

    def cpp_scope_str(self, include_self: bool = False) -> str:
        if include_self:
            if hasattr(self, "_cached_cpp_scope_include_self_str"):
                return self._cached_cpp_scope_include_self_str
        else:
            if hasattr(self, "_cached_cpp_scope_str"):
                return self._cached_cpp_scope_str

        if include_self:
            self._cached_cpp_scope_include_self_str: str = self.cpp_scope(include_self).str_cpp
            return self._cached_cpp_scope_include_self_str
        else:
            self._cached_cpp_scope_str: str = self.cpp_scope(include_self).str_cpp
            return self._cached_cpp_scope_str

    def cpp_scope(self, include_self: bool = False) -> CppScope:
        """Return this element cpp scope

        For example
        namespace Foo {
            struct S {
                void dummy();  // Will have a scope equal to ["Foo", "S"]
            }
        }
        """
        if include_self:
            if hasattr(self, "_cached_cpp_scope_include_self"):
                return self._cached_cpp_scope_include_self
        else:
            if hasattr(self, "_cached_cpp_scope"):
                return self._cached_cpp_scope

        ancestors = self.ancestors_list(include_self)
        ancestors.reverse()

        from srcmlcpp.cpp_types import CppDecl

        if isinstance(self, CppDecl):
            parent_enum = self.parent_enum_if_applicable()
            if parent_enum is not None and not parent_enum.is_enum_class():
                ancestors = ancestors[:-2]  # C enum decl leak into the parent scope!

        scope_parts: list[CppScopePart] = []
        for ancestor in ancestors:
            scope_part = ancestor.self_scope()
            if scope_part is not None:
                scope_parts.append(scope_part)

        if include_self:
            self._cached_cpp_scope_include_self = CppScope(scope_parts)
            return self._cached_cpp_scope_include_self
        else:
            self._cached_cpp_scope: CppScope = CppScope(scope_parts)
            return self._cached_cpp_scope

    def ancestors_list(self, include_self: bool = False) -> list[CppElement]:
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

    def root_cpp_unit(self) -> CppUnit:
        from srcmlcpp.cpp_types.blocks.cpp_unit import CppUnit

        return CppUnit.find_root_cpp_unit(self)

    def fill_children_parents(self) -> None:
        from srcmlcpp.cpp_types.blocks.cpp_unit import CppUnit

        if isinstance(self, CppUnit):
            top_parent = None
        else:
            top_parent = self.parent
        parents_stack: list[CppElement | None] = [top_parent]

        def visitor_fill_parent(cpp_element: CppElement, event: CppElementsVisitorEvent, _depth: int) -> None:
            nonlocal parents_stack
            if event == CppElementsVisitorEvent.OnElement:
                assert len(parents_stack) > 0

                last_parent = parents_stack[-1]
                if len(parents_stack) > 1:
                    assert last_parent is not None

                cpp_element.parent = last_parent
            elif event == CppElementsVisitorEvent.OnBeforeChildren:
                parents_stack.append(cpp_element)
            elif event == CppElementsVisitorEvent.OnAfterChildren:
                parents_stack.pop()

        self.visit_cpp_breadth_first(visitor_fill_parent)

    def __str__(self) -> str:
        return self._str_simplified_yaml()


class CppElementsVisitorEvent(Enum):
    OnElement = 1  # We are visiting this element (will be raised for all elements, incl Blocks)
    OnBeforeChildren = 2  # We are about to visit a block's children
    OnAfterChildren = 3  # We finished visiting a block's children


# This defines the type of function that will visit all the Cpp Elements
# - First param: element being visited. A same element can be visited up to three times with different events
# - Second param: event (see CppElementsVisitorEvent doc)
# - Third param: depth in the source tree
CppElementsVisitorFunction = Callable[[CppElement, CppElementsVisitorEvent, int], None]
