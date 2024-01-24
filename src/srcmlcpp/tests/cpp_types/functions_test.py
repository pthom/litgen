# pyright: reportAttributeAccessIssue=false
from __future__ import annotations
from codemanip import code_utils

import srcmlcpp


# There are lots of other tests:
# - inside classes_tests.py (methods related tests)
# - inside template_tests.py (template related tests)
# - inside litgen


def test_functions():
    options = srcmlcpp.SrcmlcppOptions()

    f = srcmlcpp.srcmlcpp_main.code_first_function_decl(options, "Foo f();")
    assert f.return_type.typenames == ["Foo"]
    assert not f.is_static()
    assert not f.is_const()
    assert len(f.specifiers) == 0
    assert not f.is_template()
    assert not f.is_arrow_notation_return_type()

    f = srcmlcpp.srcmlcpp_main.code_first_function_decl(options, "static inline virtual Foo* f();")
    assert f.is_static()
    assert not f.is_operator()
    assert not f.is_template()
    assert not f.is_virtual_method()  # no parent struct here
    assert f.returns_pointer()


def test_arrow_return():
    options = srcmlcpp.SrcmlcppOptions()
    f = srcmlcpp.srcmlcpp_main.code_first_function_decl(options, "auto f() -> Foo;")
    assert f.return_type.typenames == ["auto", "Foo"]
    assert not f.is_static()
    assert not f.is_const()
    assert len(f.specifiers) == 0
    assert not f.is_template()
    assert f.is_arrow_notation_return_type()
    assert f.str_code() == "auto f() -> Foo;"

    f = srcmlcpp.srcmlcpp_main.code_first_function_decl(options, "auto f() {}")
    assert not f.is_arrow_notation_return_type()
    assert f.is_inferred_return_type()
    assert f.str_code() == "auto f()<unprocessed_block/>"


def test_operator():
    options = srcmlcpp.SrcmlcppOptions()
    # Call operator
    f = srcmlcpp.srcmlcpp_main.code_first_function_decl(options, "int operator()(int rhs);")
    assert f.is_operator()
    assert f.operator_name() == "()"
    assert f.return_type.str_code() == "int"
    # + operator
    f = srcmlcpp.srcmlcpp_main.code_first_function_decl(options, "int operator+(int rhs);")
    assert f.is_operator()
    assert f.operator_name() == "+"
    assert f.return_type.str_code() == "int"
    # cast operator
    f = srcmlcpp.srcmlcpp_main.code_first_function_decl(options, "operator ImVec4() const;")
    assert f.is_operator()
    assert f.operator_name() == "ImVec4"
    assert not hasattr(f, "return_type")
    # inline cast operator
    f = srcmlcpp.srcmlcpp_main.code_first_function_decl(options, "inline operator ImVec4() const;")
    assert f.is_operator()
    assert f.operator_name() == "ImVec4"
    assert f.return_type.str_code() == "inline"


def test_with_qualified_types():
    code = """
        namespace Ns {
            struct S {};
            enum class E { a = 0 };
            void f1(S s);
            int f2(int);
            void f3(S s = S());
            void f4(int v = f2(4));
            void f5(E e = E::a);
        }
    """
    options = srcmlcpp.SrcmlcppOptions()
    cpp_unit = srcmlcpp.code_to_cpp_unit(options, code)
    functions = cpp_unit.all_functions_recursive()
    f1 = functions[0]
    f2 = functions[1]
    f3 = functions[2]
    f4 = functions[3]
    f5 = functions[4]

    f1_qualified = f1.with_qualified_types()
    code_utils.assert_are_codes_equal(f1.str_code(), "void f1(S s);")
    code_utils.assert_are_codes_equal(f1_qualified.str_code(), "void f1(Ns::S s);")
    assert f1_qualified is not f1

    f2_qualified = f2.with_qualified_types()
    code_utils.assert_are_codes_equal(f2.str_code(), "int f2(int );")
    code_utils.assert_are_codes_equal(f2_qualified.str_code(), "int f2(int );")
    assert f2_qualified is f2

    f3_qualified = f3.with_qualified_types()
    code_utils.assert_are_codes_equal(f3.str_code(), "void f3(S s = S());")
    code_utils.assert_are_codes_equal(f3_qualified.str_code(), "void f3(Ns::S s = Ns::S());")
    assert f3_qualified is not f3

    f4_qualified = f4.with_qualified_types()
    code_utils.assert_are_codes_equal(f4.str_code(), "void f4(int v = f2(4));")
    code_utils.assert_are_codes_equal(f4_qualified.str_code(), "void f4(int v = Ns::f2(4));")
    assert f4_qualified is not f4

    f5_qualified = f5.with_qualified_types()
    code_utils.assert_are_codes_equal(f5.str_code(), "void f5(E e = E::a);")
    # s = f5_qualified.str_code()
    # code_utils.assert_are_codes_equal(f5_qualified.str_code(), "void f5(Ns::E e = Ns::E::a);")
    assert f5_qualified is not f5
