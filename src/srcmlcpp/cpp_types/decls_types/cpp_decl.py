from __future__ import annotations
import copy
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

from srcmlcpp.cpp_types.base import (
    CppElementAndComment,
    CppElementsVisitorFunction,
    CppElementsVisitorEvent,
    CppElementComments,
)
from srcmlcpp.cpp_types.scope.cpp_scope import CppScope
from srcmlcpp.cpp_types.decls_types.cpp_type import CppType
from srcmlcpp.cpp_types.template.cpp_template_specialization import CppTemplateSpecialization
from srcmlcpp.srcmlcpp_options import (
    SrcmlcppOptions,
    _int_from_str_or_named_number_macros,
)
from srcmlcpp.srcml_wrapper import SrcmlWrapper


if TYPE_CHECKING:
    from srcmlcpp.cpp_types.cpp_enum import CppEnum


__all__ = ["CppDecl"]


class CppDeclContext(Enum):
    """Contexts where a CppDecl can occur"""

    VarDecl = "VarDecl"  # i.e. inside a decl statement that declares a variable
    EnumDecl = "EnumDecl"  # i.e. a member of an enum
    ParamDecl = "ParamDecl"  # i.e. a parameter of a function
    Unknown = "Unknown"


@dataclass
class CppDecl(CppElementAndComment):
    """
    https://www.srcml.org/doc/cpp_srcML.html#variable-declaration
    """

    _cpp_type: CppType

    _cpp_decl_with_qualified_types: CppDecl

    # decl_name, i.e. the variable name
    decl_name: str = ""

    # c_array_code will only be filled if this decl looks like:
    #   *  `int a[]:`      <-- in this case, c_array_code="[]"
    #   or
    #   *  `int a[10]:`      <-- in this case, c_array_code="[10]"
    #
    # In other cases, it will be an empty string
    c_array_code: str = ""

    # * init represent the initial aka default value.
    # With srcML, it is inside an <init><expr> node in srcML.
    # Here we retransform it to C++ code for simplicity
    #
    #     For example:
    #     int a = 5;
    #
    #     leads to:
    #         <decl_stmt>
    #             <decl>
    #                 <type> <name>int</name> </type>
    #                 <name>a</name>
    #                 <init>= <expr> <literal type="number">5</literal> </expr> </init>
    #             </decl>;
    #         </decl_stmt>
    #
    # And `<init>= <expr> <literal type="number">5</literal> </expr> </init>` is transcribed as "5"
    initial_value_code: str = ""  # initial or default value

    # indicates whether the initial value was obtained via an initializer list
    initial_value_via_initializer_list: bool = False

    bitfield_range: str = ""  # Will be filled for bitfield members

    def __init__(self, element: SrcmlWrapper, cpp_element_comments: CppElementComments) -> None:
        super().__init__(element, cpp_element_comments)

    def name(self) -> str:
        return self.decl_name

    @property
    def cpp_type(self) -> CppType:
        return self._cpp_type

    @cpp_type.setter
    def cpp_type(self, value: CppType) -> None:
        self._cpp_type = value
        self.fill_children_parents()

    def str_code(self) -> str:
        r = ""
        if hasattr(self, "cpp_type"):
            r += str(self.cpp_type) + " "
        r += self.decl_name + self.c_array_code
        if len(self.initial_value_code) > 0:
            r += " = " + self.initial_value_code
        return r

    def type_name_default_for_signature(self) -> str:
        r = ""
        if hasattr(self, "cpp_type"):
            r += str(self.cpp_type) + " "
        r += self.decl_name + self.c_array_code
        if len(self.initial_value_code) > 0:
            r += " = " + self.initial_value_code
        return r

    def has_name_or_ellipsis(self) -> bool:
        assert self.decl_name is not None
        if len(self.decl_name) > 0:
            return True
        elif "..." in self.cpp_type.modifiers:
            return True
        return False

    def __str__(self) -> str:
        r = self.str_commented()
        return r

    def __repr__(self):
        r = self.str_code()
        return r

    def is_c_string_list_ptr(self) -> bool:
        """
        Returns true if this decl looks like a const C string double pointer.
        Examples:
            const char * const items[]
            const char ** const items
            const char ** items
        :return:
        """
        is_const = "const" in self.cpp_type.specifiers
        is_char = self.cpp_type.typenames == ["char"]
        is_default_init = (
            self.initial_value_code == "" or self.initial_value_code == "NULL" or self.initial_value_code == "nullptr"
        )

        nb_indirections = 0
        nb_indirections += self.cpp_type.modifiers.count("*")
        if len(self.c_array_code) > 0:
            nb_indirections += 1

        r = is_const and is_char and nb_indirections == 2 and is_default_init
        return r

    def is_bitfield(self) -> bool:
        return len(self.bitfield_range) > 0

    def is_c_array(self) -> bool:
        """
        Returns true if this decl is a C style array, e.g.
            int v[4]
        or
            int v[]
        """
        return len(self.c_array_code) > 0

    def c_array_size_as_str(self) -> str | None:
        """
        If this decl is a c array, return its size, e.g.
            * for `int v[COUNT]` it will return "COUNT"
            * for `int v[]` it will return ""
        """
        if not self.is_c_array():
            return None
        pos = self.c_array_code.index("[")
        size_str = self.c_array_code[pos + 1 : -1]
        return size_str

    def c_array_size_as_int(self) -> int | None:
        """
        If this decl is a c array, return its size, e.g. for
            int v[4]
        It will return 4

        However, it might return None for
            int v[COUNT];
        where COUNT is a macro or constexpr value

        (but you can fill SrcmlcppOptions.named_number_macros to circumvent this)
        """
        size_as_str = self.c_array_size_as_str()
        maybe_size = _int_from_str_or_named_number_macros(self.options, size_as_str)
        return maybe_size

    def is_c_array_known_fixed_size(self) -> bool:
        """Returns true if this decl is a c array, and has a fixed size which we can interpret
        either via the code, or through size_dict
        """
        return self.c_array_size_as_int() is not None

    def is_c_array_no_size(self, options: SrcmlcppOptions) -> bool:
        """Returns true if this decl is a c array, and has a no fixed size, e.g.
        int a[];
        """
        is_array = self.is_c_array()
        if not is_array:
            return False
        size_str = self.c_array_size_as_str()
        assert size_str is not None
        has_size = len(size_str.strip()) > 0
        return is_array and not has_size

    def is_c_array_fixed_size_unparsable(self) -> bool:
        is_array = self.is_c_array()
        if not is_array:
            return False

        size_str = self.c_array_size_as_str()
        assert size_str is not None
        has_size = len(size_str.strip()) > 0
        array_size_as_int = self.c_array_size_as_int()
        r = is_array and has_size and (array_size_as_int is None)
        return r

    def is_const(self) -> bool:
        """Returns true if this decl is const"""
        return "const" in self.cpp_type.specifiers  # or "const" in self.cpp_type.names

    def _initial_value_code_with_qualified_types(self, current_scope: CppScope | None = None) -> str:
        if self.initial_value_code == "":
            return ""
        if current_scope is None:
            current_scope = self.cpp_scope()

        # initial_value_token: self.initial_value_code without (...) or {...}
        initial_value = self.initial_value_code

        cpp_unit = self.root_cpp_unit()
        r = cpp_unit._scope_identifiers.qualify_cpp_code(initial_value, current_scope)
        return r

    def with_qualified_types(self, current_scope: CppScope | None = None) -> CppDecl:
        """Qualifies the types and initial values of a decl, e.g.
                N2::Foo foo = N2::Foo()
            might become
                N1::N2::Foo foo = N1::N2::Foo()

            Here we deal only with the initial_value part (after the = sign)

            Note: We do *not* handle `using namespace SomeNamespace`, `typedef ... = T` and `using T = ...`

        This example is an extract from the tests, that shows what this method is capable of:

            int f();
            namespace N1 {
                namespace N2 {
                    struct S2 { constexpr static int s2 = 0; };
                    enum class E2 { a = 0 };  // enum class!
                    int f2();
                }
                namespace N3 {
                    enum E3 { a = 0 };        // C enum!
                    int f3();

                    // We want to qualify the parameters' declarations of this function
                    // Note the subtle difference for enum and enum class
                    // The comment column gives the expected qualified type and initial values
                    void g(
                            int _f = f(),             // => int _f = f()
                            N2::S2 s2 = N2::S2(),     // => N1::N2 s2 = N1::N2::S2()
                            N2::E2 e2 = N2::E2::a,    // => N1::N2::E2 e2 = N1::N2::E2::a
                            E3 e3 = E3::a,            // => N1::N3::E3 a = N1::N3::a
                            int _f3 = N1::N3::f3(),   // => int _f3 = N1::N3::f3()
                            int other = N1::N4::f4(), // => N1::N4::f4()                    (untouched!)
                            int _s2 = N2::S2::s2      // => N1::N2::S2::s2
                        );
                }
            }
        Then, the first parameters decls of g should be qualified as
                            int _f = f(),
                            N1::N2::S2 s2 = N1::N2::S2(),
                            N1::N2::E2 e2 = N1::N2::a,
                            N1::N3::E3 e3 = N1::N3::E3::a,
                            int _f3 = N1::N3::f3()
                            int other = N1::N4::f4()
        """
        if hasattr(self, "_cpp_decl_with_qualified_types"):
            return self._cpp_decl_with_qualified_types

        if current_scope is None:
            current_scope = self.cpp_scope()
        was_changed = False
        new_decl_cpp_type = self.cpp_type
        if hasattr(self, "cpp_type"):
            new_decl_cpp_type = self.cpp_type.with_qualified_types(current_scope)
            if new_decl_cpp_type is not self._cpp_type:
                was_changed = True

        new_initial_value_code = self._initial_value_code_with_qualified_types(current_scope)
        if new_initial_value_code != self.initial_value_code:
            was_changed = True

        if was_changed:
            new_decl = copy.deepcopy(self)
            new_decl.cpp_type = new_decl_cpp_type
            new_decl.initial_value_code = new_initial_value_code
            self._cpp_decl_with_qualified_types = new_decl
        else:
            self._cpp_decl_with_qualified_types = self
        return self._cpp_decl_with_qualified_types

    def _initial_value_code_with_terse_type(self, current_scope: CppScope | None) -> str:
        """Returns a terse version of the initial value (with only the required scoping)
        In this example code:
            namespace N0
            {
                namespace N1 {
                    namespace N2 {
                        struct S2 { constexpr static int s2 = 0; };
                    }
                    namespace N3 {
                        void g(int _s2 = N1::N2::S2::s2);
                    }
                }
            }

        the initial value of the first parameter of g
            N1::N2::S2::s2
        will be replaced by
            N2::S2::s2
        """
        if current_scope is None:
            current_scope = self.cpp_scope()

        # initial_value_fully_qualified = self._initial_value_code_with_qualified_types(current_scope)
        from srcmlcpp.cpp_types.scope.cpp_scope_process import make_terse_code

        r = make_terse_code(self.initial_value_code, current_scope.str_cpp_prefix)
        return r

    def with_terse_types(self, current_scope: CppScope | None = None) -> CppDecl:
        if current_scope is None:
            current_scope = self.cpp_scope()
        was_changed = False

        new_cpp_type = self.cpp_type.with_terse_types(current_scope)

        if new_cpp_type is not self._cpp_type:
            was_changed = True

        new_initial_value_code = self._initial_value_code_with_terse_type(current_scope)
        if new_initial_value_code != self.initial_value_code:
            was_changed = True

        if was_changed:
            new_decl = copy.deepcopy(self)
            new_decl.cpp_type = new_cpp_type
            new_decl.initial_value_code = new_initial_value_code
            return new_decl
        else:
            return self

    def with_specialized_template(self, template_specs: CppTemplateSpecialization) -> CppDecl | None:
        """Returns a new decl where "template_name" is replaced by "cpp_type"
        Returns None if this decl does not use "template_name"
        """
        new_type = self.cpp_type.with_specialized_template(template_specs)
        if new_type is None:
            return None
        else:
            new_decl = copy.deepcopy(self)
            new_decl.cpp_type = new_type
            return new_decl

    def visit_cpp_breadth_first(self, cpp_visitor_function: CppElementsVisitorFunction, depth: int = 0) -> None:
        cpp_visitor_function(self, CppElementsVisitorEvent.OnElement, depth)
        cpp_visitor_function(self, CppElementsVisitorEvent.OnBeforeChildren, depth)
        if hasattr(self, "cpp_type"):
            self.cpp_type.visit_cpp_breadth_first(cpp_visitor_function, depth + 1)
        cpp_visitor_function(self, CppElementsVisitorEvent.OnAfterChildren, depth)

    def parent_enum_if_applicable(self) -> CppEnum | None:
        """
        >> srcmlcpp xml --beautify=False "enum A{a};"
            => <enum>enum <name>A</name><block>{<decl><name>a</name></decl>}</block>;</enum>
        """
        from srcmlcpp.cpp_types.blocks import CppBlock
        from srcmlcpp.cpp_types.cpp_enum import CppEnum

        if isinstance(self.parent, CppBlock):
            if isinstance(self.parent.parent, CppEnum):
                return self.parent.parent
        return None

    def decl_context(self) -> CppDeclContext:
        from srcmlcpp.cpp_types.decls_types import CppDeclStatement
        from srcmlcpp.cpp_types.blocks import CppBlock
        from srcmlcpp.cpp_types.cpp_enum import CppEnum
        from srcmlcpp.cpp_types.functions import CppParameter, CppParameterList, CppFunctionDecl

        if isinstance(self.parent, CppDeclStatement):
            """
            >> srcmlcpp xml --beautify=False "int a"
                => <decl><type><name>int</name></type> <name>a</name></decl>
            """
            return CppDeclContext.VarDecl
        elif isinstance(self.parent, CppBlock):
            """
            >> srcmlcpp xml --beautify=False "enum A{a};"
                => <enum>enum <name>A</name><block>{<decl><name>a</name></decl>}</block>;</enum>
            """
            if isinstance(self.parent.parent, CppEnum):
                return CppDeclContext.EnumDecl
        elif isinstance(self.parent, CppParameter):
            """
            >> srcmlcpp xml --beautify=False "void f(int a);"
            <function_decl><type><name>void</name></type> <name>f</name>
                <parameter_list>(
                    <parameter><decl><type><name>int</name></type> <name>a</name></decl></parameter>)
                </parameter_list>;
            </function_decl>
            """
            if isinstance(self.parent.parent, CppParameterList):
                if isinstance(self.parent.parent.parent, CppFunctionDecl):
                    return CppDeclContext.ParamDecl
        return CppDeclContext.Unknown
