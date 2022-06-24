imgui / Todo:
* Test use imgui a base de create context / destroy context (c++ then python)

Sujet / reference GetIO() & GetStyle()
    return_value_policy::reference ne marche qu'avec pointeur
      Donc: ImGuiIO&      GetIO();  déconne
        See https://stackoverflow.com/questions/41814652/how-to-wrap-a-singleton-class-using-pybind11

    -> pas le choix ? il faut faire un GetIO_As_Pointer et ajouter le concept de synonyme...
        Idem pour ImGui::GetStyle

    Si, on a le choix:
        Soit donner le type de return a la lambda (->)
        Soit ne pas utiliser de lambda quand on peut

Sujet / input_text:
    Il faut ajouter les signatures / string
    Au moment de la generation du code de binding, il faudrait supprimer les versions avec char *
    (mais on en a besoin ensuite pendant la compil...)

Sujet / create_context default arg (idem destroy_context):
    m.def("create_context",    // imgui.h:284
    [](ImFontAtlas * shared_font_atlas = NULL)
    {
    return CreateContext(shared_font_atlas);
    },
    py::arg("shared_font_atlas") = NULL
    );
    Ne permet pas d'utiliser sans param...

Sujet / opague pointers (create_context)
    Réglé avec code manuel:
        auto pyClassImGuiContext = py::class_<ImGuiContext>
        (m, "ImGuiContext", "")
        ;


Suejt input Pointer to return output (tuple) ..

No:
* profile generate imgui -> remove flag signature
* ImVector -> List, reprendre impl (template), ou pycast (exclu par regex pour l'instant)
* Boxer les pointeur (SliderInt, input_text, etc.)


imgui: Handle widget input / output parameters
bool *, int *, float *, etc
float[2, 3, 4]
--> make return


Gerer overload multiples / methodes et functions dans stubs


change licence (ethical license for large NNs)
    -> message to science4all: https://www.facebook.com/Science4Allorg/

Ajout / pybind
    Trampoline
    Operators (https://pybind11.readthedocs.io/en/stable/advanced/classes.html#operator-overloading)



PimpMyClass !
    srcmlcpp separated
    auto pImpl from cpp: pImpl class  => header decl + cpp imp non pImpl + Doc !


implot SetupAxisTicks uses a string list, parameters order reversed!



Notes / Doc pybind11:
    Alternatives litgen:
        https://pybind11.readthedocs.io/en/stable/compiling.html#generating-binding-code-automatically
        AutoWIG:
            https://www.youtube.com/watch?v=N4q_Vud77Hw

    Nested structs and enums (inside struct or class): see https://pybind11.readthedocs.io/en/stable/classes.html#enumerations-and-internal-types
        enum / py::arithmetic() : add an option?

- add namespace hierarchy in pydef ? With option ?

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
