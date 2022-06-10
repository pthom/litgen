    // Dead end, see: https://pybind11.readthedocs.io/en/stable/advanced/cast/stl.html
    m.def("change_c_array",
        [](std::vector<BoxedUnsignedLong>& values)
        {
            auto change_c_array_adapt_fixed_size_c_arrays = [](std::vector<BoxedUnsignedLong>& values)
            {
                unsigned long values_raw[2];
                for (size_t i = 0; i < 2; ++i)
                    values_raw[i] = values[i].value;

                /*auto r=*/ change_c_array(values_raw);

                for (size_t i = 0; i < 2; ++i)
                    values[i].value = values_raw[i];
            };
            change_c_array_adapt_fixed_size_c_arrays(values);
        },
        py::arg("values")
    );

    // OK with separated arguments
    m.def("change_c_array2",
        [](BoxedUnsignedLong& values_0, BoxedUnsignedLong& values_1)
        {
            auto change_c_array_adapt_fixed_size_c_arrays = [](BoxedUnsignedLong& values_0, BoxedUnsignedLong& values_1)
            {
                unsigned long values_raw[2];
                values_raw[0] = values_0.value;
                values_raw[1] = values_1.value;

                /*auto r=*/ change_c_array(values_raw);

                values_0.value = values_raw[0];
                values_1.value = values_raw[1];
            };
            change_c_array_adapt_fixed_size_c_arrays(values_0, values_1);
        },
        py::arg("values_0"),
        py::arg("values_1")
    );


notebook



Notes / Doc pybind11:
    Alternatives litgen:
        https://pybind11.readthedocs.io/en/stable/compiling.html#generating-binding-code-automatically
        AutoWIG:
            https://www.youtube.com/watch?v=N4q_Vud77Hw

    Nested structs and enums (inside struct or class): see https://pybind11.readthedocs.io/en/stable/classes.html#enumerations-and-internal-types
        enum / py::arithmetic() : add an option?


- CI plante dans python 
- re-test integration c++
- add namespace hierarchy in pydef ? With option ?
- integration tests
    - work on full gen (namespace, comment, etc)
- gen stub
- filter function with API prefix / filter struct by eol comment


Doc avec google collab

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
    X Constructor & destructors
    X return value policy
    ? leaked_ptr (pas sur qu'on en ait besoin)
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
- definir politique vis a vis DocString and multiline comments
- code_replacement sur comments deconne:
    // Doubles the input number
    // i.e return "2 * x"    <== le * est supprimé


Pour les buffer non template, il faudra aussi vérifier le type dans l'array
    char array_type = values.dtype().char_();
        if (array_type != 'B')
            throw std::runtime_error("Bad type!");
