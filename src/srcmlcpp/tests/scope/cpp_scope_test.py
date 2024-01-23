from litgen import LitgenOptions
import litgen
from codemanip import code_utils
import srcmlcpp


def test_scope():
    from srcmlcpp import CppScope

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

    def test_scope_cache() -> None:
        # Get the scope cache
        scope_cache = cpp_unit._cache_known_identifiers_scope

        # Test Snippets scope: it should contain Color_Red (which leaks from the C enum Color)
        snippet_identifiers = scope_cache[CppScope.from_string("Snippets")]
        assert snippet_identifiers == [
            "Color",
            "Color_Red",
            "col",
            "SnippetTheme",
            "SnippetTheme::Light",
            "theme",
            "SnippetData",
            "SnippetData::Palette",
            "foo",
            "snippetsVector",
        ]

        # there should not be a scope Snippet::Color
        assert CppScope.from_string("Snippets::Color") not in scope_cache

        # Test Snippets::SnippetTheme scope: it should contain Light
        snippet_theme_identifiers = scope_cache[CppScope.from_string("Snippets::SnippetTheme")]
        assert snippet_theme_identifiers == ["Light"]

        # Test Snippets::SnippetData scope: it should contain Palette
        snippet_data_identifiers = scope_cache[CppScope.from_string("Snippets::SnippetData")]
        assert snippet_data_identifiers == ["Palette"]

    test_scope_cache()

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
