imgui / Todo:
    InputText:
        litgen doit pouvoir gerer une collection de fichier en input, chacun avec des options differentes
        -> collection avec imgui.h (sans inputText) + imgui_stdlib.h

    Sujet input Pointer to return output (tuple) ..

    Sujet: strings via text_begin / text_end ?
        Pas forcement, car
                d.add_text(imgui.ImVec2(50, 50), 42243, "hello")   # marche !!!
        >>> d = imgui.get_window_draw_list()
        >>> d.add_text()
        (self: _lg_imgui.ImDrawList, pos: _lg_imgui.ImVec2, col: int, text_begin: str, text_end: str = None) -> None



    Tester methode avec return by ref (cf scratch.txt)
        PtrFunc GetFont  (IMGUI_API ImFont*       GetFont();                                                      )
        PtrFunc GetGlyphRangesDefault  (IMGUI_API const ImWchar*    GetGlyphRangesDefault();                )
        PtrFunc GetKeyName  (IMGUI_API const char*   GetKeyName(ImGuiKey key);                                           )
        PtrFunc GetClipboardText  (IMGUI_API const char*   GetClipboardText();)
        PtrFunc GetBackgroundDrawList  (IMGUI_API ImDrawList*   GetBackgroundDrawList(); )
        PtrFunc GetIOPtr  (IMGUI_API ImGuiIO*      GetIOPtr(); )
        PtrRef GetStyle  (IMGUI_API ImGuiStyle&   GetStyle();                                 )
        PtrFunc GetStylePtr  (IMGUI_API ImGuiStyle*   GetStylePtr(); )
        PtrFunc GetDrawData  (IMGUI_API ImDrawData*   GetDrawData();                              )
        PtrFunc GetVersion  (IMGUI_API const char*   GetVersion();                               )
        PtrFunc GetWindowDrawList  (IMGUI_API ImDrawList*   GetWindowDrawList(); )
        -> perfect !

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
