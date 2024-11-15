from __future__ import annotations
import copy
from dataclasses import dataclass
from typing import cast

from codemanip import code_utils
from litgen import BindLibraryType

from srcmlcpp.cpp_types import CppDecl

from litgen.internal import boxed_python_type, cpp_to_python
from litgen.internal.adapted_types.adapted_element import AdaptedElement
from litgen.internal.context.litgen_context import LitgenContext


@dataclass
class AdaptedDecl(AdaptedElement):
    def __init__(self, lg_context: LitgenContext, decl: CppDecl) -> None:
        super().__init__(lg_context, decl)

    # override
    def cpp_element(self) -> CppDecl:
        return cast(CppDecl, self._cpp_element)

    def decl_name_cpp(self) -> str:
        decl_name_cpp = self.cpp_element().decl_name
        return decl_name_cpp

    def decl_value_cpp(self) -> str:
        decl_value_cpp = self.cpp_element().initial_value_code
        return decl_value_cpp

    def decl_name_python(self) -> str:
        decl_name_cpp = self.cpp_element().decl_name
        decl_name_python = cpp_to_python.var_name_to_python(self.options, decl_name_cpp)
        return decl_name_python

    def decl_value_python(self) -> str:
        decl_value_cpp = self.cpp_element().initial_value_code.strip()
        if decl_value_cpp.startswith("{") and decl_value_cpp.endswith("}"):
            # special case for brace init default value
            decl_value_cpp = self.cpp_element().cpp_type.typenames[0] + "(" + decl_value_cpp[1:-1] + ")"
        decl_value_python = cpp_to_python.var_value_to_python(self.lg_context, decl_value_cpp)
        return decl_value_python

    def decl_type_python(self) -> str:
        decl_type_cpp = self.cpp_element().cpp_type.str_code()
        decl_type_python = cpp_to_python.type_to_python(self.lg_context, decl_type_cpp)
        return decl_type_python

    def is_immutable_for_python(self) -> bool:
        cpp_type_name = self.cpp_element().cpp_type.name_without_modifier_specifier()
        r = cpp_to_python.is_cpp_type_immutable_for_python(cpp_type_name)
        return r

    def c_array_fixed_size_to_const_std_array(self) -> AdaptedDecl:
        """
        Processes decl that contains a *const* c style array of fixed size, e.g. `const int v[2]`

        We simply wrap it into a std::array, like this:
                `const int v[2]` --> `const std::array<int, 2> v`
        """
        cpp_element = self.cpp_element()
        assert cpp_element.is_c_array_known_fixed_size()
        assert cpp_element.is_const()
        array_size = cpp_element.c_array_size_as_int()

        # If the array is `const`, then we simply wrap it into a std::array, like this:
        # `const int v[2]` --> `[ const std::array<int, 2> v ]`
        new_cpp_decl = copy.deepcopy(self.cpp_element())
        new_cpp_decl.c_array_code = ""

        new_cpp_decl.cpp_type.specifiers.remove("const")
        cpp_type_name = new_cpp_decl.cpp_type.str_code()

        std_array_type_name = f"std::array<{cpp_type_name}, {array_size}>&"
        new_cpp_decl.cpp_type.typenames = [std_array_type_name]

        new_cpp_decl.cpp_type.specifiers.append("const")
        new_cpp_decl.decl_name = new_cpp_decl.decl_name

        new_adapted_decl = AdaptedDecl(self.lg_context, new_cpp_decl)
        return new_adapted_decl

    def c_array_fixed_size_to_mutable_new_boxed_decls(self) -> list[AdaptedDecl]:
        """
        Processes decl that contains a *non const* c style array of fixed size, e.g. `int v[2]`
            * we may need to "Box" the values if they are of an immutable type in python,
            * we separate the array into several arguments
            For example:
                `int v[2]`
            Becomes:
                `[ BoxedInt v_0, BoxedInt v_1 ]`

        :return: a list of CppDecls as described before
        """
        cpp_element = self.cpp_element()
        array_size = cpp_element.c_array_size_as_int()

        assert array_size is not None
        assert cpp_element.is_c_array_known_fixed_size()
        assert not cpp_element.is_const()

        cpp_type_name = cpp_element.cpp_type.str_code()

        if cpp_to_python.is_cpp_type_immutable_for_python(cpp_type_name):
            boxed_type_name = boxed_python_type.registered_boxed_type_name(self.lg_context, cpp_type_name)
            cpp_type_name = boxed_type_name

        new_decls: list[AdaptedDecl] = []
        for i in range(array_size):
            new_decl = copy.deepcopy(self)
            new_decl.cpp_element().decl_name = new_decl.cpp_element().decl_name + "_" + str(i)
            new_decl.cpp_element().cpp_type.typenames = [cpp_type_name]
            new_decl.cpp_element().cpp_type.modifiers = ["&"]
            new_decl.cpp_element().c_array_code = ""
            new_decls.append(new_decl)

        return new_decls

    def _str_pydef_as_pyarg(self) -> str:
        """pydef code for function parameters"""
        py_colon = "py::" if self.options.bind_library == BindLibraryType.pybind11 else "nb::"
        param_template = py_colon + 'arg("{argname_python}"){maybe_equal}{maybe_defaultvalue_cpp}'

        maybe_defaultvalue_cpp = self.cpp_element().initial_value_code
        if maybe_defaultvalue_cpp.strip().startswith("{"):
            # special case for default value with brace init
            maybe_defaultvalue_cpp = self.cpp_element().cpp_type.typenames[0] + maybe_defaultvalue_cpp
        if maybe_defaultvalue_cpp in ["NULL", "nullptr", "std::nullopt"]:
            maybe_defaultvalue_cpp = py_colon + "none()"
        if len(maybe_defaultvalue_cpp) > 0:
            maybe_equal = " = "
        else:
            maybe_equal = ""

        argname_python = self.decl_name_python()

        param_line = code_utils.replace_in_string(
            param_template,
            {
                "argname_python": argname_python,
                "maybe_equal": maybe_equal,
                "maybe_defaultvalue_cpp": maybe_defaultvalue_cpp,
            },
        )
        return param_line

    # override
    def pydef_lines(self) -> list[str]:
        """intentionally not implemented, since it depends on the context
        (is this decl a function param, a method member, an enum member, etc.)"""
        raise ValueError("Not implemented")

    # override
    def stub_lines(self) -> list[str]:
        """intentionally not implemented, since it depends on the context
        (is this decl a function param, a method member, an enum member, etc.)"""
        raise ValueError("Not implemented")


class AdaptedGlobalDecl(AdaptedDecl):
    """A global decl that should be converted to module attribute in python
    We do not change the name between cpp and python, because it is a global decl

    Very much a draft, not very reliable yet
    """

    def __init__(self, lg_context: LitgenContext, decl: CppDecl) -> None:
        super().__init__(lg_context, decl)

    # override
    def pydef_lines(self) -> list[str]:
        decl_name_cpp = self.decl_name_cpp()
        decl_value_cpp = self.decl_value_cpp()
        decl_type_cpp = self.cpp_element().cpp_type.str_code()
        decl_type_cpp = decl_type_cpp.replace("static ", "")
        decl_type_cpp = decl_type_cpp.replace("constexpr ", "")

        parent_cpp_module_var_name = cpp_to_python.cpp_scope_to_pybind_var_name(self.options, self.cpp_element())
        line = f'{parent_cpp_module_var_name}.attr("{decl_name_cpp}") = ({decl_type_cpp}) {decl_value_cpp};'
        return [line]

    def stub_lines(self) -> list[str]:
        decl_name_cpp = self.decl_name_cpp()
        decl_value_python = self.decl_value_python()
        decl_type_python = self.decl_type_python()
        line = f"{decl_name_cpp}: {decl_type_python}  # = {decl_value_python}"
        return [line]
