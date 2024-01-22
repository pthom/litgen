from litgen import LitgenOptions
import litgen
from codemanip import code_utils


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
