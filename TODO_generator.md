litgen:
    gen library
    gen_library_collection

himgui:
    pip install -e plante sous mac M1
        https://stackoverflow.com/questions/66860350/python-pip-process-are-killed-in-virtualenv-apple-m1-chip
        Essayer Poetry ?

    pb avec CI & ref imgui externe
        add_subdirectory given source "/tmp/pip-req-build-oa2nbnuv/../imgui" which
        is not an existing directory.

        M3: Des repos imgui_bindings et hello_imgui qui ne dependent pas de litgen ?
            Pas mal... Mais ne resoud pas le probleme de trouver les includes imgui pour himgui
            X --> fonctionner en cmake independant
            X --> ajout sudmodule imgui à hello_imgui
            X --> Script check versions identiques
            --> faire des submodules, et donc refaire des repos
            --> lg_hello_imgui depend de lg_imgui (setuptools)


    Compat pyimgui:
        functions params ImVec2 => split in two, example = add_rect
        return Imvec2 => investiguer, example = get_window_position() : ca retourne un "Vec2" !

    Nettoyage:
        Don't use {} in function default params

        himgui.__init__.pyi, hacké:
            ````
            from lg_imgui import ImVec2, ImVec4, ImTextureID, ImFontConfig, ImFont, ImGuiWindowFlags
            from lg_imgui import ImGuiCond, ImGuiCond_

            ImGuiCond_FirstUseEver = ImGuiCond_.first_use_ever   => pourrait être trouvé automatiquement,
                                                                mais demande intercommunication entre generation libs

            DockSpaceName = str
            from lg_imgui import ImGuiDir, ImGuiDir_
            ImGuiDir_Down = ImGuiDir_.down
            AnyEventCallback = Callable[[Any], bool]
            VoidFunction = Callable[[], None]
            ````

        Trucs à régler dans __init__.pyi:
            default_im_gui_window_type:DefaultImGuiWindowType = DefaultImGuiWindowType::ProvideFullScreenWindow



    Pb avec GImGui si HelloImGui et ImGui sont dans des modules (dll) séparés
        Fin / Solution via shared:
            Ajout SetAllocFunctionTrucMuche
                static void*   MyMallocWrapper(size_t size, void* user_data)    { IM_UNUSED(user_data); return malloc(size); }
                static void    MyFreeWrapper(void* ptr, void* user_data)        { IM_UNUSED(user_data); free(ptr); }

                //ImGui::SetAllocatorFunctions(MyMallocWrapper, MyFreeWrapper);

            Faire test sous windows !!!


litgen:
    sujet toString
        toString en hackant str:
        l.Foo.__str__ = my_str

    CI / profiling:
        ajouter un test de rapidite sur gen imgui
        remplacer instances de copy.deepcopy par un clone (or remove parent)

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
        -> message to science4all: https://www.facebook.com/Science4Allorg/
    Faire release avec numéro de version
    Doc & Demo


srcmlcpp demos:

    PimpMyClass !
        srcmlcpp separated
        auto pImpl from cpp: pImpl class  => header decl + cpp imp non pImpl + Doc !

    Cerealize / cerealize

    pimp_my_ci:
        check for doc
        check for snake_case
        hunt_fake_classes
            "a class with a constructor and only one public function is not a class. Use a namespace!"
            Example / Mailer
        prefix class members



Notes / Doc pybind11:
    Alternatives litgen:
        https://pybind11.readthedocs.io/en/stable/compiling.html#generating-binding-code-automatically
        AutoWIG:
            https://www.youtube.com/watch?v=N4q_Vud77Hw

    Nested structs and enums (inside struct or class): see https://pybind11.readthedocs.io/en/stable/classes.html#enumerations-and-internal-types
        enum / py::arithmetic() : add an option?

- add namespace hierarchy in pydef ? With option ?



Lire doc pybind / numpy and eigen...
Voir https://github.com/python/typeshed and https://github.com/microsoft/python-type-stubs


Dyndoc !!!!
    Export Text, HTML, Image, Take Screenshots, etc



Bugs:
    - Static methods: cf https://pybind11-jagerman.readthedocs.io/en/stable/classes.html?highlight=static%20method#instance-and-static-fields
        use def_static

- Later: folder in site-packages
- code_replacement sur comments deconne:
    // Doubles the input number
    // i.e return "2 * x"    <== le * est supprimé
