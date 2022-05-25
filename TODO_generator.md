srcml 
* [ ] Dump ignored regions
  * [ ] function code

* [ ] Separate library (srclmcpp)



Generic recursion:
    First parser pass -> pydef
    Second parser pass -> fill structs, enums, functions, etc

    code_types: deriver de  Pydef

test function declaree sur plusieurs lignes

- 
- stub / pyi
  - Lire le fichier entier comme une struct (i.e avec Variant)
      Comme ça, on pourra reproduire toute la doc !

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
