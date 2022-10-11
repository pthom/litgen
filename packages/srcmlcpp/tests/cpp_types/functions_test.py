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
    f = srcmlcpp.srcmlcpp_main.code_first_function_decl(options, "int operator()(int rhs);")
    assert f.is_operator()
    assert f.operator_name() == "()"
