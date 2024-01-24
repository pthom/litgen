# pyright: reportAttributeAccessIssue=false
from __future__ import annotations
from codemanip import code_utils

import srcmlcpp
from srcmlcpp.cpp_types import CppElement, CppElementsVisitorEvent, CppFunctionDecl, CppAccessType, CppElementComments


def test_str_code():
    options = srcmlcpp.SrcmlcppOptions()
    code = code_utils.unindent_code(
        """
    struct Parent {
    public:
      int x=0;
    #ifdef BLAH
    int y = 4;
    #endif
    };
    """,
        flag_strip_empty_lines=True,
    )

    struct = srcmlcpp.srcmlcpp_main.code_first_struct(options, code)
    code_utils.assert_are_codes_equal(
        struct.str_code(),
        """
        struct Parent
        {
        public: // <default_access_type/>
        public:
            int x = 0;
            #ifdef BLAH
            int y = 4;
            #endif
        };
    """,
    )
    assert struct.str_code_verbatim() == code

    options.header_filter_preprocessor_regions = True
    struct = srcmlcpp.srcmlcpp_main.code_first_struct(options, code)
    code_utils.assert_are_codes_equal(
        struct.str_code(),
        """
        struct Parent
        {
        public: // <default_access_type/>
        public:
            int x = 0;
        };
    """,
    )


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
    assert struct.has_user_defined_constructor()
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
    assert user_defined_copy_constructor.access_type_if_method() == srcmlcpp.CppAccessType.protected


def test_destructor():
    options = srcmlcpp.SrcmlcppOptions()
    code = """
    struct Foo
    {
        ~Foo();
    };
    """
    cpp_unit = srcmlcpp.code_to_cpp_unit(options, code)
    f = cpp_unit.all_functions_recursive()[0]
    assert f.is_destructor()


def test_struct_mix():
    """
    Some tests for:
        CppStruct.qualified_class_name()
        CppStruct.class_name_with_specialization()
        CppStruct.has_base_classes()
        CppStruct.base_classes()
        CppStruct.get_members()
        CppStruct.get_methods()
        CppStruct.is_final()
        CppStruct.is_virtual()
        CppStruct.is_template()

        CppStruct.with_specialized_template()
        CppStruct.is_template_fully_specialized()
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
    assert len(parent.get_members_with_access_type()) == 0
    assert len(parent.get_methods()) == 0
    assert parent.class_name == "Parent"
    assert parent.qualified_class_name() == "Ns::Parent"
    assert parent.qualified_class_name_with_specialization() == "Ns::Parent"
    assert not parent.is_final()
    assert not parent.is_virtual()
    assert not parent.is_template()

    # Test on child
    assert child.has_base_classes()
    child_base_classes = child.base_classes()
    assert len(child_base_classes) == 1
    access_type, child_base_class = child_base_classes[0]
    assert access_type == srcmlcpp.CppAccessType.public
    assert child_base_class is parent
    assert len(child.get_members_with_access_type()) == 0
    assert len(child.get_methods()) == 2
    assert child.class_name == "Child"
    assert child.qualified_class_name() == "Ns::Child"
    assert child.qualified_class_name_with_specialization() == "Ns::Child"
    assert not child.is_final()
    assert child.is_virtual()
    assert not child.is_template()

    # Test on frankenstein
    assert frankenstein.has_base_classes()
    frankenstein_base_classes = frankenstein.base_classes()
    assert len(frankenstein_base_classes) == 1
    access_type, frankenstein_base_class = frankenstein_base_classes[0]
    assert access_type == srcmlcpp.CppAccessType.protected
    assert frankenstein_base_class is child
    assert len(frankenstein.get_members_with_access_type()) == 0
    assert len(frankenstein.get_methods()) == 1
    assert frankenstein.class_name == "Frankenstein"
    assert frankenstein.qualified_class_name() == "Ns::Frankenstein"
    assert frankenstein.class_name_with_specialization() == "Frankenstein"
    assert frankenstein.is_final()
    assert frankenstein.is_virtual()
    assert frankenstein.is_template()
    # Specialize frankenstein once
    frankenstein1 = frankenstein.with_specialized_template(srcmlcpp.CppTemplateSpecialization.from_type_str("int"))
    assert frankenstein1 is not None
    assert frankenstein1.qualified_class_name_with_specialization() == "Ns::Frankenstein<int>"
    assert not frankenstein1.is_template_fully_specialized()
    # Specialize frankenstein again
    frankenstein2 = frankenstein1.with_specialized_template(srcmlcpp.CppTemplateSpecialization.from_type_str("double"))
    assert frankenstein2 is not None
    assert frankenstein2.qualified_class_name_with_specialization() == "Ns::Frankenstein<int, double>"
    assert frankenstein2.is_template_fully_specialized()

    # Test on specialized Inner
    frankenstein2_inner_structs = frankenstein2.get_elements(
        access_type=srcmlcpp.CppAccessType.private, element_type=srcmlcpp.CppStruct
    )
    assert len(frankenstein2_inner_structs) == 1
    f2_inner = frankenstein2_inner_structs[0]
    inner_specialized_code = f2_inner.str_code()
    code_utils.assert_are_codes_equal(
        inner_specialized_code,
        """
        struct Inner
        {
        public: // <default_access_type/>
            int t;
            double u;
            int get_t()<unprocessed_block/>
        };
    """,
    )


def test_methods():
    code = """
        struct Foo
        {
            Foo() {};
            void dummy();
        };
        void fn();
    """
    options = srcmlcpp.SrcmlcppOptions()
    cpp_unit = srcmlcpp.code_to_cpp_unit(options, code)

    nb_found = 0

    def visitor_check_methods(cpp_element: CppElement, event: CppElementsVisitorEvent, depth: int) -> None:
        nonlocal nb_found
        if event == CppElementsVisitorEvent.OnElement and isinstance(cpp_element, CppFunctionDecl):
            nb_found += 1
            if cpp_element.function_name == "Foo":
                assert cpp_element.is_method()
                assert cpp_element.is_constructor()
                assert cpp_element.parent_struct_name_if_method() == "Foo"
            if cpp_element.function_name == "dummy":
                assert cpp_element.is_method()
                assert not cpp_element.is_constructor()
                assert cpp_element.parent_struct_name_if_method() == "Foo"
            if cpp_element.function_name == "fn":
                assert not cpp_element.is_method()
                assert not cpp_element.is_constructor()
                assert cpp_element.parent_struct_name_if_method() is None

    cpp_unit.visit_cpp_breadth_first(visitor_check_methods)

    assert nb_found == 3


def test_add_block():
    options = srcmlcpp.SrcmlcppOptions()
    code = """
            struct Foo
            {
                int a;
            };
    """

    struct = srcmlcpp.srcmlcpp_main.code_first_struct(options, code)

    struct.add_access_block(access_type=CppAccessType.private)
    new_code = struct.str_code()
    code_utils.assert_are_codes_equal(
        new_code,
        """
            struct Foo
            {
            public: // <default_access_type/>
                int a;
            private:
            };
       """,
    )

    comments = CppElementComments.from_comments("Artificial\n public block", "Hey!")
    struct.add_access_block(access_type=CppAccessType.public, comments=comments)
    new_code = struct.str_code()
    code_utils.assert_are_codes_equal(
        new_code,
        """
            struct Foo
            {
            public: // <default_access_type/>
                int a;
            private:
            // Artificial
            //  public block
            public: // Hey!
            };
       """,
    )


def test_add_method():
    options = srcmlcpp.SrcmlcppOptions()
    code = """
            struct Foo
            {
                int a;
            };
    """
    struct = srcmlcpp.srcmlcpp_main.code_first_struct(options, code)

    struct.add_method("int get_a() { return a; }", CppAccessType.public)
    code_utils.assert_are_codes_equal(
        struct.str_code(),
        """
            struct Foo
            {
            public: // <default_access_type/>
                int a;
                int get_a()<unprocessed_block/>
            };
    """,
    )

    method = struct.get_methods()[0]
    code_utils.assert_are_codes_equal(method.str_code_verbatim(), "int get_a() { return a; }")

    comments = CppElementComments.from_comments("This is a super private method\nDon't touch", "I'm looking at you!")
    struct.add_method("void set_a(int _a) { a = _a; }", CppAccessType.private, comments)
    code_utils.assert_are_codes_equal(
        struct.str_code(),
        """
            struct Foo
            {
            public: // <default_access_type/>
                int a;
                int get_a()<unprocessed_block/>
            private:
                // This is a super private method
                // Don't touch
                void set_a(int _a)<unprocessed_block/> // I'm looking at you!
            };
    """,
    )
