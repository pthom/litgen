Refactor funct_w_lambda:
    Main Resp:
        Faire une lambda

    Other:
        Adapt buffers 
            Std / Template / Multiple / Sizeof
            Variadic args



stub:
    Pb avec buffer -> refactoring necessaire
        MY_API inline void add_inside_array(uint8_t* array, size_t array_size, uint8_t number_to_add)
                                                            ^should be removed
    Pb avec variadics:
        IMGUI_API void          Text(const char* fmt, ...)                                      IM_FMTARGS(1); // formatted text

    S'attendre a problem possible avec conversion enum / int:
        def begin_combo(    # imgui.h:509
        label: str,
        preview_value: str,
        flags: ImGuiComboFlags = 0
        ) -> bool:

  
PimpMyClass !
    srcmlcpp separated
    auto pImpl from cpp: pImpl class  => header decl + cpp imp non pImpl + Doc !


  
duplicate code_utils / add copy script

imgui
    CI compile
    pyi
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

