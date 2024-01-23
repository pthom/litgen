from litgen import LitgenOptions
import litgen
from codemanip import code_utils
import srcmlcpp


def test_apply_scoped_identifiers_to_code():
    from srcmlcpp.cpp_types.scope.cpp_scope_identifiers import apply_scoped_identifiers_to_code

    cpp_code = "std::vector<SubNamespace::Foo> fooList = SubNamespace::CreateFooList();"
    qualified_scoped_identifiers = ["Main::SubNamespace::Foo", "Main::SubNamespace::CreateFooList"]
    new_code = apply_scoped_identifiers_to_code(cpp_code, qualified_scoped_identifiers)
    assert new_code == "std::vector<Main::SubNamespace::Foo> fooList = Main::SubNamespace::CreateFooList();"

    # Test with global scope identifiers
    cpp_code = "::Foo bar = ::CreateFoo();"
    qualified_scoped_identifiers = ["Main::Foo", "Main::CreateFoo"]
    new_code = apply_scoped_identifiers_to_code(cpp_code, qualified_scoped_identifiers)
    assert new_code == "::Foo bar = ::CreateFoo();"

    # Test with nested scopes
    cpp_code = "Outer::Inner::Foo bar;"
    qualified_scoped_identifiers = ["Outer::Inner::Foo", "SomeOther::Foo"]
    new_code = apply_scoped_identifiers_to_code(cpp_code, qualified_scoped_identifiers)
    assert new_code == "Outer::Inner::Foo bar;"

    # Test with similar but different scoped identifiers
    cpp_code = "Namespace1::Foo(); Namespace2::Foo();"
    qualified_scoped_identifiers = ["Main::Namespace1::Foo", "Main::Namespace2::Foo"]
    new_code = apply_scoped_identifiers_to_code(cpp_code, qualified_scoped_identifiers)
    assert new_code == "Main::Namespace1::Foo(); Main::Namespace2::Foo();"

    # Test with no changes needed
    cpp_code = "int a = 5;"
    qualified_scoped_identifiers = ["Main::SubNamespace::Foo"]
    new_code = apply_scoped_identifiers_to_code(cpp_code, qualified_scoped_identifiers)
    assert new_code == "int a = 5;"

    # Test with an empty string
    cpp_code = ""
    qualified_scoped_identifiers = ["Main::SubNamespace::Foo"]
    new_code = apply_scoped_identifiers_to_code(cpp_code, qualified_scoped_identifiers)
    assert new_code == ""

    # Test with identifiers in strings or comments
    cpp_code = 'std::string s = "Foo::Bar"; // Foo::Bar should not be changed'
    qualified_scoped_identifiers = ["Main::Foo::Bar"]
    new_code = apply_scoped_identifiers_to_code(cpp_code, qualified_scoped_identifiers)
    assert new_code == 'std::string s = "Foo::Bar"; // Foo::Bar should not be changed'


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
    scope_cache_qualified = cpp_unit._scope_identifiers._cache_qualified_identifiers
    assert scope_cache_qualified == [
        "Snippets::Color",
        "Snippets::Color_Red",
        "Snippets::col",
        "Snippets::SnippetTheme",
        "Snippets::SnippetTheme::Light",
        "Snippets::theme",
        "Snippets::SnippetData",
        "Snippets::SnippetData::Palette",
        "Snippets::foo",
        "Snippets::snippetsVector",
    ]

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


"""
    namespace Blah { struct FooBlah{}; }
    struct Foo{};
    Point Middle(const Point& other) const;
    void Blah(Blah::FooBlah blah = Blah::FooBlah(), Foo foo = Foo());


    options.fn_template_options.add_specialization("^MaxValue$", ["int", "float"], add_suffix_to_function_name=True)

    template<typename T> T MaxValue(const std::vector<T>& values) { return *std::max_element(values.begin(), values.end());}

"""
