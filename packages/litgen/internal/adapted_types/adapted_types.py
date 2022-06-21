from __future__ import annotations
from dataclasses import dataclass
from typing import Any, List, Union, cast

from codemanip import code_replacements

from srcmlcpp.srcml_types import *
from srcmlcpp.srcml_warnings import emit_srcml_warning

from litgen.internal import cpp_to_python
from litgen.options import LitgenOptions


@dataclass
class AdaptedElement:  # (abc.ABC):  # Cannot be abstract (mypy limitation:  https://github.com/python/mypy/issues/5374)
    _cpp_element: CppElementAndComment
    options: LitgenOptions

    def __init__(self, cpp_element: CppElementAndComment, options: LitgenOptions) -> None:
        self._cpp_element = cpp_element
        self.options = options

    def _info_original_location(self, comment_token: str) -> str:
        r = cpp_to_python.info_original_location(self._cpp_element, self.options, comment_token)
        return r

    def info_original_location_cpp(self) -> str:
        return self._info_original_location("//")

    def info_original_location_python(self) -> str:
        return self._info_original_location("#")

    def _str_stub_layout_lines(
        self,
        title_lines: List[str],
        body_lines: List[str] = [],
    ) -> List[str]:
        """Common layout for class, enum, and functions stubs
        :param title_lines: class, enum or function decl + function params. Will be followed by docstring
        :param body_lines: body lines for enums and classes, [] for functions
        :return: a list of python pyi code lines for the stub declaration
        """

        # Preprocess: add location on first line
        assert len(title_lines) > 0
        first_line = title_lines[0] + self.info_original_location_python()
        title_lines = [first_line] + title_lines[1:]

        # Preprocess: align comments in body
        if len(body_lines) == 0:
            body_lines = ["pass"]
        body_lines = code_utils.align_python_comments_in_block_lines(body_lines)

        all_lines = title_lines
        all_lines += cpp_to_python.docstring_lines(self.cpp_element(), self.options)
        all_lines += body_lines

        all_lines = code_utils.indent_code_lines(
            all_lines, skip_first_line=True, indent_str=self.options.indent_python_spaces()
        )
        all_lines.append("")
        return all_lines

    # @abc.abstractmethod
    def cpp_element(self) -> Any:
        # please implement cpp_element in derived classes, it should return the correct CppElement type
        pass

    # @abc.abstractmethod
    def _str_stub_lines(self) -> List[str]:
        raise NotImplementedError()

    # @abc.abstractmethod
    def _str_pydef_lines(self) -> List[str]:
        raise NotImplementedError()

    def comment_pydef_one_line(self) -> str:
        r = cpp_to_python.comment_pydef_one_line(self._cpp_element.cpp_element_comments.full_comment(), self.options)
        return r

    def str_stub(self) -> str:
        stub_lines = self._str_stub_lines()
        r = "\n".join(stub_lines)
        return r

    def str_pydef(self) -> str:
        pydef_lines = self._str_pydef_lines()
        r = "\n".join(pydef_lines) + "\n"
        return r


@dataclass
class AdaptedEmptyLine(AdaptedElement):
    def __init__(self, cpp_empty_line: CppEmptyLine, options: LitgenOptions) -> None:
        super().__init__(cpp_empty_line, options)

    # override
    def cpp_element(self) -> CppEmptyLine:
        return cast(CppEmptyLine, self._cpp_element)

    # override
    def _str_stub_lines(self) -> List[str]:
        if self.options.python_reproduce_cpp_layout:
            return [""]
        else:
            return []

    # override
    def _str_pydef_lines(self) -> List[str]:
        return []


@dataclass
class AdaptedParameter(AdaptedElement):
    def __init__(self, param: CppParameter, options: LitgenOptions) -> None:
        super().__init__(param, options)

    # override
    def cpp_element(self) -> CppParameter:
        return cast(CppParameter, self._cpp_element)

    # override
    def _str_stub_lines(self) -> List[str]:
        raise NotImplementedError()

    # override
    def _str_pydef_lines(self) -> List[str]:
        raise NotImplementedError()

    def adapted_decl(self) -> AdaptedDecl:
        adapted_decl = AdaptedDecl(self.cpp_element().decl, self.options)
        return adapted_decl


@dataclass
class AdaptedDecl(AdaptedElement):
    def __init__(self, decl: CppDecl, options: LitgenOptions) -> None:
        super().__init__(decl, options)

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
        decl_name_python = cpp_to_python.var_name_to_python(decl_name_cpp, self.options)
        return decl_name_python

    def decl_value_python(self) -> str:
        decl_value_cpp = self.cpp_element().initial_value_code
        decl_value_python = cpp_to_python.var_value_to_python(decl_value_cpp, self.options)
        return decl_value_python

    def is_immutable_for_python(self) -> bool:
        cpp_type_name = self.cpp_element().cpp_type.str_code()
        r = cpp_to_python.is_cpp_type_immutable_for_python(cpp_type_name)
        return r

    def c_array_fixed_size_to_const_std_array(self) -> AdaptedDecl:
        """
        Processes decl that contains a *const* c style array of fixed size, e.g. `const int v[2]`

        We simply wrap it into a std::array, like this:
                `const int v[2]` --> `const std::array<int, 2> v`
        """
        cpp_element = self.cpp_element()
        assert cpp_element.is_c_array_known_fixed_size(self.options.srcml_options)
        assert cpp_element.is_const()
        array_size = cpp_element.c_array_size_as_int(self.options.srcml_options)

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

        new_adapted_decl = AdaptedDecl(new_cpp_decl, self.options)
        return new_adapted_decl

    def c_array_fixed_size_to_mutable_new_boxed_decls(self) -> List[AdaptedDecl]:
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
        srcml_options = self.options.srcml_options
        array_size = cpp_element.c_array_size_as_int(srcml_options)

        assert array_size is not None
        assert cpp_element.is_c_array_known_fixed_size(srcml_options)
        assert not cpp_element.is_const()

        cpp_type_name = cpp_element.cpp_type.str_code()

        if cpp_to_python.is_cpp_type_immutable_for_python(cpp_type_name):
            boxed_type = cpp_to_python.BoxedImmutablePythonType(cpp_type_name)
            cpp_type_name = boxed_type.boxed_type_name()

        new_decls: List[AdaptedDecl] = []
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
        param_template = 'py::arg("{argname_python}"){maybe_equal}{maybe_defaultvalue_cpp}'

        maybe_defaultvalue_cpp = self.cpp_element().initial_value_code
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
    def _str_pydef_lines(self) -> List[str]:
        """intentionally not implemented, since it depends on the context
        (is this decl a function param, a method member, an enum member, etc.)"""
        raise ValueError("Not implemented")

    # override
    def _str_stub_lines(self) -> List[str]:
        """intentionally not implemented, since it depends on the context
        (is this decl a function param, a method member, an enum member, etc.)"""
        raise ValueError("Not implemented")


@dataclass
class AdaptedEnumDecl(AdaptedDecl):
    enum_parent: AdaptedEnum

    def __init__(self, decl: CppDecl, enum_parent: AdaptedEnum, options: LitgenOptions) -> None:
        self.enum_parent = enum_parent
        super().__init__(decl, options)

    # override
    def cpp_element(self) -> CppDecl:
        return cast(CppDecl, self._cpp_element)

    def decl_name_cpp_decorated(self) -> str:
        is_class_enum = self.enum_parent.cpp_element().enum_type == "class"
        decl_name_cpp = self.cpp_element().decl_name
        if not is_class_enum:
            return decl_name_cpp
        else:
            r = self.enum_parent.cpp_element().enum_name + "::" + decl_name_cpp
            return r

    def decl_name_python(self) -> str:
        decl_name_cpp = self.cpp_element().decl_name
        decl_name_python = cpp_to_python.enum_value_name_to_python(
            self.enum_parent.cpp_element(), self.cpp_element(), self.options
        )
        return decl_name_python

    def decl_value_python(self) -> str:
        decl_value_cpp = self.cpp_element().initial_value_code
        decl_value_python = cpp_to_python.var_value_to_python(decl_value_cpp, self.options)
        #
        # Sometimes, enum decls have interdependent values like this:
        #     enum MyEnum {
        #         MyEnum_a = 1, MyEnum_b,
        #         MyEnum_foo = MyEnum_a | MyEnum_b    //
        #     };
        #
        # So, we search and replace enum strings in the default value (.init)
        #
        for other_enum_member in self.enum_parent.adapted_enum_decls:
            other_enum_value_cpp_name = other_enum_member.cpp_element().name_code()
            assert other_enum_value_cpp_name is not None
            other_enum_value_python_name = cpp_to_python.enum_value_name_to_python(
                self.enum_parent.cpp_element(), other_enum_member.cpp_element(), self.options
            )
            enum_name = self.enum_parent.enum_name_python()

            replacement = code_replacements.StringReplacement()
            replacement.replace_what = r"\b" + other_enum_value_cpp_name + r"\b"
            replacement.by_what = f"Literal[{enum_name}.{other_enum_value_python_name}]"
            decl_value_python = code_replacements.apply_one_replacement(decl_value_python, replacement)

        return decl_value_python

    # override
    def _str_stub_lines(self) -> List[str]:
        lines = []
        decl_name = self.decl_name_python()
        decl_value = self.decl_value_python()
        decl_part = f"{decl_name} = {decl_value}"

        cpp_decl = self.cpp_element()
        if cpp_to_python.python_shall_place_comment_at_end_of_line(cpp_decl, self.options):
            decl_line = decl_part + "  #" + cpp_to_python.python_comment_end_of_line(cpp_decl, self.options)
            lines.append(decl_line)
        else:
            comment_lines = cpp_to_python.python_comment_previous_lines(cpp_decl, self.options)
            lines += comment_lines
            lines.append(decl_part)

        return lines

    # override
    def _str_pydef_lines(self) -> List[str]:
        decl_name_cpp = self.decl_name_cpp_decorated()
        decl_name_python = self.decl_name_python()
        value_comment = self.comment_pydef_one_line()
        line = f'.value("{decl_name_python}", {decl_name_cpp}, "{value_comment}")'
        return [line]


@dataclass
class AdaptedComment(AdaptedElement):
    def __init(self, cpp_comment: CppComment, options: LitgenOptions):
        super().__init__(cpp_comment, options)

    # override
    def cpp_element(self) -> CppComment:
        return cast(CppComment, self._cpp_element)

    # override
    def _str_stub_lines(self) -> List[str]:
        comment_cpp = self.cpp_element().comment
        comment_python = cpp_to_python._comment_apply_replacements(comment_cpp, self.options)

        def add_comment_token(line: str):
            return "# " + line

        comment_python_lines = list(map(add_comment_token, comment_python.split("\n")))
        return comment_python_lines

    # override
    def _str_pydef_lines(self) -> List[str]:
        return []


@dataclass
class AdaptedConstructor(AdaptedElement):
    def __init__(self, ctor: CppConstructorDecl, options: LitgenOptions):
        super().__init__(ctor, options)

    # override
    def cpp_element(self) -> CppConstructorDecl:
        return cast(CppConstructorDecl, self._cpp_element)

    # override
    def _str_stub_lines(self) -> List[str]:
        raise ValueError("To be completed")

    # override
    def _str_pydef_lines(self) -> List[str]:
        raise ValueError("Not implemented")


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
        raise ValueError("To be completed")

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


@dataclass
class AdaptedEnum(AdaptedElement):
    adapted_children: List[Union[AdaptedDecl, AdaptedEmptyLine, AdaptedComment]]
    adapted_enum_decls: List[AdaptedEnumDecl]

    def __init__(self, enum_: CppEnum, options: LitgenOptions) -> None:
        super().__init__(enum_, options)
        self.adapted_children = []
        self.adapted_enum_decls = []
        self._fill_children()

    # override
    def cpp_element(self) -> CppEnum:
        return cast(CppEnum, self._cpp_element)

    def enum_name_python(self) -> str:
        r = cpp_to_python.add_underscore_if_python_reserved_word(self.cpp_element().enum_name)
        return r

    def _fill_children(self) -> None:
        children_with_values = self.cpp_element().get_children_with_filled_decl_values(self.options.srcml_options)
        for c_child in children_with_values:
            if isinstance(c_child, CppEmptyLine):
                self.adapted_children.append(AdaptedEmptyLine(c_child, self.options))
            elif isinstance(c_child, CppComment):
                self.adapted_children.append(AdaptedComment(c_child, self.options))
            elif isinstance(c_child, CppDecl):
                is_count = cpp_to_python.enum_element_is_count(self.cpp_element(), c_child, self.options)
                if not is_count:
                    new_adapted_decl = AdaptedEnumDecl(c_child, self, self.options)
                    self.adapted_children.append(new_adapted_decl)
                    self.adapted_enum_decls.append(new_adapted_decl)

    def get_adapted_decls(self) -> List[AdaptedDecl]:
        decls = list(filter(lambda c: isinstance(c, AdaptedDecl), self.adapted_children))
        return cast(List[AdaptedDecl], decls)

    # override
    def _str_stub_lines(self) -> List[str]:
        title_line = f"class {self.cpp_element().enum_name}(Enum):"

        body_lines: List[str] = []
        for child in self.adapted_children:
            body_lines += child._str_stub_lines()

        all_lines = self._str_stub_layout_lines([title_line], body_lines)
        return all_lines

    # override
    def _str_pydef_lines(self) -> List[str]:
        enum_name_cpp = self.cpp_element().enum_name
        enum_name_python = self.enum_name_python()
        comment = self.comment_pydef_one_line()
        location = self.info_original_location_cpp()

        lines: List[str] = []

        # Enum decl first line
        enum_decl_line = f'py::enum_<{enum_name_cpp}>(m, "{enum_name_python}", py::arithmetic(), "{comment}"){location}'
        lines += [enum_decl_line]

        # Enum values
        for child in self.adapted_children:
            if isinstance(child, AdaptedEnumDecl):
                adapted_decl = cast(AdaptedEnumDecl, child)
                value_decl_lines = adapted_decl._str_pydef_lines()
                lines += value_decl_lines

        # Add ; on the last line
        assert len(lines) > 0
        last_line = lines[-1]
        last_line = code_utils.add_item_before_cpp_comment(last_line, ";")
        lines[-1] = last_line

        # indent lines
        lines = code_utils.indent_code_lines(lines, skip_first_line=True, indent_str=self.options.indent_cpp_spaces())

        return lines

    def __str__(self) -> str:
        return self.str_stub()


@dataclass
class AdaptedFunction(AdaptedElement):
    """
    AdaptedFunction is at the heart of litgen's function and parameters transformations.

    Litgen may apply some adaptations to function  parameters:
        * c buffers are transformed to py::arrays
        * c strings lists are transformed to List[string]
        * c arrays are boxed or transformed to List
        * variadic format params are discarded
        * (etc.)

    AdaptedFunction may contain two cpp functions:
        * self._cpp_element / self.cpp_element() will contain the original C++ function declaration
        * self.cpp_adapted_function is an adapted C++ function where some parameters might have been adapted.

    Below is a full concrete example in order to clarify.

    1/ Given this C++ function
            ````cpp
            // This is foo's doc:
            //     :param buffer & count: modifiable buffer and its size
            //     :param out_values: output double values
            //     :param in_flags: input bool flags
            //     :param text and ... : formatted text
            void Foo(uint8_t * buffer, size_t count, double out_values[2], const bool in_flags[2], const char* text, ...);
            ````

    2/ Then the generated python callable function will have the following signature in the stub:

        ````python
        def foo(
            buffer: numpy.ndarray,                             # The C buffer was transformed into a py::array
            out_values_0: BoxedDouble,                         # modifiable array params were "Boxed"
            out_values_1: BoxedDouble,
            in_flags: List[bool],                              # const array params are passed as a list
            text: str                                          # Variadic ("...") params are removed from the signature
            ) -> None:
            ''' This is foo's doc:
            :param buffer: modifiable buffer and its size
            :param out_values: output float values
            :param in_flags: input bool flags
            :param text and ... : formatted text
            '''
            pass
        ````

    3/ And the `cpp_adapted_function` C++ signature would be:
        ````cpp
        void Foo(
            py::array & buffer,
            BoxedDouble & out_values_0, BoxedDouble & out_values_1,
            const std::array<bool, 2>& in_flags,
            const char * text);
        ````

    4/ And `cpp_adapter_code` would contains some C++ code that defines several lambdas in order to adapt
    the new C++ signature to the original one.
    It will be generated by `apply_all_adapters` and it will look like:

        ````cpp
        auto Foo_adapt_c_buffers = [](               // First lambda that calls Foo()
            py::array & buffer,
            double out_values[2],
            const bool in_flags[2],
            const char * text, ... )
        {
            // ... Some glue code
            Foo(static_cast<uint8_t *>(buffer_from_pyarray), static_cast<size_t>(buffer_count), out_values, in_flags, text, );
        };

        auto Foo_adapt_fixed_size_c_arrays = [&Foo_adapt_c_buffers](   // Second lambda that calls the first lambda
            py::array & buffer,
            BoxedDouble & out_values_0, BoxedDouble & out_values_1,
            const std::array<bool, 2>& in_flags,
            const char * text, ... )
        {
            // ... Some glue code
            Foo_adapt_c_buffers(buffer, out_values_raw, in_flags.data(), text, );
        };

        auto Foo_adapt_variadic_format = [&Foo_adapt_fixed_size_c_arrays]( // Third lambda that calls the second lambda
            py::array & buffer,                                            // This is the lambda that is published
            BoxedDouble & out_values_0,                                    // as a python interface!
            BoxedDouble & out_values_1,
            const std::array<bool, 2>& in_flags,
            const char * text)
        {
            // ... Some glue code
            Foo_adapt_fixed_size_c_arrays(buffer, out_values_0, out_values_1, in_flags, "%s", text);
        };
        ````

    5/ And `lambda_to_call` will contain the name of the lambda that is published
      (in our example, it is "Foo_adapt_variadic_format")
    """

    cpp_adapted_function: CppFunctionDecl
    parent_struct_name: str
    cpp_adapter_code: Optional[str] = None
    lambda_to_call: Optional[str] = None

    def __init__(self, function_infos: CppFunctionDecl, parent_struct_name: str, options: LitgenOptions) -> None:
        from litgen.internal.adapt_function.make_adapted_function import apply_all_adapters

        self.cpp_adapted_function = function_infos
        self.parent_struct_name = parent_struct_name
        self.cpp_adapter_code = None
        self.lambda_to_call = None
        super().__init__(function_infos, options)

        apply_all_adapters(self)

    # override
    def cpp_element(self) -> CppFunctionDecl:
        return cast(CppFunctionDecl, self._cpp_element)

    def is_method(self) -> bool:
        return len(self.parent_struct_name) > 0

    def is_constructor(self) -> bool:
        r = self.is_method() and self.cpp_adapted_function.function_name == self.parent_struct_name
        return r

    def function_name_python(self) -> str:
        r = cpp_to_python.function_name_to_python(self.cpp_adapted_function.function_name, self.options)
        return r

    def return_type_python(self) -> str:
        return_type_cpp = self.cpp_adapted_function.full_return_type(self.options.srcml_options)
        return_type_python = cpp_to_python.type_to_python(return_type_cpp, self.options)
        return return_type_python

    def adapted_parameters(self) -> List[AdaptedParameter]:
        r: List[AdaptedParameter] = []
        for param in self.cpp_adapted_function.parameter_list.parameters:
            adapted_param = AdaptedParameter(param, self.options)
            r.append(adapted_param)
        return r

    def _paramlist_call_python(self) -> List[str]:
        cpp_parameters = self.cpp_adapted_function.parameter_list.parameters
        r = []
        for param in cpp_parameters:
            param_name_python = cpp_to_python.var_name_to_python(param.decl.decl_name, self.options)
            param_type_cpp = param.decl.cpp_type.str_code()
            param_type_python = cpp_to_python.type_to_python(param_type_cpp, self.options)
            param_default_value = cpp_to_python.var_value_to_python(param.default_value(), self.options)

            param_code = f"{param_name_python}: {param_type_python}"
            if len(param_default_value) > 0:
                param_code += f" = {param_default_value}"

            r.append(param_code)
        return r

    #
    # _str_stub_lines()
    #
    # override
    def _str_stub_lines(self) -> List[str]:
        function_def_code = f"def {self.function_name_python()}("
        return_code = f") -> {self.return_type_python()}:"
        params_strs = self._paramlist_call_python()

        # Try to add function decl + all params and return type on the same line
        def function_name_and_params_on_one_line() -> Optional[str]:
            first_code_line_full = function_def_code
            first_code_line_full += ", ".join(params_strs)
            first_code_line_full += return_code
            if len(first_code_line_full) < self.options.python_max_line_length:
                return first_code_line_full
            else:
                return None

        # Else put params one by line
        def function_name_and_params_line_by_line() -> List[str]:
            params_strs_comma = []
            for i, param_str in enumerate(params_strs):
                if i < len(params_strs) - 1:
                    params_strs_comma.append(param_str + ", ")
                else:
                    params_strs_comma.append(param_str)
            lines = [function_def_code] + params_strs_comma + [return_code]
            return lines

        all_on_one_line = function_name_and_params_on_one_line()

        title_lines = [all_on_one_line] if all_on_one_line is not None else function_name_and_params_line_by_line()
        body_lines: List[str] = []
        r = self._str_stub_layout_lines(title_lines, body_lines)
        return r

    #
    # _str_pydef_lines()
    #

    def _pydef_pyarg_list(self) -> List[str]:
        pyarg_strs: List[str] = []
        for param in self.cpp_adapted_function.parameter_list.parameters:
            adapted_decl = AdaptedDecl(param.decl, self.options)
            pyarg_str = adapted_decl._str_pydef_as_pyarg()
            pyarg_strs.append(pyarg_str)
        return pyarg_strs

    def _pydef_function_return_value_policy(self) -> str:
        """Parses the return_value_policy from the function end of line comment
        For example:
            // A static instance (which python shall not delete, as enforced by the marker return_policy below)
            static Foo& Instance() { static Foo instance; return instance; }       // return_value_policy::reference
        """
        token = "return_value_policy::"
        eol_comment = self.cpp_element().cpp_element_comments.eol_comment_code()
        if "return_value_policy::" in eol_comment:
            return_value_policy = eol_comment[eol_comment.index(token) + len(token) :]
            return return_value_policy
        else:
            return ""

    def _pydef_return_str(self) -> str:
        """Creates the return part of the pydef"""

        template_code = "{return_or_nothing}{self_prefix}{function_to_call}({params_call_inner})"

        return_or_nothing = (
            "return " if self.cpp_adapted_function.full_return_type(self.options.srcml_options) != "void" else ""
        )
        self_prefix = "self." if (self.is_method() and self.lambda_to_call is None) else ""
        # fill function_to_call
        function_to_call = (
            self.lambda_to_call if self.lambda_to_call is not None else self.cpp_adapted_function.function_name
        )
        # Fill params_call_inner
        params_call_inner = self.cpp_adapted_function.parameter_list.names_only_for_call()

        code = code_utils.replace_in_string(
            template_code,
            {
                "return_or_nothing": return_or_nothing,
                "self_prefix": self_prefix,
                "function_to_call": function_to_call,
                "params_call_inner": params_call_inner,
            },
        )
        return code

    def _pydef_constructor_str(self) -> str:
        """
        A constructor decl look like this
            .def(py::init<ARG_TYPES_LIST>(),
            PY_ARG_LIST
            DOC_STRING);
        """

        template_code = code_utils.unindent_code(
            """
            .def(py::init<{arg_types}>(){maybe_comma}{location}
            {_i_}{maybe_pyarg}{maybe_comma}
            {_i_}{maybe_docstring}"""
        )[1:]

        function_infos = self.cpp_element()

        if "delete" in function_infos.specifiers:
            return ""

        _i_ = self.options.indent_cpp_spaces()

        arg_types = function_infos.parameter_list.types_only_for_template()
        location = self.info_original_location_cpp()

        if len(self._pydef_pyarg_list()) > 0:
            maybe_pyarg = ", ".join(self._pydef_pyarg_list())
        else:
            maybe_pyarg = None

        if len(self.comment_pydef_one_line()) > 0:
            maybe_docstring = f'"{self.comment_pydef_one_line()}"'
        else:
            maybe_docstring = None

        # Apply simple replacements
        code = template_code
        code = code_utils.replace_in_string(
            code,
            {
                "_i_": _i_,
                "location": location,
                "arg_types": arg_types,
            },
        )

        # Apply replacements with possible line removal
        code = code_utils.replace_in_string_remove_line_if_none(
            code,
            {
                "maybe_docstring": maybe_docstring,
                "maybe_pyarg": maybe_pyarg,
            },
        )

        # Process maybe_comma
        code = code_utils.replace_maybe_comma(code)

        code = code_utils.add_item_before_cpp_comment(code, ")")

        return code

    def _pydef_full_str_impl(self) -> str:
        """Create the full code of the pydef"""

        template_code = code_utils.unindent_code(
            """
            {module_or_class}.def("{function_name}",{location}
            {_i_}[]({params_call_with_self_if_method})
            {_i_}{
            {_i_}{_i_}{lambda_adapter_code}
            {maybe_empty_line}
            {_i_}{_i_}{return_code};
            {_i_}}{maybe_comma}
            {_i_}{maybe_py_arg}{maybe_comma}
            {_i_}{maybe_docstring}{maybe_comma}
            {_i_}{maybe_return_value_policy}{maybe_comma}
            ){semicolon_if_not_method}"""
        )[1:]

        function_infos = self.cpp_adapted_function

        # fill _i_
        _i_ = self.options.indent_cpp_spaces()

        # fill module_or_class, function_name, location
        module_or_class = "" if self.is_method() else "m"
        function_name = self.function_name_python()
        location = self.info_original_location_cpp()

        # fill params_call_with_self_if_method
        _params_list = function_infos.parameter_list.types_names_default_for_signature_list()
        if self.is_method():
            _self_param = f"{self.parent_struct_name} & self"
            if function_infos.is_const():
                _self_param = "const " + _self_param
            _params_list = [_self_param] + _params_list
        params_call_with_self_if_method = ", ".join(_params_list)

        # fill return_code
        return_code = self._pydef_return_str()

        # fill lambda_adapter_code
        lambda_adapter_code = self.cpp_adapter_code

        if lambda_adapter_code is not None:
            lambda_adapter_code = code_utils.indent_code(
                lambda_adapter_code,
                indent_str=self.options.indent_cpp_spaces() * 2,
                skip_first_line=True,
            )
            if lambda_adapter_code[-1] == "\n":  # type: ignore
                lambda_adapter_code = lambda_adapter_code[:-1]  # type: ignore

        # fill maybe_empty_line, semicolon_if_not_method
        maybe_empty_line = "" if lambda_adapter_code is not None else None
        semicolon_if_not_method = ";" if not self.is_method() else ""

        # fill maybe_py_arg
        pyarg_codes = self._pydef_pyarg_list()
        if len(pyarg_codes) > 0:
            maybe_py_arg = ", ".join(pyarg_codes)
        else:
            maybe_py_arg = None

        # fill maybe_docstring
        comment = self.comment_pydef_one_line()
        if len(comment) == 0:
            maybe_docstring = None
        else:
            maybe_docstring = f'"{comment}"'

        # Fill maybe_return_value_policy
        return_value_policy = self._pydef_function_return_value_policy()
        if len(return_value_policy) > 0:
            maybe_return_value_policy = f"pybind11::return_value_policy::{return_value_policy}"
        else:
            maybe_return_value_policy = None

        # Apply simple replacements
        code = template_code
        code = code_utils.replace_in_string(
            code,
            {
                "_i_": _i_,
                "module_or_class": module_or_class,
                "function_name": function_name,
                "location": location,
                "return_code": return_code,
                "params_call_with_self_if_method": params_call_with_self_if_method,
                "semicolon_if_not_method": semicolon_if_not_method,
            },
        )

        # Apply replacements with possible line removal
        code = code_utils.replace_in_string_remove_line_if_none(
            code,
            {
                "lambda_adapter_code": lambda_adapter_code,
                "maybe_empty_line": maybe_empty_line,
                "maybe_docstring": maybe_docstring,
                "maybe_return_value_policy": maybe_return_value_policy,
                "maybe_py_arg": maybe_py_arg,
            },
        )

        # Process maybe_comma
        code = code_utils.replace_maybe_comma(code, nb_skipped_final_lines=1)

        return code

    # override
    def _str_pydef_lines(self) -> List[str]:
        if self.is_constructor():
            code = self._pydef_constructor_str()
        else:
            code = self._pydef_full_str_impl()
        lines = code.split("\n")
        return lines


@dataclass
class AdaptedBlock(AdaptedElement):
    adapted_elements: List[
        Union[
            AdaptedEmptyLine,
            # AdaptedDecl,
            AdaptedComment,
            AdaptedClass,
            AdaptedFunction,
            AdaptedEnum,
            AdaptedNamespace,
        ]
    ]

    def __init__(self, block: CppBlock, options: LitgenOptions) -> None:
        super().__init__(block, options)
        self.adapted_elements = []
        self._fill_adapted_elements()

    # override
    def cpp_element(self) -> CppBlock:
        return cast(CppBlock, self._cpp_element)

    def _fill_adapted_elements(self) -> None:
        for child in self.cpp_element().block_children:
            if isinstance(child, CppEmptyLine):
                self.adapted_elements.append(AdaptedEmptyLine(child, self.options))
            elif isinstance(child, CppComment):
                self.adapted_elements.append(AdaptedComment(child, self.options))
            elif isinstance(child, CppStruct):
                self.adapted_elements.append(AdaptedClass(child, self.options))
            elif isinstance(child, CppFunctionDecl):
                no_class_name = ""
                self.adapted_elements.append(AdaptedFunction(child, no_class_name, self.options))
            elif isinstance(child, CppEnum):
                self.adapted_elements.append(AdaptedEnum(child, self.options))
            elif isinstance(child, CppNamespace):
                self.adapted_elements.append(AdaptedNamespace(child, self.options))
            elif isinstance(child, CppDeclStatement):
                emit_srcml_warning(
                    child.srcml_element,
                    f"Block elements of type {child.tag()} are not supported in python conversion",
                    self.options.srcml_options,
                )

    # override
    def _str_stub_lines(self) -> List[str]:

        lines = []
        for adapted_element in self.adapted_elements:

            element_lines = adapted_element._str_stub_lines()
            lines += element_lines
        return lines

    # override
    def _str_pydef_lines(self) -> List[str]:
        from litgen.internal.adapted_types.line_spacer import LineSpacer

        line_spacer = LineSpacer()

        lines = []
        for adapted_element in self.adapted_elements:
            element_lines = adapted_element._str_pydef_lines()

            spacing_lines = line_spacer.spacing_lines(adapted_element, element_lines)
            lines += spacing_lines

            lines += element_lines
        return lines


@dataclass
class AdaptedNamespace(AdaptedElement):
    adapted_block: AdaptedBlock

    def __init__(self, namespace_: CppNamespace, options: LitgenOptions) -> None:
        super().__init__(namespace_, options)
        self.adapted_block = AdaptedBlock(self.cpp_element().block, self.options)

    def namespace_name(self) -> str:
        return self.cpp_element().ns_name

    # override
    def cpp_element(self) -> CppNamespace:
        return cast(CppNamespace, self._cpp_element)

    # override
    def _str_stub_lines(self) -> List[str]:
        raise ValueError("To be completed")

    # override
    def _str_pydef_lines(self) -> List[str]:
        location = self.info_original_location_cpp()
        namespace_name = self.namespace_name()
        block_code_lines = self.adapted_block._str_pydef_lines()

        lines: List[str] = []
        lines.append(f"// <namespace {namespace_name}>{location}")
        lines += block_code_lines
        lines.append(f"// </namespace {namespace_name}>")
        return lines


class AdaptedUnit(AdaptedBlock):
    def __init__(self, unit: CppUnit, options: LitgenOptions):
        super().__init__(unit, options)

    # override
    def cpp_element(self) -> CppUnit:
        return cast(CppUnit, self._cpp_element)

    # override
    def _str_stub_lines(self) -> List[str]:
        raise ValueError("To be completed")

    # override
    def _str_pydef_lines(self) -> List[str]:
        raise ValueError("To be completed")
