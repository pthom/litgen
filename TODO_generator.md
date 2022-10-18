imgui_bundle:
    Review description (imgui first)
    Re-try add mahi-gui

Finir lg_testrunner


himgui:
    run mypy on init.pyi de himgui
    namespace:

    Compat pyimgui:
        functions params ImVec2 => split in two, example = add_rect
        return Imvec2 => investiguer, example = get_window_position() : ca retourne un "Vec2" !

    Nettoyage:
        himgui.__init__.pyi, hacké:
            ````
            from lg_imgui import ImVec2, ImVec4, ImTextureID, ImFontConfig, ImFont, ImGuiWindowFlags
            from lg_imgui import ImGuiCond, ImGuiCond_

            ImGuiCond_FirstUseEver = ImGuiCond_.first_use_ever   => pourrait être trouvé automatiquement,
                                                                mais demande intercommunication entre generation libs
                                                                (SAVE REPLACEMENTS?)

            DockSpaceName = str
            from lg_imgui import ImGuiDir, ImGuiDir_
            ImGuiDir_Down = ImGuiDir_.down
            AnyEventCallback = Callable[[Any], bool]
            VoidFunction = Callable[[], None]
            ````

        Trucs à régler dans __init__.pyi:
            default_im_gui_window_type:DefaultImGuiWindowType = DefaultImGuiWindowType::ProvideFullScreenWindow



litgen:
    sujet toString
        toString en hackant str:
        l.Foo.__str__ = my_str

    implot
        SetupAxisTicks uses a string list, parameters order reversed!

    Sujet / Namespaces

    Ajout / pybind
        Namespace
        Trampoline
        Operators (https://pybind11.readthedocs.io/en/stable/advanced/classes.html#operator-overloading)


srcmlcpp:
    Refactor: srcmlcpp = main repo, main project, etc
        separer srcml pur de srcmlcpp ?
    change licence (ethical license for large NNs)
        -> regarder liste ici: https://spdx.org/licenses/
        -> message to science4all: https://www.facebook.com/Science4Allorg/
    Faire release avec numéro de version
    Doc & Demo


Notes / Doc pybind11:






Bugs:
