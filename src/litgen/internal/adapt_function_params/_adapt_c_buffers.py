from __future__ import annotations
import copy
from typing import Optional

from codemanip import code_utils

from srcmlcpp import SrcmlcppException
from srcmlcpp.cpp_types import CppFunctionDecl, CppParameter

from litgen.internal import cpp_to_python
from litgen.internal.adapt_function_params._lambda_adapter import LambdaAdapter
from litgen.internal.adapted_types import AdaptedFunction
from litgen.options import LitgenOptions


def _possible_buffer_pointer_types(options: LitgenOptions) -> list[str]:
    types = [t + "*" for t in options._fn_params_buffer_types_list()] + [
        t + " *" for t in options._fn_params_buffer_types_list()
    ]
    return types


def _possible_buffer_template_pointer_types(options: LitgenOptions) -> list[str]:
    types = [t + "*" for t in options._fn_params_buffer_template_types_list()] + [
        t + " *" for t in options._fn_params_buffer_template_types_list()
    ]
    return types


def _looks_like_param_buffer_standard(options: LitgenOptions, param: CppParameter) -> bool:
    for possible_buffer_type in _possible_buffer_pointer_types(options):
        param_type_code = param.full_type()
        if code_utils.contains_pointer_type(param_type_code, possible_buffer_type):
            return True
    return False


def _looks_like_param_template_buffer(options: LitgenOptions, param: CppParameter) -> bool:
    for possible_buffer_type in _possible_buffer_template_pointer_types(options):
        param_type_code = param.full_type()
        if code_utils.contains_pointer_type(param_type_code, possible_buffer_type):
            return True
    return False


def _name_looks_like_buffer_standard_or_template(options: LitgenOptions, param: CppParameter) -> bool:
    return _looks_like_param_buffer_standard(options, param) or _looks_like_param_template_buffer(options, param)


def _name_looks_like_buffer_size(options: LitgenOptions, param: CppParameter) -> bool:
    r = code_utils.does_match_regex(options.fn_params_buffer_size_names__regex, param.variable_name())
    return r


class _AdaptBuffersHelper:
    adapted_function: AdaptedFunction
    function_infos: CppFunctionDecl
    options: LitgenOptions

    def __init__(self, options: LitgenOptions, adapted_function: AdaptedFunction) -> None:
        self.adapted_function = adapted_function
        self.function_infos = adapted_function.cpp_adapted_function
        self.options = options

        if self.shall_adapt():
            # Check that there is one stride param at most
            nb_strides = 0
            for idx_param in range(self._nb_params()):
                if self._is_stride_param(idx_param):
                    nb_strides += 1
            if nb_strides > 1:
                raise SrcmlcppException("More than one stride param found!")

        if self.has_template_buffer_param() and self.shall_adapt():
            self.adapted_function.has_adapted_template_buffer = True

    def lambda_input(self, idx_param: int) -> Optional[str]:
        if self._is_buffer_standard(idx_param):
            r = self._lambda_input_buffer_standard_convert_part(idx_param)
            r += self._lambda_input_buffer_standard_check_part(idx_param)
            return r
        elif self._is_stride_param(idx_param):
            r = self.lambda_input_stride_param(idx_param)
            return r
        elif self._is_buffer_template(idx_param):
            r = self._lambda_input_buffer_standard_convert_part(idx_param)
            return r
        else:
            return None

    def new_visible_interface_param(self, idx_param: int) -> Optional[CppParameter]:
        param = self._param(idx_param)
        if self._is_buffer_template_or_not(idx_param):
            return self._new_param_buffer_standard(idx_param)
        elif self._is_stride_param(idx_param):
            return self._new_param_stride(idx_param)
        elif self._is_buffer_size(idx_param):
            return None
        else:
            return param

    def adapted_inner_param(self, idx_param: int) -> str:
        param = self._param(idx_param)
        if self._is_buffer_standard(idx_param):
            r = self._adapted_param_buffer_standard(idx_param)
            return r
        elif self._is_buffer_size(idx_param):
            r = self._adapted_param_buffer_size(idx_param)
            return r
        elif self._is_stride_param(idx_param):
            r = self._adapted_param_stride(idx_param)
            return r
        elif self._is_buffer_template(idx_param):
            r = "adapted_param_looks_like_param_template_buffer"
            return r
        else:
            r = param.decl.decl_name
            return r

    def shall_adapt(self) -> bool:
        if not code_utils.does_match_regex(
            self.options.fn_params_replace_buffer_by_array__regex,
            self.adapted_function.cpp_adapted_function.function_name,
        ):
            return False
        for idx in range(self._nb_params()):
            if self._is_buffer_template_or_not(idx):
                return True
        return False

    def has_template_buffer_param(self) -> bool:
        param = self._last_template_buffer_param()
        return param is not None

    def _param(self, idx_param: int) -> CppParameter:
        assert 0 <= idx_param < len(self.function_infos.parameter_list.parameters)
        return self.function_infos.parameter_list.parameters[idx_param]

    def _params(self) -> list[CppParameter]:
        return self.function_infos.parameter_list.parameters

    def _nb_params(self) -> int:
        return len(self._params())

    def _is_buffer_size(self, idx_param: int) -> bool:
        if idx_param == 0:
            return False
        # Test if this is a size preceded by a buffer
        param_n0 = self._param(idx_param)
        param_n1 = self._param(idx_param - 1)
        if _name_looks_like_buffer_size(self.options, param_n0) and _name_looks_like_buffer_standard_or_template(
            self.options, param_n1
        ):
            return True
        return False

    def _is_stride_param(self, idx_param: int) -> bool:
        """For `stride` parameters"""
        param = self._param(idx_param)
        param_default_value = param.default_value()
        return param_default_value.strip().startswith("sizeof")

    def _last_template_buffer_param(self) -> Optional[CppParameter]:
        params = self.function_infos.parameter_list.parameters

        def is_template_buffer(param):
            return _looks_like_param_template_buffer(self.options, param)

        template_buffer_params = list(filter(is_template_buffer, params))
        if len(template_buffer_params) == 0:
            return None
        else:
            return template_buffer_params[-1]

    def _is_buffer_template_or_not(self, idx_param: int) -> bool:
        """
        In this example:
        foo(Widget *widgets, float *buf1, const uint_32_t *buf2, int bufs_count);
                - widgets is not a buffer (type Widget is not acceptable, see options)
                - buf2 is a buffer, because it is of an acceptable type, and followed by a buffer size
                - buf2 is a buffer, because it is of an acceptable type, and followed by a series of buffer(s),
                  followed by a buffer size
        """
        nb_params = len(self._params())

        # Test if this is a buffer (optionally followed by other buffers), then followed by a size
        nb_additional_buffers = 0
        nb_max_additional_buffers = 5
        while nb_additional_buffers < nb_max_additional_buffers:
            idx_buffer_param = idx_param + nb_additional_buffers
            idx_size_param = idx_param + nb_additional_buffers + 1
            if idx_size_param >= nb_params:
                return False
            if not _name_looks_like_buffer_standard_or_template(self.options, self._param(idx_buffer_param)):
                return False
            if _name_looks_like_buffer_size(self.options, self._param(idx_size_param)):
                return True
            nb_additional_buffers += 1

        return False

    def _is_buffer_template(self, idx_param: int) -> bool:
        if not self._is_buffer_template_or_not(idx_param):
            return False
        r = _looks_like_param_template_buffer(self.options, self._param(idx_param))
        return r

    def _is_buffer_standard(self, idx_param: int) -> bool:
        if not self._is_buffer_template_or_not(idx_param):
            return False
        r = not _looks_like_param_template_buffer(self.options, self._param(idx_param))
        return r

    def _adapted_cpp_parameters_template_static_cast(self, pyarray_type_char: str) -> str:
        adapted_cpp_params = []
        for idx_param, param in enumerate(self.function_infos.parameter_list.parameters):
            if _looks_like_param_template_buffer(self.options, param):
                param_name = self._buffer_from_pyarray_name(idx_param)
                cpp_type = cpp_to_python.py_array_type_to_cpp_type(pyarray_type_char)
                if self._is_const(idx_param):
                    cpp_type = "const " + cpp_type
                adapted_cpp_param = f"static_cast<{cpp_type} *>({param_name})"
                adapted_cpp_params.append(adapted_cpp_param)
            else:
                adapted_cpp_params.append(self.adapted_inner_param(idx_param))
        r = ", ".join(adapted_cpp_params)
        return r

    def make_adapted_lambda_code_end_template_buffer(self) -> str:
        template_intro = """
            #ifdef _WIN32
            using np_uint_l = uint32_t;
            using np_int_l = int32_t;
            #else
            using np_uint_l = uint64_t;
            using np_int_l = int64_t;
            #endif
            // call the correct template version by casting
            char {template_buffer_name}_type = {template_buffer_name}.dtype().char_();
        """

        template_loop_type = """
            {maybe_else}if ({template_buffer_name}_type == '{pyarray_type_char}')
            {_i_}{maybe_return}{function_or_lambda_to_call}({adapted_cpp_parameters_with_static_cast});
        """

        template_outro = """
            // If we reach this point, the array type is not supported!
            else
            {_i_}throw std::runtime_error(std::string("Bad array type ('") + {template_buffer_name}_type + "') for param {template_buffer_name}");
        """  # noqa

        def process_templates() -> str:
            options = self.options

            # Fill _i_
            _i_ = options._indent_cpp_spaces()

            # Fill template_buffer_name
            _template_buffer_param = self._last_template_buffer_param()
            assert _template_buffer_param is not None
            template_buffer_name = _template_buffer_param.decl.decl_name

            # Fill function_or_lambda_to_call
            if self.adapted_function.lambda_to_call is not None:
                function_or_lambda_to_call = self.adapted_function.lambda_to_call
            else:
                if self.adapted_function.is_method():
                    function_or_lambda_to_call = (
                        "self." + self.adapted_function.cpp_adapted_function.function_name_with_specialization()
                    )
                else:
                    function_or_lambda_to_call = (
                        self.adapted_function.cpp_adapted_function.qualified_function_name_with_specialization()
                    )

            # Fill maybe_return
            _fn_return_type = self.function_infos.str_full_return_type()
            maybe_return = "" if _fn_return_type == "void" else "return "

            #
            # Apply replacements
            #
            full_code = ""

            # Add intro
            intro = template_intro
            intro = code_utils.unindent_code(intro, flag_strip_empty_lines=True)
            intro = code_utils.replace_in_string(intro, {"template_buffer_name": template_buffer_name})

            full_code += intro + "\n"

            # Add loop code
            for i, cpp_numeric_type in enumerate(self.options._fn_params_buffer_types_list()):
                pyarray_type_char = cpp_to_python.cpp_type_to_py_array_type(cpp_numeric_type)

                # fill maybe_else
                maybe_else = "" if i == 0 else "else "

                # Fill adapted_cpp_parameters_with_static_cast
                adapted_cpp_parameters_with_static_cast = self._adapted_cpp_parameters_template_static_cast(
                    pyarray_type_char
                )

                loop_code = code_utils.unindent_code(template_loop_type, flag_strip_empty_lines=True) + "\n"
                loop_code = code_utils.replace_in_string(
                    loop_code,
                    {
                        "_i_": _i_,
                        "maybe_else": maybe_else,
                        "template_buffer_name": template_buffer_name,
                        "pyarray_type_char": pyarray_type_char,
                        "maybe_return": maybe_return,
                        "function_or_lambda_to_call": function_or_lambda_to_call,
                        "adapted_cpp_parameters_with_static_cast": adapted_cpp_parameters_with_static_cast,
                    },
                )

                full_code += loop_code

            # Add outro
            outro = template_outro
            outro = code_utils.unindent_code(outro, flag_strip_empty_lines=True)
            outro = code_utils.replace_in_string(
                outro,
                {
                    "_i_": _i_,
                    "template_buffer_name": template_buffer_name,
                },
            )

            full_code += outro
            return full_code

        code = process_templates()
        return code

    def _new_param_buffer_standard(self, idx_param: int) -> CppParameter:
        new_param = copy.deepcopy(self._param(idx_param))
        new_param.decl.cpp_type.typenames = ["py::array"]
        new_param.decl.cpp_type.modifiers = ["&"]
        if self._is_const(idx_param):
            new_param.decl.cpp_type.specifiers = ["const"]
        else:
            new_param.decl.cpp_type.specifiers = []
        return new_param

    def _adapted_param_buffer_size(self, idx_param: int) -> str:
        param = self._param(idx_param)
        raw_size_type = param.decl.cpp_type.typenames[0]
        count_variable = self._pyarray_count(idx_param)
        r = f"static_cast<{raw_size_type}>({count_variable})"
        return r

    def _param_name(self, idx_param: int) -> str:
        return self._param(idx_param).decl.decl_name

    def _is_const(self, idx_param: int) -> bool:
        r = "const" in self._param(idx_param).decl.cpp_type.specifiers
        return r

    def _buffer_from_pyarray_name(self, idx_param: int) -> str:
        return f"{self._param_name(idx_param)}_from_pyarray"

    def _last_idx_buffer_param_before(self, idx_param: int) -> Optional[int]:
        r = None
        for i, param in enumerate(self.function_infos.parameter_list.parameters):
            if i <= idx_param and _name_looks_like_buffer_standard_or_template(self.options, param):
                r = i
        return r

    def _pyarray_count(self, idx_param: int) -> str:
        last_idx_buffer_param = self._last_idx_buffer_param_before(idx_param)
        if last_idx_buffer_param is None:
            raise SrcmlcppException("No previous buffer param!")
        return f"{self._param_name(last_idx_buffer_param)}_count"

    def _const_space_or_empty(self, idx_param: int) -> str:
        return "const " if self._is_const(idx_param) else ""

    def _original_raw_type(self, idx_param: int) -> str:
        return self._param(idx_param).decl.cpp_type.typenames[0]

    def _adapted_param_buffer_standard(self, idx_param: int) -> str:
        const_space_or_empty = "const " if self._is_const(idx_param) else ""
        r = f"static_cast<{const_space_or_empty}{self._original_raw_type(idx_param)} *>({self._buffer_from_pyarray_name(idx_param)})"  # noqa
        return r

    def _lambda_input_buffer_standard_convert_part(self, idx_param: int) -> str:
        mutable_or_empty = "" if self._is_const(idx_param) else "mutable_"
        mutable_or_const = "const" if self._is_const(idx_param) else "mutable"

        _ = self
        template = f"""
                    // convert py::array to C standard buffer ({mutable_or_const})
                    {_._const_space_or_empty(idx_param)}void * {_._buffer_from_pyarray_name(idx_param)} = {_._param_name(idx_param)}.{mutable_or_empty}data();
                    py::ssize_t {_._pyarray_count(idx_param)} = {_._param_name(idx_param)}.shape()[0];
                """  # noqa
        template = code_utils.unindent_code(template, flag_strip_empty_lines=True) + "\n"
        return template

    def _expected_dtype_char(self, idx_param: int) -> str:
        dtype_char = cpp_to_python.cpp_type_to_py_array_type(self._original_raw_type(idx_param))
        return dtype_char

    def _lambda_input_buffer_standard_check_part(self, idx_param: int) -> str:
        _ = self
        template = f"""
                char {_._param_name(idx_param)}_type = {_._param_name(idx_param)}.dtype().char_();
                if ({_._param_name(idx_param)}_type != '{_._expected_dtype_char(idx_param)}')
                    throw std::runtime_error(std::string(R"msg(
                            Bad type!  Expected a numpy array of native type:
                                        {_._const_space_or_empty(idx_param)}{_._original_raw_type(idx_param)} *
                                    Which is equivalent to
                                        {_._expected_dtype_char(idx_param)}
                                    (using py::array::dtype().char_() as an id)
                        )msg"));
            """
        template = code_utils.unindent_code(template, flag_strip_empty_lines=True) + "\n"
        return template

    def _stride_adapted_name(self, idx_param: int) -> str:
        idx_buffer_param_before = self._last_idx_buffer_param_before(idx_param)
        assert idx_buffer_param_before is not None
        adapted_stride_name = f"{self._param_name(idx_buffer_param_before)}_stride"
        return adapted_stride_name

    def _adapted_param_stride(self, idx_param: int) -> str:
        stride_param = self._param(idx_param)
        stride_adapted_name = self._stride_adapted_name(idx_param)
        stride_param_raw_type = stride_param.decl.cpp_type.typenames[0]
        if stride_param_raw_type != "int":
            r = f"static_cast<{stride_param_raw_type}>({stride_adapted_name})"
        else:
            r = stride_adapted_name
        return r

    def lambda_input_stride_param(self, idx_param: int) -> str:
        stride_param = self._param(idx_param)
        adapted_stride_name = self._stride_adapted_name(idx_param)
        param_stride_name = stride_param.decl.decl_name

        idx_buffer_param_before = self._last_idx_buffer_param_before(idx_param)
        assert idx_buffer_param_before is not None
        buffer_name = self._param_name(idx_buffer_param_before)
        template = f"""
            // process stride default value (which was a sizeof in C++)
            int {adapted_stride_name} = {param_stride_name};
            if ({adapted_stride_name} == -1)
                {adapted_stride_name} = (int){buffer_name}.itemsize();
        """
        template = code_utils.unindent_code(template, flag_strip_empty_lines=True) + "\n"
        return template

    def _new_param_stride(self, idx_param: int) -> CppParameter:
        stride_param = self._param(idx_param)
        new_stride_param = copy.deepcopy(stride_param)
        new_stride_param.decl.cpp_type.typenames = ["int"]
        new_stride_param.decl.initial_value_code = "-1"
        return new_stride_param


def adapt_c_buffers(adapted_function: AdaptedFunction) -> Optional[LambdaAdapter]:
    """
        We want to adapt functions that use C buffers like this:
            MY_API inline int8_t foo(const int8_t* values, int count);
    `

        we will generate a lambda that looks like
            m.def("foo",
                [](py::array & values)
                {
                    auto foo_adapt_c_buffers = [](py::array & values)
                    {
                        // convert py::array to C standard buffer (mutable)
                        void * values_from_pyarray = values.mutable_data();
                        py::ssize_t values_count = values.shape()[0];
                        char values_type = values.dtype().char_();
                        if (values_type != 'b')
                            throw std::runtime_error(std::string(R"msg(
                                    Bad type!  Expected a numpy array of native type:
                                                int8_t *
                                            Which is equivalent to
                                                b
                                            (using py::array::dtype().char_() as an id)
                                )msg"));

                        auto r = foo(static_cast<int8_t *>(values_from_pyarray), static_cast<int8_t>(values_count));
                        return r;
                    };

                    return foo_adapt_c_buffers(values);
                },
                py::arg("values")
            );

    """
    options = adapted_function.options
    helper = _AdaptBuffersHelper(options, adapted_function)

    if not helper.shall_adapt():
        return None

    lambda_adapter = LambdaAdapter()
    lambda_adapter.new_function_infos = copy.deepcopy(adapted_function.cpp_adapted_function)

    new_function_params: list[CppParameter] = []

    for idx_param, _old_param in enumerate(adapted_function.cpp_adapted_function.parameter_list.parameters):
        # Create new calling param
        new_param = helper.new_visible_interface_param(idx_param)
        if new_param is not None:
            new_function_params.append(new_param)
        # Fill lambda_input
        lambda_input = helper.lambda_input(idx_param)
        if lambda_input is not None:
            if len(lambda_adapter.lambda_input_code) > 0:
                lambda_adapter.lambda_input_code += "\n"
            lambda_adapter.lambda_input_code += lambda_input
        # Fill adapted_cpp_parameter_list (those that will call the original C style function)
        adapted_param = helper.adapted_inner_param(idx_param)
        lambda_adapter.adapted_cpp_parameter_list.append(adapted_param)

    # replaces _make_adapted_lambda_code_end() for buffers (which are more complex)
    if helper.has_template_buffer_param():
        lambda_adapter.lambda_template_end = helper.make_adapted_lambda_code_end_template_buffer()

    lambda_adapter.new_function_infos.parameter_list.parameters = new_function_params
    lambda_adapter.lambda_name = adapted_function.cpp_adapted_function.function_name + "_adapt_c_buffers"

    return lambda_adapter
