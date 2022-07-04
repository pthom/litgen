check himgui DLL on linux

test branche devel de srcML

himgui:
    Compat pyimgui:
        functions params ImVec2 => split in two, example = add_rect
        return Imvec2 => investiguer, example = get_window_position() : ca retourne un "Vec2" !



    Nettoyage:
        Don't use {} in function default params
        Ajout overrideAssetsFolder dans HelloImGui
        himgui.__init__.pyi, hacké:
            ````
            from lg_imgui import ImVec2, ImVec4, ImTextureID, ImFontConfig, ImFont, ImGuiWindowFlags
            from lg_imgui import ImGuiCond, ImGuiCond_

            ImGuiCond_FirstUseEver = ImGuiCond_.first_use_ever   => pourrait être trouvé automatiquement,
                                                                mais demande intercommunication entre generation libs

            DockSpaceName = str
            from lg_imgui import ImGuiDir, ImGuiDir_
            ImGuiDir_Down = ImGuiDir_.down
            AnyEventCallback = Callable[[Any], bool]
            VoidFunction = Callable[[], None]
            ````

        Trucs à régler dans __init__.pyi:
            default_im_gui_window_type:DefaultImGuiWindowType = DefaultImGuiWindowType::ProvideFullScreenWindow



    Pb avec GImGui si HelloImGui et ImGui sont dans des modules (dll) séparés
        Fin / Solution via shared:
            Ajout SetAllocFunctionTrucMuche
                static void*   MyMallocWrapper(size_t size, void* user_data)    { IM_UNUSED(user_data); return malloc(size); }
                static void    MyFreeWrapper(void* ptr, void* user_data)        { IM_UNUSED(user_data); free(ptr); }

                //ImGui::SetAllocatorFunctions(MyMallocWrapper, MyFreeWrapper);

            Faire test sous linux !!!

    Solutions:
        - Soit gérer le passage de GImGui (semble pas simple, une allocation de GImGui échoue...)
            En fait, il au moment ou on inclue imgui_internal depuis une autre dll (ici HelloImGui::AbstractRunner) , il faut
                #define GImGui
                definir une variable globale GImGui, la récupérer depuis CreateContext et la stocker, puis la donner
                a ImGui

        - Soit lier les deux modules (genre imgui = submodule de himgui, avec defsubmodule)

        Probleme en cours: le module imgui compilé pour l'instant est fait pour une version statique
        Il faudrait compiler ImGui avec options

        Status / GImGui:
            imgui_internal.h:
                #ifndef GImGui
                extern IMGUI_API ImGuiContext* GImGui;  // Current implicit context pointer
                #endif
            imgui.cpp
                #ifndef GImGui
                ImGuiContext*   GImGui = NULL;
                #endif
            GImGui utilisé dans imgui.cpp, imgui_internal.h mais pas dans imgui.h

        Status / Compil imgui dans le projet
            HelloImGui ne compile pas sa propre version de ImGui
            examples_real_libs/imgui compile en statique

        L'erreur se produit dans
                imgui_internal.h
                    inline ImFont*          GetDefaultFont() {
                    ImGuiContext& g = *GImGui;       // NULL !!!!!!!!
            appelé par
                imgui.cpp: void ImGui::NewFrame()
                    Dans NewFrame, GImGui est bon, jusqu'a l'appel de GetDefaultFont, ou il devient NULL
                    (car on est alors dans le inline de HelloImGui ?)



        -> C'est trop horrible a debugger dans context complet
            Faire un programme minimal

            static void*   MyMallocWrapper(size_t size, void* user_data)    { IM_UNUSED(user_data); return malloc(size); }
            static void    MyFreeWrapper(void* ptr, void* user_data)        { IM_UNUSED(user_data); free(ptr); }



litgen:
    sujet toString
        toString en hackant str:
        l.Foo.__str__ = my_str

    CI / profiling:
        ajouter un test de rapidite sur gen imgui
        remplacer instances de copy.deepcopy par un clone (or remove parent)

    implot
        SetupAxisTicks uses a string list, parameters order reversed!

    Sujet / Namespaces

    Ajout / pybind
        Namespace
        Trampoline
        Operators (https://pybind11.readthedocs.io/en/stable/advanced/classes.html#operator-overloading)


srcmlcpp:
    Refactor: srcmlcpp = main repo, main project, etc
        separer srcml pur de srcmlcpp ?
    change licence (ethical license for large NNs)
        -> message to science4all: https://www.facebook.com/Science4Allorg/
    Faire release avec numéro de version
    Doc & Demo


srcmlcpp demos:

    PimpMyClass !
        srcmlcpp separated
        auto pImpl from cpp: pImpl class  => header decl + cpp imp non pImpl + Doc !

    Cerealize / cerealize

    pimp_my_ci:
        check for doc
        check for snake_case
        hunt_fake_classes
            "a class with a constructor and only one public function is not a class. Use a namespace!"
            Example / Mailer
        prefix class members



Notes / Doc pybind11:
    Alternatives litgen:
        https://pybind11.readthedocs.io/en/stable/compiling.html#generating-binding-code-automatically
        AutoWIG:
            https://www.youtube.com/watch?v=N4q_Vud77Hw

    Nested structs and enums (inside struct or class): see https://pybind11.readthedocs.io/en/stable/classes.html#enumerations-and-internal-types
        enum / py::arithmetic() : add an option?

- add namespace hierarchy in pydef ? With option ?



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
