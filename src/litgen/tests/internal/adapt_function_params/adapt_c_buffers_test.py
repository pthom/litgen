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
                    // Check if the array is 1D and C-contiguous
                    if (! (buf.ndim() == 1 && buf.strides(0) == buf.itemsize()) )
                        throw std::runtime_error("The array must be 1D and contiguous");

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
                    // Check if the array is 1D and C-contiguous
                    if (! (buf.ndim() == 1 && buf.strides(0) == buf.itemsize()) )
                        throw std::runtime_error("The array must be 1D and contiguous");

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
                    // Check if the array is 1D and C-contiguous
                    if (! (buf1.ndim() == 1 && buf1.strides(0) == buf1.itemsize()) )
                        throw std::runtime_error("The array must be 1D and contiguous");

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

                    // Check if the array is 1D and C-contiguous
                    if (! (buf2.ndim() == 1 && buf2.strides(0) == buf2.itemsize()) )
                        throw std::runtime_error("The array must be 1D and contiguous");

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
                    // Check if the array is 1D and C-contiguous
                    if (! (buf.ndim() == 1 && buf.strides(0) == buf.itemsize()) )
                        throw std::runtime_error("The array must be 1D and contiguous");

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


def test_nanobind_buffer() -> None:
    code = """
    void foo(uint8_t* buffer, size_t buffer_size);
    """
    options = litgen.LitgenOptions()
    options.fn_params_replace_buffer_by_array__regex = r".*"
    options.bind_library = litgen.BindLibraryType.nanobind
    generated_code = litgen.generate_code(options, code)
    # logging.warning("\n" + generated_code.pydef_code)
    code_utils.assert_are_codes_equal(
        generated_code.pydef_code,
        """
        m.def("foo",
            [](nb::ndarray<> & buffer)
            {
                auto foo_adapt_c_buffers = [](nb::ndarray<> & buffer)
                {
                    // Check if the array is 1D and C-contiguous
                    if (! (buffer.ndim() == 1 && buffer.stride(0) == 1))
                        throw std::runtime_error("The array must be 1D and contiguous");

                    // convert nb::ndarray to C standard buffer (mutable)
                    void * buffer_from_pyarray = buffer.data();
                    size_t buffer_count = buffer.shape(0);
                    // Check the type of the ndarray (generic type and size)
                    //   - Step 1: check the generic type (one of dtype_code::Int, UInt, Float, Bfloat, Complex, Bool = 6);
                    uint8_t dtype_code_python_0 = buffer.dtype().code;
                    uint8_t dtype_code_cpp_0 = static_cast<uint8_t>(nb::dlpack::dtype_code::UInt);
                    if (dtype_code_python_0 != dtype_code_cpp_0)
                        throw std::runtime_error(std::string(R"msg(
                                Bad type! While checking the generic type (dtype_code=UInt)!
                            )msg"));
                    //   - Step 2: check the size of the type
                    size_t size_python_0 = buffer.dtype().bits / 8;
                    size_t size_cpp_0 = sizeof(uint8_t);
                    if (size_python_0 != size_cpp_0)
                        throw std::runtime_error(std::string(R"msg(
                                Bad type! Size mismatch, while checking the size of the type (for param "buffer")!
                            )msg"));

                    foo(static_cast<uint8_t *>(buffer_from_pyarray), static_cast<size_t>(buffer_count));
                };

                foo_adapt_c_buffers(buffer);
            },     nb::arg("buffer"));
        """,
    )


def test_template_buffer_nanobind():
    code = """
    template<typename T> MY_API int foo(const T *buf, size_t count, bool flag);
    """
    options = litgen.LitgenOptions()
    options.fn_params_replace_buffer_by_array__regex = r".*"
    options.bind_library = litgen.BindLibraryType.nanobind
    generated_code = litgen.generate_code(options, code)
    # print("\n" + generated_code.pydef_code)
    code_utils.assert_are_codes_equal(
        generated_code.pydef_code,
        """
        m.def("foo",
            [](const nb::ndarray<> & buf, bool flag) -> MY_API int
            {
                auto foo_adapt_c_buffers = [](const nb::ndarray<> & buf, bool flag) -> MY_API int
                {
                    // Check if the array is 1D and C-contiguous
                    if (! (buf.ndim() == 1 && buf.stride(0) == 1))
                        throw std::runtime_error("The array must be 1D and contiguous");

                    // convert nb::ndarray to C standard buffer (const)
                    const void * buf_from_pyarray = buf.data();
                    size_t buf_count = buf.shape(0);

                    using np_uint_l = uint64_t;
                    using np_int_l = int64_t;

                    // Define a lambda to compute the letter code for the buffer type
                    auto _nanobind_buffer_type_to_letter_code = [](uint8_t dtype_code, size_t sizeof_item)  -> char
                    {
                        #define DCODE(T) static_cast<uint8_t>(nb::dlpack::dtype_code::T)
                            const std::array<std::tuple<uint8_t, size_t, char>, 11> mappings = {{
                                {DCODE(UInt), 1, 'B'}, {DCODE(UInt), 2, 'H'}, {DCODE(UInt), 4, 'I'}, {DCODE(UInt), 8, 'L'},
                                {DCODE(Int), 1, 'b'}, {DCODE(Int), 2, 'h'}, {DCODE(Int), 4, 'i'}, {DCODE(Int), 8, 'l'},
                                {DCODE(Float), 4, 'f'}, {DCODE(Float), 8, 'd'}, {DCODE(Float), 16, 'g'}
                            }};
                        #undef DCODE
                        for (const auto& [code_val, size, letter] : mappings)
                            if (code_val == dtype_code && size == sizeof_item)
                                return letter;
                        throw std::runtime_error("Unsupported dtype");
                    };

                    // Compute the letter code for the buffer type
                    uint8_t dtype_code_buf = buf.dtype().code;
                    size_t sizeof_item_buf = buf.dtype().bits / 8;
                    char buf_type = _nanobind_buffer_type_to_letter_code(dtype_code_buf, sizeof_item_buf);

                    // call the correct template version by casting
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
            },     nb::arg("buf"), nb::arg("flag"));
        """,
    )
