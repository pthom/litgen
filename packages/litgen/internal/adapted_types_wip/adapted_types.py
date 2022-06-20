from __future__ import annotations
import abc
from dataclasses import dataclass
from typing import cast, List, Union, Any

from codemanip import code_replacements

from srcmlcpp.srcml_types import *

from litgen.options import LitgenOptions
from litgen.internal import cpp_to_python


@dataclass
class AdaptedElement:  # (abc.ABC):  # Cannot be abstract (mypy limitation:  https://github.com/python/mypy/issues/5374)
    _cpp_element: CppElementAndComment
    options: LitgenOptions

    def __init__(self, cpp_element: CppElementAndComment, options: LitgenOptions):
        self._cpp_element = cpp_element
        self.options = options

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
        first_line = title_lines[0] + cpp_to_python.info_original_location_python(self._cpp_element, self.options)
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
    def _str_stub_lines(self):
        pass

    def str_stub(self) -> str:
        stub_lines = self._str_stub_lines()
        r = "\n".join(stub_lines)
        return r


@dataclass
class AdaptedEmptyLine(AdaptedElement):
    def __init__(self, cpp_empty_line: CppEmptyLine, options: LitgenOptions):
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


@dataclass
class AdaptedDecl(AdaptedElement):
    def __init__(self, decl: CppDecl, options: LitgenOptions):
        super().__init__(decl, options)

    # override
    def cpp_element(self) -> CppDecl:
        return cast(CppDecl, self._cpp_element)

    def decl_name(self) -> str:
        # le code de decl_python_var_name pourrait revenir ici
        decl_name_cpp = self.cpp_element().decl_name
        decl_name_python = cpp_to_python.var_name_to_python(decl_name_cpp, self.options)
        return decl_name_python

    def decl_value(self) -> str:
        decl_value_cpp = self.cpp_element().initial_value_code
        decl_value_python = cpp_to_python.var_value_to_python(decl_value_cpp, self.options)
        return decl_value_python

    # override
    def _str_stub_lines(self) -> List[str]:
        lines = []

        decl_part = f"{self.decl_name()} = {self.decl_value()}"

        cpp_decl = self.cpp_element()
        if cpp_to_python.python_shall_place_comment_at_end_of_line(cpp_decl, self.options):
            decl_line = decl_part + "  #" + cpp_to_python.python_comment_end_of_line(cpp_decl, self.options)
            lines.append(decl_line)
        else:
            comment_lines = cpp_to_python.python_comment_previous_lines(cpp_decl, self.options)
            lines += comment_lines
            lines.append(decl_part)

        return lines


@dataclass
class AdaptedEnumDecl(AdaptedDecl):
    enum_parent: AdaptedEnum

    def __init__(self, decl: CppDecl, enum_parent: AdaptedEnum, options: LitgenOptions):
        self.enum_parent = enum_parent
        super().__init__(decl, options)

    # override
    def cpp_element(self) -> CppDecl:
        return cast(CppDecl, self._cpp_element)

    def decl_value(self):
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
        for other_enum_member in self.enum_parent.cpp_element().get_children_with_filled_decl_values(
            self.options.srcml_options
        ):
            if isinstance(other_enum_member, CppDecl):
                other_enum_value_cpp_name = other_enum_member.name_code()
                assert other_enum_value_cpp_name is not None
                other_enum_value_python_name = cpp_to_python.enum_value_name_to_python(
                    self.enum_parent.cpp_element(), other_enum_member, self.options
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
        decl_name = self.decl_name()
        decl_value = self.decl_value()
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


@dataclass
class AdaptedClass(AdaptedElement):
    def __init__(self, class_: CppStruct, options: LitgenOptions):
        super().__init__(class_, options)

    # override
    def cpp_element(self) -> CppStruct:
        return cast(CppStruct, self._cpp_element)

    def class_name_python(self) -> str:
        r = cpp_to_python.add_underscore_if_python_reserved_word(self.cpp_element().class_name)
        return r

    # override
    def _str_stub_lines(self) -> List[str]:
        raise ValueError("To be completed")


@dataclass
class AdaptedEnum(AdaptedElement):
    children: List[Union[AdaptedDecl, AdaptedEmptyLine, AdaptedComment]]

    def __init__(self, enum_: CppEnum, options: LitgenOptions):
        super().__init__(enum_, options)
        self.children = []
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
                self.children.append(AdaptedEmptyLine(c_child, self.options))
            elif isinstance(c_child, CppComment):
                self.children.append(AdaptedComment(c_child, self.options))
            elif isinstance(c_child, CppDecl):
                new_adapted_decl = AdaptedEnumDecl(c_child, self, self.options)
                is_count = cpp_to_python.enum_element_is_count(
                    self.cpp_element(), new_adapted_decl.cpp_element(), self.options
                )
                if not is_count:
                    self.children.append(new_adapted_decl)

    def get_decls(self) -> List[AdaptedDecl]:
        decls = list(filter(lambda c: isinstance(c, AdaptedDecl), self.children))
        return cast(List[AdaptedDecl], decls)

    # override
    def _str_stub_lines(self) -> List[str]:
        title_line = f"class {self.cpp_element().enum_name}(Enum):"

        body_lines: List[str] = []
        for child in self.children:
            body_lines += child._str_stub_lines()

        all_lines = self._str_stub_layout_lines([title_line], body_lines)
        return all_lines

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

    def __init__(self, function_infos: CppFunctionDecl, parent_struct_name: str, options: LitgenOptions):
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

    def is_method(self):
        return len(self.parent_struct_name) > 0

    def function_name_python(self):
        r = cpp_to_python.function_name_to_python(self.cpp_adapted_function.function_name, self.options)
        return r

    def return_type_python(self):
        return_type_cpp = self.cpp_adapted_function.full_return_type(self.options.srcml_options)
        return_type_python = cpp_to_python.type_to_python(return_type_cpp, self.options)
        return return_type_python

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


@dataclass
class AdaptedCppUnit(AdaptedElement):
    def __init__(self, cpp_unit: CppUnit, options: LitgenOptions):
        super().__init__(cpp_unit, options)

    # override
    def cpp_element(self) -> CppUnit:
        return cast(CppUnit, self._cpp_element)

    # override
    def _str_stub_lines(self) -> List[str]:
        raise ValueError("To be completed")
