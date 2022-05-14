- OK ! Test overidde function
- OK! Test keyword inline
- OK! Test array: Semi Ok. 
  ok Type size inconsistency
  ok Template functions?
  ok Check authorized buffer_types in options (uint8_t ok, not char, etc) 
  ok test avec const 

- stub / pyi 

- Lire le fichier entier comme une struct (i.e avec Variant)
    Comme ça, on pourra reproduire toute la doc !

- toString en hackant str:
    l.Foo.__str__ = my_str

def checkChessboard(img: Mat, size) -> typing.Any:
    """checkChessboard(img, size) -> retval"""
    

OK! Test use class

Lire doc pybind / numpy and eigen...
Voir https://github.com/python/typeshed and https://github.com/microsoft/python-type-stubs



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
