from litgen import LitgenOptions
import litgen
from codemanip import code_utils
import srcmlcpp


# def test_apply_scoped_identifiers_to_code():
#     from srcmlcpp.cpp_types.scope.cpp_scope_identifiers import apply_scoped_identifiers_to_code
#
#     cpp_code = "std::vector<SubNamespace::Foo> fooList = SubNamespace::CreateFooList();"
#     qualified_scoped_identifiers = ["Main::SubNamespace::Foo", "Main::SubNamespace::CreateFooList"]
#     new_code = apply_scoped_identifiers_to_code(cpp_code, qualified_scoped_identifiers)
#     assert new_code == "std::vector<Main::SubNamespace::Foo> fooList = Main::SubNamespace::CreateFooList();"
#
#     # Test with global scope identifiers
#     cpp_code = "::Foo bar = ::CreateFoo();"
#     qualified_scoped_identifiers = ["Main::Foo", "Main::CreateFoo"]
#     new_code = apply_scoped_identifiers_to_code(cpp_code, qualified_scoped_identifiers)
#     assert new_code == "::Foo bar = ::CreateFoo();"
#
#     # Test with nested scopes
#     cpp_code = "Outer::Inner::Foo bar;"
#     qualified_scoped_identifiers = ["Outer::Inner::Foo", "SomeOther::Foo"]
#     new_code = apply_scoped_identifiers_to_code(cpp_code, qualified_scoped_identifiers)
#     assert new_code == "Outer::Inner::Foo bar;"
#
#     # Test with similar but different scoped identifiers
#     cpp_code = "Namespace1::Foo(); Namespace2::Foo();"
#     qualified_scoped_identifiers = ["Main::Namespace1::Foo", "Main::Namespace2::Foo"]
#     new_code = apply_scoped_identifiers_to_code(cpp_code, qualified_scoped_identifiers)
#     assert new_code == "Main::Namespace1::Foo(); Main::Namespace2::Foo();"
#
#     # Test with no changes needed
#     cpp_code = "int a = 5;"
#     qualified_scoped_identifiers = ["Main::SubNamespace::Foo"]
#     new_code = apply_scoped_identifiers_to_code(cpp_code, qualified_scoped_identifiers)
#     assert new_code == "int a = 5;"
#
#     # Test with an empty string
#     cpp_code = ""
#     qualified_scoped_identifiers = ["Main::SubNamespace::Foo"]
#     new_code = apply_scoped_identifiers_to_code(cpp_code, qualified_scoped_identifiers)
#     assert new_code == ""
#
#     # Test with identifiers in strings or comments
#     cpp_code = 'std::string s = "Foo::Bar"; // Foo::Bar should not be changed'
#     qualified_scoped_identifiers = ["Main::Foo::Bar"]
#     new_code = apply_scoped_identifiers_to_code(cpp_code, qualified_scoped_identifiers)
#     assert new_code == 'std::string s = "Foo::Bar"; // Foo::Bar should not be changed'


def test_scope():
    code = """
    namespace Snippets
    {
        enum Color
        {
            Color_Red,  // Should leak to Snippets scope
        };
        Color col = Color_Red;

        enum class SnippetTheme
        {
            Light,
        };
        SnippetTheme theme = SnippetTheme::Light;

        struct SnippetData
        {
            SnippetTheme Palette = SnippetTheme::Light;
        };

        int foo(int a = 2);

        std::vector<SnippetData> snippetsVector;
    }
    """
    options = srcmlcpp.SrcmlcppOptions()
    cpp_unit = srcmlcpp.code_to_cpp_unit(options, code)

    # Get the scope cache
    _scoped_identifiers = cpp_unit._scope_identifiers._scoped_identifiers
    _scoped_identifiers_repr = repr(_scoped_identifiers)
    # assert scope_cache_qualified_repr == "{Snippets: ['Color', 'Color_Red', 'col', 'SnippetTheme', 'theme', 'SnippetData', 'foo', 'snippetsVector'], Snippets::SnippetTheme: ['Light'], Snippets::SnippetData: ['Palette']}"

    def test_qualified_types() -> None:
        decls = cpp_unit.all_decl_recursive()
        assert len(decls) == 7

        decl_col = decls[1]
        decl_col_qualified = decl_col.with_qualified_types()
        assert decl_col_qualified.str_code() == "Snippets::Color col = Snippets::Color_Red"

        decl_theme = decls[3]
        decl_theme_qualified = decl_theme.with_qualified_types()
        assert decl_theme_qualified.str_code() == "Snippets::SnippetTheme theme = Snippets::SnippetTheme::Light"

        decl_palette = decls[4]
        decl_palette_qualified = decl_palette.with_qualified_types()
        assert decl_palette_qualified.str_code() == "Snippets::SnippetTheme Palette = Snippets::SnippetTheme::Light"

        decl_snippets_vector = decls[6]
        decl_snippets_vector_qualified = decl_snippets_vector.with_qualified_types()
        assert decl_snippets_vector_qualified.str_code() == "std::vector<Snippets::SnippetData> snippetsVector"

    test_qualified_types()


def test_scope_2():
    code = """
        namespace HelloImGui
        {
            namespace ImGuiDefaultSettings
            {
                void LoadDefaultFont_WithFontAwesomeIcons();
            }

            struct RunnerCallbacks
            {
                VoidFunction LoadAdditionalFonts = ImGuiDefaultSettings::LoadDefaultFont_WithFontAwesomeIcons;
            };
        }
    """
    options = srcmlcpp.SrcmlcppOptions()
    cpp_unit = srcmlcpp.code_to_cpp_unit(options, code)

    decls = cpp_unit.all_decl_recursive()
    assert len(decls) == 1

    decl_load_additional_fonts = decls[0]
    decl_load_additional_fonts_qualified = decl_load_additional_fonts.with_qualified_types()
    assert (
        decl_load_additional_fonts_qualified.str_code()
        == "VoidFunction LoadAdditionalFonts = HelloImGui::ImGuiDefaultSettings::LoadDefaultFont_WithFontAwesomeIcons"
    )


def test_decl_qualified_type():
    code = """
        namespace N1 {
            namespace N2 { enum class E2 { a = 0 };  /* enum class! */ }
            namespace N3 {
                enum E3 { a = 0 };        // C enum!

                void g(
                        N2::E2 e2 = N2::E2::a    // => N1::N2::E2 e2 = N1::N2::E2::a       (enum class)
                    );
            }
        }
    """
    options = srcmlcpp.SrcmlcppOptions()
    cpp_unit = srcmlcpp.code_to_cpp_unit(options, code)

    g = cpp_unit.all_functions_recursive()[0]

    params = g.parameter_list.parameters

    # N2::E2 e2 = N2::E2::a,    // => N1::N2::E2 e2 = N1::N2::E2::a (enum class)
    param_e2 = params[0]
    e2_cpp_type = param_e2.decl.cpp_type
    assert e2_cpp_type.str_code() == "N2::E2"
    e2_cpp_type_qualified = e2_cpp_type.with_qualified_types()
    assert e2_cpp_type_qualified.str_code() == "N1::N2::E2"

    e2_value = param_e2.decl.initial_value_code
    assert e2_value == "N2::E2::a"
    e2_value_qualified = param_e2.decl._initial_value_code_with_qualified_types()
    assert e2_value_qualified == "N1::N2::E2::a"


def test_scope_terse_type():
    code = """
    namespace A
    {
        enum class Foo { Foo1 = 0 };
        struct MyClass
        {
            MyClass(A::Foo foo = A::Foo::Foo1);
            Foo foo = Foo::Foo1;
        };
    }

    """
    options = srcmlcpp.SrcmlcppOptions()
    cpp_unit = srcmlcpp.code_to_cpp_unit(options, code)
    functions = cpp_unit.all_functions_recursive()
    assert len(functions) == 1
    ctor = functions[0]
    ctor_qualified = ctor.with_qualified_types()
    ctor_terse = ctor_qualified.with_terse_types()
    assert ctor_terse.str_code() == "MyClass(Foo foo = Foo::Foo1)"


def test_scope4():
    code = """
    namespace N { void Foo() {}  }

    namespace A
    {
        enum class Foo { Foo1 = 0, };

        struct ClassNoDefaultCtor
        {
            ClassNoDefaultCtor(Foo foo = Foo::Foo1);
            Foo foo = Foo::Foo1;
        };
    }
    """
    options = srcmlcpp.SrcmlcppOptions()
    cpp_unit = srcmlcpp.code_to_cpp_unit(options, code)
    ctor = cpp_unit.all_functions_recursive()[1]
    ctor_qualified = ctor.with_qualified_types()
    assert repr(ctor_qualified) == "ClassNoDefaultCtor(A::Foo foo = A::Foo::Foo1)"


def test_scope_vector():
    code = """
    namespace HelloImGui
    {
        enum class EdgeToolbarType
        {
            Top,
            Bottom,
            Left,
            Right
        };

        std::vector<EdgeToolbarType> AllEdgeToolbarTypes();
    }
    """
    options = srcmlcpp.SrcmlcppOptions()
    cpp_unit = srcmlcpp.code_to_cpp_unit(options, code)
    fn = cpp_unit.all_functions_recursive()[0]
    fn_qualified = fn.with_qualified_types()
    assert repr(fn_qualified) == "std::vector<HelloImGui::EdgeToolbarType> AllEdgeToolbarTypes()"
    fn_terse = fn_qualified.with_terse_types()
    assert repr(fn_terse) == "std::vector<EdgeToolbarType> AllEdgeToolbarTypes()"


def test_make_terse_scope():
    from srcmlcpp.cpp_types.scope.cpp_scope_process import make_terse_code, _make_terse_scoped_identifier
    from srcmlcpp.cpp_types.scope.cpp_scope import CppScope

    cpp_code = "N0::N1::N3::S3"
    current_scope = CppScope.from_string("N0::N1::N3")
    new_cpp_code = make_terse_code(cpp_code, current_scope.str_cpp_prefix)
    assert new_cpp_code == "S3"

    scoped_identifier = "N1::N3::S3"
    current_scope = CppScope.from_string("N0::N1::N3")
    new_scoped_identifier = _make_terse_scoped_identifier(scoped_identifier, current_scope.str_cpp)
    assert new_scoped_identifier == "S3"


def test_scope_test_litgen2():
    code = """
    namespace HelloImGui
    {
        struct DockingSplit {};
        struct DockingParams
        {
            DockingParams(std::vector<DockingSplit> dockingSplits = std::vector<DockingSplit>());
            std::vector<DockingSplit>   dockingSplits;
        };
    }
    """
    # options = litgen.LitgenOptions()
    # options.srcmlcpp_options.namespaces_root = ["HelloImGui"]
    # generated_code = litgen.generate_code(options, code)
    # print(generated_code.stub_code)
    options = srcmlcpp.SrcmlcppOptions()
    cpp_unit = srcmlcpp.code_to_cpp_unit(options, code)
    ctor = cpp_unit.all_functions_recursive()[0]
    ctor_qualified = ctor.with_qualified_types()
    assert (
        repr(ctor_qualified)
        == "DockingParams(std::vector<HelloImGui::DockingSplit> dockingSplits = std::vector<HelloImGui::DockingSplit>())"
    )
    ctor_terse = ctor_qualified.with_terse_types()
    assert repr(ctor_terse) == "DockingParams(std::vector<DockingSplit> dockingSplits = std::vector<DockingSplit>())"


def test_scope_with_litgen():
    code = """
    namespace DaftLib
    {
        struct Point
        {
            void *data = nullptr;
            int x = 0, y= 0;
        };
    }
    """
    options = LitgenOptions()
    options.namespaces_root = ["DaftLib"]
    generated_code = litgen.generate_code(options, code)
    code_utils.assert_are_codes_equal(
        generated_code.pydef_code,
        """
        auto pyClassPoint =
            py::class_<DaftLib::Point>
                (m, "Point", "")
            .def(py::init<>([](
            int x = 0, int y = 0)
            {
                auto r = std::make_unique<DaftLib::Point>();
                r->x = x;
                r->y = y;
                return r;
            })
            , py::arg("x") = 0, py::arg("y") = 0
            )
            .def_readwrite("data", &DaftLib::Point::data, "")
            .def_readwrite("x", &DaftLib::Point::x, "")
            .def_readwrite("y", &DaftLib::Point::y, "")
            ;
        """,
    )


def test_make_terse_scoped_identifier():
    from srcmlcpp.cpp_types.scope.cpp_scope_process import _make_terse_scoped_identifier

    assert _make_terse_scoped_identifier("A::B::C", "A::B::C::D") == "C"
    assert _make_terse_scoped_identifier("A::Foo::Foo1", "A") == "Foo::Foo1"  # error: Foo1
    assert _make_terse_scoped_identifier("std::vector", "Main") == "std::vector"  # error! "vector"
    assert _make_terse_scoped_identifier("N1::N3::S3", "N0::N1::N3") == "S3"  # OK

    # N1::N2::S2::s1
    # Context= N0::N1::N3
    # => N2::S2::s1
    scoped_identifier = "N1::N2::S2::s1"
    context = "N0::N1::N3"
    r = _make_terse_scoped_identifier(scoped_identifier, context)
    assert r == "N2::S2::s1"
