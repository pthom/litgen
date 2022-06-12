import os, sys; _THIS_DIR = os.path.dirname(__file__); sys.path.append(_THIS_DIR + "/../..")

import srcmlcpp
from srcmlcpp import srcml_main
from litgen.internal import code_utils, module_pydef_generator
import litgen


def read_file_content(filename):
    with open(filename, "r") as f:
        content = f.read()
    return content


def play_parse(code):
    options = litgen.code_style_imgui()
    cpp_unit = srcmlcpp.code_to_cpp_unit(options, code)
    print(cpp_unit)


def play_imgui():
    options = litgen.code_style_imgui()
    source_filename = os.path.realpath(_THIS_DIR + "/../../examples_real_libs/imgui/imgui/imgui.h")
    cpp_unit = srcmlcpp.file_to_cpp_unit(options.srcml_options, source_filename)
    # print(cpp_unit)

def play_implot():
    options = litgen.code_style_implot()
    options.original_location_flag_show = True
    source_filename = os.path.realpath(_THIS_DIR + "/../../examples_real_libs/implot/implot/implot.h")
    cpp_unit = srcmlcpp.file_to_cpp_unit(options.srcml_options, source_filename)
    # print(cpp_unit)
    pydef_code = module_pydef_generator.generate_pydef(cpp_unit, options)
    print(pydef_code)


def play_pydef(code):
    # options = litgen.options.code_style_implot()
    # options.srcml_options.functions_api_prefixes = ["MY_API"]
    # options.srcml_options.api_suffixes = ["MY_API"]

    # options = litgen.options.CodeStyleOptions()
    # options.cpp_indent_size = 4
    # options.cpp_indent_with_tabs = False

    options = litgen.code_style_imgui()

    options.original_location_flag_show = True

    from srcmlcpp import srcml_utils
    xml = srcmlcpp.code_to_srcml(code, dump_positions=False)
    # print(srcml_utils.srcml_to_str_readable(xml))
    print(srcml_utils.srcml_to_str(xml))

    pydef_code = litgen.generate_pydef(code, options, add_boxed_types_definitions=True)
    print(f">>>\n{pydef_code}<<<")

#test_code()


def play_pyi(code):
    # options = litgen.options.code_style_implot()
    # options.srcml_options.functions_api_prefixes = ["MY_API"]
    # options.srcml_options.api_suffixes = ["MY_API"]

    # options = litgen.options.CodeStyleOptions()
    # options.cpp_indent_size = 4
    # options.cpp_indent_with_tabs = False

    options = litgen.code_style_imgui()

    options.original_location_flag_show = True

    # from srcmlcpp import srcml_utils
    # xml = srcmlcpp.code_to_srcml(code, dump_positions=False)
    # # print(srcml_utils.srcml_to_str_readable(xml))
    # print(srcml_utils.srcml_to_str(xml))

    pyi_code = litgen.generate_pyi(code, options, add_boxed_types_definitions=True)
    print(f">>>\n{pyi_code}<<<")



# IMGUI_API bool          Combo(const char* label, int* current_item, const char* const items[], int items_count);
# options = code_style_implot()
# options.srcml_options.functions_api_prefixes = ["MY_API"]
# play_parse(code)
# code = """
# template<typename T> IMGUI_API void foo();
# """
# play_pydef(code)
# play_imgui()

# play_implot()


# import litgen
# options = litgen.CodeStyleOptions()
# options.srcml_options.functions_api_prefixes = ["MY_API", "IMGUI_API"]
# code = """
# const char ** const items=some_default_value();
# """
#
# pydef_code = litgen.generate_pydef(code, options)
# print(pydef_code)

code = """
// Keys value 0 to 511 are left unused as legacy native/opaque key values (< 1.87)
// Keys value >= 512 are named keys (>= 1.87)
enum ImGuiKey_
{
    // Keyboard
    ImGuiKey_None = 0,
    ImGuiKey_Tab = 512,             // == ImGuiKey_NamedKey_BEGIN
    ImGuiKey_LeftArrow,
    ImGuiKey_RightArrow,
    ImGuiKey_UpArrow,
    ImGuiKey_DownArrow,
    ImGuiKey_PageUp,
    ImGuiKey_PageDown,
    ImGuiKey_Home,
    ImGuiKey_End,
    ImGuiKey_Insert,
    ImGuiKey_Delete,
    ImGuiKey_Backspace,
    ImGuiKey_Space,
    ImGuiKey_Enter,
    ImGuiKey_Escape,
    ImGuiKey_LeftCtrl, ImGuiKey_LeftShift, ImGuiKey_LeftAlt, ImGuiKey_LeftSuper,
    ImGuiKey_RightCtrl, ImGuiKey_RightShift, ImGuiKey_RightAlt, ImGuiKey_RightSuper,
    ImGuiKey_Menu,
    ImGuiKey_0, ImGuiKey_1, ImGuiKey_2, ImGuiKey_3, ImGuiKey_4, ImGuiKey_5, ImGuiKey_6, ImGuiKey_7, ImGuiKey_8, ImGuiKey_9,
    ImGuiKey_A, ImGuiKey_B, ImGuiKey_C, ImGuiKey_D, ImGuiKey_E, ImGuiKey_F, ImGuiKey_G, ImGuiKey_H, ImGuiKey_I, ImGuiKey_J,
    ImGuiKey_K, ImGuiKey_L, ImGuiKey_M, ImGuiKey_N, ImGuiKey_O, ImGuiKey_P, ImGuiKey_Q, ImGuiKey_R, ImGuiKey_S, ImGuiKey_T,
    ImGuiKey_U, ImGuiKey_V, ImGuiKey_W, ImGuiKey_X, ImGuiKey_Y, ImGuiKey_Z,
    ImGuiKey_F1, ImGuiKey_F2, ImGuiKey_F3, ImGuiKey_F4, ImGuiKey_F5, ImGuiKey_F6,
    ImGuiKey_F7, ImGuiKey_F8, ImGuiKey_F9, ImGuiKey_F10, ImGuiKey_F11, ImGuiKey_F12,
    ImGuiKey_Apostrophe,        // '
    ImGuiKey_Comma,             // ,
    ImGuiKey_Minus,             // -
    ImGuiKey_Period,            // .
    ImGuiKey_Slash,             // /
    ImGuiKey_Semicolon,         // ;
    ImGuiKey_Equal,             // =
    ImGuiKey_LeftBracket,       // [
    ImGuiKey_Backslash,         // \ (this text inhibit multiline comment caused by backslash)
    ImGuiKey_RightBracket,      // ]
    ImGuiKey_GraveAccent,       // `
    ImGuiKey_CapsLock,
    ImGuiKey_ScrollLock,
    ImGuiKey_NumLock,
    ImGuiKey_PrintScreen,
    ImGuiKey_Pause,
    ImGuiKey_Keypad0, ImGuiKey_Keypad1, ImGuiKey_Keypad2, ImGuiKey_Keypad3, ImGuiKey_Keypad4,
    ImGuiKey_Keypad5, ImGuiKey_Keypad6, ImGuiKey_Keypad7, ImGuiKey_Keypad8, ImGuiKey_Keypad9,
    ImGuiKey_KeypadDecimal,
    ImGuiKey_KeypadDivide,
    ImGuiKey_KeypadMultiply,
    ImGuiKey_KeypadSubtract,
    ImGuiKey_KeypadAdd,
    ImGuiKey_KeypadEnter,
    ImGuiKey_KeypadEqual,

    // Gamepad (some of those are analog values, 0.0f to 1.0f)                              // NAVIGATION action
    ImGuiKey_GamepadStart,          // Menu (Xbox)          + (Switch)   Start/Options (PS) // --
    ImGuiKey_GamepadBack,           // View (Xbox)          - (Switch)   Share (PS)         // --
    ImGuiKey_GamepadFaceUp,         // Y (Xbox)             X (Switch)   Triangle (PS)      // -> ImGuiNavInput_Input
    ImGuiKey_GamepadFaceDown,       // A (Xbox)             B (Switch)   Cross (PS)         // -> ImGuiNavInput_Activate
    ImGuiKey_GamepadFaceLeft,       // X (Xbox)             Y (Switch)   Square (PS)        // -> ImGuiNavInput_Menu
    ImGuiKey_GamepadFaceRight,      // B (Xbox)             A (Switch)   Circle (PS)        // -> ImGuiNavInput_Cancel
    ImGuiKey_GamepadDpadUp,         // D-pad Up                                             // -> ImGuiNavInput_DpadUp
    ImGuiKey_GamepadDpadDown,       // D-pad Down                                           // -> ImGuiNavInput_DpadDown
    ImGuiKey_GamepadDpadLeft,       // D-pad Left                                           // -> ImGuiNavInput_DpadLeft
    ImGuiKey_GamepadDpadRight,      // D-pad Right                                          // -> ImGuiNavInput_DpadRight
    ImGuiKey_GamepadL1,             // L Bumper (Xbox)      L (Switch)   L1 (PS)            // -> ImGuiNavInput_FocusPrev + ImGuiNavInput_TweakSlow
    ImGuiKey_GamepadR1,             // R Bumper (Xbox)      R (Switch)   R1 (PS)            // -> ImGuiNavInput_FocusNext + ImGuiNavInput_TweakFast
    ImGuiKey_GamepadL2,             // L Trigger (Xbox)     ZL (Switch)  L2 (PS) [Analog]
    ImGuiKey_GamepadR2,             // R Trigger (Xbox)     ZR (Switch)  R2 (PS) [Analog]
    ImGuiKey_GamepadL3,             // L Thumbstick (Xbox)  L3 (Switch)  L3 (PS)
    ImGuiKey_GamepadR3,             // R Thumbstick (Xbox)  R3 (Switch)  R3 (PS)
    ImGuiKey_GamepadLStickUp,       // [Analog]                                             // -> ImGuiNavInput_LStickUp
    ImGuiKey_GamepadLStickDown,     // [Analog]                                             // -> ImGuiNavInput_LStickDown
    ImGuiKey_GamepadLStickLeft,     // [Analog]                                             // -> ImGuiNavInput_LStickLeft
    ImGuiKey_GamepadLStickRight,    // [Analog]                                             // -> ImGuiNavInput_LStickRight
    ImGuiKey_GamepadRStickUp,       // [Analog]
    ImGuiKey_GamepadRStickDown,     // [Analog]
    ImGuiKey_GamepadRStickLeft,     // [Analog]
    ImGuiKey_GamepadRStickRight,    // [Analog]

    // Keyboard Modifiers (explicitly submitted by backend via AddKeyEvent() calls)
    // - This is mirroring the data also written to io.KeyCtrl, io.KeyShift, io.KeyAlt, io.KeySuper, in a format allowing
    //   them to be accessed via standard key API, allowing calls such as IsKeyPressed(), IsKeyReleased(), querying duration etc.
    // - Code polling every keys (e.g. an interface to detect a key press for input mapping) might want to ignore those
    //   and prefer using the real keys (e.g. ImGuiKey_LeftCtrl, ImGuiKey_RightCtrl instead of ImGuiKey_ModCtrl).
    // - In theory the value of keyboard modifiers should be roughly equivalent to a logical or of the equivalent left/right keys.
    //   In practice: it's complicated; mods are often provided from different sources. Keyboard layout, IME, sticky keys and
    //   backends tend to interfere and break that equivalence. The safer decision is to relay that ambiguity down to the end-user...
    ImGuiKey_ModCtrl, ImGuiKey_ModShift, ImGuiKey_ModAlt, ImGuiKey_ModSuper,

    // End of list
    ImGuiKey_COUNT,                 // No valid ImGuiKey is ever greater than this value

    // [Internal] Prior to 1.87 we required user to fill io.KeysDown[512] using their own native index + a io.KeyMap[] array.
    // We are ditching this method but keeping a legacy path for user code doing e.g. IsKeyPressed(MY_NATIVE_KEY_CODE)
    ImGuiKey_NamedKey_BEGIN         = 512,
    ImGuiKey_NamedKey_END           = ImGuiKey_COUNT,
    ImGuiKey_NamedKey_COUNT         = ImGuiKey_NamedKey_END - ImGuiKey_NamedKey_BEGIN,
#ifdef IMGUI_DISABLE_OBSOLETE_KEYIO
    ImGuiKey_KeysData_SIZE          = ImGuiKey_NamedKey_COUNT,          // Size of KeysData[]: only hold named keys
    ImGuiKey_KeysData_OFFSET        = ImGuiKey_NamedKey_BEGIN           // First key stored in io.KeysData[0]. Accesses to io.KeysData[] must use (key - ImGuiKey_KeysData_OFFSET).
#else
    ImGuiKey_KeysData_SIZE          = ImGuiKey_COUNT,                   // Size of KeysData[]: hold legacy 0..512 keycodes + named keys
    ImGuiKey_KeysData_OFFSET        = 0                                 // First key stored in io.KeysData[0]. Accesses to io.KeysData[] must use (key - ImGuiKey_KeysData_OFFSET).
#endif

#ifndef IMGUI_DISABLE_OBSOLETE_FUNCTIONS
    , ImGuiKey_KeyPadEnter = ImGuiKey_KeypadEnter   // Renamed in 1.87
#endif
};

"""

play_pyi(code)
