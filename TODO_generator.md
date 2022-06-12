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


- Resoudre les exclude de implot en ajoutant des callback qui hackent:
  soit les params d'une fonction
  soit le body de la lambda


Lire doc pybind / numpy and eigen...
Voir https://github.com/python/typeshed and https://github.com/microsoft/python-type-stubs


Dyndoc !!!!
    Export Text, HTML, Image, Take Screenshots, etc



Bugs:
    - Static methods: cf https://pybind11-jagerman.readthedocs.io/en/stable/classes.html?highlight=static%20method#instance-and-static-fields 
        use def_static


- private / public
- class (same as struct, except public)
- ToString ?
- Online Interface with google colab


- test dans implot
- test dans immvision
- methods

- Later: folder in site-packages
- code_replacement sur comments deconne:
    // Doubles the input number
    // i.e return "2 * x"    <== le * est supprimé


Pour les buffer non template, il faudra aussi vérifier le type dans l'array
    char array_type = values.dtype().char_();
        if (array_type != 'B')
            throw std::runtime_error("Bad type!");
