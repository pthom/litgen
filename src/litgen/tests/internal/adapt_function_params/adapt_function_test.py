from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from codemanip import code_utils

import srcmlcpp
from srcmlcpp import srcmlcpp_main
from srcmlcpp.cpp_types import CppFunctionDecl

import litgen


@dataclass
class AdaptedFunction2(CppFunctionDecl):
    function_infos: CppFunctionDecl
    parent_struct_name: str
    cpp_adapter_code: Optional[str] = None
    lambda_to_call: Optional[str] = None

    def __init__(self, function_infos: CppFunctionDecl, parent_struct_name: str):
        self.__dict__ = {**function_infos.__dict__, **self.__dict__}
        self.function_infos = function_infos
        self.parent_struct_name = parent_struct_name
        self.cpp_adapter_code = None
        self.lambda_to_call = None

    def is_method(self):
        return len(self.parent_struct_name) > 0


def test_inherit():
    options = srcmlcpp.SrcmlcppOptions()
    code = "void Foo();"
    cpp_function = srcmlcpp_main.code_first_child_of_type(options, CppFunctionDecl, code)
    assert isinstance(cpp_function, CppFunctionDecl)
    _ = AdaptedFunction2(cpp_function, "Foo")


def test_lambda_correctly_returns_reference():
    """
    Test for check the "auto& lambda_result" has a reference
    """
    options = litgen.LitgenOptions()
    code = """
    class MyClass {
    public:
        MyClass& setArray(const uint8_t arr[20]) {
            memcpy(_signature, arr, sizeof(arr));
            return *this;
        }
    private:
        uint8_t _arr[20];
    };
    """

    generated_code = litgen.generate_code(options, code)
    code_utils.assert_are_codes_equal(
        generated_code.pydef_code,
        """
        auto pyClassMyClass =
            py::class_<MyClass>
                (m, "MyClass", "")
            .def(py::init<>()) // implicit default constructor
            .def("set_array",
                [](MyClass & self, const std::array<uint8_t, 20>& arr) -> MyClass &
                {
                    auto setArray_adapt_fixed_size_c_arrays = [&self](const std::array<uint8_t, 20>& arr) -> MyClass &
                    {
                        auto& lambda_result = self.setArray(arr.data());
                        return lambda_result;
                    };

                    return setArray_adapt_fixed_size_c_arrays(arr);
                },     py::arg("arr"))
            ;
    """,
    )
