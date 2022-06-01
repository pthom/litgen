- align struct
- ctor default or not
  - strct.has_implicit_public_default_ctor()
- gen stub
- integration tests
  - work on full gen (namespace, comment, etc)
- filter function with API prefix

- separate module srcmlcpp
  - option / log time srcml caller

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
