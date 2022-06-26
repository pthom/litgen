litgen:

    sujet callbacks C avec imgui
        il a fallu supprimer les callback de InputText dans imgui_stdlib
            -> voir si d'autres signatures avec callback trainent et s'il faut faire qq chose
            -> oui il n'y en a que deux:
                IMGUI_API void          SetNextWindowSizeConstraints(const ImVec2& size_min, const ImVec2& size_max, ImGuiSizeCallback custom_callback = NULL, void* custom_callback_data = NULL); // set next window size limits. use -1,-1 on either X/Y axis to preserve the current size. Sizes will be rounded down. Use callback to apply non-trivial programmatic constraints.
                IMGUI_API void  AddCallback(ImDrawCallback callback, void* callback_data);  // Your rendering function must check for 'UserCallback' in ImDrawCmd and call the function instead of rendering triangles.


    Sujet input Pointer to return output (tuple) ..

    Sujet / Namespaces


    Ajout / pybind
        Namespace
        Trampoline
        Operators (https://pybind11.readthedocs.io/en/stable/advanced/classes.html#operator-overloading)

    imgui:
        InputText (need multiple files & options)
        Signature / ComboBox
        Test app imgui
        N profile generate imgui -> remove flag signature
        N Pas urgent, voire nefaste : ImVector -> List, reprendre impl (template), ou pycast (exclu par regex pour l'instant)

    implot
        SetupAxisTicks uses a string list, parameters order reversed!

    sujet toString
        toString en hackant str:
        l.Foo.__str__ = my_str

    CI / profiling:
        ajouter un test de rapidite sur gen imgui
        remplacer instances de copy.deepcopy par un clone (or remove parent)

srcmlcpp:
    Refactor: srcmlcpp = main repo, main project, etc
    change licence (ethical license for large NNs)
        -> message to science4all: https://www.facebook.com/Science4Allorg/


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
