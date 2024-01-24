from __future__ import annotations
import os
import sys

from codemanip import code_utils

from srcmlcpp import srcmlcpp_main

import litgen
from litgen.internal import LitgenContext
from litgen.internal.adapted_types import AdaptedFunction


_THIS_DIR = os.path.dirname(__file__)
sys.path.append(_THIS_DIR + "/../..")


def gen_pydef_code(code: str) -> str:
    options = litgen.LitgenOptions()
    options.fn_params_replace_buffer_by_array__regex = r".*"
    options.srcmlcpp_options.functions_api_prefixes = "MY_API"
    lg_context = LitgenContext(options)

    cpp_function = srcmlcpp_main.code_first_function_decl(options.srcmlcpp_options, code)
    adapted_function = AdaptedFunction(lg_context, cpp_function, False)
    generated_code = adapted_function.str_pydef()
    return generated_code


def test_mutable_buffer_return_int():
    code = """
    MY_API int foo(uint32_t *buf, size_t count);
    """
    generated_code = gen_pydef_code(code)
    # logging. warning("\n" + generated_code)
    code_utils.assert_are_codes_equal(
        generated_code,
        """
        m.def("foo",
            [](py::array & buf) -> int
            {
                auto foo_adapt_c_buffers = [](py::array & buf) -> int
                {
                    // convert py::array to C standard buffer (mutable)
                    void * buf_from_pyarray = buf.mutable_data();
                    py::ssize_t buf_count = buf.shape()[0];
                    char buf_type = buf.dtype().char_();
                    if (buf_type != 'I')
                        throw std::runtime_error(std::string(R"msg(
                                Bad type!  Expected a numpy array of native type:
                                            uint32_t *
                                        Which is equivalent to
                                            I
                                        (using py::array::dtype().char_() as an id)
                            )msg"));

                    auto lambda_result = foo(static_cast<uint32_t *>(buf_from_pyarray), static_cast<size_t>(buf_count));
                    return lambda_result;
                };

                return foo_adapt_c_buffers(buf);
            },     py::arg("buf"));
        """,
    )


def test_const_buffer_return_void_stride():
    code = """
    MY_API void foo(const uint32_t *buf, size_t count, size_t stride = sizeof(uint32_t));
    """
    generated_code = gen_pydef_code(code)
    # logging. warning("\n" + generated_code)
    code_utils.assert_are_codes_equal(
        generated_code,
        """
        m.def("foo",
            [](const py::array & buf, int stride = -1)
            {
                auto foo_adapt_c_buffers = [](const py::array & buf, int stride = -1)
                {
                    // convert py::array to C standard buffer (const)
                    const void * buf_from_pyarray = buf.data();
                    py::ssize_t buf_count = buf.shape()[0];
                    char buf_type = buf.dtype().char_();
                    if (buf_type != 'I')
                        throw std::runtime_error(std::string(R"msg(
                                Bad type!  Expected a numpy array of native type:
                                            const uint32_t *
                                        Which is equivalent to
                                            I
                                        (using py::array::dtype().char_() as an id)
                            )msg"));

                    // process stride default value (which was a sizeof in C++)
                    int buf_stride = stride;
                    if (buf_stride == -1)
                        buf_stride = (int)buf.itemsize();

                    foo(static_cast<const uint32_t *>(buf_from_pyarray), static_cast<size_t>(buf_count), static_cast<size_t>(buf_stride));
                };

                foo_adapt_c_buffers(buf, stride);
            },     py::arg("buf"), py::arg("stride") = -1);
        """,
    )


def test_two_buffers():
    code = """
    MY_API int foo(const uint32_t *buf1, size_t count1, const uint32_t *buf2, size_t count2);
    """
    generated_code = gen_pydef_code(code)
    # logging. warning("\n" + generated_code)
    code_utils.assert_are_codes_equal(
        generated_code,
        """
        m.def("foo",
            [](const py::array & buf1, const py::array & buf2) -> int
            {
                auto foo_adapt_c_buffers = [](const py::array & buf1, const py::array & buf2) -> int
                {
                    // convert py::array to C standard buffer (const)
                    const void * buf1_from_pyarray = buf1.data();
                    py::ssize_t buf1_count = buf1.shape()[0];
                    char buf1_type = buf1.dtype().char_();
                    if (buf1_type != 'I')
                        throw std::runtime_error(std::string(R"msg(
                                Bad type!  Expected a numpy array of native type:
                                            const uint32_t *
                                        Which is equivalent to
                                            I
                                        (using py::array::dtype().char_() as an id)
                            )msg"));

                    // convert py::array to C standard buffer (const)
                    const void * buf2_from_pyarray = buf2.data();
                    py::ssize_t buf2_count = buf2.shape()[0];
                    char buf2_type = buf2.dtype().char_();
                    if (buf2_type != 'I')
                        throw std::runtime_error(std::string(R"msg(
                                Bad type!  Expected a numpy array of native type:
                                            const uint32_t *
                                        Which is equivalent to
                                            I
                                        (using py::array::dtype().char_() as an id)
                            )msg"));

                    auto lambda_result = foo(static_cast<const uint32_t *>(buf1_from_pyarray), static_cast<size_t>(buf1_count), static_cast<const uint32_t *>(buf2_from_pyarray), static_cast<size_t>(buf2_count));
                    return lambda_result;
                };

                return foo_adapt_c_buffers(buf1, buf2);
            },     py::arg("buf1"), py::arg("buf2"));
        """,
    )


def test_template_buffer():
    code = """
    template<typename T> MY_API int foo(const T *buf, size_t count, bool flag);
    """
    generated_code = gen_pydef_code(code)
    # logging. warning("\n" + generated_code)
    code_utils.assert_are_codes_equal(
        generated_code,
        """
        m.def("foo",
            [](const py::array & buf, bool flag) -> int
            {
                auto foo_adapt_c_buffers = [](const py::array & buf, bool flag) -> int
                {
                    // convert py::array to C standard buffer (const)
                    const void * buf_from_pyarray = buf.data();
                    py::ssize_t buf_count = buf.shape()[0];

                    #ifdef _WIN32
                    using np_uint_l = uint32_t;
                    using np_int_l = int32_t;
                    #else
                    using np_uint_l = uint64_t;
                    using np_int_l = int64_t;
                    #endif
                    // call the correct template version by casting
                    char buf_type = buf.dtype().char_();
                    if (buf_type == 'B')
                        return foo(static_cast<const uint8_t *>(buf_from_pyarray), static_cast<size_t>(buf_count), flag);
                    else if (buf_type == 'b')
                        return foo(static_cast<const int8_t *>(buf_from_pyarray), static_cast<size_t>(buf_count), flag);
                    else if (buf_type == 'H')
                        return foo(static_cast<const uint16_t *>(buf_from_pyarray), static_cast<size_t>(buf_count), flag);
                    else if (buf_type == 'h')
                        return foo(static_cast<const int16_t *>(buf_from_pyarray), static_cast<size_t>(buf_count), flag);
                    else if (buf_type == 'I')
                        return foo(static_cast<const uint32_t *>(buf_from_pyarray), static_cast<size_t>(buf_count), flag);
                    else if (buf_type == 'i')
                        return foo(static_cast<const int32_t *>(buf_from_pyarray), static_cast<size_t>(buf_count), flag);
                    else if (buf_type == 'L')
                        return foo(static_cast<const np_uint_l *>(buf_from_pyarray), static_cast<size_t>(buf_count), flag);
                    else if (buf_type == 'l')
                        return foo(static_cast<const np_int_l *>(buf_from_pyarray), static_cast<size_t>(buf_count), flag);
                    else if (buf_type == 'f')
                        return foo(static_cast<const float *>(buf_from_pyarray), static_cast<size_t>(buf_count), flag);
                    else if (buf_type == 'd')
                        return foo(static_cast<const double *>(buf_from_pyarray), static_cast<size_t>(buf_count), flag);
                    else if (buf_type == 'g')
                        return foo(static_cast<const long double *>(buf_from_pyarray), static_cast<size_t>(buf_count), flag);
                    else if (buf_type == 'q')
                        return foo(static_cast<const long long *>(buf_from_pyarray), static_cast<size_t>(buf_count), flag);
                    // If we reach this point, the array type is not supported!
                    else
                        throw std::runtime_error(std::string("Bad array type ('") + buf_type + "') for param buf");
                };

                return foo_adapt_c_buffers(buf, flag);
            },     py::arg("buf"), py::arg("flag"));
        """,
    )
