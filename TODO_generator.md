imgui / Todo:
    * profile generate imgui
    * patch on imgui code string
    * ImVector -> List, reprendre impl (template), ou pycast (exclu par regex pour l'instant)
    * interdire variables nommees str (cf input_text)
    * Boxer les pointeur (SliderInt, input_text, etc.)


struct ImGuiOnceUponAFrame
{
    ImGuiOnceUponAFrame() { RefFrame = -1; }
    mutable int RefFrame; // ---> virer mutable
    operator bool() const { int current_frame = ImGui::GetFrameCount(); if (RefFrame == current_frame) return false; RefFrame = current_frame; return true; }
};

Gerer overload multiples / methodes et functions dans stubs

Probleme avec code ci-dessous: le constructeur est ignoré
     struct BoxedUnsignedLong // MY_API
      {
      unsigned long value;
      BoxedUnsignedLong(unsigned long v = {}) : value(v) {}
      std::string __repr__() const { return std::string("BoxedUnsignedLong(") + std::to_string(value) + ")"; }
      };


BoxedTypes

https://stackoverflow.com/questions/8820276/docstring-for-variable -> Use typing.Annotated to provide a docstring for variables.

* Move & rename module_pydef_generator_test.py



imgui: Handle widget input / output parameters
        bool *, int *, float *, etc
        float[2, 3, 4]
        --> make return

change licence (ethical license for large NNs)
    -> message to science4all: https://www.facebook.com/Science4Allorg/

stub:
    S'attendre a problem possible avec conversion enum / int:
        def begin_combo(    # imgui.h:509
        label: str,
        preview_value: str,
        flags: ImGuiComboFlags = 0
        ) -> bool:

Ajout / pybind
    Trampoline
    Operators (https://pybind11.readthedocs.io/en/stable/advanced/classes.html#operator-overloading)



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
