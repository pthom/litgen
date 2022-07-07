litgen:
    IM_ASSERT -> exception
    Debug dans implot!!!

    gen library
    gen_library_collection

himgui:
    cpp_to_python_translation_table:
        by namespace
            -> dans replacements_cache
    adapted_namespace:
        extract to file
        add cpp_to_python_replacements (functions & decls)
    namespace:
        options / generate submodule ?
        comment generer stub:
            soit https://www.reddit.com/r/learnpython/comments/dek8fy/how_to_create_a_stub_file_for_a_submodule_in_a_c/
            soit fake class with staticmethods
    adapted_class:
        add cpp_to_python_replacements (functions & decls)
    may be option replacement no regex
    run mypy on init.pyi de himgui

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
        -> regarder liste ici: https://spdx.org/licenses/
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
