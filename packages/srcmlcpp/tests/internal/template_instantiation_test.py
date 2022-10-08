from codemanip import code_utils

from srcmlcpp.srcml_types import *
import srcmlcpp


def instantiate_function(function_code: str, cpp_type_str: str, template_name: str = "") -> Optional[CppFunctionDecl]:
    srcml_options = srcmlcpp.SrcmlOptions()
    cpp_unit = srcmlcpp.code_to_cpp_unit(srcml_options, function_code)
    f = cpp_unit.all_functions()[0]
    f_inst = f.with_instantiated_template(srcmlcpp.TemplateInstantiationSpec(cpp_type_str, template_name))
    return f_inst


def instantiate_class(class_code: str, cpp_type_str: str, template_name: str = "") -> Optional[CppStruct]:
    srcml_options = srcmlcpp.SrcmlOptions()
    cpp_unit = srcmlcpp.code_to_cpp_unit(srcml_options, class_code)
    c = cpp_unit.all_structs_recursive()[0]
    c_inst = c.with_instantiated_template(srcmlcpp.TemplateInstantiationSpec(cpp_type_str, template_name))
    return c_inst


def test_instantiate_function():
    # Case 1: instantiate for a templated function
    #    The name f becomes f<int>
    code = "template<typename T> T f();"
    f_inst = instantiate_function(code, "int")
    code_utils.assert_are_codes_equal(f_inst, "int f<int>();")

    # Case 2: instantiate for non templated function
    #         (this could be a non template method of a template class)
    #    f become f<int>
    code = "T f();"
    f_inst = instantiate_function(code, "int", "T")
    code_utils.assert_are_codes_equal(f_inst, "int f();")

    # Case 3 : instantiate with complex dependent parameter type
    code = "template<typename T> T sum2(std::array<T, 2> values);"
    code_utils.assert_are_codes_equal(instantiate_function(code, "int"), "int sum2<int>(std::array<int, 2> values);")


# def test_instantiate_class():
#     code = """
#     template<typename T>
#     struct Foo
#     {
#         T value0, value1;
#         int x, y;
#
#         std::array<T, 2> getValue(const T& m);
#
#         struct Inner
#         {
#             T inner_values[2];
#         };
#
#         std::function<T(T)> my_function();
#     };
#     """
#     c_inst = instantiate_class(code, "unsigned int")
#     code_utils.assert_are_codes_equal(str(c_inst), """
#         struct Foo
#         {
#             public:// <default_access_type/>
#                 unsigned int value0;
#                 unsigned int value1;
#                 int x;
#                 int y;
#
#                 std::array<unsigned int, 2> getValue(const unsigned int & m);
#
#                 struct Inner
#                 {
#                     public:// <default_access_type/>
#                         unsigned int inner_values[2];
#                 };
#
#                 std::function<unsigned int(unsigned int)> my_function();
#         };
#     """)
