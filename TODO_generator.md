- OK ! Test overidde function
- OK! Test keyword inline
- OK! Test array: Semi Ok. 
  ok Type size inconsistency
  ok Template functions?
  ok Check authorized buffer_types in options (uint8_t ok, not char, etc) 
  ok test avec const 

OK! Test use class

Bugs:
    - Constructor & desructors
    - leaked_ptr
    - Static methods



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
