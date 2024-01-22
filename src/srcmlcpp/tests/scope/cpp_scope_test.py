from litgen import LitgenOptions
import litgen
from codemanip import code_utils
import srcmlcpp


def test_known_elements():
    code = """
            int f();
            constexpr int Global = 0;
            namespace N1
            {
                namespace N2
                {
                    struct S2 { int s2_value = 0; };
                    enum class E2 { a = 0 };  // enum class!
                    int f2();
                }

                namespace N3
                {
                    enum E3 { a = 0 };        // C enum!
                    int f3();

                    // We want to qualify the parameters' declarations of this function
                    void g(
                            int _f = f(),
                            N2::S2 s2 = N2::S2(),
                            N2::E2 e2 = N2::a,      // subtle difference for
                            E3 e3 = E3::a,          // enum and enum class
                            int _f3 = N1::N3::f3(),
                            int other = N1::N4::f4() // unknown function
                        );

                    int n3_value = 0;
                } // namespace N3
            }  // namespace N1
    """
    options = srcmlcpp.SrcmlcppOptions()
    cpp_unit = srcmlcpp.code_to_cpp_unit(options, code)

    known_types = cpp_unit.known_types()
    known_types_names = [k.name() for k in known_types]
    assert known_types_names == ["S2", "E2", "E3"]

    known_callables = cpp_unit.known_callables()
    known_callables_names = [k.name() for k in known_callables]
    assert known_callables_names == ["f", "S2", "f2", "f3", "g"]

    known_callables_init_list = cpp_unit.known_callables_init_list()
    known_callables_init_list_names = [k.name() for k in known_callables_init_list]
    assert known_callables_init_list_names == ["S2"]

    known_values = cpp_unit.known_values()
    known_values_names = [k.name() for k in known_values]
    assert known_values_names == ["Global", "s2_value", "a", "a", "n3_value"]


def test_scope():
    from srcmlcpp import CppDecl

    code = """
    namespace Snippets
    {
        enum class SnippetTheme
        {
            Light,
        };
        struct SnippetData
        {
            SnippetTheme Palette = SnippetTheme::Light;
        };

        }
    """
    options = srcmlcpp.SrcmlcppOptions()
    cpp_unit = srcmlcpp.code_to_cpp_unit(options, code)
    decls = cpp_unit.all_elements_of_type(srcmlcpp.CppDecl)
    palette_decl = decls[1]
    assert isinstance(palette_decl, CppDecl)
    palette_scope = palette_decl.cpp_scope()

    palette_type = palette_decl.cpp_type
    palette_type_qualified = palette_type.with_qualified_types(palette_scope)
    assert palette_type_qualified.str_code() == "Snippets::SnippetTheme"

    palette_decl_qualified = palette_decl.with_qualified_types(palette_scope)
    assert palette_decl_qualified.cpp_type.str_code() == "Snippets::SnippetTheme"

    print(palette_decl_qualified.initial_value_code)


    # palette_decl.in

    print("a")




def test_scope_root_namespace_with_classes():
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


def test_truc():
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
    options = LitgenOptions()
    options.namespaces_root = ["HelloImGui"]
    generated_code = litgen.generate_code(options, code)
    # print(generated_code.pydef_code)
    code_utils.assert_are_codes_equal(
        generated_code.pydef_code,
        """
        auto pyClassRunnerCallbacks =
            py::class_<HelloImGui::RunnerCallbacks>
                (m, "RunnerCallbacks", "")
            .def(py::init<>([](
            VoidFunction LoadAdditionalFonts = HelloImGui::ImGuiDefaultSettings::LoadDefaultFont_WithFontAwesomeIcons)
            {
                auto r = std::make_unique<HelloImGui::RunnerCallbacks>();
                r->LoadAdditionalFonts = LoadAdditionalFonts;
                return r;
            })
            , py::arg("load_additional_fonts") = HelloImGui::ImGuiDefaultSettings::LoadDefaultFont_WithFontAwesomeIcons
            )
            .def_readwrite("load_additional_fonts", &HelloImGui::RunnerCallbacks::LoadAdditionalFonts, "")
            ;

        { // <namespace ImGuiDefaultSettings>
            py::module_ pyNsImGuiDefaultSettings = m.def_submodule("im_gui_default_settings", "");
            pyNsImGuiDefaultSettings.def("load_default_font_with_font_awesome_icons",
                HelloImGui::ImGuiDefaultSettings::LoadDefaultFont_WithFontAwesomeIcons);
        } // </namespace ImGuiDefaultSettings>
    """,
    )


def test_scope_with_vector():
    code = """
    namespace Main
    {
        int a = 0;
        //struct Foo {};
        //std::vector<Foo> s = {};
    }
    """
    options = LitgenOptions()
    options.namespaces_root = ["Main"]
    generated_code = litgen.generate_code(options, code)
    print(generated_code.pydef_code)


"""
    namespace Blah { struct FooBlah{}; }
    struct Foo{};
    Point Middle(const Point& other) const;
    void Blah(Blah::FooBlah blah = Blah::FooBlah(), Foo foo = Foo());


    options.fn_template_options.add_specialization("^MaxValue$", ["int", "float"], add_suffix_to_function_name=True)

    template<typename T> T MaxValue(const std::vector<T>& values) { return *std::max_element(values.begin(), values.end());}

"""
