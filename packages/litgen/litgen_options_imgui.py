from codemanip.code_replacements import RegexReplacementList

from litgen.options import LitgenOptions


def _preprocess_imgui_code(code: str) -> str:
    """
    The imgui code uses two macros (IM_FMTARGS and IM_FMTLIST) which help the compiler
        #define IM_FMTARGS(FMT)             __attribute__((format(printf, FMT, FMT+1)))
        #define IM_FMTLIST(FMT)             __attribute__((format(printf, FMT, 0)))

    They are used like this:
        IMGUI_API bool          TreeNode(const char* str_id, const char* fmt, ...) IM_FMTARGS(2);

    They are removed before processing the header, because they would not be correctly interpreted by srcml.
    """
    import re

    new_code = code
    new_code = re.sub(r"IM_FMTARGS\(\d\)", "", new_code)
    new_code = re.sub(r"IM_FMTLIST\(\d\)", "", new_code)
    return new_code


def litgen_options_imgui() -> LitgenOptions:
    from litgen.internal import cpp_to_python

    options = LitgenOptions()

    options.generate_to_string = False
    options.cpp_indent_size = 4

    options.code_replacements = cpp_to_python.standard_code_replacements()
    options.code_replacements.merge_replacements(
        RegexReplacementList.from_string(r"\bImVector\s*<\s*([\w:]*)\s*> -> List[\1]")
    )

    options.python_max_line_length = -1  # in ImGui, the function decls are on *one* line
    options.python_convert_to_snake_case = True
    options.original_location_flag_show = True
    options.original_signature_flag_show = True

    options.srcml_options.functions_api_prefixes = ["IMGUI_API"]
    options.srcml_options.header_guard_suffixes.append("IMGUI_DISABLE")

    options.srcml_options.code_preprocess_function = _preprocess_imgui_code

    options.fn_exclude_by_name__regexes = [
        # IMGUI_API void          SetAllocatorFunctions(ImGuiMemAllocFunc alloc_func, ImGuiMemFreeFunc free_func, void* user_data = NULL);
        #                                               ^
        # IMGUI_API void          GetAllocatorFunctions(ImGuiMemAllocFunc* p_alloc_func, ImGuiMemFreeFunc* p_free_func, void** p_user_data);
        #                                               ^
        # IMGUI_API void*         MemAlloc(size_t size);
        #           ^
        # IMGUI_API void          MemFree(void* ptr);
        #                                 ^
        r"\bGetAllocatorFunctions\b",
        r"\bSetAllocatorFunctions\b",
        r"\bMemAlloc\b",
        r"\bMemFree\b",
        # IMGUI_API void              GetTexDataAsAlpha8(unsigned char** out_pixels, int* out_width, int* out_height, int* out_bytes_per_pixel = NULL);  // 1 byte per-pixel
        #                                                             ^
        # IMGUI_API void              GetTexDataAsRGBA32(unsigned char** out_pixels, int* out_width, int* out_height, int* out_bytes_per_pixel = NULL);  // 4 bytes-per-pixel
        #                                                             ^
        r"\bGetTexDataAsAlpha8\b",
        r"\bGetTexDataAsRGBA32\b",
        # IMGUI_API ImVec2            CalcTextSizeA(float size, float max_width, float wrap_width, const char* text_begin, const char* text_end = NULL, const char** remaining = NULL) const; // utf8
        #                                                                                                                                                         ^
        r"\bCalcTextSizeA\b",
        "appendfv",
        # Exclude function whose name ends with V, like for example
        #       IMGUI_API void          TextV(const char* fmt, va_list args)                            IM_FMTLIST(1);
        # which are utilities for variadic print format
        r"\w*V\Z",
    ]

    options.member_exclude_by_name__regexes = [
        #     typedef void (*ImDrawCallback)(const ImDrawList* parent_list, const ImDrawCmd* cmd);
        #     ImDrawCallback  UserCallback;       // 4-8  // If != NULL, call the function instead of rendering the vertices. clip_rect and texture_id will be set normally.
        #     ^
        r"\bUserCallback\b",
        # struct ImDrawData
        # { ...
        #     ImDrawList**    CmdLists;               // Array of ImDrawList* to render. The ImDrawList are owned by ImGuiContext and only pointed to from here.
        #               ^
        # }
        r"\bCmdLists\b",
    ]

    options.member_exclude_by_type__regexes = [
        r"^char\s*\*",
        r"const ImWchar\s*\*",
        r"unsigned char\s*\*",
        r"unsigned int\s*\*",
    ]

    options.class_exclude_by_name__regexes = [r"^ImVector\b", "ImGuiTextBuffer"]

    options.member_numeric_c_array_types += [
        "ImGuiID",
        "ImS8",
        "ImU8",
        "ImS16",
        "ImU16",
        "ImS32",
        "ImU32",
        "ImS64",
        "ImU64",
    ]

    options.fn_force_overload__regexes = [
        r"^SetScroll",
        r"^Drag",
        r"^Slider",
        r"^InputText",
        r"Popup",
        r"DrawList",
        r"^Table",
    ]

    options.fn_return_force_policy_reference_for_pointers__regexes = [r".*"]
    options.fn_return_force_policy_reference_for_references__regexes = [r".*"]

    options.fn_params_replace_buffer_by_array__regexes = [r".*"]
    options.fn_params_buffer_types += ["float"]

    options.fn_params_exclude_types__regexes = [
        "Callback$"  # Exclude callbacks from the params when they have a default value
        # (since imgui use bare C function pointers, not easily portable)
    ]

    # Version where we use Boxed types everywhere
    # options.fn_params_adapt_modifiable_immutable_regexes = [r".*"]
    # Version where we return tuples
    options.fn_params_replace_modifiable_c_array_by_boxed__regexes = []
    options.fn_params_output_modifiable_immutable_to_return__regexes = [r".*"]

    options.srcml_options.flag_show_progress = True

    return options
