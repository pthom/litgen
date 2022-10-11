import srcmlcpp


def test_constructor_destructor():
    options = srcmlcpp.SrcmlcppOptions()

    code = """
        struct Foo {
        };
    """
    struct = srcmlcpp.srcmlcpp_main.code_first_struct(options, code)
    assert not struct.has_deleted_default_constructor()
    assert not struct.has_user_defined_constructor()
    assert struct.get_user_defined_copy_constructor() is None
    assert not struct.has_private_destructor()

    code = """
        struct Foo {
            // If a struct has only one constructor which is = default,
            // the struct will not be considered as containing a user defined constructor
            Foo() = default;
        private:
            ~Foo();
        };
    """
    struct = srcmlcpp.srcmlcpp_main.code_first_struct(options, code)
    assert not struct.has_deleted_default_constructor()
    assert not struct.has_user_defined_constructor()
    assert struct.get_user_defined_copy_constructor() is None
    assert struct.has_private_destructor()

    code = """
        struct Foo {
            Foo() = delete;
            Foo(int v);
            ~Foo();
        };
    """
    struct = srcmlcpp.srcmlcpp_main.code_first_struct(options, code)
    assert struct.has_deleted_default_constructor()
    assert struct.has_user_defined_constructor()
    assert struct.get_user_defined_copy_constructor() is None
    assert not struct.has_private_destructor()

    code = """
        class Foo {
        public:
            Foo();
            ~Foo();
        protected:
            Foo(const Foo& other);
        };
    """
    struct = srcmlcpp.srcmlcpp_main.code_first_struct(options, code)
    assert not struct.has_deleted_default_constructor()
    assert struct.has_user_defined_constructor()
    assert not struct.has_private_destructor()
    # Test user_defined_copy_constructor
    user_defined_copy_constructor = struct.get_user_defined_copy_constructor()
    assert user_defined_copy_constructor is not None
    assert user_defined_copy_constructor.access_type_if_method() == srcmlcpp.CppAccessTypes.protected
