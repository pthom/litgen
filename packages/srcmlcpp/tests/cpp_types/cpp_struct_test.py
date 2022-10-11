from codemanip import code_utils

import srcmlcpp


# # Test str_code + str_code_verbatim
# c = parent.str_code()
# cv = parent.str_code_verbatim()
# print("a")


def test_struct_mix():
    """
    Tests
        CppStruct.qualified_class_name()
        CppStruct.class_name_with_instantiation()
        CppStruct.has_base_classes()
        CppStruct.base_classes()
        CppStruct.get_members()
        CppStruct.get_methods()
        CppStruct.is_final()
        CppStruct.is_virtual()
        CppStruct.is_template()
    """

    code = code_utils.unindent_code(
        """
   namespace Ns
    {
        struct Parent {
        };

        struct Child : public Parent {
            virtual int f() { return 0; }
            virtual int g() = 0;
        };

        template<typename T, class U>
        class Frankenstein final: protected Child
        {
            struct Inner {
                T t;
                U u;
                T get_t() { return t; }
            };
            int g() override { return 1; }
        };
    }
    """,
        flag_strip_empty_lines=True,
    )
    options = srcmlcpp.SrcmlcppOptions()
    cpp_unit = srcmlcpp.code_to_cpp_unit(options, code)

    all_structs = cpp_unit.all_structs_recursive()
    assert len(all_structs) == 4

    parent = cpp_unit.find_struct_or_class("Ns::Parent")
    assert parent is not None
    child = cpp_unit.find_struct_or_class("Ns::Child")
    assert child is not None
    frankenstein = cpp_unit.find_struct_or_class("Ns::Frankenstein")
    assert frankenstein is not None
    inner = cpp_unit.find_struct_or_class("Ns::Frankenstein::Inner")
    assert inner is not None

    # Test on parent
    assert not parent.has_base_classes()
    assert len(parent.base_classes()) == 0
    assert len(parent.get_members()) == 0
    assert len(parent.get_methods()) == 0
    assert parent.class_name == "Parent"
    assert parent.qualified_class_name() == "Ns::Parent"
    assert parent.qualified_class_name_with_instantiation() == "Ns::Parent"
    assert not parent.is_final()
    assert not parent.is_virtual()
    assert not parent.is_template()

    # Test on child
    assert child.has_base_classes()
    child_base_classes = child.base_classes()
    assert len(child_base_classes) == 1
    access_type, child_base_class = child_base_classes[0]
    assert access_type == srcmlcpp.CppAccessTypes.public
    assert child_base_class is parent
    assert len(child.get_members()) == 0
    assert len(child.get_methods()) == 2
    assert child.class_name == "Child"
    assert child.qualified_class_name() == "Ns::Child"
    assert child.qualified_class_name_with_instantiation() == "Ns::Child"
    assert not child.is_final()
    assert child.is_virtual()
    assert not child.is_template()

    # Test on frankenstein
    assert frankenstein.has_base_classes()
    frankenstein_base_classes = frankenstein.base_classes()
    assert len(frankenstein_base_classes) == 1
    access_type, frankenstein_base_class = frankenstein_base_classes[0]
    assert access_type == srcmlcpp.CppAccessTypes.protected
    assert frankenstein_base_class is child
    assert len(frankenstein.get_members()) == 0
    assert len(frankenstein.get_methods()) == 1
    assert frankenstein.class_name == "Frankenstein"
    assert frankenstein.qualified_class_name() == "Ns::Frankenstein"
    assert frankenstein.class_name_with_instantiation() == "Frankenstein"
    # s = frankenstein.str_template()
    assert frankenstein.is_final()
    assert frankenstein.is_virtual()
    assert frankenstein.is_template()


"""
'struct Parent
{
public:// <default_access_type/>
};
'
"""

"""
'struct Parent {
        };
'
"""


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
