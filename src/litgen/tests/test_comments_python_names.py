import litgen
from codemanip import code_utils


def test_comments_python_names_in_backticks():
    code = """
        namespace HelloImGui
        {
            enum class RendererBackendType { FirstAvailable, Metal };
            enum MyFlags_ { MyFlags_None = 0, MyFlags_NoTitleBar = 1 };
            namespace ManualRender { void Render(); }

            struct RunnerParams
            {
                // Set `RunnerParams::fpsIdle`, see `ManualRender::Render()` and `HelloImGui::GetRunnerParams()`
                float fpsIdle = 9.f;
                // `RendererBackendType::FirstAvailable`, `MyFlags_NoTitleBar`, `Metal`, `ImGui::GetStyle().FontScaleDpi = fpsIdle`, `FancyFunction()`
                int a = 0;
                // Unchanged: `HelloImGui::Run(const RunnerParams&)`, `ImGui::Unknown()`, `ImVec2(0, fpsIdle)`, `fps::idle`, `Render`, `bool IsIdle(float fpsIdle)`, `if (IsIdle()) { a = 1; }`, `id(obj)`
                int b = 0;
                // `fpsIdle=True`, `Render/GetRunnerParams()`. Unchanged: `Begin/GetRunnerParams()`, `SimpleParams`
                int c = 0;
            };
            RunnerParams* GetRunnerParams();
            bool IsIdle(int id);
            void FancyFunction(const char* data, size_t size);  // bound by hand, see custom_bindings below
        }
    """
    options = litgen.LitgenOptions()
    options.comments_python_names_in_backticks = True
    options.namespaces_root = ["HelloImGui"]
    options.comments_python_modules = {"HelloImGui": "hello_imgui", "ImGui": "imgui"}
    options.comments_python_names_of_other_modules = {"imgui": {"get_style", "font_scale_dpi"}}
    options.var_names_replacements.add_last_replacement(r"^id$", "id_")  # as imgui does: `id(obj)` is Python's
    options.fn_exclude_by_name__regex = "^FancyFunction$"
    options.custom_bindings.add_custom_bindings_to_main_module(
        stub_code="def fancy_function(\n    data: bytes,\n    simple_params: int = 0,\n) -> None:\n    pass\n",
        pydef_code="",
    )
    generated_code = litgen.generate_code(options, code)

    code_utils.assert_are_codes_equal(
        generated_code.stub_code,
        '''
        class RendererBackendType(enum.IntEnum):
            first_available = enum.auto() # (= 0)
            metal = enum.auto()           # (= 1)
        class MyFlags_(enum.IntEnum):
            none = enum.auto()         # (= 0)
            no_title_bar = enum.auto() # (= 1)

        class RunnerParams:
            # Set `RunnerParams.fps_idle`, see `manual_render.render()` and `hello_imgui.get_runner_params()`
            fps_idle: float = 9.
            # `RendererBackendType.first_available`, `MyFlags_.no_title_bar`, `metal`, `imgui.get_style().font_scale_dpi = fps_idle`, `fancy_function()`
            a: int = 0
            # Unchanged: `HelloImGui::Run(const RunnerParams&)`, `ImGui::Unknown()`, `ImVec2(0, fpsIdle)`, `fps::idle`, `Render`, `bool IsIdle(float fpsIdle)`, `if (IsIdle()) { a = 1; }`, `id(obj)`
            b: int = 0
            # `fps_idle=True`, `render/get_runner_params()`. Unchanged: `Begin/GetRunnerParams()`, `SimpleParams`
            c: int = 0
            def __init__(self, fps_idle: float = 9., a: int = 0, b: int = 0, c: int = 0) -> None:
                """Auto-generated default constructor with named params"""
                pass
        def get_runner_params() -> RunnerParams:
            pass
        def is_idle(id_: int) -> bool:
            pass


        # <submodule manual_render>
        class manual_render:  # Proxy class that introduces typings for the *submodule* manual_render
            pass  # (This corresponds to a C++ namespace. All methods are static!)
            @staticmethod
            def render() -> None:
                pass

        # </submodule manual_render>

        # <custom_bindings>
        def fancy_function(
            data: bytes,
            simple_params: int = 0,
        ) -> None:
            pass
        # </custom_bindings>
    ''',
    )


def test_fn_docstring_additions():
    code = """
        namespace ImGui
        {
            bool Begin(const char* name);
            bool MenuItem(const char* label); // return true when activated
        }
        struct Clipper { void Begin(int items_count); };
    """
    options = litgen.LitgenOptions()
    options.namespaces_root = ["ImGui"]
    options.fn_docstring_additions = {
        "ImGui::Begin": "Python: `begin_simple()` returns a bool.",
        "ImGui::MenuItem": "Python: `menu_item_simple()` too.",
    }
    generated_code = litgen.generate_code(options, code)

    code_utils.assert_are_codes_equal(
        generated_code.stub_code,
        '''
        def begin(name: str) -> bool:
            """Python: `begin_simple()` returns a bool."""
            pass
        def menu_item(label: str) -> bool:
            """ return True when activated
            Python: `menu_item_simple()` too.
            """
            pass

        class Clipper:
            def begin(self, items_count: int) -> None:
                pass
            def __init__(self) -> None:
                """Auto-generated default constructor"""
                pass
    ''',
    )
