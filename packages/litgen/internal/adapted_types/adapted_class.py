from typing import cast
from dataclasses import dataclass
from typing import Any, Union

from codemanip import code_replacements
from srcmlcpp.srcml_types import *
from litgen.options import LitgenOptions
from litgen.internal import cpp_to_python

from litgen.internal.adapted_types.adapted_element import AdaptedElement
from litgen.internal.adapted_types.adapted_comment import AdaptedEmptyLine, AdaptedComment
from litgen.internal.adapted_types.adapted_decl import AdaptedDecl
from litgen.internal.adapted_types.adapted_function import AdaptedFunction


@dataclass
class AdaptedClass(AdaptedElement):
    adapted_public_children: List[Union[AdaptedEmptyLine, AdaptedComment, AdaptedDecl, AdaptedFunction]]

    def __init__(self, class_: CppStruct, options: LitgenOptions):
        super().__init__(class_, options)
        self.adapted_public_children = []
        self._fill_public_children()

    # override
    def cpp_element(self) -> CppStruct:
        return cast(CppStruct, self._cpp_element)

    def class_name_python(self) -> str:
        r = cpp_to_python.add_underscore_if_python_reserved_word(self.cpp_element().class_name)
        return r

    def _is_member_numeric_array(self, adapted_decl: AdaptedDecl):
        options = self.options
        cpp_decl = adapted_decl.cpp_element()
        array_typename = cpp_decl.cpp_type.str_code()
        if array_typename not in options.c_array_numeric_member_types:
            return False
        if not options.c_array_numeric_member_flag_replace:
            return False
        if cpp_decl.c_array_size_as_int(options.srcml_options) is None:
            return False
        return True

    def _check_can_add_public_member_array_known_fixed_size(self, cpp_decl: CppDecl) -> bool:
        # Cf. https://stackoverflow.com/questions/58718884/binding-an-array-using-pybind11
        options = self.options
        array_typename = cpp_decl.cpp_type.str_code()
        if array_typename not in options.c_array_numeric_member_types:
            emit_srcml_warning(
                cpp_decl.srcml_element,
                """
                AdaptedClass: Only numeric C Style arrays are supported
                Hint: use a vector, or extend `options.c_array_numeric_member_types`
                """,
                options.srcml_options,
            )
            return False

        if not options.c_array_numeric_member_flag_replace:
            emit_srcml_warning(
                cpp_decl.srcml_element,
                """
                AdaptedClass: Detected a numeric C Style array, but will not export it.
                Hint: set `options.c_array_numeric_member_flag_replace = True`
                """,
                options.srcml_options,
            )
            return False

        if cpp_decl.c_array_size_as_int(options.srcml_options) is None:
            array_size_str = cpp_decl.c_array_size_as_str()
            emit_srcml_warning(
                cpp_decl.srcml_element,
                f"""
                    AdaptedClass: Detected a numeric C Style array, but will not export it because its size is not parsable.
                    Hint: may be, add the value "{array_size_str}" to `options.c_array_numeric_member_size_dict`
                    """,
                options.srcml_options,
            )
            return False

        return True

    def _check_can_add_public_member(self, cpp_decl: CppDecl) -> bool:
        if cpp_decl.is_bitfield():  # is_bitfield()
            emit_srcml_warning(
                cpp_decl.srcml_element,
                f"AdaptedClass: Skipped bitfield member {cpp_decl.decl_name}",
                self.options.srcml_options,
            )
            return False

        elif cpp_decl.is_c_array_fixed_size_unparsable(self.options.srcml_options):
            emit_srcml_warning(
                cpp_decl.srcml_element,
                """
                AdaptedClass: Can't parse the size of this array.
                Hint: use a vector, or extend `options.c_array_numeric_member_types`
                """,
                self.options.srcml_options,
            )
            return False

        elif cpp_decl.is_c_array_known_fixed_size(self.options.srcml_options):
            return self._check_can_add_public_member_array_known_fixed_size(cpp_decl)

        else:
            return True

    def _fill_public_children(self) -> None:
        for child in self.cpp_element().get_public_elements():
            if isinstance(child, CppEmptyLine):
                self.adapted_public_children.append(AdaptedEmptyLine(child, self.options))
            elif isinstance(child, CppComment):
                self.adapted_public_children.append(AdaptedComment(child, self.options))
            elif isinstance(child, CppFunctionDecl):
                class_name_cpp = self.cpp_element().class_name
                self.adapted_public_children.append(AdaptedFunction(child, class_name_cpp, self.options))
            elif isinstance(child, CppDeclStatement):
                for cpp_decl in child.cpp_decls:
                    if self._check_can_add_public_member(cpp_decl):
                        adapted_decl = AdaptedDecl(cpp_decl, self.options)
                        self.adapted_public_children.append(adapted_decl)
            else:
                emit_srcml_warning(
                    child.srcml_element,
                    f"Public elements of type {child.tag()} are not supported in python conversion",
                    self.options.srcml_options,
                )

    def _str_pydef_member_numeric_array(self, adapted_decl: AdaptedDecl) -> str:
        assert adapted_decl in self.adapted_public_children
        # Cf. https://stackoverflow.com/questions/58718884/binding-an-array-using-pybind11

        struct_name = self.cpp_element().class_name
        location = adapted_decl.info_original_location_cpp()
        name_python = adapted_decl.decl_name_python()
        name_cpp = adapted_decl.decl_name_cpp()
        comment = adapted_decl.comment_pydef_one_line()

        array_typename = adapted_decl.cpp_element().cpp_type.str_code()
        array_size = adapted_decl.cpp_element().c_array_size_as_int(self.options.srcml_options)
        assert array_size is not None

        template_code = f"""
            .def_property("{name_python}",{location}
                []({struct_name} &self) -> pybind11::array
                {{
                    auto dtype = pybind11::dtype(pybind11::format_descriptor<{array_typename}>::format());
                    auto base = pybind11::array(dtype, {{{array_size}}}, {{sizeof({array_typename})}});
                    return pybind11::array(dtype, {{{array_size}}}, {{sizeof({array_typename})}}, self.{name_cpp}, base);
                }}, []({struct_name}& self) {{}},
                "{comment}")
            """
        r = code_utils.unindent_code(template_code, flag_strip_empty_lines=True) + "\n"
        return r

    def _str_pydef_member_readwrite_property(self, adapted_decl: AdaptedDecl) -> str:
        assert adapted_decl in self.adapted_public_children

        struct_name = self.cpp_element().class_name
        location = adapted_decl.info_original_location_cpp()
        name_python = adapted_decl.decl_name_python()
        name_cpp = adapted_decl.decl_name_cpp()
        comment = adapted_decl.comment_pydef_one_line()

        r = f'.def_readwrite("{name_python}", &{struct_name}::{name_cpp}, "{comment}"){location}\n'
        return r

    def _str_pydef_member(self, adapted_decl: AdaptedDecl) -> str:
        assert adapted_decl in self.adapted_public_children

        if self._is_member_numeric_array(adapted_decl):
            return self._str_pydef_member_numeric_array(adapted_decl)
        else:
            return self._str_pydef_member_readwrite_property(adapted_decl)

    # override
    def _str_stub_lines(self) -> List[str]:
        class_name = self.class_name_python()
        title = f"class {class_name}:"
        title_lines = [title]

        body_lines: List[str] = []
        for child in self.adapted_public_children:
            if isinstance(child, AdaptedDecl):
                child_lines = child._str_stub_class_member()
            else:
                child_lines = child._str_stub_lines()
            body_lines += child_lines

        r = self._str_stub_layout_lines(title_lines, body_lines)
        return r

    # override
    def _str_pydef_lines(self) -> List[str]:
        if self.cpp_element().is_templated_class():
            emit_srcml_warning(
                self.cpp_element().srcml_element, "Template classes are not yet supported", self.options.srcml_options
            )
            return []

        options = self.options
        _i_ = options.indent_cpp_spaces()

        struct_name = self.cpp_element().class_name
        location = self.info_original_location_cpp()
        comment = self.comment_pydef_one_line()

        code_intro = ""
        code_intro += f"auto pyClass{struct_name} = py::class_<{struct_name}>{location}\n"
        code_intro += f'{_i_}(m, "{struct_name}", "{comment}")\n'

        if options.generate_to_string:
            code_outro = f'{_i_}.def("__repr__", [](const {struct_name}& v) {{ return ToString(v); }});'
        else:
            code_outro = f"{_i_};"

        code = code_intro

        if not self.cpp_element().has_non_default_ctor() and not self.cpp_element().has_deleted_default_ctor():
            code += f"{_i_}.def(py::init<>()) // implicit default constructor\n"
        if self.cpp_element().has_deleted_default_ctor():
            code += f"{_i_}// (default constructor explicitly deleted)\n"

        for child in self.adapted_public_children:
            if isinstance(child, AdaptedEmptyLine) or isinstance(child, AdaptedComment):
                continue  # not handled in pydef
            elif isinstance(child, AdaptedDecl):
                decl_code = self._str_pydef_member(child)
                code += code_utils.indent_code(decl_code, indent_str=options.indent_cpp_spaces())
            elif isinstance(child, AdaptedFunction):
                # method
                decl_code = child.str_pydef()
                code += code_utils.indent_code(decl_code, indent_str=options.indent_cpp_spaces())

        code = code + code_outro

        lines = code.split("\n")
        return lines
