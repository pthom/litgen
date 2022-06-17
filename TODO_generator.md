S'arranger pour que mypy ou un linter repere les erreurs de variables pas declarees.
Cf status de ce repo.

* package function_adapt
  * renames
  * API avec derivation

* sub package adapt param
  * gen pyi class & structs
  Il faut que pydef_generator (ou peut etre meme srcml_types) puisse faire un tri
  Dans enum, supprimer count, precalculer valeur des decls des enum quand dependent du previous
  Dans struct, il y a des traitement sur les membres (array et cie)
  --> faire equivalent de adapt_function pour structs et enums


imgui: Handle widget input / output parameters
        bool *, int *, float *, etc
        float[2, 3, 4]
        --> make return


stub:
    S'attendre a problem possible avec conversion enum / int:
        def begin_combo(    # imgui.h:509
        label: str,
        preview_value: str,
        flags: ImGuiComboFlags = 0
        ) -> bool:


PimpMyClass !
    srcmlcpp separated
    auto pImpl from cpp: pImpl class  => header decl + cpp imp non pImpl + Doc !


widgets avec int*, float*, bool* : Boxer

implot SetupAxisTicks uses a string list, parameters order reversed!



Notes / Doc pybind11:
    Alternatives litgen:
        https://pybind11.readthedocs.io/en/stable/compiling.html#generating-binding-code-automatically
        AutoWIG:
            https://www.youtube.com/watch?v=N4q_Vud77Hw

    Nested structs and enums (inside struct or class): see https://pybind11.readthedocs.io/en/stable/classes.html#enumerations-and-internal-types
        enum / py::arithmetic() : add an option?

- add namespace hierarchy in pydef ? With option ?
- integration tests
    - work on full gen (namespace, comment, etc)


- toString en hackant str:
    l.Foo.__str__ = my_str


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
