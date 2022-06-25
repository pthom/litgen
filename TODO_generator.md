litgen:
    srcml:
        renames & internal
        Faire un objet srcmlcpp
            element
            srcml_options
                to_verbatim_code
                to_xml
                to_yaml
                emit_warning

    Sujet / multiples fichiers input


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


srcmlcpp:
    Refactor: srcmlcpp = main repo, main project, etc

    change licence (ethical license for large NNs)
        -> message to science4all: https://www.facebook.com/Science4Allorg/

PimpMyClass !
    srcmlcpp separated
    auto pImpl from cpp: pImpl class  => header decl + cpp imp non pImpl + Doc !


Cerealize / cerealize




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
