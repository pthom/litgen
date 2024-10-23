// ============================================================================
// This file was autogenerated
// It is presented side to side with its source: mix_adapters_class_test.h
// It is not used in the compilation
//    (see integration_tests/bindings/pybind_mylib.cpp which contains the full binding
//     code, including this code)
// ============================================================================

#include <nanobind/nanobind.h>
#include <nanobind/stl/string.h>
#include <nanobind/stl/function.h>
#include "mylib_main/mylib.h"

namespace py = nanobind;

// <litgen_glue_code>  // Autogenerated code below! Do not edit!
struct BoxedBool
{
    bool value;
    BoxedBool(bool v = false) : value(v) {}
    std::string __repr__() const { return std::string("BoxedBool(") + std::to_string(value) + ")"; }
};
struct BoxedInt
{
    int value;
    BoxedInt(int v = 0) : value(v) {}
    std::string __repr__() const { return std::string("BoxedInt(") + std::to_string(value) + ")"; }
};
struct BoxedString
{
    std::string value;
    BoxedString(std::string v = "") : value(v) {}
    std::string __repr__() const { return std::string("BoxedString(") + value + ")"; }
};

// </litgen_glue_code> // Autogenerated code end


void py_init_module_mylib(py::module_& m)
{
    // <litgen_pydef> // Autogenerated code below! Do not edit!
    ////////////////////    <generated_from:BoxedTypes>    ////////////////////
    auto pyClassBoxedBool =
        py::class_<BoxedBool>
            (m, "BoxedBool", "")
        .def_rw("value", &BoxedBool::value, "")
        .def(py::init<bool>(),
            py::arg("v") = false)
        .def("__repr__",
            &BoxedBool::__repr__)
        ;


    auto pyClassBoxedInt =
        py::class_<BoxedInt>
            (m, "BoxedInt", "")
        .def_rw("value", &BoxedInt::value, "")
        .def(py::init<int>(),
            py::arg("v") = 0)
        .def("__repr__",
            &BoxedInt::__repr__)
        ;


    auto pyClassBoxedString =
        py::class_<BoxedString>
            (m, "BoxedString", "")
        .def_rw("value", &BoxedString::value, "")
        .def(py::init<std::string>(),
            py::arg("v") = "")
        .def("__repr__",
            &BoxedString::__repr__)
        ;
    ////////////////////    </generated_from:BoxedTypes>    ////////////////////


    ////////////////////    <generated_from:mix_adapters_class_test.h>    ////////////////////

    { // <namespace SomeNamespace>
        py::module_ pyNsSomeNamespace = m.def_submodule("some_namespace", "");
        auto pyNsSomeNamespace_ClassBlah =
            py::class_<SomeNamespace::Blah>
                (pyNsSomeNamespace, "Blah", "struct Blah")
            .def(py::init<>()) // implicit default constructor
            .def("toggle_bool_pointer",
                [](SomeNamespace::Blah & self, BoxedBool & v)
                {
                    auto ToggleBoolPointer_adapt_modifiable_immutable = [&self](BoxedBool & v)
                    {
                        bool * v_boxed_value = & (v.value);

                        self.ToggleBoolPointer(v_boxed_value);
                    };

                    ToggleBoolPointer_adapt_modifiable_immutable(v);
                },
                py::arg("v"),
                "//, int vv[2])")
            .def("toggle_bool_pointer_get_points",
                [](SomeNamespace::Blah & self, BoxedBool & v, BoxedInt & vv_0, BoxedInt & vv_1)
                {
                    auto ToggleBoolPointerGetPoints_adapt_fixed_size_c_arrays = [&self](bool * v, BoxedInt & vv_0, BoxedInt & vv_1)
                    {
                        int vv_raw[2];
                        vv_raw[0] = vv_0.value;
                        vv_raw[1] = vv_1.value;

                        self.ToggleBoolPointerGetPoints(v, vv_raw);

                        vv_0.value = vv_raw[0];
                        vv_1.value = vv_raw[1];
                    };
                    auto ToggleBoolPointerGetPoints_adapt_modifiable_immutable = [&ToggleBoolPointerGetPoints_adapt_fixed_size_c_arrays](BoxedBool & v, BoxedInt & vv_0, BoxedInt & vv_1)
                    {
                        bool * v_boxed_value = & (v.value);

                        ToggleBoolPointerGetPoints_adapt_fixed_size_c_arrays(v_boxed_value, vv_0, vv_1);
                    };

                    ToggleBoolPointerGetPoints_adapt_modifiable_immutable(v, vv_0, vv_1);
                },     py::arg("v"), py::arg("vv_0"), py::arg("vv_1"))
            .def("modify_string",
                [](SomeNamespace::Blah & self, BoxedString & s)
                {
                    auto ModifyString_adapt_modifiable_immutable = [&self](BoxedString & s)
                    {
                        std::string * s_boxed_value = & (s.value);

                        self.ModifyString(s_boxed_value);
                    };

                    ModifyString_adapt_modifiable_immutable(s);
                },     py::arg("s"))
            .def("change_bool_int",
                [](SomeNamespace::Blah & self, const char * label, int value) -> std::tuple<bool, int>
                {
                    auto ChangeBoolInt_adapt_modifiable_immutable_to_return = [&self](const char * label, int value) -> std::tuple<bool, int>
                    {
                        int * value_adapt_modifiable = & value;

                        bool r = self.ChangeBoolInt(label, value_adapt_modifiable);
                        return std::make_tuple(r, value);
                    };

                    return ChangeBoolInt_adapt_modifiable_immutable_to_return(label, value);
                },     py::arg("label"), py::arg("value"))
            .def("add_inside_buffer",
                [](SomeNamespace::Blah & self, py::ndarray<uint8_t> & buffer, uint8_t number_to_add)
                {
                    auto add_inside_buffer_adapt_c_buffers = [&self](py::ndarray<uint8_t> & buffer, uint8_t number_to_add)
                    {
                        // convert py::array to C standard buffer (mutable)
                        void * buffer_from_pyarray = buffer.data();
                        size_t buffer_count = buffer.shape(0);
                        uint8_t buffer_type = buffer.dtype().code;
                        auto expected_type_0 = static_cast<uint8_t>(py::dlpack::dtype_code::UInt);
                        if (buffer_type != expected_type_0)
                            throw std::runtime_error(std::string(R"msg(
                                    Bad type!  Expected a numpy array of native type:
                                                uint8_t *
                                            Which is equivalent to
                                                dtype_code::UInt
                                            (using py::ndarray::dtype().code as an id)
                                )msg"));

                        self.add_inside_buffer(static_cast<uint8_t *>(buffer_from_pyarray), static_cast<size_t>(buffer_count), number_to_add);
                    };

                    add_inside_buffer_adapt_c_buffers(buffer, number_to_add);
                },     py::arg("buffer"), py::arg("number_to_add"))
            .def("const_array2_add",
                [](SomeNamespace::Blah & self, const std::array<int, 2>& values) -> int
                {
                    auto const_array2_add_adapt_fixed_size_c_arrays = [&self](const std::array<int, 2>& values) -> int
                    {
                        auto lambda_result = self.const_array2_add(values.data());
                        return lambda_result;
                    };

                    return const_array2_add_adapt_fixed_size_c_arrays(values);
                },     py::arg("values"))
            .def("c_string_list_total_size",
                [](SomeNamespace::Blah & self, const std::vector<std::string> & items, BoxedInt & output_0, BoxedInt & output_1) -> size_t
                {
                    auto c_string_list_total_size_adapt_fixed_size_c_arrays = [&self](const char * const items[], int items_count, BoxedInt & output_0, BoxedInt & output_1) -> size_t
                    {
                        int output_raw[2];
                        output_raw[0] = output_0.value;
                        output_raw[1] = output_1.value;

                        auto lambda_result = self.c_string_list_total_size(items, items_count, output_raw);

                        output_0.value = output_raw[0];
                        output_1.value = output_raw[1];
                        return lambda_result;
                    };
                    auto c_string_list_total_size_adapt_c_string_list = [&c_string_list_total_size_adapt_fixed_size_c_arrays](const std::vector<std::string> & items, BoxedInt & output_0, BoxedInt & output_1) -> size_t
                    {
                        std::vector<const char *> items_ptrs;
                        items_ptrs.reserve(items.size());
                        for (const auto& v: items)
                            items_ptrs.push_back(v.c_str());
                        int items_count = static_cast<int>(items.size());

                        auto lambda_result = c_string_list_total_size_adapt_fixed_size_c_arrays(items_ptrs.data(), items_count, output_0, output_1);
                        return lambda_result;
                    };

                    return c_string_list_total_size_adapt_c_string_list(items, output_0, output_1);
                },     py::arg("items"), py::arg("output_0"), py::arg("output_1"))
            ;
        { // <namespace SomeInnerNamespace>
            py::module_ pyNsSomeNamespace_NsSomeInnerNamespace = pyNsSomeNamespace.def_submodule("some_inner_namespace", "namespace SomeInnerNamespace");
            pyNsSomeNamespace_NsSomeInnerNamespace.def("toggle_bool_pointer",
                [](BoxedBool & v)
                {
                    auto ToggleBoolPointer_adapt_modifiable_immutable = [](BoxedBool & v)
                    {
                        bool * v_boxed_value = & (v.value);

                        SomeNamespace::SomeInnerNamespace::ToggleBoolPointer(v_boxed_value);
                    };

                    ToggleBoolPointer_adapt_modifiable_immutable(v);
                },
                py::arg("v"),
                "//, int vv[2])");

            pyNsSomeNamespace_NsSomeInnerNamespace.def("toggle_bool_pointer_get_points",
                [](BoxedBool & v, BoxedInt & vv_0, BoxedInt & vv_1)
                {
                    auto ToggleBoolPointerGetPoints_adapt_fixed_size_c_arrays = [](bool * v, BoxedInt & vv_0, BoxedInt & vv_1)
                    {
                        int vv_raw[2];
                        vv_raw[0] = vv_0.value;
                        vv_raw[1] = vv_1.value;

                        SomeNamespace::SomeInnerNamespace::ToggleBoolPointerGetPoints(v, vv_raw);

                        vv_0.value = vv_raw[0];
                        vv_1.value = vv_raw[1];
                    };
                    auto ToggleBoolPointerGetPoints_adapt_modifiable_immutable = [&ToggleBoolPointerGetPoints_adapt_fixed_size_c_arrays](BoxedBool & v, BoxedInt & vv_0, BoxedInt & vv_1)
                    {
                        bool * v_boxed_value = & (v.value);

                        ToggleBoolPointerGetPoints_adapt_fixed_size_c_arrays(v_boxed_value, vv_0, vv_1);
                    };

                    ToggleBoolPointerGetPoints_adapt_modifiable_immutable(v, vv_0, vv_1);
                },     py::arg("v"), py::arg("vv_0"), py::arg("vv_1"));

            pyNsSomeNamespace_NsSomeInnerNamespace.def("modify_string",
                [](BoxedString & s)
                {
                    auto ModifyString_adapt_modifiable_immutable = [](BoxedString & s)
                    {
                        std::string * s_boxed_value = & (s.value);

                        SomeNamespace::SomeInnerNamespace::ModifyString(s_boxed_value);
                    };

                    ModifyString_adapt_modifiable_immutable(s);
                },     py::arg("s"));

            pyNsSomeNamespace_NsSomeInnerNamespace.def("change_bool_int",
                [](const char * label, int value) -> std::tuple<bool, int>
                {
                    auto ChangeBoolInt_adapt_modifiable_immutable_to_return = [](const char * label, int value) -> std::tuple<bool, int>
                    {
                        int * value_adapt_modifiable = & value;

                        bool r = SomeNamespace::SomeInnerNamespace::ChangeBoolInt(label, value_adapt_modifiable);
                        return std::make_tuple(r, value);
                    };

                    return ChangeBoolInt_adapt_modifiable_immutable_to_return(label, value);
                },     py::arg("label"), py::arg("value"));

            pyNsSomeNamespace_NsSomeInnerNamespace.def("add_inside_buffer",
                [](py::ndarray<uint8_t> & buffer, uint8_t number_to_add)
                {
                    auto add_inside_buffer_adapt_c_buffers = [](py::ndarray<uint8_t> & buffer, uint8_t number_to_add)
                    {
                        // convert py::array to C standard buffer (mutable)
                        void * buffer_from_pyarray = buffer.data();
                        size_t buffer_count = buffer.shape(0);
                        uint8_t buffer_type = buffer.dtype().code;
                        auto expected_type_0 = static_cast<uint8_t>(py::dlpack::dtype_code::UInt);
                        if (buffer_type != expected_type_0)
                            throw std::runtime_error(std::string(R"msg(
                                    Bad type!  Expected a numpy array of native type:
                                                uint8_t *
                                            Which is equivalent to
                                                dtype_code::UInt
                                            (using py::ndarray::dtype().code as an id)
                                )msg"));

                        SomeNamespace::SomeInnerNamespace::add_inside_buffer(static_cast<uint8_t *>(buffer_from_pyarray), static_cast<size_t>(buffer_count), number_to_add);
                    };

                    add_inside_buffer_adapt_c_buffers(buffer, number_to_add);
                },     py::arg("buffer"), py::arg("number_to_add"));

            pyNsSomeNamespace_NsSomeInnerNamespace.def("const_array2_add",
                [](const std::array<int, 2>& values) -> int
                {
                    auto const_array2_add_adapt_fixed_size_c_arrays = [](const std::array<int, 2>& values) -> int
                    {
                        auto lambda_result = SomeNamespace::SomeInnerNamespace::const_array2_add(values.data());
                        return lambda_result;
                    };

                    return const_array2_add_adapt_fixed_size_c_arrays(values);
                },     py::arg("values"));

            pyNsSomeNamespace_NsSomeInnerNamespace.def("c_string_list_total_size",
                [](const std::vector<std::string> & items, BoxedInt & output_0, BoxedInt & output_1) -> size_t
                {
                    auto c_string_list_total_size_adapt_fixed_size_c_arrays = [](const char * const items[], int items_count, BoxedInt & output_0, BoxedInt & output_1) -> size_t
                    {
                        int output_raw[2];
                        output_raw[0] = output_0.value;
                        output_raw[1] = output_1.value;

                        auto lambda_result = SomeNamespace::SomeInnerNamespace::c_string_list_total_size(items, items_count, output_raw);

                        output_0.value = output_raw[0];
                        output_1.value = output_raw[1];
                        return lambda_result;
                    };
                    auto c_string_list_total_size_adapt_c_string_list = [&c_string_list_total_size_adapt_fixed_size_c_arrays](const std::vector<std::string> & items, BoxedInt & output_0, BoxedInt & output_1) -> size_t
                    {
                        std::vector<const char *> items_ptrs;
                        items_ptrs.reserve(items.size());
                        for (const auto& v: items)
                            items_ptrs.push_back(v.c_str());
                        int items_count = static_cast<int>(items.size());

                        auto lambda_result = c_string_list_total_size_adapt_fixed_size_c_arrays(items_ptrs.data(), items_count, output_0, output_1);
                        return lambda_result;
                    };

                    return c_string_list_total_size_adapt_c_string_list(items, output_0, output_1);
                },     py::arg("items"), py::arg("output_0"), py::arg("output_1"));
        } // </namespace SomeInnerNamespace>

    } // </namespace SomeNamespace>
    ////////////////////    </generated_from:mix_adapters_class_test.h>    ////////////////////

    // </litgen_pydef> // Autogenerated code end
}