# type: ignore
import sys
from typing import Literal, List, Any
import numpy as np
from enum import Enum
import numpy

##################################################
#    Manually inserted code (typedefs, etc.)
##################################################

VoidPtr = Any

#-----------------------------------------------------------------------------
# [SECTION] Forward declarations and basic types
#-----------------------------------------------------------------------------

"""
// Forward declarations
struct ImDrawChannel;               // Temporary storage to output draw commands out of order, used by ImDrawListSplitter and ImDrawList::ChannelsSplit()
struct ImDrawCmd;                   // A single draw command within a parent ImDrawList (generally maps to 1 GPU draw call, unless it is a callback)
struct ImDrawData;                  // All draw command lists required to render the frame + pos/size coordinates to use for the projection matrix.
struct ImDrawList;                  // A single draw command list (generally one per window, conceptually you may see this as a dynamic "mesh" builder)
struct ImDrawListSharedData;        // Data shared among multiple draw lists (typically owned by parent ImGui context, but you may create one yourself)
struct ImDrawListSplitter;          // Helper to split a draw list into different layers which can be drawn into out of order, then flattened back.
struct ImDrawVert;                  // A single vertex (pos + uv + col = 20 bytes by default. Override layout with IMGUI_OVERRIDE_DRAWVERT_STRUCT_LAYOUT)
struct ImFont;                      // Runtime data for a single font within a parent ImFontAtlas
struct ImFontAtlas;                 // Runtime data for multiple fonts, bake multiple fonts into a single texture, TTF/OTF font loader
struct ImFontBuilderIO;             // Opaque interface to a font builder (stb_truetype or FreeType).
struct ImFontConfig;                // Configuration data when adding a font or merging fonts
struct ImFontGlyph;                 // A single font glyph (code point + coordinates within in ImFontAtlas + offset)
struct ImFontGlyphRangesBuilder;    // Helper to build glyph ranges from text/string data
struct ImColor;                     // Helper functions to create a color that can be converted to either u32 or float4 (*OBSOLETE* please avoid using)
struct ImGuiContext;                // Dear ImGui context (opaque structure, unless including imgui_internal.h)
struct ImGuiIO;                     // Main configuration and I/O between your application and ImGui
struct ImGuiInputTextCallbackData;  // Shared state of InputText() when using custom ImGuiInputTextCallback (rare/advanced use)
struct ImGuiKeyData;                // Storage for ImGuiIO and IsKeyDown(), IsKeyPressed() etc functions.
struct ImGuiListClipper;            // Helper to manually clip large list of items
struct ImGuiOnceUponAFrame;         // Helper for running a block of code not more than once a frame
struct ImGuiPayload;                // User data payload for drag and drop operations
struct ImGuiPlatformImeData;        // Platform IME data for io.SetPlatformImeDataFn() function.
struct ImGuiSizeCallbackData;       // Callback data when using SetNextWindowSizeConstraints() (rare/advanced use)
struct ImGuiStorage;                // Helper for key->value storage
struct ImGuiStyle;                  // Runtime data for styling/colors
struct ImGuiTableSortSpecs;         // Sorting specifications for a table (often handling sort specs for a single column, occasionally more)
struct ImGuiTableColumnSortSpecs;   // Sorting specification for one column of a table
struct ImGuiTextBuffer;             // Helper to hold and append into a text buffer (~string builder)
struct ImGuiTextFilter;             // Helper to parse and apply text filters (e.g. "aaaaa[,bbbbb][,ccccc]")
struct ImGuiViewport;               // A Platform Window (always only one in 'master' branch), in the future may represent Platform Monitor
"""
# We forward declare only the opaque structures
ImGuiContext = Any
ImDrawListSharedData = Any
ImDrawVert = Any
ImFontBuilderIO = Any


"""
// Enums/Flags (declared as int for compatibility with old C++, to allow using as flags without overhead, and to not pollute the top of this file)
// - Tip: Use your programming IDE navigation facilities on the names in the _central column_ below to find the actual flags/enum lists!
//   In Visual Studio IDE: CTRL+comma ("Edit.GoToAll") can follow symbols in comments, whereas CTRL+F12 ("Edit.GoToImplementation") cannot.
//   With Visual Assist installed: ALT+G ("VAssistX.GoToImplementation") can also follow symbols in comments.
typedef int ImGuiCol;               // -> enum ImGuiCol_             // Enum: A color identifier for styling
typedef int ImGuiCond;              // -> enum ImGuiCond_            // Enum: A condition for many Set*() functions
typedef int ImGuiDataType;          // -> enum ImGuiDataType_        // Enum: A primary data type
typedef int ImGuiDir;               // -> enum ImGuiDir_             // Enum: A cardinal direction
typedef int ImGuiKey;               // -> enum ImGuiKey_             // Enum: A key identifier
typedef int ImGuiNavInput;          // -> enum ImGuiNavInput_        // Enum: An input identifier for navigation
typedef int ImGuiMouseButton;       // -> enum ImGuiMouseButton_     // Enum: A mouse button identifier (0=left, 1=right, 2=middle)
typedef int ImGuiMouseCursor;       // -> enum ImGuiMouseCursor_     // Enum: A mouse cursor identifier
typedef int ImGuiSortDirection;     // -> enum ImGuiSortDirection_   // Enum: A sorting direction (ascending or descending)
typedef int ImGuiStyleVar;          // -> enum ImGuiStyleVar_        // Enum: A variable identifier for styling
typedef int ImGuiTableBgTarget;     // -> enum ImGuiTableBgTarget_   // Enum: A color target for TableSetBgColor()
typedef int ImDrawFlags;            // -> enum ImDrawFlags_          // Flags: for ImDrawList functions
typedef int ImDrawListFlags;        // -> enum ImDrawListFlags_      // Flags: for ImDrawList instance
typedef int ImFontAtlasFlags;       // -> enum ImFontAtlasFlags_     // Flags: for ImFontAtlas build
typedef int ImGuiBackendFlags;      // -> enum ImGuiBackendFlags_    // Flags: for io.BackendFlags
typedef int ImGuiButtonFlags;       // -> enum ImGuiButtonFlags_     // Flags: for InvisibleButton()
typedef int ImGuiColorEditFlags;    // -> enum ImGuiColorEditFlags_  // Flags: for ColorEdit4(), ColorPicker4() etc.
typedef int ImGuiConfigFlags;       // -> enum ImGuiConfigFlags_     // Flags: for io.ConfigFlags
typedef int ImGuiComboFlags;        // -> enum ImGuiComboFlags_      // Flags: for BeginCombo()
typedef int ImGuiDragDropFlags;     // -> enum ImGuiDragDropFlags_   // Flags: for BeginDragDropSource(), AcceptDragDropPayload()
typedef int ImGuiFocusedFlags;      // -> enum ImGuiFocusedFlags_    // Flags: for IsWindowFocused()
typedef int ImGuiHoveredFlags;      // -> enum ImGuiHoveredFlags_    // Flags: for IsItemHovered(), IsWindowHovered() etc.
typedef int ImGuiInputTextFlags;    // -> enum ImGuiInputTextFlags_  // Flags: for InputText(), InputTextMultiline()
typedef int ImGuiModFlags;          // -> enum ImGuiModFlags_        // Flags: for io.KeyMods (Ctrl/Shift/Alt/Super)
typedef int ImGuiPopupFlags;        // -> enum ImGuiPopupFlags_      // Flags: for OpenPopup*(), BeginPopupContext*(), IsPopupOpen()
typedef int ImGuiSelectableFlags;   // -> enum ImGuiSelectableFlags_ // Flags: for Selectable()
typedef int ImGuiSliderFlags;       // -> enum ImGuiSliderFlags_     // Flags: for DragFloat(), DragInt(), SliderFloat(), SliderInt() etc.
typedef int ImGuiTabBarFlags;       // -> enum ImGuiTabBarFlags_     // Flags: for BeginTabBar()
typedef int ImGuiTabItemFlags;      // -> enum ImGuiTabItemFlags_    // Flags: for BeginTabItem()
typedef int ImGuiTableFlags;        // -> enum ImGuiTableFlags_      // Flags: For BeginTable()
typedef int ImGuiTableColumnFlags;  // -> enum ImGuiTableColumnFlags_// Flags: For TableSetupColumn()
typedef int ImGuiTableRowFlags;     // -> enum ImGuiTableRowFlags_   // Flags: For TableNextRow()
typedef int ImGuiTreeNodeFlags;     // -> enum ImGuiTreeNodeFlags_   // Flags: for TreeNode(), TreeNodeEx(), CollapsingHeader()
typedef int ImGuiViewportFlags;     // -> enum ImGuiViewportFlags_   // Flags: for ImGuiViewport
typedef int ImGuiWindowFlags;       // -> enum ImGuiWindowFlags_     // Flags: for Begin(), BeginChild()
"""
ImGuiCol = int               # -> enum ImGuiCol_             # Enum: A color identifier for styling
ImGuiCond = int              # -> enum ImGuiCond_            # Enum: A condition for many Set*() functions
ImGuiDataType = int          # -> enum ImGuiDataType_        # Enum: A primary data type
ImGuiDir = int               # -> enum ImGuiDir_             # Enum: A cardinal direction
ImGuiKey = int               # -> enum ImGuiKey_             # Enum: A key identifier
ImGuiNavInput = int          # -> enum ImGuiNavInput_        # Enum: An input identifier for navigation
ImGuiMouseButton = int       # -> enum ImGuiMouseButton_     # Enum: A mouse button identifier (0=left, 1=right, 2=middle)
ImGuiMouseCursor = int       # -> enum ImGuiMouseCursor_     # Enum: A mouse cursor identifier
ImGuiSortDirection = int     # -> enum ImGuiSortDirection_   # Enum: A sorting direction (ascending or descending)
ImGuiStyleVar = int          # -> enum ImGuiStyleVar_        # Enum: A variable identifier for styling
ImGuiTableBgTarget = int     # -> enum ImGuiTableBgTarget_   # Enum: A color target for TableSetBgColor()
ImDrawFlags = int            # -> enum ImDrawFlags_          # Flags: for ImDrawList functions
ImDrawListFlags = int        # -> enum ImDrawListFlags_      # Flags: for ImDrawList instance
ImFontAtlasFlags = int       # -> enum ImFontAtlasFlags_     # Flags: for ImFontAtlas build
ImGuiBackendFlags = int      # -> enum ImGuiBackendFlags_    # Flags: for io.BackendFlags
ImGuiButtonFlags = int       # -> enum ImGuiButtonFlags_     # Flags: for InvisibleButton()
ImGuiColorEditFlags = int    # -> enum ImGuiColorEditFlags_  # Flags: for ColorEdit4(), ColorPicker4() etc.
ImGuiConfigFlags = int       # -> enum ImGuiConfigFlags_     # Flags: for io.ConfigFlags
ImGuiComboFlags = int        # -> enum ImGuiComboFlags_      # Flags: for BeginCombo()
ImGuiDragDropFlags = int     # -> enum ImGuiDragDropFlags_   # Flags: for BeginDragDropSource(), AcceptDragDropPayload()
ImGuiFocusedFlags = int      # -> enum ImGuiFocusedFlags_    # Flags: for IsWindowFocused()
ImGuiHoveredFlags = int      # -> enum ImGuiHoveredFlags_    # Flags: for IsItemHovered(), IsWindowHovered() etc.
ImGuiInputTextFlags = int    # -> enum ImGuiInputTextFlags_  # Flags: for InputText(), InputTextMultiline()
ImGuiModFlags = int          # -> enum ImGuiModFlags_        # Flags: for io.KeyMods (Ctrl/Shift/Alt/Super)
ImGuiPopupFlags = int        # -> enum ImGuiPopupFlags_      # Flags: for OpenPopup*(), BeginPopupContext*(), IsPopupOpen()
ImGuiSelectableFlags = int   # -> enum ImGuiSelectableFlags_ # Flags: for Selectable()
ImGuiSliderFlags = int       # -> enum ImGuiSliderFlags_     # Flags: for DragFloat(), DragInt(), SliderFloat(), SliderInt() etc.
ImGuiTabBarFlags = int       # -> enum ImGuiTabBarFlags_     # Flags: for BeginTabBar()
ImGuiTabItemFlags = int      # -> enum ImGuiTabItemFlags_    # Flags: for BeginTabItem()
ImGuiTableFlags = int        # -> enum ImGuiTableFlags_      # Flags: For BeginTable()
ImGuiTableColumnFlags = int  # -> enum ImGuiTableColumnFlags_# Flags: For TableSetupColumn()
ImGuiTableRowFlags = int     # -> enum ImGuiTableRowFlags_   # Flags: For TableNextRow()
ImGuiTreeNodeFlags = int     # -> enum ImGuiTreeNodeFlags_   # Flags: for TreeNode(), TreeNodeEx(), CollapsingHeader()
ImGuiViewportFlags = int     # -> enum ImGuiViewportFlags_   # Flags: for ImGuiViewport
ImGuiWindowFlags = int       # -> enum ImGuiWindowFlags_     # Flags: for Begin(), BeginChild()


"""
// ImTexture: user data for renderer backend to identify a texture [Compile-time configurable type]
// - To use something else than an opaque void* pointer: override with e.g. '#define ImTextureID MyTextureType*' in your imconfig.h file.
// - This can be whatever to you want it to be! read the FAQ about ImTextureID for details.
#ifndef ImTextureID
typedef void* ImTextureID;          // Default: store a pointer or an integer fitting in a pointer (most renderer backends are ok with that)
#endif
"""
ImTextureID = VoidPtr

"""
// ImDrawIdx: vertex index. [Compile-time configurable type]
// - To use 16-bit indices + allow large meshes: backend need to set 'io.BackendFlags |= ImGuiBackendFlags_RendererHasVtxOffset' and handle ImDrawCmd::VtxOffset (recommended).
// - To use 32-bit indices: override with '#define ImDrawIdx unsigned int' in your imconfig.h file.
#ifndef ImDrawIdx
typedef unsigned short ImDrawIdx;   // Default: 16-bit (for maximum compatibility with renderer backends)
#endif
"""
ImDrawIdx = int


"""
// Scalar data types
typedef unsigned int        ImGuiID;// A unique ID used by widgets (typically the result of hashing a stack of string)
typedef signed char         ImS8;   // 8-bit signed integer
typedef unsigned char       ImU8;   // 8-bit unsigned integer
typedef signed short        ImS16;  // 16-bit signed integer
typedef unsigned short      ImU16;  // 16-bit unsigned integer
typedef signed int          ImS32;  // 32-bit signed integer == int
typedef unsigned int        ImU32;  // 32-bit unsigned integer (often used to store packed colors)
typedef signed   long long  ImS64;  // 64-bit signed integer
typedef unsigned long long  ImU64;  // 64-bit unsigned integer
"""
# Scalar data types
ImGuiID = int# A unique ID used by widgets (typically the result of hashing a stack of string)
ImS8 = int   # 8-bit integer
ImU8 = int   # 8-bit integer
ImS16 = int  # 16-bit integer
ImU16 = int  # 16-bit integer
ImS32 = int  # 32-bit integer == int
ImU32 = int  # 32-bit integer (often used to store packed colors)
ImS64 = int  # 64-bit integer
ImU64 = int  # 64-bit integer


"""
// Character types
// (we generally use UTF-8 encoded string in the API. This is storage specifically for a decoded character used for keyboard input and display)
typedef unsigned short ImWchar16;   // A single decoded U16 character/code point. We encode them as multi bytes UTF-8 when used in strings.
typedef unsigned int ImWchar32;     // A single decoded U32 character/code point. We encode them as multi bytes UTF-8 when used in strings.
#ifdef IMGUI_USE_WCHAR32            // ImWchar [configurable type: override in imconfig.h with '#define IMGUI_USE_WCHAR32' to support Unicode planes 1-16]
typedef ImWchar32 ImWchar;
#else
typedef ImWchar16 ImWchar;
#endif
"""
ImWchar = int
ImWchar16 = int
ImWchar32 = int


"""
// Callback and functions types
typedef int     (*ImGuiInputTextCallback)(ImGuiInputTextCallbackData* data);    // Callback function for ImGui::InputText()
typedef void    (*ImGuiSizeCallback)(ImGuiSizeCallbackData* data);              // Callback function for ImGui::SetNextWindowSizeConstraints()
typedef void*   (*ImGuiMemAllocFunc)(size_t sz, void* user_data);               // Function signature for ImGui::SetAllocatorFunctions()
typedef void    (*ImGuiMemFreeFunc)(void* ptr, void* user_data);                // Function signature for ImGui::SetAllocatorFunctions()
"""
"""
#ifndef ImDrawCallback
    typedef void (*ImDrawCallback)(const ImDrawList* parent_list, const ImDrawCmd* cmd);
#endif
"""
ImGuiInputTextCallback = Any       # These types are C function pointers
ImGuiSizeCallback = Any            # and thus are hard to create from python
ImGuiMemAllocFunc = Any
ImGuiMemFreeFunc = Any
ImDrawCallback = Any


"""
// Helpers macros to generate 32-bit encoded colors
// User can declare their own format by #defining the 5 _SHIFT/_MASK macros in their imconfig file.
#ifndef IM_COL32_R_SHIFT
#ifdef IMGUI_USE_BGRA_PACKED_COLOR
#define IM_COL32_R_SHIFT    16
#define IM_COL32_G_SHIFT    8
#define IM_COL32_B_SHIFT    0
#define IM_COL32_A_SHIFT    24
#define IM_COL32_A_MASK     0xFF000000
#else
#define IM_COL32_R_SHIFT    0
#define IM_COL32_G_SHIFT    8
#define IM_COL32_B_SHIFT    16
#define IM_COL32_A_SHIFT    24
#define IM_COL32_A_MASK     0xFF000000
#endif
#endif
#define IM_COL32(R,G,B,A)    (((ImU32)(A)<<IM_COL32_A_SHIFT) | ((ImU32)(B)<<IM_COL32_B_SHIFT) | ((ImU32)(G)<<IM_COL32_G_SHIFT) | ((ImU32)(R)<<IM_COL32_R_SHIFT))
#define IM_COL32_WHITE       IM_COL32(255,255,255,255)  // Opaque white = 0xFFFFFFFF
#define IM_COL32_BLACK       IM_COL32(0,0,0,255)        // Opaque black
#define IM_COL32_BLACK_TRANS IM_COL32(0,0,0,0)          // Transparent black = 0x00000000
"""
IM_COL32_R_SHIFT= 0
IM_COL32_G_SHIFT = 8
IM_COL32_B_SHIFT = 16
IM_COL32_A_SHIFT = 24


def IM_COL32(r: ImU32, g: ImU32, b: ImU32, a: ImU32) -> ImU32:
    r = ((a<<IM_COL32_A_SHIFT) | (b<<IM_COL32_B_SHIFT) | (g<<IM_COL32_G_SHIFT) | (r<<IM_COL32_R_SHIFT))
    return r


IM_COL32_WHITE = IM_COL32(255, 255, 255, 255)
IM_COL32_BLACK = IM_COL32(0, 0, 0, 255)


"""
Additional customizations
"""
ImGuiTextRange = Any # internal structure of ImGuiTextFilter, composed of string pointers (cannot be easily adapted)
ImGuiStoragePair = Any


# Disable black formatter
# fmt: off

##################################################
#    AUTO GENERATED CODE BELOW
##################################################
# <litgen_stub> // Autogenerated code below! Do not edit!
# <Autogenerated_Boxed_Types>
class BoxedBool:    # imgui.h:1
    value:bool                                      # imgui.h:3
    def __init__(self, v: bool = False) -> None:    # imgui.h:4
        pass
    def __repr__(self) -> str:                      # imgui.h:5
        pass
class BoxedInt:    # imgui.h:1
    value:int                                  # imgui.h:3
    def __init__(self, v: int = 0) -> None:    # imgui.h:4
        pass
    def __repr__(self) -> str:                 # imgui.h:5
        pass
class BoxedUnsignedInt:    # imgui.h:1
    value:int                                  # imgui.h:3
    def __init__(self, v: int = 0) -> None:    # imgui.h:4
        pass
    def __repr__(self) -> str:                 # imgui.h:5
        pass
class BoxedFloat:    # imgui.h:1
    value:float                                   # imgui.h:3
    def __init__(self, v: float = 0.) -> None:    # imgui.h:4
        pass
    def __repr__(self) -> str:                    # imgui.h:5
        pass
class BoxedDouble:    # imgui.h:1
    value:float                                   # imgui.h:3
    def __init__(self, v: float = 0.) -> None:    # imgui.h:4
        pass
    def __repr__(self) -> str:                    # imgui.h:5
        pass
# </Autogenerated_Boxed_Types>


# dear imgui, v1.88 WIP
# (headers)

# Help:
# - Read FAQ at http://dearimgui.org/faq
# - Newcomers, read 'Programmer guide' in imgui.cpp for notes on how to setup Dear ImGui in your codebase.
# - Call and read ImGui::ShowDemoWindow() in imgui_demo.cpp. All applications in examples/ are doing that.
# Read imgui.cpp for details, links and comments.

# Resources:
# - FAQ                   http://dearimgui.org/faq
# - Homepage & latest     https://github.com/ocornut/imgui
# - Releases & changelog  https://github.com/ocornut/imgui/releases
# - Gallery               https://github.com/ocornut/imgui/issues/5243 (please post your screenshots/video there!)
# - Wiki                  https://github.com/ocornut/imgui/wiki (lots of good stuff there)
# - Glossary              https://github.com/ocornut/imgui/wiki/Glossary
# - Issues & support      https://github.com/ocornut/imgui/issues

# Getting Started?
# - For first-time users having issues compiling/linking/running or issues loading fonts:
#   please post in https://github.com/ocornut/imgui/discussions if you cannot find a solution in resources above.

#
#
#Index of this file:
#// [SECTION] Header mess
#// [SECTION] Forward declarations and basic types
#// [SECTION] Dear ImGui end-user API functions
#// [SECTION] Flags & Enumerations
#// [SECTION] Helpers: Memory allocations macros, ImVector<>
#// [SECTION] ImGuiStyle
#// [SECTION] ImGuiIO
#// [SECTION] Misc data structures (ImGuiInputTextCallbackData, ImGuiSizeCallbackData, ImGuiPayload, ImGuiTableSortSpecs, ImGuiTableColumnSortSpecs)
#// [SECTION] Helpers (ImGuiOnceUponAFrame, ImGuiTextFilter, ImGuiTextBuffer, ImGuiStorage, ImGuiListClipper, ImColor)
#// [SECTION] Drawing API (ImDrawCallback, ImDrawCmd, ImDrawIdx, ImDrawVert, ImDrawChannel, ImDrawListSplitter, ImDrawFlags, ImDrawListFlags, ImDrawList, ImDrawData)
#// [SECTION] Font API (ImFontConfig, ImFontGlyph, ImFontGlyphRangesBuilder, ImFontAtlasFlags, ImFontAtlas, ImFont)
#// [SECTION] Viewports (ImGuiViewportFlags, ImGuiViewport)
#// [SECTION] Platform Dependent Interfaces (ImGuiPlatformImeData)
#// [SECTION] Obsolete functions and types
#
#


# Configuration file with compile-time options (edit imconfig.h or '#define IMGUI_USER_CONFIG "myfilename.h" from your build system')


#-----------------------------------------------------------------------------
# [SECTION] Header mess
#-----------------------------------------------------------------------------

# Includes

# Version
# (Integer encoded as XYYZZ for use in #if preprocessor conditionals. Work in progress versions typically starts at XYY99 then bounce up to XYY00, XYY01 etc. when release tagging happens)

# Define attributes of all API symbols declarations (e.g. for DLL under Windows)
# IMGUI_API is used for core imgui functions, IMGUI_IMPL_API is used for the default backends files (imgui_impl_xxx.h)
# Using dear imgui via a shared library is not recommended, because we don't guarantee backward nor forward ABI compatibility (also function call overhead, as dear imgui is a call-heavy API)

# Helper Macros

# Helper Macros - IM_FMTARGS, IM_FMTLIST: Apply printf-style warnings to our formatting functions.

# Disable some of MSVC most aggressive Debug runtime checks in function header/footer (used in some simple/low-level functions)

# Warnings

#-----------------------------------------------------------------------------
# [SECTION] Forward declarations and basic types
#-----------------------------------------------------------------------------

# Forward declarations

# Enums/Flags (declared as int for compatibility with old C++, to allow using as flags without overhead, and to not pollute the top of this file)
# - Tip: Use your programming IDE navigation facilities on the names in the _central column_ below to find the actual flags/enum lists!
#   In Visual Studio IDE: CTRL+comma ("Edit.GoToAll") can follow symbols in comments, whereas CTRL+F12 ("Edit.GoToImplementation") cannot.
#   With Visual Assist installed: ALT+G ("VAssistX.GoToImplementation") can also follow symbols in comments.
# -> enum ImGuiWindowFlags_     // Flags: for Begin(), BeginChild()

# ImTexture: user data for renderer backend to identify a texture [Compile-time configurable type]
# - To use something else than an opaque None* pointer: override with e.g. '#define ImTextureID MyTextureType*' in your imconfig.h file.
# - This can be whatever to you want it to be! read the FAQ about ImTextureID for details.

# ImDrawIdx: vertex index. [Compile-time configurable type]
# - To use 16-bit indices + allow large meshes: backend need to set 'io.BackendFlags |= ImGuiBackendFlags_RendererHasVtxOffset' and handle ImDrawCmd::VtxOffset (recommended).
# - To use 32-bit indices: override with '#define ImDrawIdx unsigned int' in your imconfig.h file.

# Scalar data types

# Character types
# (we generally use UTF-8 encoded string in the API. This is storage specifically for a decoded character used for keyboard input and display)
# A single decoded U32 character/code point. We encode them as multi bytes UTF-8 when used in strings.

# Callback and functions types

class ImVec2:    # imgui.h:249
    x:float                                              # imgui.h:251
    y:float                                              # imgui.h:251
    def __init__(self) -> None:                          # imgui.h:252
        pass
    def __init__(self, _x: float, _y: float) -> None:    # imgui.h:253
        pass
    # We very rarely use this [] operator, the assert overhead is fine.

class ImVec4:    # imgui.h:262
    """ ImVec4: 4D vector used to store clipping rectangles, colors etc. [Compile-time configurable type]"""
    x:float                                                                    # imgui.h:264
    y:float                                                                    # imgui.h:264
    z:float                                                                    # imgui.h:264
    w:float                                                                    # imgui.h:264
    def __init__(self) -> None:                                                # imgui.h:265
        pass
    def __init__(self, _x: float, _y: float, _z: float, _w: float) -> None:    # imgui.h:266
        pass

#-----------------------------------------------------------------------------
# [SECTION] Dear ImGui end-user API functions
# (Note that ImGui:: being a namespace, you can add extra ImGui:: functions in your own separate file. Please don't modify imgui source files!)
#-----------------------------------------------------------------------------

# <Namespace ImGui>
# Context creation and access
# - Each context create its own ImFontAtlas by default. You may instance one yourself and pass it to CreateContext() to share a font atlas between contexts.
# - DLL users: heaps and globals are not shared across DLL boundaries! You will need to call SetCurrentContext() + SetAllocatorFunctions()
#   for each static/DLL boundary you are calling from. Read "Context and Memory Allocators" section of imgui.cpp for details.
def CreateContext(shared_font_atlas: ImFontAtlas = None) -> ImGuiContext:    # imgui.h:284
    pass
def DestroyContext(ctx: ImGuiContext = None) -> None:    # imgui.h:285
    """ None = destroy current context"""
    pass
def GetCurrentContext() -> ImGuiContext:    # imgui.h:286
    pass
def SetCurrentContext(ctx: ImGuiContext) -> None:    # imgui.h:287
    pass

# Main
def GetIO() -> ImGuiIO:    # imgui.h:290
    """ access the IO structure (mouse/keyboard/gamepad inputs, time, various configuration options/flags)"""
    pass
def GetStyle() -> ImGuiStyle:    # imgui.h:291
    """ access the Style structure (colors, sizes). Always use PushStyleCol(), PushStyleVar() to modify style mid-frame!"""
    pass
def NewFrame() -> None:    # imgui.h:292
    """ start a new Dear ImGui frame, you can submit any command from this point until Render()/EndFrame()."""
    pass
def EndFrame() -> None:    # imgui.h:293
    """ ends the Dear ImGui frame. automatically called by Render(). If you don't need to render data (skipping rendering) you may call EndFrame() without Render()... but you'll have wasted CPU already! If you don't need to render, better to not create any windows and not call NewFrame() at all!"""
    pass
def Render() -> None:    # imgui.h:294
    """ ends the Dear ImGui frame, finalize the draw data. You can then get call GetDrawData()."""
    pass
def GetDrawData() -> ImDrawData:    # imgui.h:295
    """ valid after Render() and until the next call to NewFrame(). this is what you have to render."""
    pass

# Demo, Debug, Information
def ShowDemoWindow(p_open: BoxedBool = None) -> None:    # imgui.h:298
    """ create Demo window. demonstrate most ImGui features. call this to learn about the library! try to make it always available in your application!"""
    pass
def ShowMetricsWindow(p_open: BoxedBool = None) -> None:    # imgui.h:299
    """ create Metrics/Debugger window. display Dear ImGui internals: windows, draw commands, various internal state, etc."""
    pass
def ShowStackToolWindow(p_open: BoxedBool = None) -> None:    # imgui.h:300
    """ create Stack Tool window. hover items with mouse to query information about the source of their unique ID."""
    pass
def ShowAboutWindow(p_open: BoxedBool = None) -> None:    # imgui.h:301
    """ create About window. display Dear ImGui version, credits and build/system information."""
    pass
def ShowStyleEditor(ref: ImGuiStyle = None) -> None:    # imgui.h:302
    """ add style editor block (not a window). you can pass in a reference ImGuiStyle structure to compare to, revert to and save to (else it uses the default style)"""
    pass
def ShowStyleSelector(label: str) -> bool:    # imgui.h:303
    """ add style selector block (not a window), essentially a combo listing the default styles."""
    pass
def ShowFontSelector(label: str) -> None:    # imgui.h:304
    """ add font selector block (not a window), essentially a combo listing the loaded fonts."""
    pass
def ShowUserGuide() -> None:    # imgui.h:305
    """ add basic help/info block (not a window): how to manipulate ImGui as a end-user (mouse/keyboard controls)."""
    pass
def GetVersion() -> str:    # imgui.h:306
    """ get the compiled version string e.g. "1.80 WIP" (essentially the value for IMGUI_VERSION from the compiled version of imgui.cpp)"""
    pass

# Styles
def StyleColorsDark(dst: ImGuiStyle = None) -> None:    # imgui.h:309
    """ new, recommended style (default)"""
    pass
def StyleColorsLight(dst: ImGuiStyle = None) -> None:    # imgui.h:310
    """ best used with borders and a custom, thicker font"""
    pass
def StyleColorsClassic(dst: ImGuiStyle = None) -> None:    # imgui.h:311
    """ classic imgui style"""
    pass

# Windows
# - Begin() = push window to the stack and start appending to it. End() = pop window from the stack.
# - Passing 'bool* p_open != None' shows a window-closing widget in the upper-right corner of the window,
#   which clicking will set the boolean to False when clicked.
# - You may append multiple times to the same window during the same frame by calling Begin()/End() pairs multiple times.
#   Some information such as 'flags' or 'p_open' will only be considered by the first call to Begin().
# - Begin() return False to indicate the window is collapsed or fully clipped, so you may early out and omit submitting
#   anything to the window. Always call a matching End() for each Begin() call, regardless of its return value!
#   [Important: due to legacy reason, this is inconsistent with most other functions such as BeginMenu/EndMenu,
#    BeginPopup/EndPopup, etc. where the EndXXX call should only be called if the corresponding BeginXXX function
#    returned True. Begin and BeginChild are the only odd ones out. Will be fixed in a future update.]
# - Note that the bottom of window stack always contains a window called "Debug".
def Begin(name: str, p_open: BoxedBool = None, flags: ImGuiWindowFlags = 0) -> bool:    # imgui.h:325
    pass
def End() -> None:    # imgui.h:326
    pass

# Child Windows
# - Use child windows to begin into a self-contained independent scrolling/clipping regions within a host window. Child windows can embed their own child.
# - For each independent axis of 'size': ==0.0: use remaining host window size / >0.0: fixed size / <0.0: use remaining window size minus abs(size) / Each axis can use a different mode, e.g. ImVec2(0,400).
# - BeginChild() returns False to indicate the window is collapsed or fully clipped, so you may early out and omit submitting anything to the window.
#   Always call a matching EndChild() for each BeginChild() call, regardless of its return value.
#   [Important: due to legacy reason, this is inconsistent with most other functions such as BeginMenu/EndMenu,
#    BeginPopup/EndPopup, etc. where the EndXXX call should only be called if the corresponding BeginXXX function
#    returned True. Begin and BeginChild are the only odd ones out. Will be fixed in a future update.]
def BeginChild(str_id: str, size: ImVec2 = ImVec2(0, 0), border: bool = False, flags: ImGuiWindowFlags = 0) -> bool:    # imgui.h:336
    pass
def BeginChild(id: ImGuiID, size: ImVec2 = ImVec2(0, 0), border: bool = False, flags: ImGuiWindowFlags = 0) -> bool:    # imgui.h:337
    pass
def EndChild() -> None:    # imgui.h:338
    pass

# Windows Utilities
# - 'current window' = the window we are appending into while inside a Begin()/End() block. 'next window' = next window we will Begin() into.
def IsWindowAppearing() -> bool:    # imgui.h:342
    pass
def IsWindowCollapsed() -> bool:    # imgui.h:343
    pass
def IsWindowFocused(flags: ImGuiFocusedFlags = 0) -> bool:    # imgui.h:344
    """ is current window focused? or its root/child, depending on flags. see flags for options."""
    pass
def IsWindowHovered(flags: ImGuiHoveredFlags = 0) -> bool:    # imgui.h:345
    """ is current window hovered (and typically: not blocked by a popup/modal)? see flags for options. NB: If you are trying to check whether your mouse should be dispatched to imgui or to your app, you should use the 'io.WantCaptureMouse' boolean for that! Please read the FAQ!"""
    pass
def GetWindowDrawList() -> ImDrawList:    # imgui.h:346
    """ get draw list associated to the current window, to append your own drawing primitives"""
    pass
def GetWindowPos() -> ImVec2:    # imgui.h:347
    """ get current window position in screen space (useful if you want to do your own drawing via the DrawList API)"""
    pass
def GetWindowSize() -> ImVec2:    # imgui.h:348
    """ get current window size"""
    pass
def GetWindowWidth() -> float:    # imgui.h:349
    """ get current window width (shortcut for GetWindowSize().x)"""
    pass
def GetWindowHeight() -> float:    # imgui.h:350
    """ get current window height (shortcut for GetWindowSize().y)"""
    pass

# Window manipulation
# - Prefer using SetNextXXX functions (before Begin) rather that SetXXX functions (after Begin).
def SetNextWindowPos(pos: ImVec2, cond: ImGuiCond = 0, pivot: ImVec2 = ImVec2(0, 0)) -> None:    # imgui.h:354
    """ set next window position. call before Begin(). use pivot=(0.5,0.5) to center on given point, etc."""
    pass
def SetNextWindowSize(size: ImVec2, cond: ImGuiCond = 0) -> None:    # imgui.h:355
    """ set next window size. set axis to 0.0 to force an auto-fit on this axis. call before Begin()"""
    pass
def SetNextWindowSizeConstraints(size_min: ImVec2, size_max: ImVec2, custom_callback: ImGuiSizeCallback = None, custom_callback_data: Any = None) -> None:    # imgui.h:356
    """ set next window size limits. use -1,-1 on either X/Y axis to preserve the current size. Sizes will be rounded down. Use callback to apply non-trivial programmatic constraints."""
    pass
def SetNextWindowContentSize(size: ImVec2) -> None:    # imgui.h:357
    """ set next window content size (~ scrollable client area, which enforce the range of scrollbars). Not including window decorations (title bar, menu bar, etc.) nor WindowPadding. set an axis to 0.0 to leave it automatic. call before Begin()"""
    pass
def SetNextWindowCollapsed(collapsed: bool, cond: ImGuiCond = 0) -> None:    # imgui.h:358
    """ set next window collapsed state. call before Begin()"""
    pass
def SetNextWindowFocus() -> None:    # imgui.h:359
    """ set next window to be focused / top-most. call before Begin()"""
    pass
def SetNextWindowBgAlpha(alpha: float) -> None:    # imgui.h:360
    """ set next window background color alpha. helper to easily override the Alpha component of ImGuiCol_WindowBg/ChildBg/PopupBg. you may also use ImGuiWindowFlags_NoBackground."""
    pass
def SetWindowPos(pos: ImVec2, cond: ImGuiCond = 0) -> None:    # imgui.h:361
    """ (not recommended) set current window position - call within Begin()/End(). prefer using SetNextWindowPos(), as this may incur tearing and side-effects."""
    pass
def SetWindowSize(size: ImVec2, cond: ImGuiCond = 0) -> None:    # imgui.h:362
    """ (not recommended) set current window size - call within Begin()/End(). set to ImVec2(0, 0) to force an auto-fit. prefer using SetNextWindowSize(), as this may incur tearing and minor side-effects."""
    pass
def SetWindowCollapsed(collapsed: bool, cond: ImGuiCond = 0) -> None:    # imgui.h:363
    """ (not recommended) set current window collapsed state. prefer using SetNextWindowCollapsed()."""
    pass
def SetWindowFocus() -> None:    # imgui.h:364
    """ (not recommended) set current window to be focused / top-most. prefer using SetNextWindowFocus()."""
    pass
def SetWindowFontScale(scale: float) -> None:    # imgui.h:365
    """ [OBSOLETE] set font scale. Adjust IO.FontGlobalScale if you want to scale all windows. This is an old API! For correct scaling, prefer to reload font + rebuild ImFontAtlas + call style.ScaleAllSizes()."""
    pass
def SetWindowPos(name: str, pos: ImVec2, cond: ImGuiCond = 0) -> None:    # imgui.h:366
    """ set named window position."""
    pass
def SetWindowSize(name: str, size: ImVec2, cond: ImGuiCond = 0) -> None:    # imgui.h:367
    """ set named window size. set axis to 0.0 to force an auto-fit on this axis."""
    pass
def SetWindowCollapsed(name: str, collapsed: bool, cond: ImGuiCond = 0) -> None:    # imgui.h:368
    """ set named window collapsed state"""
    pass
def SetWindowFocus(name: str) -> None:    # imgui.h:369
    """ set named window to be focused / top-most. use None to remove focus."""
    pass

# Content region
# - Retrieve available space from a given point. GetContentRegionAvail() is frequently useful.
# - Those functions are bound to be redesigned (they are confusing, incomplete and the Min/Max return values are in local window coordinates which increases confusion)
def GetContentRegionAvail() -> ImVec2:    # imgui.h:374
    """ == GetContentRegionMax() - GetCursorPos()"""
    pass
def GetContentRegionMax() -> ImVec2:    # imgui.h:375
    """ current content boundaries (typically window boundaries including scrolling, or current column boundaries), in windows coordinates"""
    pass
def GetWindowContentRegionMin() -> ImVec2:    # imgui.h:376
    """ content boundaries min for the full window (roughly (0,0)-Scroll), in window coordinates"""
    pass
def GetWindowContentRegionMax() -> ImVec2:    # imgui.h:377
    """ content boundaries max for the full window (roughly (0,0)+Size-Scroll) where Size can be override with SetNextWindowContentSize(), in window coordinates"""
    pass

# Windows Scrolling
def GetScrollX() -> float:    # imgui.h:380
    """ get scrolling amount [0 .. GetScrollMaxX()]"""
    pass
def GetScrollY() -> float:    # imgui.h:381
    """ get scrolling amount [0 .. GetScrollMaxY()]"""
    pass
def SetScrollX(scroll_x: float) -> None:    # imgui.h:382
    """ set scrolling amount [0 .. GetScrollMaxX()]"""
    pass
def SetScrollY(scroll_y: float) -> None:    # imgui.h:383
    """ set scrolling amount [0 .. GetScrollMaxY()]"""
    pass
def GetScrollMaxX() -> float:    # imgui.h:384
    """ get maximum scrolling amount ~~ ContentSize.x - WindowSize.x - DecorationsSize.x"""
    pass
def GetScrollMaxY() -> float:    # imgui.h:385
    """ get maximum scrolling amount ~~ ContentSize.y - WindowSize.y - DecorationsSize.y"""
    pass
def SetScrollHereX(center_x_ratio: float = 0.5) -> None:    # imgui.h:386
    """ adjust scrolling amount to make current cursor position visible. center_x_ratio=0.0: left, 0.5: center, 1.0: right. When using to make a "default/current item" visible, consider using SetItemDefaultFocus() instead."""
    pass
def SetScrollHereY(center_y_ratio: float = 0.5) -> None:    # imgui.h:387
    """ adjust scrolling amount to make current cursor position visible. center_y_ratio=0.0: top, 0.5: center, 1.0: bottom. When using to make a "default/current item" visible, consider using SetItemDefaultFocus() instead."""
    pass
def SetScrollFromPosX(local_x: float, center_x_ratio: float = 0.5) -> None:    # imgui.h:388
    """ adjust scrolling amount to make given position visible. Generally GetCursorStartPos() + offset to compute a valid position."""
    pass
def SetScrollFromPosY(local_y: float, center_y_ratio: float = 0.5) -> None:    # imgui.h:389
    """ adjust scrolling amount to make given position visible. Generally GetCursorStartPos() + offset to compute a valid position."""
    pass

# Parameters stacks (shared)
def PushFont(font: ImFont) -> None:    # imgui.h:392
    """ use None as a shortcut to push default font"""
    pass
def PopFont() -> None:    # imgui.h:393
    pass
def PushStyleColor(idx: ImGuiCol, col: ImU32) -> None:    # imgui.h:394
    """ modify a style color. always use this if you modify the style after NewFrame()."""
    pass
def PushStyleColor(idx: ImGuiCol, col: ImVec4) -> None:    # imgui.h:395
    pass
def PopStyleColor(count: int = 1) -> None:    # imgui.h:396
    pass
def PushStyleVar(idx: ImGuiStyleVar, val: float) -> None:    # imgui.h:397
    """ modify a style float variable. always use this if you modify the style after NewFrame()."""
    pass
def PushStyleVar(idx: ImGuiStyleVar, val: ImVec2) -> None:    # imgui.h:398
    """ modify a style ImVec2 variable. always use this if you modify the style after NewFrame()."""
    pass
def PopStyleVar(count: int = 1) -> None:    # imgui.h:399
    pass
def PushAllowKeyboardFocus(allow_keyboard_focus: bool) -> None:    # imgui.h:400
    """ == tab stop enable. Allow focusing using TAB/Shift-TAB, enabled by default but you can disable it for certain widgets"""
    pass
def PopAllowKeyboardFocus() -> None:    # imgui.h:401
    pass
def PushButtonRepeat(repeat: bool) -> None:    # imgui.h:402
    """ in 'repeat' mode, Button*() functions return repeated True in a typematic manner (using io.KeyRepeatDelay/io.KeyRepeatRate setting). Note that you can call IsItemActive() after any Button() to tell if the button is held in the current frame."""
    pass
def PopButtonRepeat() -> None:    # imgui.h:403
    pass

# Parameters stacks (current window)
def PushItemWidth(item_width: float) -> None:    # imgui.h:406
    """ push width of items for common large "item+label" widgets. >0.0: width in pixels, <0.0 align xx pixels to the right of window (so -FLT_MIN always align width to the right side)."""
    pass
def PopItemWidth() -> None:    # imgui.h:407
    pass
def SetNextItemWidth(item_width: float) -> None:    # imgui.h:408
    """ set width of the _next_ common large "item+label" widget. >0.0: width in pixels, <0.0 align xx pixels to the right of window (so -FLT_MIN always align width to the right side)"""
    pass
def CalcItemWidth() -> float:    # imgui.h:409
    """ width of item given pushed settings and current cursor position. NOT necessarily the width of last item unlike most 'Item' functions."""
    pass
def PushTextWrapPos(wrap_local_pos_x: float = 0.0) -> None:    # imgui.h:410
    """ push word-wrapping position for Text*() commands. < 0.0: no wrapping; 0.0: wrap to end of window (or column); > 0.0: wrap at 'wrap_pos_x' position in window local space"""
    pass
def PopTextWrapPos() -> None:    # imgui.h:411
    pass

# Style read access
# - Use the style editor (ShowStyleEditor() function) to interactively see what the colors are)
def GetFont() -> ImFont:    # imgui.h:415
    """ get current font"""
    pass
def GetFontSize() -> float:    # imgui.h:416
    """ get current font size (= height in pixels) of current font with current scale applied"""
    pass
def GetFontTexUvWhitePixel() -> ImVec2:    # imgui.h:417
    """ get UV coordinate for a while pixel, useful to draw custom shapes via the ImDrawList API"""
    pass
def GetColorU32(idx: ImGuiCol, alpha_mul: float = 1.0) -> ImU32:    # imgui.h:418
    """ retrieve given style color with style alpha applied and optional extra alpha multiplier, packed as a 32-bit value suitable for ImDrawList"""
    pass
def GetColorU32(col: ImVec4) -> ImU32:    # imgui.h:419
    """ retrieve given color with style alpha applied, packed as a 32-bit value suitable for ImDrawList"""
    pass
def GetColorU32(col: ImU32) -> ImU32:    # imgui.h:420
    """ retrieve given color with style alpha applied, packed as a 32-bit value suitable for ImDrawList"""
    pass
def GetStyleColorVec4(idx: ImGuiCol) -> ImVec4:    # imgui.h:421
    """ retrieve style color as stored in ImGuiStyle structure. use to feed back into PushStyleColor(), otherwise use GetColorU32() to get style color with style alpha baked in."""
    pass

# Cursor / Layout
# - By "cursor" we mean the current output position.
# - The typical widget behavior is to output themselves at the current cursor position, then move the cursor one line down.
# - You can call SameLine() between widgets to undo the last carriage return and output at the right of the preceding widget.
# - Attention! We currently have inconsistencies between window-local and absolute positions we will aim to fix with future API:
#    Window-local coordinates:   SameLine(), GetCursorPos(), SetCursorPos(), GetCursorStartPos(), GetContentRegionMax(), GetWindowContentRegion*(), PushTextWrapPos()
#    Absolute coordinate:        GetCursorScreenPos(), SetCursorScreenPos(), all ImDrawList:: functions.
def Separator() -> None:    # imgui.h:430
    """ separator, generally horizontal. inside a menu bar or in horizontal layout mode, this becomes a vertical separator."""
    pass
def SameLine(offset_from_start_x: float = 0.0, spacing: float = -1.0) -> None:    # imgui.h:431
    """ call between widgets or groups to layout them horizontally. X position given in window coordinates."""
    pass
def NewLine() -> None:    # imgui.h:432
    """ undo a SameLine() or force a new line when in an horizontal-layout context."""
    pass
def Spacing() -> None:    # imgui.h:433
    """ add vertical spacing."""
    pass
def Dummy(size: ImVec2) -> None:    # imgui.h:434
    """ add a dummy item of given size. unlike InvisibleButton(), Dummy() won't take the mouse click or be navigable into."""
    pass
def Indent(indent_w: float = 0.0) -> None:    # imgui.h:435
    """ move content position toward the right, by indent_w, or style.IndentSpacing if indent_w <= 0"""
    pass
def Unindent(indent_w: float = 0.0) -> None:    # imgui.h:436
    """ move content position back to the left, by indent_w, or style.IndentSpacing if indent_w <= 0"""
    pass
def BeginGroup() -> None:    # imgui.h:437
    """ lock horizontal starting position"""
    pass
def EndGroup() -> None:    # imgui.h:438
    """ unlock horizontal starting position + capture the whole group bounding box into one "item" (so you can use IsItemHovered() or layout primitives such as SameLine() on whole group, etc.)"""
    pass
def GetCursorPos() -> ImVec2:    # imgui.h:439
    """ cursor position in window coordinates (relative to window position)"""
    pass
def GetCursorPosX() -> float:    # imgui.h:440
    """   (some functions are using window-relative coordinates, such as: GetCursorPos, GetCursorStartPos, GetContentRegionMax, GetWindowContentRegion* etc."""
    pass
def GetCursorPosY() -> float:    # imgui.h:441
    """    other functions such as GetCursorScreenPos or everything in ImDrawList::"""
    pass
def SetCursorPos(local_pos: ImVec2) -> None:    # imgui.h:442
    """    are using the main, absolute coordinate system."""
    pass
def SetCursorPosX(local_x: float) -> None:    # imgui.h:443
    """    GetWindowPos() + GetCursorPos() == GetCursorScreenPos() etc.)"""
    pass
def SetCursorPosY(local_y: float) -> None:    # imgui.h:444
    pass
def GetCursorStartPos() -> ImVec2:    # imgui.h:445
    """ initial cursor position in window coordinates"""
    pass
def GetCursorScreenPos() -> ImVec2:    # imgui.h:446
    """ cursor position in absolute coordinates (useful to work with ImDrawList API). generally top-left == GetMainViewport()->Pos == (0,0) in single viewport mode, and bottom-right == GetMainViewport()->Pos+Size == io.DisplaySize in single-viewport mode."""
    pass
def SetCursorScreenPos(pos: ImVec2) -> None:    # imgui.h:447
    """ cursor position in absolute coordinates"""
    pass
def AlignTextToFramePadding() -> None:    # imgui.h:448
    """ vertically align upcoming text baseline to FramePadding.y so that it will align properly to regularly framed items (call if you have text on a line before a framed item)"""
    pass
def GetTextLineHeight() -> float:    # imgui.h:449
    """ ~ FontSize"""
    pass
def GetTextLineHeightWithSpacing() -> float:    # imgui.h:450
    """ ~ FontSize + style.ItemSpacing.y (distance in pixels between 2 consecutive lines of text)"""
    pass
def GetFrameHeight() -> float:    # imgui.h:451
    """ ~ FontSize + style.FramePadding.y * 2"""
    pass
def GetFrameHeightWithSpacing() -> float:    # imgui.h:452
    """ ~ FontSize + style.FramePadding.y * 2 + style.ItemSpacing.y (distance in pixels between 2 consecutive lines of framed widgets)"""
    pass

# ID stack/scopes
# Read the FAQ (docs/FAQ.md or http://dearimgui.org/faq) for more details about how ID are handled in dear imgui.
# - Those questions are answered and impacted by understanding of the ID stack system:
#   - "Q: Why is my widget not reacting when I click on it?"
#   - "Q: How can I have widgets with an empty label?"
#   - "Q: How can I have multiple widgets with the same label?"
# - Short version: ID are hashes of the entire ID stack. If you are creating widgets in a loop you most likely
#   want to push a unique identifier (e.g. object pointer, loop index) to uniquely differentiate them.
# - You can also use the "Label##foobar" syntax within widget label to distinguish them from each others.
# - In this header file we use the "label"/"name" terminology to denote a string that will be displayed + used as an ID,
#   whereas "str_id" denote a string that is only used as an ID and not normally displayed.
def PushID(str_id: str) -> None:    # imgui.h:465
    """ push string into the ID stack (will hash string)."""
    pass
def PushID(str_id_begin: str, str_id_end: str) -> None:    # imgui.h:466
    """ push string into the ID stack (will hash string)."""
    pass
def PushID(ptr_id: Any) -> None:    # imgui.h:467
    """ push pointer into the ID stack (will hash pointer)."""
    pass
def PushID(int_id: int) -> None:    # imgui.h:468
    """ push integer into the ID stack (will hash integer)."""
    pass
def PopID() -> None:    # imgui.h:469
    """ pop from the ID stack."""
    pass
def GetID(str_id: str) -> ImGuiID:    # imgui.h:470
    """ calculate unique ID (hash of whole ID stack + given parameter). e.g. if you want to query into ImGuiStorage yourself"""
    pass
def GetID(str_id_begin: str, str_id_end: str) -> ImGuiID:    # imgui.h:471
    pass
def GetID(ptr_id: Any) -> ImGuiID:    # imgui.h:472
    pass

# Widgets: Text
def TextUnformatted(text: str, text_end: str = None) -> None:    # imgui.h:475
    """ raw text without formatting. Roughly equivalent to Text("%s", text) but: A) doesn't require null terminated string if 'text_end' is specified, B) it's faster, no memory copy is done, no buffer size limits, recommended for long chunks of text."""
    pass
def Text(fmt: str) -> None:    # imgui.h:476
    """ formatted text"""
    pass
def TextColored(col: ImVec4, fmt: str) -> None:    # imgui.h:478
    """ shortcut for PushStyleColor(ImGuiCol_Text, col); Text(fmt, ...); PopStyleColor();"""
    pass
def TextDisabled(fmt: str) -> None:    # imgui.h:480
    """ shortcut for PushStyleColor(ImGuiCol_Text, style.Colors[ImGuiCol_TextDisabled]); Text(fmt, ...); PopStyleColor();"""
    pass
def TextWrapped(fmt: str) -> None:    # imgui.h:482
    """ shortcut for PushTextWrapPos(0.0); Text(fmt, ...); PopTextWrapPos();. Note that this won't work on an auto-resizing window if there's no other widgets to extend the window width, yoy may need to set a size using SetNextWindowSize()."""
    pass
def LabelText(label: str, fmt: str) -> None:    # imgui.h:484
    """ display text+label aligned the same way as value+label widgets"""
    pass
def BulletText(fmt: str) -> None:    # imgui.h:486
    """ shortcut for Bullet()+Text()"""
    pass

# Widgets: Main
# - Most widgets return True when the value has been changed or when pressed/selected
# - You may also use one of the many IsItemXXX functions (e.g. IsItemActive, IsItemHovered, etc.) to query widget state.
def Button(label: str, size: ImVec2 = ImVec2(0, 0)) -> bool:    # imgui.h:492
    """ button"""
    pass
def SmallButton(label: str) -> bool:    # imgui.h:493
    """ button with FramePadding=(0,0) to easily embed within text"""
    pass
def InvisibleButton(str_id: str, size: ImVec2, flags: ImGuiButtonFlags = 0) -> bool:    # imgui.h:494
    """ flexible button behavior without the visuals, frequently useful to build custom behaviors using the public api (along with IsItemActive, IsItemHovered, etc.)"""
    pass
def ArrowButton(str_id: str, dir: ImGuiDir) -> bool:    # imgui.h:495
    """ square button with an arrow shape"""
    pass
def Image(user_texture_id: ImTextureID, size: ImVec2, uv0: ImVec2 = ImVec2(0, 0), uv1: ImVec2 = ImVec2(1,1), tint_col: ImVec4 = ImVec4(1,1,1,1), border_col: ImVec4 = ImVec4(0,0,0,0)) -> None:    # imgui.h:496
    pass
def ImageButton(user_texture_id: ImTextureID, size: ImVec2, uv0: ImVec2 = ImVec2(0, 0), uv1: ImVec2 = ImVec2(1,1), frame_padding: int = -1, bg_col: ImVec4 = ImVec4(0,0,0,0), tint_col: ImVec4 = ImVec4(1,1,1,1)) -> bool:    # imgui.h:497
    """ <0 frame_padding uses default frame padding settings. 0 for no padding"""
    pass
def Checkbox(label: str, v: BoxedBool) -> bool:    # imgui.h:498
    pass
def CheckboxFlags(label: str, flags: BoxedInt, flags_value: int) -> bool:    # imgui.h:499
    pass
def CheckboxFlags(label: str, flags: BoxedUnsignedInt, flags_value: int) -> bool:    # imgui.h:500
    pass
def RadioButton(label: str, active: bool) -> bool:    # imgui.h:501
    """ use with e.g. if (RadioButton("one", my_value==1)) { my_value = 1; }"""
    pass
def RadioButton(label: str, v: BoxedInt, v_button: int) -> bool:    # imgui.h:502
    """ shortcut to handle the above pattern when value is an integer"""
    pass
def ProgressBar(fraction: float, size_arg: ImVec2 = ImVec2(-sys.float_info.min, 0), overlay: str = None) -> None:    # imgui.h:503
    pass
def Bullet() -> None:    # imgui.h:504
    """ draw a small circle + keep the cursor on the same line. advance cursor x position by GetTreeNodeToLabelSpacing(), same distance that TreeNode() uses"""
    pass

# Widgets: Combo Box
# - The BeginCombo()/EndCombo() api allows you to manage your contents and selection state however you want it, by creating e.g. Selectable() items.
# - The old Combo() api are helpers over BeginCombo()/EndCombo() which are kept available for convenience purpose. This is analogous to how ListBox are created.
def BeginCombo(label: str, preview_value: str, flags: ImGuiComboFlags = 0) -> bool:    # imgui.h:509
    pass
def EndCombo() -> None:    # imgui.h:510
    """ only call EndCombo() if BeginCombo() returns True!"""
    pass
def Combo(label: str, current_item: BoxedInt, items: List[str], popup_max_height_in_items: int = -1) -> bool:    # imgui.h:511
    pass
def Combo(label: str, current_item: BoxedInt, items_separated_by_zeros: str, popup_max_height_in_items: int = -1) -> bool:    # imgui.h:512
    """ Separate items with \0 within a string, end item-list with \0\0. e.g. "One\0Two\0Three\0" """
    pass

# Widgets: Drag Sliders
# - CTRL+Click on any drag box to turn them into an input box. Manually input values aren't clamped by default and can go off-bounds. Use ImGuiSliderFlags_AlwaysClamp to always clamp.
# - For all the Float2/Float3/Float4/Int2/Int3/Int4 versions of every functions, note that a 'float v[X]' function argument is the same as 'float* v',
#   the array syntax is just a way to document the number of elements that are expected to be accessible. You can pass address of your first element out of a contiguous set, e.g. &myvector.x
# - Adjust format string to decorate the value with a prefix, a suffix, or adapt the editing and display precision e.g. "%.3" -> 1.234; "%5.2 secs" -> 01.23 secs; "Biscuit: %.0" -> Biscuit: 1; etc.
# - Format string may also be set to None or use the default format ("%f" or "%d").
# - Speed are per-pixel of mouse movement (v_speed=0.2: mouse needs to move by 5 pixels to increase value by 1). For gamepad/keyboard navigation, minimum speed is Max(v_speed, minimum_step_at_given_precision).
# - Use v_min < v_max to clamp edits to given limits. Note that CTRL+Click manual input can override those limits if ImGuiSliderFlags_AlwaysClamp is not used.
# - Use v_max = FLT_MAX / INT_MAX etc to avoid clamping to a maximum, same with v_min = -FLT_MAX / INT_MIN to avoid clamping to a minimum.
# - We use the same sets of flags for DragXXX() and SliderXXX() functions as the features are the same and it makes it easier to swap them.
# - Legacy: Pre-1.78 there are DragXXX() function signatures that takes a final `float power=1.0' argument instead of the `ImGuiSliderFlags flags=0' argument.
#   If you get a warning converting a float to ImGuiSliderFlags, read https://github.com/ocornut/imgui/issues/3361
def DragFloat(label: str, v: BoxedFloat, v_speed: float = 1.0, v_min: float = 0.0, v_max: float = 0.0, format: str = "%.3", flags: ImGuiSliderFlags = 0) -> bool:    # imgui.h:527
    """ If v_min >= v_max we have no bound"""
    pass
def DragFloat2(label: str, v_0: BoxedFloat, v_1: BoxedFloat, v_speed: float = 1.0, v_min: float = 0.0, v_max: float = 0.0, format: str = "%.3", flags: ImGuiSliderFlags = 0) -> bool:    # imgui.h:528
    pass
def DragFloat3(label: str, v_0: BoxedFloat, v_1: BoxedFloat, v_2: BoxedFloat, v_speed: float = 1.0, v_min: float = 0.0, v_max: float = 0.0, format: str = "%.3", flags: ImGuiSliderFlags = 0) -> bool:    # imgui.h:529
    pass
def DragFloat4(label: str, v_0: BoxedFloat, v_1: BoxedFloat, v_2: BoxedFloat, v_3: BoxedFloat, v_speed: float = 1.0, v_min: float = 0.0, v_max: float = 0.0, format: str = "%.3", flags: ImGuiSliderFlags = 0) -> bool:    # imgui.h:530
    pass
def DragFloatRange2(label: str, v_current_min: BoxedFloat, v_current_max: BoxedFloat, v_speed: float = 1.0, v_min: float = 0.0, v_max: float = 0.0, format: str = "%.3", format_max: str = None, flags: ImGuiSliderFlags = 0) -> bool:    # imgui.h:531
    pass
def DragInt(label: str, v: BoxedInt, v_speed: float = 1.0, v_min: int = 0, v_max: int = 0, format: str = "%d", flags: ImGuiSliderFlags = 0) -> bool:    # imgui.h:532
    """ If v_min >= v_max we have no bound"""
    pass
def DragInt2(label: str, v_0: BoxedInt, v_1: BoxedInt, v_speed: float = 1.0, v_min: int = 0, v_max: int = 0, format: str = "%d", flags: ImGuiSliderFlags = 0) -> bool:    # imgui.h:533
    pass
def DragInt3(label: str, v_0: BoxedInt, v_1: BoxedInt, v_2: BoxedInt, v_speed: float = 1.0, v_min: int = 0, v_max: int = 0, format: str = "%d", flags: ImGuiSliderFlags = 0) -> bool:    # imgui.h:534
    pass
def DragInt4(label: str, v_0: BoxedInt, v_1: BoxedInt, v_2: BoxedInt, v_3: BoxedInt, v_speed: float = 1.0, v_min: int = 0, v_max: int = 0, format: str = "%d", flags: ImGuiSliderFlags = 0) -> bool:    # imgui.h:535
    pass
def DragIntRange2(label: str, v_current_min: BoxedInt, v_current_max: BoxedInt, v_speed: float = 1.0, v_min: int = 0, v_max: int = 0, format: str = "%d", format_max: str = None, flags: ImGuiSliderFlags = 0) -> bool:    # imgui.h:536
    pass
def DragScalar(label: str, data_type: ImGuiDataType, p_data: Any, v_speed: float = 1.0, p_min: Any = None, p_max: Any = None, format: str = None, flags: ImGuiSliderFlags = 0) -> bool:    # imgui.h:537
    pass
def DragScalarN(label: str, data_type: ImGuiDataType, p_data: Any, components: int, v_speed: float = 1.0, p_min: Any = None, p_max: Any = None, format: str = None, flags: ImGuiSliderFlags = 0) -> bool:    # imgui.h:538
    pass

# Widgets: Regular Sliders
# - CTRL+Click on any slider to turn them into an input box. Manually input values aren't clamped by default and can go off-bounds. Use ImGuiSliderFlags_AlwaysClamp to always clamp.
# - Adjust format string to decorate the value with a prefix, a suffix, or adapt the editing and display precision e.g. "%.3" -> 1.234; "%5.2 secs" -> 01.23 secs; "Biscuit: %.0" -> Biscuit: 1; etc.
# - Format string may also be set to None or use the default format ("%f" or "%d").
# - Legacy: Pre-1.78 there are SliderXXX() function signatures that takes a final `float power=1.0' argument instead of the `ImGuiSliderFlags flags=0' argument.
#   If you get a warning converting a float to ImGuiSliderFlags, read https://github.com/ocornut/imgui/issues/3361
def SliderFloat(label: str, v: BoxedFloat, v_min: float, v_max: float, format: str = "%.3", flags: ImGuiSliderFlags = 0) -> bool:    # imgui.h:546
    """ adjust format to decorate the value with a prefix or a suffix for in-slider labels or unit display."""
    pass
def SliderFloat2(label: str, v_0: BoxedFloat, v_1: BoxedFloat, v_min: float, v_max: float, format: str = "%.3", flags: ImGuiSliderFlags = 0) -> bool:    # imgui.h:547
    pass
def SliderFloat3(label: str, v_0: BoxedFloat, v_1: BoxedFloat, v_2: BoxedFloat, v_min: float, v_max: float, format: str = "%.3", flags: ImGuiSliderFlags = 0) -> bool:    # imgui.h:548
    pass
def SliderFloat4(label: str, v_0: BoxedFloat, v_1: BoxedFloat, v_2: BoxedFloat, v_3: BoxedFloat, v_min: float, v_max: float, format: str = "%.3", flags: ImGuiSliderFlags = 0) -> bool:    # imgui.h:549
    pass
def SliderAngle(label: str, v_rad: BoxedFloat, v_degrees_min: float = -360.0, v_degrees_max: float = +360.0, format: str = "%.0 deg", flags: ImGuiSliderFlags = 0) -> bool:    # imgui.h:550
    pass
def SliderInt(label: str, v: BoxedInt, v_min: int, v_max: int, format: str = "%d", flags: ImGuiSliderFlags = 0) -> bool:    # imgui.h:551
    pass
def SliderInt2(label: str, v_0: BoxedInt, v_1: BoxedInt, v_min: int, v_max: int, format: str = "%d", flags: ImGuiSliderFlags = 0) -> bool:    # imgui.h:552
    pass
def SliderInt3(label: str, v_0: BoxedInt, v_1: BoxedInt, v_2: BoxedInt, v_min: int, v_max: int, format: str = "%d", flags: ImGuiSliderFlags = 0) -> bool:    # imgui.h:553
    pass
def SliderInt4(label: str, v_0: BoxedInt, v_1: BoxedInt, v_2: BoxedInt, v_3: BoxedInt, v_min: int, v_max: int, format: str = "%d", flags: ImGuiSliderFlags = 0) -> bool:    # imgui.h:554
    pass
def SliderScalar(label: str, data_type: ImGuiDataType, p_data: Any, p_min: Any, p_max: Any, format: str = None, flags: ImGuiSliderFlags = 0) -> bool:    # imgui.h:555
    pass
def SliderScalarN(label: str, data_type: ImGuiDataType, p_data: Any, components: int, p_min: Any, p_max: Any, format: str = None, flags: ImGuiSliderFlags = 0) -> bool:    # imgui.h:556
    pass
def VSliderFloat(label: str, size: ImVec2, v: BoxedFloat, v_min: float, v_max: float, format: str = "%.3", flags: ImGuiSliderFlags = 0) -> bool:    # imgui.h:557
    pass
def VSliderInt(label: str, size: ImVec2, v: BoxedInt, v_min: int, v_max: int, format: str = "%d", flags: ImGuiSliderFlags = 0) -> bool:    # imgui.h:558
    pass
def VSliderScalar(label: str, size: ImVec2, data_type: ImGuiDataType, p_data: Any, p_min: Any, p_max: Any, format: str = None, flags: ImGuiSliderFlags = 0) -> bool:    # imgui.h:559
    pass

# Widgets: Input with Keyboard
# - If you want to use InputText() with std::string or any custom dynamic string type, see misc/cpp/imgui_stdlib.h and comments in imgui_demo.cpp.
# - Most of the ImGuiInputTextFlags flags are only useful for InputText() and not for InputFloatX, InputIntX, InputDouble etc.
def InputText(label: str, buf: char, buf_size: int, flags: ImGuiInputTextFlags = 0, callback: ImGuiInputTextCallback = None, user_data: Any = None) -> bool:    # imgui.h:564
    pass
def InputTextMultiline(label: str, buf: char, buf_size: int, size: ImVec2 = ImVec2(0, 0), flags: ImGuiInputTextFlags = 0, callback: ImGuiInputTextCallback = None, user_data: Any = None) -> bool:    # imgui.h:565
    pass
def InputTextWithHint(label: str, hint: str, buf: char, buf_size: int, flags: ImGuiInputTextFlags = 0, callback: ImGuiInputTextCallback = None, user_data: Any = None) -> bool:    # imgui.h:566
    pass
def InputFloat(label: str, v: BoxedFloat, step: float = 0.0, step_fast: float = 0.0, format: str = "%.3", flags: ImGuiInputTextFlags = 0) -> bool:    # imgui.h:567
    pass
def InputFloat2(label: str, v_0: BoxedFloat, v_1: BoxedFloat, format: str = "%.3", flags: ImGuiInputTextFlags = 0) -> bool:    # imgui.h:568
    pass
def InputFloat3(label: str, v_0: BoxedFloat, v_1: BoxedFloat, v_2: BoxedFloat, format: str = "%.3", flags: ImGuiInputTextFlags = 0) -> bool:    # imgui.h:569
    pass
def InputFloat4(label: str, v_0: BoxedFloat, v_1: BoxedFloat, v_2: BoxedFloat, v_3: BoxedFloat, format: str = "%.3", flags: ImGuiInputTextFlags = 0) -> bool:    # imgui.h:570
    pass
def InputInt(label: str, v: BoxedInt, step: int = 1, step_fast: int = 100, flags: ImGuiInputTextFlags = 0) -> bool:    # imgui.h:571
    pass
def InputInt2(label: str, v_0: BoxedInt, v_1: BoxedInt, flags: ImGuiInputTextFlags = 0) -> bool:    # imgui.h:572
    pass
def InputInt3(label: str, v_0: BoxedInt, v_1: BoxedInt, v_2: BoxedInt, flags: ImGuiInputTextFlags = 0) -> bool:    # imgui.h:573
    pass
def InputInt4(label: str, v_0: BoxedInt, v_1: BoxedInt, v_2: BoxedInt, v_3: BoxedInt, flags: ImGuiInputTextFlags = 0) -> bool:    # imgui.h:574
    pass
def InputDouble(label: str, v: BoxedDouble, step: float = 0.0, step_fast: float = 0.0, format: str = "%.6", flags: ImGuiInputTextFlags = 0) -> bool:    # imgui.h:575
    pass
def InputScalar(label: str, data_type: ImGuiDataType, p_data: Any, p_step: Any = None, p_step_fast: Any = None, format: str = None, flags: ImGuiInputTextFlags = 0) -> bool:    # imgui.h:576
    pass
def InputScalarN(label: str, data_type: ImGuiDataType, p_data: Any, components: int, p_step: Any = None, p_step_fast: Any = None, format: str = None, flags: ImGuiInputTextFlags = 0) -> bool:    # imgui.h:577
    pass

# Widgets: Color Editor/Picker (tip: the ColorEdit* functions have a little color square that can be left-clicked to open a picker, and right-clicked to open an option menu.)
# - Note that in C++ a 'float v[X]' function argument is the _same_ as 'float* v', the array syntax is just a way to document the number of elements that are expected to be accessible.
# - You can pass the address of a first float element out of a contiguous structure, e.g. &myvector.x
def ColorEdit3(label: str, col_0: BoxedFloat, col_1: BoxedFloat, col_2: BoxedFloat, flags: ImGuiColorEditFlags = 0) -> bool:    # imgui.h:582
    pass
def ColorEdit4(label: str, col_0: BoxedFloat, col_1: BoxedFloat, col_2: BoxedFloat, col_3: BoxedFloat, flags: ImGuiColorEditFlags = 0) -> bool:    # imgui.h:583
    pass
def ColorPicker3(label: str, col_0: BoxedFloat, col_1: BoxedFloat, col_2: BoxedFloat, flags: ImGuiColorEditFlags = 0) -> bool:    # imgui.h:584
    pass
def ColorPicker4(label: str, col_0: BoxedFloat, col_1: BoxedFloat, col_2: BoxedFloat, col_3: BoxedFloat, flags: ImGuiColorEditFlags = 0, ref_col: float = None) -> bool:    # imgui.h:585
    pass
def ColorButton(desc_id: str, col: ImVec4, flags: ImGuiColorEditFlags = 0, size: ImVec2 = ImVec2(0, 0)) -> bool:    # imgui.h:586
    """ display a color square/button, hover for details, return True when pressed."""
    pass
def SetColorEditOptions(flags: ImGuiColorEditFlags) -> None:    # imgui.h:587
    """ initialize current options (generally on application startup) if you want to select a default format, picker type, etc. User will be able to change many settings, unless you pass the _NoOptions flag to your calls."""
    pass

# Widgets: Trees
# - TreeNode functions return True when the node is open, in which case you need to also call TreePop() when you are finished displaying the tree node contents.
def TreeNode(label: str) -> bool:    # imgui.h:591
    pass
def TreeNode(str_id: str, fmt: str) -> bool:    # imgui.h:592
    """ helper variation to easily decorelate the id from the displayed string. Read the FAQ about why and how to use ID. to align arbitrary text at the same level as a TreeNode() you can use Bullet()."""
    pass
def TreeNode(ptr_id: Any, fmt: str) -> bool:    # imgui.h:593
    """ " """
    pass
def TreeNodeEx(label: str, flags: ImGuiTreeNodeFlags = 0) -> bool:    # imgui.h:596
    pass
def TreeNodeEx(str_id: str, flags: ImGuiTreeNodeFlags, fmt: str) -> bool:    # imgui.h:597
    pass
def TreeNodeEx(ptr_id: Any, flags: ImGuiTreeNodeFlags, fmt: str) -> bool:    # imgui.h:598
    pass
def TreePush(str_id: str) -> None:    # imgui.h:601
    """ ~ Indent()+PushId(). Already called by TreeNode() when returning True, but you can call TreePush/TreePop yourself if desired."""
    pass
def TreePush(ptr_id: Any = None) -> None:    # imgui.h:602
    """ " """
    pass
def TreePop() -> None:    # imgui.h:603
    """ ~ Unindent()+PopId()"""
    pass
def GetTreeNodeToLabelSpacing() -> float:    # imgui.h:604
    """ horizontal distance preceding label when using TreeNode*() or Bullet() == (g.FontSize + style.FramePadding.x*2) for a regular unframed TreeNode"""
    pass
def CollapsingHeader(label: str, flags: ImGuiTreeNodeFlags = 0) -> bool:    # imgui.h:605
    """ if returning 'True' the header is open. doesn't indent nor push on ID stack. user doesn't have to call TreePop()."""
    pass
def CollapsingHeader(label: str, p_visible: BoxedBool, flags: ImGuiTreeNodeFlags = 0) -> bool:    # imgui.h:606
    """ when 'p_visible != None': if '*p_visible==True' display an additional small close button on upper right of the header which will set the bool to False when clicked, if '*p_visible==False' don't display the header."""
    pass
def SetNextItemOpen(is_open: bool, cond: ImGuiCond = 0) -> None:    # imgui.h:607
    """ set next TreeNode/CollapsingHeader open state."""
    pass

# Widgets: Selectables
# - A selectable highlights when hovered, and can display another color when selected.
# - Neighbors selectable extend their highlight bounds in order to leave no gap between them. This is so a series of selected Selectable appear contiguous.
def Selectable(label: str, selected: bool = False, flags: ImGuiSelectableFlags = 0, size: ImVec2 = ImVec2(0, 0)) -> bool:    # imgui.h:612
    """ "bool selected" carry the selection state (read-only). Selectable() is clicked is returns True so you can modify your selection state. size.x==0.0: use remaining width, size.x>0.0: specify width. size.y==0.0: use label height, size.y>0.0: specify height"""
    pass
def Selectable(label: str, p_selected: BoxedBool, flags: ImGuiSelectableFlags = 0, size: ImVec2 = ImVec2(0, 0)) -> bool:    # imgui.h:613
    """ "bool* p_selected" point to the selection state (read-write), as a convenient helper."""
    pass

# Widgets: List Boxes
# - This is essentially a thin wrapper to using BeginChild/EndChild with some stylistic changes.
# - The BeginListBox()/EndListBox() api allows you to manage your contents and selection state however you want it, by creating e.g. Selectable() or any items.
# - The simplified/old ListBox() api are helpers over BeginListBox()/EndListBox() which are kept available for convenience purpose. This is analoguous to how Combos are created.
# - Choose frame width:   size.x > 0.0: custom  /  size.x < 0.0 or -FLT_MIN: right-align   /  size.x = 0.0 (default): use current ItemWidth
# - Choose frame height:  size.y > 0.0: custom  /  size.y < 0.0 or -FLT_MIN: bottom-align  /  size.y = 0.0 (default): arbitrary default height which can fit ~7 items
def BeginListBox(label: str, size: ImVec2 = ImVec2(0, 0)) -> bool:    # imgui.h:621
    """ open a framed scrolling region"""
    pass
def EndListBox() -> None:    # imgui.h:622
    """ only call EndListBox() if BeginListBox() returned True!"""
    pass
def ListBox(label: str, current_item: BoxedInt, items: List[str], height_in_items: int = -1) -> bool:    # imgui.h:623
    pass

# Widgets: Data Plotting
# - Consider using ImPlot (https://github.com/epezent/implot) which is much better!
def PlotLines(label: str, values: np.ndarray, values_offset: int = 0, overlay_text: str = None, scale_min: float = sys.float_info.max, scale_max: float = sys.float_info.max, graph_size: ImVec2 = ImVec2(0, 0), stride: int = -1) -> None:    # imgui.h:628
    pass
def PlotHistogram(label: str, values: np.ndarray, values_offset: int = 0, overlay_text: str = None, scale_min: float = sys.float_info.max, scale_max: float = sys.float_info.max, graph_size: ImVec2 = ImVec2(0, 0), stride: int = -1) -> None:    # imgui.h:630
    pass

# Widgets: Value() Helpers.
# - Those are merely shortcut to calling Text() with a format string. Output single value in "name: value" format (tip: freely declare more in your code to handle your types. you can add functions to the ImGui namespace)
def Value(prefix: str, b: bool) -> None:    # imgui.h:635
    pass
def Value(prefix: str, v: int) -> None:    # imgui.h:636
    pass
def Value(prefix: str, v: int) -> None:    # imgui.h:637
    pass
def Value(prefix: str, v: float, float_format: str = None) -> None:    # imgui.h:638
    pass

# Widgets: Menus
# - Use BeginMenuBar() on a window ImGuiWindowFlags_MenuBar to append to its menu bar.
# - Use BeginMainMenuBar() to create a menu bar at the top of the screen and append to it.
# - Use BeginMenu() to create a menu. You can call BeginMenu() multiple time with the same identifier to append more items to it.
# - Not that MenuItem() keyboardshortcuts are displayed as a convenience but _not processed_ by Dear ImGui at the moment.
def BeginMenuBar() -> bool:    # imgui.h:645
    """ append to menu-bar of current window (requires ImGuiWindowFlags_MenuBar flag set on parent window)."""
    pass
def EndMenuBar() -> None:    # imgui.h:646
    """ only call EndMenuBar() if BeginMenuBar() returns True!"""
    pass
def BeginMainMenuBar() -> bool:    # imgui.h:647
    """ create and append to a full screen menu-bar."""
    pass
def EndMainMenuBar() -> None:    # imgui.h:648
    """ only call EndMainMenuBar() if BeginMainMenuBar() returns True!"""
    pass
def BeginMenu(label: str, enabled: bool = True) -> bool:    # imgui.h:649
    """ create a sub-menu entry. only call EndMenu() if this returns True!"""
    pass
def EndMenu() -> None:    # imgui.h:650
    """ only call EndMenu() if BeginMenu() returns True!"""
    pass
def MenuItem(label: str, shortcut: str = None, selected: bool = False, enabled: bool = True) -> bool:    # imgui.h:651
    """ return True when activated."""
    pass
def MenuItem(label: str, shortcut: str, p_selected: BoxedBool, enabled: bool = True) -> bool:    # imgui.h:652
    """ return True when activated + toggle (*p_selected) if p_selected != None"""
    pass

# Tooltips
# - Tooltip are windows following the mouse. They do not take focus away.
def BeginTooltip() -> None:    # imgui.h:656
    """ begin/append a tooltip window. to create full-featured tooltip (with any kind of items)."""
    pass
def EndTooltip() -> None:    # imgui.h:657
    pass
def SetTooltip(fmt: str) -> None:    # imgui.h:658
    """ set a text-only tooltip, typically use with ImGui::IsItemHovered(). override any previous call to SetTooltip()."""
    pass

# Popups, Modals
#  - They block normal mouse hovering detection (and therefore most mouse interactions) behind them.
#  - If not modal: they can be closed by clicking anywhere outside them, or by pressing ESCAPE.
#  - Their visibility state (~bool) is held internally instead of being held by the programmer as we are used to with regular Begin*() calls.
#  - The 3 properties above are related: we need to retain popup visibility state in the library because popups may be closed as any time.
#  - You can bypass the hovering restriction by using ImGuiHoveredFlags_AllowWhenBlockedByPopup when calling IsItemHovered() or IsWindowHovered().
#  - IMPORTANT: Popup identifiers are relative to the current ID stack, so OpenPopup and BeginPopup generally needs to be at the same level of the stack.
#    This is sometimes leading to confusing mistakes. May rework this in the future.

# Popups: begin/end functions
#  - BeginPopup(): query popup state, if open start appending into the window. Call EndPopup() afterwards. ImGuiWindowFlags are forwarded to the window.
#  - BeginPopupModal(): block every interactions behind the window, cannot be closed by user, add a dimming background, has a title bar.
def BeginPopup(str_id: str, flags: ImGuiWindowFlags = 0) -> bool:    # imgui.h:673
    """ return True if the popup is open, and you can start outputting to it."""
    pass
def BeginPopupModal(name: str, p_open: BoxedBool = None, flags: ImGuiWindowFlags = 0) -> bool:    # imgui.h:674
    """ return True if the modal is open, and you can start outputting to it."""
    pass
def EndPopup() -> None:    # imgui.h:675
    """ only call EndPopup() if BeginPopupXXX() returns True!"""
    pass

# Popups: open/close functions
#  - OpenPopup(): set popup state to open. ImGuiPopupFlags are available for opening options.
#  - If not modal: they can be closed by clicking anywhere outside them, or by pressing ESCAPE.
#  - CloseCurrentPopup(): use inside the BeginPopup()/EndPopup() scope to close manually.
#  - CloseCurrentPopup() is called by default by Selectable()/MenuItem() when activated (FIXME: need some options).
#  - Use ImGuiPopupFlags_NoOpenOverExistingPopup to avoid opening a popup if there's already one at the same level. This is equivalent to e.g. testing for !IsAnyPopupOpen() prior to OpenPopup().
#  - Use IsWindowAppearing() after BeginPopup() to tell if a window just opened.
#  - IMPORTANT: Notice that for OpenPopupOnItemClick() we exceptionally default flags to 1 (== ImGuiPopupFlags_MouseButtonRight) for backward compatibility with older API taking 'int mouse_button = 1' parameter
def OpenPopup(str_id: str, popup_flags: ImGuiPopupFlags = 0) -> None:    # imgui.h:685
    """ call to mark popup as open (don't call every frame!)."""
    pass
def OpenPopup(id: ImGuiID, popup_flags: ImGuiPopupFlags = 0) -> None:    # imgui.h:686
    """ id overload to facilitate calling from nested stacks"""
    pass
def OpenPopupOnItemClick(str_id: str = None, popup_flags: ImGuiPopupFlags = 1) -> None:    # imgui.h:687
    """ helper to open popup when clicked on last item. Default to ImGuiPopupFlags_MouseButtonRight == 1. (note: actually triggers on the mouse _released_ event to be consistent with popup behaviors)"""
    pass
def CloseCurrentPopup() -> None:    # imgui.h:688
    """ manually close the popup we have begin-ed into."""
    pass

# Popups: open+begin combined functions helpers
#  - Helpers to do OpenPopup+BeginPopup where the Open action is triggered by e.g. hovering an item and right-clicking.
#  - They are convenient to easily create context menus, hence the name.
#  - IMPORTANT: Notice that BeginPopupContextXXX takes ImGuiPopupFlags just like OpenPopup() and unlike BeginPopup(). For full consistency, we may add ImGuiWindowFlags to the BeginPopupContextXXX functions in the future.
#  - IMPORTANT: Notice that we exceptionally default their flags to 1 (== ImGuiPopupFlags_MouseButtonRight) for backward compatibility with older API taking 'int mouse_button = 1' parameter, so if you add other flags remember to re-add the ImGuiPopupFlags_MouseButtonRight.
def BeginPopupContextItem(str_id: str = None, popup_flags: ImGuiPopupFlags = 1) -> bool:    # imgui.h:695
    """ open+begin popup when clicked on last item. Use str_id==None to associate the popup to previous item. If you want to use that on a non-interactive item such as Text() you need to pass in an explicit ID here. read comments in .cpp!"""
    pass
def BeginPopupContextWindow(str_id: str = None, popup_flags: ImGuiPopupFlags = 1) -> bool:    # imgui.h:696
    """ open+begin popup when clicked on current window."""
    pass
def BeginPopupContextVoid(str_id: str = None, popup_flags: ImGuiPopupFlags = 1) -> bool:    # imgui.h:697
    """ open+begin popup when clicked in None (where there are no windows)."""
    pass

# Popups: query functions
#  - IsPopupOpen(): return True if the popup is open at the current BeginPopup() level of the popup stack.
#  - IsPopupOpen() with ImGuiPopupFlags_AnyPopupId: return True if any popup is open at the current BeginPopup() level of the popup stack.
#  - IsPopupOpen() with ImGuiPopupFlags_AnyPopupId + ImGuiPopupFlags_AnyPopupLevel: return True if any popup is open.
def IsPopupOpen(str_id: str, flags: ImGuiPopupFlags = 0) -> bool:    # imgui.h:703
    """ return True if the popup is open."""
    pass

# Tables
# - Full-featured replacement for old Columns API.
# - See Demo->Tables for demo code. See top of imgui_tables.cpp for general commentary.
# - See ImGuiTableFlags_ and ImGuiTableColumnFlags_ enums for a description of available flags.
# The typical call flow is:
# - 1. Call BeginTable(), early out if returning False.
# - 2. Optionally call TableSetupColumn() to submit column name/flags/defaults.
# - 3. Optionally call TableSetupScrollFreeze() to request scroll freezing of columns/rows.
# - 4. Optionally call TableHeadersRow() to submit a header row. Names are pulled from TableSetupColumn() data.
# - 5. Populate contents:
#    - In most situations you can use TableNextRow() + TableSetColumnIndex(N) to start appending into a column.
#    - If you are using tables as a sort of grid, where every columns is holding the same type of contents,
#      you may prefer using TableNextColumn() instead of TableNextRow() + TableSetColumnIndex().
#      TableNextColumn() will automatically wrap-around into the next row if needed.
#    - IMPORTANT: Comparatively to the old Columns() API, we need to call TableNextColumn() for the first column!
#    - Summary of possible call flow:
#        --------------------------------------------------------------------------------------------------------
#        TableNextRow() -> TableSetColumnIndex(0) -> Text("Hello 0") -> TableSetColumnIndex(1) -> Text("Hello 1")  // OK
#        TableNextRow() -> TableNextColumn()      -> Text("Hello 0") -> TableNextColumn()      -> Text("Hello 1")  // OK
#                          TableNextColumn()      -> Text("Hello 0") -> TableNextColumn()      -> Text("Hello 1")  // OK: TableNextColumn() automatically gets to next row!
#        TableNextRow()                           -> Text("Hello 0")                                               // Not OK! Missing TableSetColumnIndex() or TableNextColumn()! Text will not appear!
#        --------------------------------------------------------------------------------------------------------
# - 5. Call EndTable()
def BeginTable(str_id: str, column: int, flags: ImGuiTableFlags = 0, outer_size: ImVec2 = ImVec2(0.0, 0.0), inner_width: float = 0.0) -> bool:    # imgui.h:728
    pass
def EndTable() -> None:    # imgui.h:729
    """ only call EndTable() if BeginTable() returns True!"""
    pass
def TableNextRow(row_flags: ImGuiTableRowFlags = 0, min_row_height: float = 0.0) -> None:    # imgui.h:730
    """ append into the first cell of a new row."""
    pass
def TableNextColumn() -> bool:    # imgui.h:731
    """ append into the next column (or first column of next row if currently in last column). Return True when column is visible."""
    pass
def TableSetColumnIndex(column_n: int) -> bool:    # imgui.h:732
    """ append into the specified column. Return True when column is visible."""
    pass

# Tables: Headers & Columns declaration
# - Use TableSetupColumn() to specify label, resizing policy, default width/weight, id, various other flags etc.
# - Use TableHeadersRow() to create a header row and automatically submit a TableHeader() for each column.
#   Headers are required to perform: reordering, sorting, and opening the context menu.
#   The context menu can also be made available in columns body using ImGuiTableFlags_ContextMenuInBody.
# - You may manually submit headers using TableNextRow() + TableHeader() calls, but this is only useful in
#   some advanced use cases (e.g. adding custom widgets in header row).
# - Use TableSetupScrollFreeze() to lock columns/rows so they stay visible when scrolled.
def TableSetupColumn(label: str, flags: ImGuiTableColumnFlags = 0, init_width_or_weight: float = 0.0, user_id: ImGuiID = 0) -> None:    # imgui.h:742
    pass
def TableSetupScrollFreeze(cols: int, rows: int) -> None:    # imgui.h:743
    """ lock columns/rows so they stay visible when scrolled."""
    pass
def TableHeadersRow() -> None:    # imgui.h:744
    """ submit all headers cells based on data provided to TableSetupColumn() + submit context menu"""
    pass
def TableHeader(label: str) -> None:    # imgui.h:745
    """ submit one header cell manually (rarely used)"""
    pass

# Tables: Sorting & Miscellaneous functions
# - Sorting: call TableGetSortSpecs() to retrieve latest sort specs for the table. None when not sorting.
#   When 'sort_specs->SpecsDirty == True' you should sort your data. It will be True when sorting specs have
#   changed since last call, or the first time. Make sure to set 'SpecsDirty = False' after sorting,
#   else you may wastefully sort your data every frame!
# - Functions args 'int column_n' treat the default value of -1 as the same as passing the current column index.
def TableGetSortSpecs() -> ImGuiTableSortSpecs:    # imgui.h:753
    """ get latest sort specs for the table (None if not sorting).  Lifetime: don't hold on this pointer over multiple frames or past any subsequent call to BeginTable()."""
    pass
def TableGetColumnCount() -> int:    # imgui.h:754
    """ return number of columns (value passed to BeginTable)"""
    pass
def TableGetColumnIndex() -> int:    # imgui.h:755
    """ return current column index."""
    pass
def TableGetRowIndex() -> int:    # imgui.h:756
    """ return current row index."""
    pass
def TableGetColumnName(column_n: int = -1) -> str:    # imgui.h:757
    """ return "" if column didn't have a name declared by TableSetupColumn(). Pass -1 to use current column."""
    pass
def TableGetColumnFlags(column_n: int = -1) -> ImGuiTableColumnFlags:    # imgui.h:758
    """ return column flags so you can query their Enabled/Visible/Sorted/Hovered status flags. Pass -1 to use current column."""
    pass
def TableSetColumnEnabled(column_n: int, v: bool) -> None:    # imgui.h:759
    """ change user accessible enabled/disabled state of a column. Set to False to hide the column. User can use the context menu to change this themselves (right-click in headers, or right-click in columns body with ImGuiTableFlags_ContextMenuInBody)"""
    pass
def TableSetBgColor(target: ImGuiTableBgTarget, color: ImU32, column_n: int = -1) -> None:    # imgui.h:760
    """ change the color of a cell, row, or column. See ImGuiTableBgTarget_ flags for details."""
    pass

# Legacy Columns API (prefer using Tables!)
# - You can also use SameLine(pos_x) to mimic simplified columns.
def Columns(count: int = 1, id: str = None, border: bool = True) -> None:    # imgui.h:764
    pass
def NextColumn() -> None:    # imgui.h:765
    """ next column, defaults to current row or next row if the current row is finished"""
    pass
def GetColumnIndex() -> int:    # imgui.h:766
    """ get current column index"""
    pass
def GetColumnWidth(column_index: int = -1) -> float:    # imgui.h:767
    """ get column width (in pixels). pass -1 to use current column"""
    pass
def SetColumnWidth(column_index: int, width: float) -> None:    # imgui.h:768
    """ set column width (in pixels). pass -1 to use current column"""
    pass
def GetColumnOffset(column_index: int = -1) -> float:    # imgui.h:769
    """ get position of column line (in pixels, from the left side of the contents region). pass -1 to use current column, otherwise 0..GetColumnsCount() inclusive. column 0 is typically 0.0"""
    pass
def SetColumnOffset(column_index: int, offset_x: float) -> None:    # imgui.h:770
    """ set position of column line (in pixels, from the left side of the contents region). pass -1 to use current column"""
    pass
def GetColumnsCount() -> int:    # imgui.h:771
    pass

# Tab Bars, Tabs
def BeginTabBar(str_id: str, flags: ImGuiTabBarFlags = 0) -> bool:    # imgui.h:774
    """ create and append into a TabBar"""
    pass
def EndTabBar() -> None:    # imgui.h:775
    """ only call EndTabBar() if BeginTabBar() returns True!"""
    pass
def BeginTabItem(label: str, p_open: BoxedBool = None, flags: ImGuiTabItemFlags = 0) -> bool:    # imgui.h:776
    """ create a Tab. Returns True if the Tab is selected."""
    pass
def EndTabItem() -> None:    # imgui.h:777
    """ only call EndTabItem() if BeginTabItem() returns True!"""
    pass
def TabItemButton(label: str, flags: ImGuiTabItemFlags = 0) -> bool:    # imgui.h:778
    """ create a Tab behaving like a button. return True when clicked. cannot be selected in the tab bar."""
    pass
def SetTabItemClosed(tab_or_docked_window_label: str) -> None:    # imgui.h:779
    """ notify TabBar or Docking system of a closed tab/window ahead (useful to reduce visual flicker on reorderable tab bars). For tab-bar: call after BeginTabBar() and before Tab submissions. Otherwise call with a window name."""
    pass

# Logging/Capture
# - All text output from the interface can be captured into tty/file/clipboard. By default, tree nodes are automatically opened during logging.
def LogToTTY(auto_open_depth: int = -1) -> None:    # imgui.h:783
    """ start logging to tty (stdout)"""
    pass
def LogToFile(auto_open_depth: int = -1, filename: str = None) -> None:    # imgui.h:784
    """ start logging to file"""
    pass
def LogToClipboard(auto_open_depth: int = -1) -> None:    # imgui.h:785
    """ start logging to OS clipboard"""
    pass
def LogFinish() -> None:    # imgui.h:786
    """ stop logging (close file, etc.)"""
    pass
def LogButtons() -> None:    # imgui.h:787
    """ helper to display buttons for logging to tty/file/clipboard"""
    pass
def LogText(fmt: str) -> None:    # imgui.h:788
    """ pass text data straight to log (without being displayed)"""
    pass

# Drag and Drop
# - On source items, call BeginDragDropSource(), if it returns True also call SetDragDropPayload() + EndDragDropSource().
# - On target candidates, call BeginDragDropTarget(), if it returns True also call AcceptDragDropPayload() + EndDragDropTarget().
# - If you stop calling BeginDragDropSource() the payload is preserved however it won't have a preview tooltip (we currently display a fallback "..." tooltip, see #1725)
# - An item can be both drag source and drop target.
def BeginDragDropSource(flags: ImGuiDragDropFlags = 0) -> bool:    # imgui.h:796
    """ call after submitting an item which may be dragged. when this return True, you can call SetDragDropPayload() + EndDragDropSource()"""
    pass
def SetDragDropPayload(type: str, data: Any, sz: int, cond: ImGuiCond = 0) -> bool:    # imgui.h:797
    """ type is a user defined string of maximum 32 characters. Strings starting with '_' are reserved for dear imgui internal types. Data is copied and held by imgui. Return True when payload has been accepted."""
    pass
def EndDragDropSource() -> None:    # imgui.h:798
    """ only call EndDragDropSource() if BeginDragDropSource() returns True!"""
    pass
def BeginDragDropTarget() -> bool:    # imgui.h:799
    """ call after submitting an item that may receive a payload. If this returns True, you can call AcceptDragDropPayload() + EndDragDropTarget()"""
    pass
def AcceptDragDropPayload(type: str, flags: ImGuiDragDropFlags = 0) -> ImGuiPayload:    # imgui.h:800
    """ accept contents of a given type. If ImGuiDragDropFlags_AcceptBeforeDelivery is set you can peek into the payload before the mouse button is released."""
    pass
def EndDragDropTarget() -> None:    # imgui.h:801
    """ only call EndDragDropTarget() if BeginDragDropTarget() returns True!"""
    pass
def GetDragDropPayload() -> ImGuiPayload:    # imgui.h:802
    """ peek directly into the current payload from anywhere. may return None. use ImGuiPayload::IsDataType() to test for the payload type."""
    pass

# Disabling [BETA API]
# - Disable all user interactions and dim items visuals (applying style.DisabledAlpha over current colors)
# - Those can be nested but it cannot be used to enable an already disabled section (a single BeginDisabled(True) in the stack is enough to keep everything disabled)
# - BeginDisabled(False) essentially does nothing useful but is provided to facilitate use of boolean expressions. If you can avoid calling BeginDisabled(False)/EndDisabled() best to avoid it.
def BeginDisabled(disabled: bool = True) -> None:    # imgui.h:808
    pass
def EndDisabled() -> None:    # imgui.h:809
    pass

# Clipping
# - Mouse hovering is affected by ImGui::PushClipRect() calls, unlike direct calls to ImDrawList::PushClipRect() which are render only.
def PushClipRect(clip_rect_min: ImVec2, clip_rect_max: ImVec2, intersect_with_current_clip_rect: bool) -> None:    # imgui.h:813
    pass
def PopClipRect() -> None:    # imgui.h:814
    pass

# Focus, Activation
# - Prefer using "SetItemDefaultFocus()" over "if (IsWindowAppearing()) SetScrollHereY()" when applicable to signify "this is the default item"
def SetItemDefaultFocus() -> None:    # imgui.h:818
    """ make last item the default focused item of a window."""
    pass
def SetKeyboardFocusHere(offset: int = 0) -> None:    # imgui.h:819
    """ focus keyboard on the next widget. Use positive 'offset' to access sub components of a multiple component widget. Use -1 to access previous widget."""
    pass

# Item/Widgets Utilities and Query Functions
# - Most of the functions are referring to the previous Item that has been submitted.
# - See Demo Window under "Widgets->Querying Status" for an interactive visualization of most of those functions.
def IsItemHovered(flags: ImGuiHoveredFlags = 0) -> bool:    # imgui.h:824
    """ is the last item hovered? (and usable, aka not blocked by a popup, etc.). See ImGuiHoveredFlags for more options."""
    pass
def IsItemActive() -> bool:    # imgui.h:825
    """ is the last item active? (e.g. button being held, text field being edited. This will continuously return True while holding mouse button on an item. Items that don't interact will always return False)"""
    pass
def IsItemFocused() -> bool:    # imgui.h:826
    """ is the last item focused for keyboard/gamepad navigation?"""
    pass
def IsItemClicked(mouse_button: ImGuiMouseButton = 0) -> bool:    # imgui.h:827
    """ is the last item hovered and mouse clicked on? (**)  == IsMouseClicked(mouse_button) && IsItemHovered()Important. (**) this it NOT equivalent to the behavior of e.g. Button(). Read comments in function definition."""
    pass
def IsItemVisible() -> bool:    # imgui.h:828
    """ is the last item visible? (items may be out of sight because of clipping/scrolling)"""
    pass
def IsItemEdited() -> bool:    # imgui.h:829
    """ did the last item modify its underlying value this frame? or was pressed? This is generally the same as the "bool" return value of many widgets."""
    pass
def IsItemActivated() -> bool:    # imgui.h:830
    """ was the last item just made active (item was previously inactive)."""
    pass
def IsItemDeactivated() -> bool:    # imgui.h:831
    """ was the last item just made inactive (item was previously active). Useful for Undo/Redo patterns with widgets that requires continuous editing."""
    pass
def IsItemDeactivatedAfterEdit() -> bool:    # imgui.h:832
    """ was the last item just made inactive and made a value change when it was active? (e.g. Slider/Drag moved). Useful for Undo/Redo patterns with widgets that requires continuous editing. Note that you may get False positives (some widgets such as Combo()/ListBox()/Selectable() will return True even when clicking an already selected item)."""
    pass
def IsItemToggledOpen() -> bool:    # imgui.h:833
    """ was the last item open state toggled? set by TreeNode()."""
    pass
def IsAnyItemHovered() -> bool:    # imgui.h:834
    """ is any item hovered?"""
    pass
def IsAnyItemActive() -> bool:    # imgui.h:835
    """ is any item active?"""
    pass
def IsAnyItemFocused() -> bool:    # imgui.h:836
    """ is any item focused?"""
    pass
def GetItemRectMin() -> ImVec2:    # imgui.h:837
    """ get upper-left bounding rectangle of the last item (screen space)"""
    pass
def GetItemRectMax() -> ImVec2:    # imgui.h:838
    """ get lower-right bounding rectangle of the last item (screen space)"""
    pass
def GetItemRectSize() -> ImVec2:    # imgui.h:839
    """ get size of last item"""
    pass
def SetItemAllowOverlap() -> None:    # imgui.h:840
    """ allow last item to be overlapped by a subsequent item. sometimes useful with invisible buttons, selectables, etc. to catch unused area."""
    pass

# Viewports
# - Currently represents the Platform Window created by the application which is hosting our Dear ImGui windows.
# - In 'docking' branch with multi-viewport enabled, we extend this concept to have multiple active viewports.
# - In the future we will extend this concept further to also represent Platform Monitor and support a "no main platform window" operation mode.
def GetMainViewport() -> ImGuiViewport:    # imgui.h:846
    """ return primary/default viewport. This can never be None."""
    pass

# Background/Foreground Draw Lists
def GetBackgroundDrawList() -> ImDrawList:    # imgui.h:849
    """ this draw list will be the first rendered one. Useful to quickly draw shapes/text behind dear imgui contents."""
    pass
def GetForegroundDrawList() -> ImDrawList:    # imgui.h:850
    """ this draw list will be the last rendered one. Useful to quickly draw shapes/text over dear imgui contents."""
    pass

# Miscellaneous Utilities
def IsRectVisible(size: ImVec2) -> bool:    # imgui.h:853
    """ test if rectangle (of given size, starting from cursor position) is visible / not clipped."""
    pass
def IsRectVisible(rect_min: ImVec2, rect_max: ImVec2) -> bool:    # imgui.h:854
    """ test if rectangle (in screen space) is visible / not clipped. to perform coarse clipping on user's side."""
    pass
def GetTime() -> float:    # imgui.h:855
    """ get global imgui time. incremented by io.DeltaTime every frame."""
    pass
def GetFrameCount() -> int:    # imgui.h:856
    """ get global imgui frame count. incremented by 1 every frame."""
    pass
def GetDrawListSharedData() -> ImDrawListSharedData:    # imgui.h:857
    """ you may use this when creating your own ImDrawList instances."""
    pass
def GetStyleColorName(idx: ImGuiCol) -> str:    # imgui.h:858
    """ get a string corresponding to the enum value (for display, saving, etc.)."""
    pass
def SetStateStorage(storage: ImGuiStorage) -> None:    # imgui.h:859
    """ replace current window storage with our own (if you want to manipulate it yourself, typically clear subsection of it)"""
    pass
def GetStateStorage() -> ImGuiStorage:    # imgui.h:860
    pass
def BeginChildFrame(id: ImGuiID, size: ImVec2, flags: ImGuiWindowFlags = 0) -> bool:    # imgui.h:861
    """ helper to create a child window / scrolling region that looks like a normal widget frame"""
    pass
def EndChildFrame() -> None:    # imgui.h:862
    """ always call EndChildFrame() regardless of BeginChildFrame() return values (which indicates a collapsed/clipped window)"""
    pass

def CalcTextSize(text: str, text_end: str = None, hide_text_after_double_hash: bool = False, wrap_width: float = -1.0) -> ImVec2:    # imgui.h:865
    """ Text Utilities"""
    pass

# Color Utilities
def ColorConvertU32ToFloat4(in_: ImU32) -> ImVec4:    # imgui.h:868
    pass
def ColorConvertFloat4ToU32(in_: ImVec4) -> ImU32:    # imgui.h:869
    pass
def ColorConvertHSVtoRGB(h: float, s: float, v: float, out_r: BoxedFloat, out_g: BoxedFloat, out_b: BoxedFloat) -> None:    # imgui.h:871
    pass

# Inputs Utilities: Keyboard
# Without IMGUI_DISABLE_OBSOLETE_KEYIO: (legacy support)
#   - For 'ImGuiKey key' you can still use your legacy native/user indices according to how your backend/engine stored them in io.KeysDown[].
# With IMGUI_DISABLE_OBSOLETE_KEYIO: (this is the way forward)
#   - Any use of 'ImGuiKey' will assert when key < 512 will be passed, previously reserved as native/user keys indices
#   - GetKeyIndex() is pass-through and therefore deprecated (gone if IMGUI_DISABLE_OBSOLETE_KEYIO is defined)
def IsKeyDown(key: ImGuiKey) -> bool:    # imgui.h:879
    """ is key being held."""
    pass
def IsKeyPressed(key: ImGuiKey, repeat: bool = True) -> bool:    # imgui.h:880
    """ was key pressed (went from !Down to Down)? if repeat=True, uses io.KeyRepeatDelay / KeyRepeatRate"""
    pass
def IsKeyReleased(key: ImGuiKey) -> bool:    # imgui.h:881
    """ was key released (went from Down to !Down)?"""
    pass
def GetKeyPressedAmount(key: ImGuiKey, repeat_delay: float, rate: float) -> int:    # imgui.h:882
    """ uses provided repeat rate/delay. return a count, most often 0 or 1 but might be >1 if RepeatRate is small enough that DeltaTime > RepeatRate"""
    pass
def GetKeyName(key: ImGuiKey) -> str:    # imgui.h:883
    """ [DEBUG] returns English name of the key. Those names a provided for debugging purpose and are not meant to be saved persistently not compared."""
    pass
def SetNextFrameWantCaptureKeyboard(want_capture_keyboard: bool) -> None:    # imgui.h:884
    """ Override io.WantCaptureKeyboard flag next frame (said flag is left for your application to handle, typically when True it instructs your app to ignore inputs). e.g. force capture keyboard when your widget is being hovered. This is equivalent to setting "io.WantCaptureKeyboard = want_capture_keyboard"; after the next NewFrame() call."""
    pass

# Inputs Utilities: Mouse
# - To refer to a mouse button, you may use named enums in your code e.g. ImGuiMouseButton_Left, ImGuiMouseButton_Right.
# - You can also use regular integer: it is forever guaranteed that 0=Left, 1=Right, 2=Middle.
# - Dragging operations are only reported after mouse has moved a certain distance away from the initial clicking position (see 'lock_threshold' and 'io.MouseDraggingThreshold')
def IsMouseDown(button: ImGuiMouseButton) -> bool:    # imgui.h:890
    """ is mouse button held?"""
    pass
def IsMouseClicked(button: ImGuiMouseButton, repeat: bool = False) -> bool:    # imgui.h:891
    """ did mouse button clicked? (went from !Down to Down). Same as GetMouseClickedCount() == 1."""
    pass
def IsMouseReleased(button: ImGuiMouseButton) -> bool:    # imgui.h:892
    """ did mouse button released? (went from Down to !Down)"""
    pass
def IsMouseDoubleClicked(button: ImGuiMouseButton) -> bool:    # imgui.h:893
    """ did mouse button double-clicked? Same as GetMouseClickedCount() == 2. (note that a double-click will also report IsMouseClicked() == True)"""
    pass
def GetMouseClickedCount(button: ImGuiMouseButton) -> int:    # imgui.h:894
    """ return the number of successive mouse-clicks at the time where a click happen (otherwise 0)."""
    pass
def IsMouseHoveringRect(r_min: ImVec2, r_max: ImVec2, clip: bool = True) -> bool:    # imgui.h:895
    """ is mouse hovering given bounding rect (in screen space). clipped by current clipping settings, but disregarding of other consideration of focus/window ordering/popup-block."""
    pass
def IsMousePosValid(mouse_pos: ImVec2 = None) -> bool:    # imgui.h:896
    """ by convention we use (-FLT_MAX,-FLT_MAX) to denote that there is no mouse available"""
    pass
def IsAnyMouseDown() -> bool:    # imgui.h:897
    """ [WILL OBSOLETE] is any mouse button held? This was designed for backends, but prefer having backend maintain a mask of held mouse buttons, because upcoming input queue system will make this invalid."""
    pass
def GetMousePos() -> ImVec2:    # imgui.h:898
    """ shortcut to ImGui::GetIO().MousePos provided by user, to be consistent with other calls"""
    pass
def GetMousePosOnOpeningCurrentPopup() -> ImVec2:    # imgui.h:899
    """ retrieve mouse position at the time of opening popup we have BeginPopup() into (helper to avoid user backing that value themselves)"""
    pass
def IsMouseDragging(button: ImGuiMouseButton, lock_threshold: float = -1.0) -> bool:    # imgui.h:900
    """ is mouse dragging? (if lock_threshold < -1.0, uses io.MouseDraggingThreshold)"""
    pass
def GetMouseDragDelta(button: ImGuiMouseButton = 0, lock_threshold: float = -1.0) -> ImVec2:    # imgui.h:901
    """ return the delta from the initial clicking position while the mouse button is pressed or was just released. This is locked and return 0.0 until the mouse moves past a distance threshold at least once (if lock_threshold < -1.0, uses io.MouseDraggingThreshold)"""
    pass
def ResetMouseDragDelta(button: ImGuiMouseButton = 0) -> None:    # imgui.h:902
    pass
def GetMouseCursor() -> ImGuiMouseCursor:    # imgui.h:903
    """ get desired cursor type, reset in ImGui::NewFrame(), this is updated during the frame. valid before Render(). If you use software rendering by setting io.MouseDrawCursor ImGui will render those for you"""
    pass
def SetMouseCursor(cursor_type: ImGuiMouseCursor) -> None:    # imgui.h:904
    """ set desired cursor type"""
    pass
def SetNextFrameWantCaptureMouse(want_capture_mouse: bool) -> None:    # imgui.h:905
    """ Override io.WantCaptureMouse flag next frame (said flag is left for your application to handle, typical when True it instucts your app to ignore inputs). This is equivalent to setting "io.WantCaptureMouse = want_capture_mouse;" after the next NewFrame() call."""
    pass

# Clipboard Utilities
# - Also see the LogToClipboard() function to capture GUI into clipboard, or easily output text data to the clipboard.
def GetClipboardText() -> str:    # imgui.h:909
    pass
def SetClipboardText(text: str) -> None:    # imgui.h:910
    pass

# Settings/.Ini Utilities
# - The disk functions are automatically called if io.IniFilename != None (default is "imgui.ini").
# - Set io.IniFilename to None to load/save manually. Read io.WantSaveIniSettings description about handling .ini saving manually.
# - Important: default value "imgui.ini" is relative to current working dir! Most apps will want to lock this to an absolute path (e.g. same path as executables).
def LoadIniSettingsFromDisk(ini_filename: str) -> None:    # imgui.h:916
    """ call after CreateContext() and before the first call to NewFrame(). NewFrame() automatically calls LoadIniSettingsFromDisk(io.IniFilename)."""
    pass
def LoadIniSettingsFromMemory(ini_data: str, ini_size: int = 0) -> None:    # imgui.h:917
    """ call after CreateContext() and before the first call to NewFrame() to provide .ini data from your own data source."""
    pass
def SaveIniSettingsToDisk(ini_filename: str) -> None:    # imgui.h:918
    """ this is automatically called (if io.IniFilename is not empty) a few seconds after any modification that should be reflected in the .ini file (and also by DestroyContext)."""
    pass
def SaveIniSettingsToMemory(out_ini_size: int = None) -> str:    # imgui.h:919
    """ return a zero-terminated string with the .ini data which you can save by your own mean. call when io.WantSaveIniSettings is set, then save data by your own mean and clear io.WantSaveIniSettings."""
    pass

# Debug Utilities
def DebugTextEncoding(text: str) -> None:    # imgui.h:922
    pass
def DebugCheckVersionAndDataLayout(version_str: str, sz_io: int, sz_style: int, sz_vec2: int, sz_vec4: int, sz_drawvert: int, sz_drawidx: int) -> bool:    # imgui.h:923
    """ This is called by IMGUI_CHECKVERSION() macro."""
    pass

# Memory Allocators
# - Those functions are not reliant on the current context.
# - DLL users: heaps and globals are not shared across DLL boundaries! You will need to call SetCurrentContext() + SetAllocatorFunctions()
#   for each static/DLL boundary you are calling from. Read "Context and Memory Allocators" section of imgui.cpp for more details.

# </Namespace ImGui>

#-----------------------------------------------------------------------------
# [SECTION] Flags & Enumerations
#-----------------------------------------------------------------------------

class ImGuiWindowFlags_(Enum):    # imgui.h:941
    """ Flags for ImGui::Begin()"""
    None_ = 0
    NoTitleBar = 1 << 0                 # Disable title-bar
    NoResize = 1 << 1                   # Disable user resizing with the lower-right grip
    NoMove = 1 << 2                     # Disable user moving the window
    NoScrollbar = 1 << 3                # Disable scrollbars (window can still scroll with mouse or programmatically)
    NoScrollWithMouse = 1 << 4          # Disable user vertically scrolling with mouse wheel. On child window, mouse wheel will be forwarded to the parent unless NoScrollbar is also set.
    NoCollapse = 1 << 5                 # Disable user collapsing window by double-clicking on it. Also referred to as Window Menu Button (e.g. within a docking node).
    AlwaysAutoResize = 1 << 6           # Resize every window to its content every frame
    NoBackground = 1 << 7               # Disable drawing background color (WindowBg, etc.) and outside border. Similar as using SetNextWindowBgAlpha(0.0).
    NoSavedSettings = 1 << 8            # Never load/save settings in .ini file
    NoMouseInputs = 1 << 9              # Disable catching mouse, hovering test with pass through.
    MenuBar = 1 << 10                   # Has a menu-bar
    HorizontalScrollbar = 1 << 11       # Allow horizontal scrollbar to appear (off by default). You may use SetNextWindowContentSize(ImVec2(width,0.0)); prior to calling Begin() to specify width. Read code in imgui_demo in the "Horizontal Scrolling" section.
    NoFocusOnAppearing = 1 << 12        # Disable taking focus when transitioning from hidden to visible state
    NoBringToFrontOnFocus = 1 << 13     # Disable bringing window to front when taking focus (e.g. clicking on it or programmatically giving it focus)
    AlwaysVerticalScrollbar = 1 << 14   # Always show vertical scrollbar (even if ContentSize.y < Size.y)
    AlwaysHorizontalScrollbar = 1<< 15  # Always show horizontal scrollbar (even if ContentSize.x < Size.x)
    AlwaysUseWindowPadding = 1 << 16    # Ensure child windows without border uses style.WindowPadding (ignored by default for non-bordered child windows, because more convenient)
    NoNavInputs = 1 << 18               # No gamepad/keyboard navigation within the window
    NoNavFocus = 1 << 19                # No focusing toward this window with gamepad/keyboard navigation (e.g. skipped by CTRL+TAB)
    UnsavedDocument = 1 << 20           # Display a dot next to the title. When used in a tab/docking context, tab is selected when clicking the X + closure is not assumed (will wait for user to stop submitting the tab). Otherwise closure is assumed when pressing the X, so if you keep submitting the tab may reappear at end of tab bar.
    NoNav = Literal[ImGuiWindowFlags_.NoNavInputs] | Literal[ImGuiWindowFlags_.NoNavFocus]
    NoDecoration = Literal[ImGuiWindowFlags_.NoTitleBar] | Literal[ImGuiWindowFlags_.NoResize] | Literal[ImGuiWindowFlags_.NoScrollbar] | Literal[ImGuiWindowFlags_.NoCollapse]
    NoInputs = Literal[ImGuiWindowFlags_.NoMouseInputs] | Literal[ImGuiWindowFlags_.NoNavInputs] | Literal[ImGuiWindowFlags_.NoNavFocus]

    # [Internal]
    NavFlattened = 1 << 23              # [BETA] On child window: allow gamepad/keyboard navigation to cross over parent border to this child or between sibling child windows.
    ChildWindow = 1 << 24               # Don't use! For internal use by BeginChild()
    Tooltip = 1 << 25                   # Don't use! For internal use by BeginTooltip()
    Popup = 1 << 26                     # Don't use! For internal use by BeginPopup()
    Modal = 1 << 27                     # Don't use! For internal use by BeginPopupModal()
    ChildMenu = 1 << 28                 # Don't use! For internal use by BeginMenu()
    #ImGuiWindowFlags_ResizeFromAnySide    = 1 << 17,  // [Obsolete] --> Set io.ConfigWindowsResizeFromEdges=True and make sure mouse cursors are supported by backend (io.BackendFlags & ImGuiBackendFlags_HasMouseCursors)

class ImGuiInputTextFlags_(Enum):    # imgui.h:979
    """ Flags for ImGui::InputText()"""
    None_ = 0
    CharsDecimal = 1 << 0          # Allow 0123456789.+-*/
    CharsHexadecimal = 1 << 1      # Allow 0123456789ABCDEFabcdef
    CharsUppercase = 1 << 2        # Turn a..z into A..Z
    CharsNoBlank = 1 << 3          # Filter out spaces, tabs
    AutoSelectAll = 1 << 4         # Select entire text when first taking mouse focus
    EnterReturnsTrue = 1 << 5      # Return 'True' when Enter is pressed (as opposed to every time the value was modified). Consider looking at the IsItemDeactivatedAfterEdit() function.
    CallbackCompletion = 1 << 6    # Callback on pressing TAB (for completion handling)
    CallbackHistory = 1 << 7       # Callback on pressing Up/Down arrows (for history handling)
    CallbackAlways = 1 << 8        # Callback on each iteration. User code may query cursor position, modify text buffer.
    CallbackCharFilter = 1 << 9    # Callback on character inputs to replace or discard them. Modify 'EventChar' to replace or discard, or return 1 in callback to discard.
    AllowTabInput = 1 << 10        # Pressing TAB input a '\t' character into the text field
    CtrlEnterForNewLine = 1 << 11  # In multi-line mode, unfocus with Enter, add new line with Ctrl+Enter (default is opposite: unfocus with Ctrl+Enter, add line with Enter).
    NoHorizontalScroll = 1 << 12   # Disable following the cursor horizontally
    AlwaysOverwrite = 1 << 13      # Overwrite mode
    ReadOnly = 1 << 14             # Read-only mode
    Password = 1 << 15             # Password mode, display all characters as '*'
    NoUndoRedo = 1 << 16           # Disable undo/redo. Note that input text owns the text data while active, if you want to provide your own undo/redo stack you need e.g. to call ClearActiveID().
    CharsScientific = 1 << 17      # Allow 0123456789.+-*/eE (Scientific notation input)
    CallbackResize = 1 << 18       # Callback on buffer capacity changes request (beyond 'buf_size' parameter value), allowing the string to grow. Notify when the string wants to be resized (for string types which hold a cache of their Size). You will be provided a new BufSize in the callback and NEED to honor it. (see misc/cpp/imgui_stdlib.h for an example of using this)
    CallbackEdit = 1 << 19
    # Callback on any edit (note that InputText() already returns True on edit, the callback is useful mainly to manipulate the underlying buffer while focus is active)

    # Obsolete names (will be removed soon)

class ImGuiTreeNodeFlags_(Enum):    # imgui.h:1010
    """ Flags for ImGui::TreeNodeEx(), ImGui::CollapsingHeader*()"""
    None_ = 0
    Selected = 1 << 0               # Draw as selected
    Framed = 1 << 1                 # Draw frame with background (e.g. for CollapsingHeader)
    AllowItemOverlap = 1 << 2       # Hit testing to allow subsequent widgets to overlap this one
    NoTreePushOnOpen = 1 << 3       # Don't do a TreePush() when open (e.g. for CollapsingHeader) = no extra indent nor pushing on ID stack
    NoAutoOpenOnLog = 1 << 4        # Don't automatically and temporarily open node when Logging is active (by default logging will automatically open tree nodes)
    DefaultOpen = 1 << 5            # Default node to be open
    OpenOnDoubleClick = 1 << 6      # Need double-click to open node
    OpenOnArrow = 1 << 7            # Only open when clicking on the arrow part. If ImGuiTreeNodeFlags_OpenOnDoubleClick is also set, single-click arrow or double-click all box to open.
    Leaf = 1 << 8                   # No collapsing, no arrow (use as a convenience for leaf nodes).
    Bullet = 1 << 9                 # Display a bullet instead of arrow
    FramePadding = 1 << 10          # Use FramePadding (even for an unframed text node) to vertically align text baseline to regular widget height. Equivalent to calling AlignTextToFramePadding().
    SpanAvailWidth = 1 << 11        # Extend hit box to the right-most edge, even if not framed. This is not the default in order to allow adding other items on the same line. In the future we may refactor the hit system to be front-to-back, allowing natural overlaps and then this can become the default.
    SpanFullWidth = 1 << 12         # Extend hit box to the left-most and right-most edges (bypass the indented area).
    NavLeftJumpsBackHere = 1 << 13  # (WIP) Nav: left direction may move to this TreeNode() from any of its child (items submitted between TreeNode and TreePop)
    #ImGuiTreeNodeFlags_NoScrollOnOpen     = 1 << 14,  // FIXME: TODO: Disable automatic scroll on TreePop() if node got just open and contents is not visible
    CollapsingHeader = Literal[ImGuiTreeNodeFlags_.Framed] | Literal[ImGuiTreeNodeFlags_.NoTreePushOnOpen] | Literal[ImGuiTreeNodeFlags_.NoAutoOpenOnLog]

class ImGuiPopupFlags_(Enum):    # imgui.h:1039
    """ Flags for OpenPopup*(), BeginPopupContext*(), IsPopupOpen() functions.
     - To be backward compatible with older API which took an 'int mouse_button = 1' argument, we need to treat
       small flags values as a mouse button index, so we encode the mouse button in the first few bits of the flags.
       It is therefore guaranteed to be legal to pass a mouse button index in ImGuiPopupFlags.
     - For the same reason, we exceptionally default the ImGuiPopupFlags argument of BeginPopupContextXXX functions to 1 instead of 0.
       IMPORTANT: because the default parameter is 1 (==ImGuiPopupFlags_MouseButtonRight), if you rely on the default parameter
       and want to another another flag, you need to pass in the ImGuiPopupFlags_MouseButtonRight flag.
     - Multiple buttons currently cannot be combined/or-ed in those functions (we could allow it later).
    """
    None_ = 0
    MouseButtonLeft = 0               # For BeginPopupContext*(): open on Left Mouse release. Guaranteed to always be == 0 (same as ImGuiMouseButton_Left)
    MouseButtonRight = 1              # For BeginPopupContext*(): open on Right Mouse release. Guaranteed to always be == 1 (same as ImGuiMouseButton_Right)
    MouseButtonMiddle = 2             # For BeginPopupContext*(): open on Middle Mouse release. Guaranteed to always be == 2 (same as ImGuiMouseButton_Middle)
    MouseButtonMask_ = 0x1F
    MouseButtonDefault_ = 1
    NoOpenOverExistingPopup = 1 << 5  # For OpenPopup*(), BeginPopupContext*(): don't open if there's already a popup at the same level of the popup stack
    NoOpenOverItems = 1 << 6          # For BeginPopupContextWindow(): don't return True when hovering items, only when hovering empty space
    AnyPopupId = 1 << 7               # For IsPopupOpen(): ignore the ImGuiID parameter and test for any popup.
    AnyPopupLevel = 1 << 8            # For IsPopupOpen(): search/test at any level of the popup stack (default test in the current level)
    AnyPopup = Literal[ImGuiPopupFlags_.AnyPopupId] | Literal[ImGuiPopupFlags_.AnyPopupLevel]

class ImGuiSelectableFlags_(Enum):    # imgui.h:1055
    """ Flags for ImGui::Selectable()"""
    None_ = 0
    DontClosePopups = 1 << 0   # Clicking this don't close parent popup window
    SpanAllColumns = 1 << 1    # Selectable frame can span all columns (text will still fit in current column)
    AllowDoubleClick = 1 << 2  # Generate press events on double clicks too
    Disabled = 1 << 3          # Cannot be selected, display grayed out text
    AllowItemOverlap = 1 << 4  # (WIP) Hit testing to allow subsequent widgets to overlap this one

class ImGuiComboFlags_(Enum):    # imgui.h:1066
    """ Flags for ImGui::BeginCombo()"""
    None_ = 0
    PopupAlignLeft = 1 << 0  # Align the popup toward the left by default
    HeightSmall = 1 << 1     # Max ~4 items visible. Tip: If you want your combo popup to be a specific size you can use SetNextWindowSizeConstraints() prior to calling BeginCombo()
    HeightRegular = 1 << 2   # Max ~8 items visible (default)
    HeightLarge = 1 << 3     # Max ~20 items visible
    HeightLargest = 1 << 4   # As many fitting items as possible
    NoArrowButton = 1 << 5   # Display on the preview box without the square arrow button
    NoPreview = 1 << 6       # Display only a square arrow button
    HeightMask_ = Literal[ImGuiComboFlags_.HeightSmall] | Literal[ImGuiComboFlags_.HeightRegular] | Literal[ImGuiComboFlags_.HeightLarge] | Literal[ImGuiComboFlags_.HeightLargest]

class ImGuiTabBarFlags_(Enum):    # imgui.h:1080
    """ Flags for ImGui::BeginTabBar()"""
    None_ = 0
    Reorderable = 1 << 0                   # Allow manually dragging tabs to re-order them + New tabs are appended at the end of list
    AutoSelectNewTabs = 1 << 1             # Automatically select new tabs when they appear
    TabListPopupButton = 1 << 2            # Disable buttons to open the tab list popup
    NoCloseWithMiddleMouseButton = 1 << 3  # Disable behavior of closing tabs (that are submitted with p_open != None) with middle mouse button. You can still repro this behavior on user's side with if (IsItemHovered() && IsMouseClicked(2)) *p_open = False.
    NoTabListScrollingButtons = 1 << 4     # Disable scrolling buttons (apply when fitting policy is ImGuiTabBarFlags_FittingPolicyScroll)
    NoTooltip = 1 << 5                     # Disable tooltips when hovering a tab
    FittingPolicyResizeDown = 1 << 6       # Resize tabs when they don't fit
    FittingPolicyScroll = 1 << 7           # Add scroll buttons when tabs don't fit
    FittingPolicyMask_ = Literal[ImGuiTabBarFlags_.FittingPolicyResizeDown] | Literal[ImGuiTabBarFlags_.FittingPolicyScroll]
    FittingPolicyDefault_ = Literal[ImGuiTabBarFlags_.FittingPolicyResizeDown]

class ImGuiTabItemFlags_(Enum):    # imgui.h:1096
    """ Flags for ImGui::BeginTabItem()"""
    None_ = 0
    UnsavedDocument = 1 << 0               # Display a dot next to the title + tab is selected when clicking the X + closure is not assumed (will wait for user to stop submitting the tab). Otherwise closure is assumed when pressing the X, so if you keep submitting the tab may reappear at end of tab bar.
    SetSelected = 1 << 1                   # Trigger flag to programmatically make the tab selected when calling BeginTabItem()
    NoCloseWithMiddleMouseButton = 1 << 2  # Disable behavior of closing tabs (that are submitted with p_open != None) with middle mouse button. You can still repro this behavior on user's side with if (IsItemHovered() && IsMouseClicked(2)) *p_open = False.
    NoPushId = 1 << 3                      # Don't call PushID(tab->ID)/PopID() on BeginTabItem()/EndTabItem()
    NoTooltip = 1 << 4                     # Disable tooltip for the given tab
    NoReorder = 1 << 5                     # Disable reordering this tab or having another tab cross over this tab
    Leading = 1 << 6                       # Enforce the tab position to the left of the tab bar (after the tab list popup button)
    Trailing = 1 << 7                      # Enforce the tab position to the right of the tab bar (before the scrolling buttons)

class ImGuiTableFlags_(Enum):    # imgui.h:1131
    """ Flags for ImGui::BeginTable()
     - Important! Sizing policies have complex and subtle side effects, much more so than you would expect.
       Read comments/demos carefully + experiment with live demos to get acquainted with them.
     - The DEFAULT sizing policies are:
        - Default to ImGuiTableFlags_SizingFixedFit    if ScrollX is on, or if host window has ImGuiWindowFlags_AlwaysAutoResize.
        - Default to ImGuiTableFlags_SizingStretchSame if ScrollX is off.
     - When ScrollX is off:
        - Table defaults to ImGuiTableFlags_SizingStretchSame -> all Columns defaults to ImGuiTableColumnFlags_WidthStretch with same weight.
        - Columns sizing policy allowed: Stretch (default), Fixed/Auto.
        - Fixed Columns (if any) will generally obtain their requested width (unless the table cannot fit them all).
        - Stretch Columns will share the remaining width according to their respective weight.
        - Mixed Fixed/Stretch columns is possible but has various side-effects on resizing behaviors.
          The typical use of mixing sizing policies is: any number of LEADING Fixed columns, followed by one or two TRAILING Stretch columns.
          (this is because the visible order of columns have subtle but necessary effects on how they react to manual resizing).
     - When ScrollX is on:
        - Table defaults to ImGuiTableFlags_SizingFixedFit -> all Columns defaults to ImGuiTableColumnFlags_WidthFixed
        - Columns sizing policy allowed: Fixed/Auto mostly.
        - Fixed Columns can be enlarged as needed. Table will show an horizontal scrollbar if needed.
        - When using auto-resizing (non-resizable) fixed columns, querying the content width to use item right-alignment e.g. SetNextItemWidth(-FLT_MIN) doesn't make sense, would create a feedback loop.
        - Using Stretch columns OFTEN DOES NOT MAKE SENSE if ScrollX is on, UNLESS you have specified a value for 'inner_width' in BeginTable().
          If you specify a value for 'inner_width' then effectively the scrolling space is known and Stretch or mixed Fixed/Stretch columns become meaningful again.
     - Read on documentation at the top of imgui_tables.cpp for details.
    """
    # Features
    None_ = 0
    Resizable = 1 << 0                                                                                # Enable resizing columns.
    Reorderable = 1 << 1                                                                              # Enable reordering columns in header row (need calling TableSetupColumn() + TableHeadersRow() to display headers)
    Hideable = 1 << 2                                                                                 # Enable hiding/disabling columns in context menu.
    Sortable = 1 << 3                                                                                 # Enable sorting. Call TableGetSortSpecs() to obtain sort specs. Also see ImGuiTableFlags_SortMulti and ImGuiTableFlags_SortTristate.
    NoSavedSettings = 1 << 4                                                                          # Disable persisting columns order, width and sort settings in the .ini file.
    ContextMenuInBody = 1 << 5                                                                        # Right-click on columns body/contents will display table context menu. By default it is available in TableHeadersRow().
    # Decorations
    RowBg = 1 << 6                                                                                    # Set each RowBg color with ImGuiCol_TableRowBg or ImGuiCol_TableRowBgAlt (equivalent of calling TableSetBgColor with ImGuiTableBgFlags_RowBg0 on each row manually)
    BordersInnerH = 1 << 7                                                                            # Draw horizontal borders between rows.
    BordersOuterH = 1 << 8                                                                            # Draw horizontal borders at the top and bottom.
    BordersInnerV = 1 << 9                                                                            # Draw vertical borders between columns.
    BordersOuterV = 1 << 10                                                                           # Draw vertical borders on the left and right sides.
    BordersH = Literal[ImGuiTableFlags_.BordersInnerH] | Literal[ImGuiTableFlags_.BordersOuterH]      # Draw horizontal borders.
    BordersV = Literal[ImGuiTableFlags_.BordersInnerV] | Literal[ImGuiTableFlags_.BordersOuterV]      # Draw vertical borders.
    BordersInner = Literal[ImGuiTableFlags_.BordersInnerV] | Literal[ImGuiTableFlags_.BordersInnerH]  # Draw inner borders.
    BordersOuter = Literal[ImGuiTableFlags_.BordersOuterV] | Literal[ImGuiTableFlags_.BordersOuterH]  # Draw outer borders.
    Borders = Literal[ImGuiTableFlags_.BordersInner] | Literal[ImGuiTableFlags_.BordersOuter]         # Draw all borders.
    NoBordersInBody = 1 << 11                                                                         # [ALPHA] Disable vertical borders in columns Body (borders will always appears in Headers). -> May move to style
    NoBordersInBodyUntilResize = 1 << 12                                                              # [ALPHA] Disable vertical borders in columns Body until hovered for resize (borders will always appears in Headers). -> May move to style
    # Sizing Policy (read above for defaults)
    SizingFixedFit = 1 << 13                                                                          # Columns default to _WidthFixed or _WidthAuto (if resizable or not resizable), matching contents width.
    SizingFixedSame = 2 << 13                                                                         # Columns default to _WidthFixed or _WidthAuto (if resizable or not resizable), matching the maximum contents width of all columns. Implicitly enable ImGuiTableFlags_NoKeepColumnsVisible.
    SizingStretchProp = 3 << 13                                                                       # Columns default to _WidthStretch with default weights proportional to each columns contents widths.
    SizingStretchSame = 4 << 13                                                                       # Columns default to _WidthStretch with default weights all equal, unless overridden by TableSetupColumn().
    # Sizing Extra Options
    NoHostExtendX = 1 << 16                                                                           # Make outer width auto-fit to columns, overriding outer_size.x value. Only available when ScrollX/ScrollY are disabled and Stretch columns are not used.
    NoHostExtendY = 1 << 17                                                                           # Make outer height stop exactly at outer_size.y (prevent auto-extending table past the limit). Only available when ScrollX/ScrollY are disabled. Data below the limit will be clipped and not visible.
    NoKeepColumnsVisible = 1 << 18                                                                    # Disable keeping column always minimally visible when ScrollX is off and table gets too small. Not recommended if columns are resizable.
    PreciseWidths = 1 << 19                                                                           # Disable distributing remainder width to stretched columns (width allocation on a 100-wide table with 3 columns: Without this flag: 33,33,34. With this flag: 33,33,33). With larger number of columns, resizing will appear to be less smooth.
    # Clipping
    NoClip = 1 << 20                                                                                  # Disable clipping rectangle for every individual columns (reduce draw command count, items will be able to overflow into other columns). Generally incompatible with TableSetupScrollFreeze().
    # Padding
    PadOuterX = 1 << 21                                                                               # Default if BordersOuterV is on. Enable outer-most padding. Generally desirable if you have headers.
    NoPadOuterX = 1 << 22                                                                             # Default if BordersOuterV is off. Disable outer-most padding.
    NoPadInnerX = 1 << 23                                                                             # Disable inner padding between columns (double inner padding if BordersOuterV is on, single inner padding if BordersOuterV is off).
    # Scrolling
    ScrollX = 1 << 24                                                                                 # Enable horizontal scrolling. Require 'outer_size' parameter of BeginTable() to specify the container size. Changes default sizing policy. Because this create a child window, ScrollY is currently generally recommended when using ScrollX.
    ScrollY = 1 << 25                                                                                 # Enable vertical scrolling. Require 'outer_size' parameter of BeginTable() to specify the container size.
    # Sorting
    SortMulti = 1 << 26                                                                               # Hold shift when clicking headers to sort on multiple column. TableGetSortSpecs() may return specs where (SpecsCount > 1).
    SortTristate = 1 << 27                                                                            # Allow no sorting, disable default sorting. TableGetSortSpecs() may return specs where (SpecsCount == 0).

    # [Internal] Combinations and masks
    SizingMask_ = Literal[ImGuiTableFlags_.SizingFixedFit] | Literal[ImGuiTableFlags_.SizingFixedSame] | Literal[ImGuiTableFlags_.SizingStretchProp] | Literal[ImGuiTableFlags_.SizingStretchSame]

    # Obsolete names (will be removed soon)

class ImGuiTableColumnFlags_(Enum):    # imgui.h:1188
    """ Flags for ImGui::TableSetupColumn()"""
    # Input configuration flags
    None_ = 0
    Disabled = 1 << 0               # Overriding/master disable flag: hide column, won't show in context menu (unlike calling TableSetColumnEnabled() which manipulates the user accessible state)
    DefaultHide = 1 << 1            # Default as a hidden/disabled column.
    DefaultSort = 1 << 2            # Default as a sorting column.
    WidthStretch = 1 << 3           # Column will stretch. Preferable with horizontal scrolling disabled (default if table sizing policy is _SizingStretchSame or _SizingStretchProp).
    WidthFixed = 1 << 4             # Column will not stretch. Preferable with horizontal scrolling enabled (default if table sizing policy is _SizingFixedFit and table is resizable).
    NoResize = 1 << 5               # Disable manual resizing.
    NoReorder = 1 << 6              # Disable manual reordering this column, this will also prevent other columns from crossing over this column.
    NoHide = 1 << 7                 # Disable ability to hide/disable this column.
    NoClip = 1 << 8                 # Disable clipping for this column (all NoClip columns will render in a same draw command).
    NoSort = 1 << 9                 # Disable ability to sort on this field (even if ImGuiTableFlags_Sortable is set on the table).
    NoSortAscending = 1 << 10       # Disable ability to sort in the ascending direction.
    NoSortDescending = 1 << 11      # Disable ability to sort in the descending direction.
    NoHeaderLabel = 1 << 12         # TableHeadersRow() will not submit label for this column. Convenient for some small columns. Name will still appear in context menu.
    NoHeaderWidth = 1 << 13         # Disable header text width contribution to automatic column width.
    PreferSortAscending = 1 << 14   # Make the initial sort direction Ascending when first sorting on this column (default).
    PreferSortDescending = 1 << 15  # Make the initial sort direction Descending when first sorting on this column.
    IndentEnable = 1 << 16          # Use current Indent value when entering cell (default for column 0).
    IndentDisable = 1 << 17         # Ignore current Indent value when entering cell (default for columns > 0). Indentation changes _within_ the cell will still be honored.

    # Output status flags, read-only via TableGetColumnFlags()
    IsEnabled = 1 << 24             # Status: is enabled == not hidden by user/api (referred to as "Hide" in _DefaultHide and _NoHide) flags.
    IsVisible = 1 << 25             # Status: is visible == is enabled AND not clipped by scrolling.
    IsSorted = 1 << 26              # Status: is currently part of the sort specs
    IsHovered = 1 << 27             # Status: is hovered by mouse

    # [Internal] Combinations and masks
    WidthMask_ = Literal[ImGuiTableColumnFlags_.WidthStretch] | Literal[ImGuiTableColumnFlags_.WidthFixed]
    IndentMask_ = Literal[ImGuiTableColumnFlags_.IndentEnable] | Literal[ImGuiTableColumnFlags_.IndentDisable]
    StatusMask_ = Literal[ImGuiTableColumnFlags_.IsEnabled] | Literal[ImGuiTableColumnFlags_.IsVisible] | Literal[ImGuiTableColumnFlags_.IsSorted] | Literal[ImGuiTableColumnFlags_.IsHovered]
    NoDirectResize_ = 1 << 30
    # [Internal] Disable user resizing this column directly (it may however we resized indirectly from its left edge)

    # Obsolete names (will be removed soon)

class ImGuiTableRowFlags_(Enum):    # imgui.h:1230
    """ Flags for ImGui::TableNextRow()"""
    None_ = 0
    Headers = 1 << 0  # Identify header row (set default background color + width of its contents accounted differently for auto column width)

class ImGuiTableBgTarget_(Enum):    # imgui.h:1245
    """ Enum for ImGui::TableSetBgColor()
     Background colors are rendering in 3 layers:
      - Layer 0: draw with RowBg0 color if set, otherwise draw with ColumnBg0 if set.
      - Layer 1: draw with RowBg1 color if set, otherwise draw with ColumnBg1 if set.
      - Layer 2: draw with CellBg color if set.
     The purpose of the two row/columns layers is to let you decide if a background color changes should override or blend with the existing color.
     When using ImGuiTableFlags_RowBg on the table, each row has the RowBg0 color automatically set for odd/even rows.
     If you set the color of RowBg0 target, your color will override the existing RowBg0 color.
     If you set the color of RowBg1 or ColumnBg1 target, your color will blend over the RowBg0 color.
    """
    None_ = 0
    RowBg0 = 1  # Set row background color 0 (generally used for background, automatically set when ImGuiTableFlags_RowBg is used)
    RowBg1 = 2  # Set row background color 1 (generally used for selection marking)
    CellBg = 3  # Set cell background color (top-most color)

class ImGuiFocusedFlags_(Enum):    # imgui.h:1254
    """ Flags for ImGui::IsWindowFocused()"""
    None_ = 0
    ChildWindows = 1 << 0      # Return True if any children of the window is focused
    RootWindow = 1 << 1        # Test from root window (top most parent of the current hierarchy)
    AnyWindow = 1 << 2         # Return True if any window is focused. Important: If you are trying to tell how to dispatch your low-level inputs, do NOT use this. Use 'io.WantCaptureMouse' instead! Please read the FAQ!
    NoPopupHierarchy = 1 << 3  # Do not consider popup hierarchy (do not treat popup emitter as parent of popup) (when used with _ChildWindows or _RootWindow)
    #ImGuiFocusedFlags_DockHierarchy               = 1 << 4,   // Consider docking hierarchy (treat dockspace host as parent of docked window) (when used with _ChildWindows or _RootWindow)
    RootAndChildWindows = Literal[ImGuiFocusedFlags_.RootWindow] | Literal[ImGuiFocusedFlags_.ChildWindows]

class ImGuiHoveredFlags_(Enum):    # imgui.h:1268
    """ Flags for ImGui::IsItemHovered(), ImGui::IsWindowHovered()
     Note: if you are trying to check whether your mouse should be dispatched to Dear ImGui or to your app, you should use 'io.WantCaptureMouse' instead! Please read the FAQ!
     Note: windows with the ImGuiWindowFlags_NoInputs flag are ignored by IsWindowHovered() calls.
    """
    None_ = 0                              # Return True if directly over the item/window, not obstructed by another window, not obstructed by an active popup or modal blocking inputs under them.
    ChildWindows = 1 << 0                  # IsWindowHovered() only: Return True if any children of the window is hovered
    RootWindow = 1 << 1                    # IsWindowHovered() only: Test from root window (top most parent of the current hierarchy)
    AnyWindow = 1 << 2                     # IsWindowHovered() only: Return True if any window is hovered
    NoPopupHierarchy = 1 << 3              # IsWindowHovered() only: Do not consider popup hierarchy (do not treat popup emitter as parent of popup) (when used with _ChildWindows or _RootWindow)
    #ImGuiHoveredFlags_DockHierarchy               = 1 << 4,   // IsWindowHovered() only: Consider docking hierarchy (treat dockspace host as parent of docked window) (when used with _ChildWindows or _RootWindow)
    AllowWhenBlockedByPopup = 1 << 5       # Return True even if a popup window is normally blocking access to this item/window
    #ImGuiHoveredFlags_AllowWhenBlockedByModal     = 1 << 6,   // Return True even if a modal popup window is normally blocking access to this item/window. FIXME-TODO: Unavailable yet.
    AllowWhenBlockedByActiveItem = 1 << 7  # Return True even if an active item is blocking access to this item/window. Useful for Drag and Drop patterns.
    AllowWhenOverlapped = 1 << 8           # IsItemHovered() only: Return True even if the position is obstructed or overlapped by another window
    AllowWhenDisabled = 1 << 9             # IsItemHovered() only: Return True even if the item is disabled
    NoNavOverride = 1 << 10                # Disable using gamepad/keyboard navigation state when active, always query mouse.
    RectOnly = Literal[ImGuiHoveredFlags_.AllowWhenBlockedByPopup] | Literal[ImGuiHoveredFlags_.AllowWhenBlockedByActiveItem] | Literal[ImGuiHoveredFlags_.AllowWhenOverlapped]
    RootAndChildWindows = Literal[ImGuiHoveredFlags_.RootWindow] | Literal[ImGuiHoveredFlags_.ChildWindows]

class ImGuiDragDropFlags_(Enum):    # imgui.h:1287
    """ Flags for ImGui::BeginDragDropSource(), ImGui::AcceptDragDropPayload()"""
    None_ = 0
    # BeginDragDropSource() flags
    SourceNoPreviewTooltip = 1 << 0                                                                                            # By default, a successful call to BeginDragDropSource opens a tooltip so you can display a preview or description of the source contents. This flag disable this behavior.
    SourceNoDisableHover = 1 << 1                                                                                              # By default, when dragging we clear data so that IsItemHovered() will return False, to avoid subsequent user code submitting tooltips. This flag disable this behavior so you can still call IsItemHovered() on the source item.
    SourceNoHoldToOpenOthers = 1 << 2                                                                                          # Disable the behavior that allows to open tree nodes and collapsing header by holding over them while dragging a source item.
    SourceAllowNullID = 1 << 3                                                                                                 # Allow items such as Text(), Image() that have no unique identifier to be used as drag source, by manufacturing a temporary identifier based on their window-relative position. This is extremely unusual within the dear imgui ecosystem and so we made it explicit.
    SourceExtern = 1 << 4                                                                                                      # External source (from outside of dear imgui), won't attempt to read current item/window info. Will always return True. Only one Extern source can be active simultaneously.
    SourceAutoExpirePayload = 1 << 5                                                                                           # Automatically expire the payload if the source cease to be submitted (otherwise payloads are persisting while being dragged)
    # AcceptDragDropPayload() flags
    AcceptBeforeDelivery = 1 << 10                                                                                             # AcceptDragDropPayload() will returns True even before the mouse button is released. You can then call IsDelivery() to test if the payload needs to be delivered.
    AcceptNoDrawDefaultRect = 1 << 11                                                                                          # Do not draw the default highlight rectangle when hovering over target.
    AcceptNoPreviewTooltip = 1 << 12                                                                                           # Request hiding the BeginDragDropSource tooltip from the BeginDragDropTarget site.
    AcceptPeekOnly = Literal[ImGuiDragDropFlags_.AcceptBeforeDelivery] | Literal[ImGuiDragDropFlags_.AcceptNoDrawDefaultRect]  # For peeking ahead and inspecting the payload before delivery.

# Standard Drag and Drop payload types. You can define you own payload types using short strings. Types starting with '_' are defined by Dear ImGui.

class ImGuiDataType_(Enum):    # imgui.h:1309
    """ A primary data type"""
    S8 = 0      # signed char / char (with sensible compilers)
    U8 = 1      # unsigned char
    S16 = 2     # short
    U16 = 3     # unsigned short
    S32 = 4     # int
    U32 = 5     # unsigned int
    S64 = 6     # long long / __int64
    U64 = 7     # unsigned long long / unsigned __int64
    Float = 8   # float
    Double = 9  # double
    COUNT = 10

class ImGuiDir_(Enum):    # imgui.h:1325
    """ A cardinal direction"""
    None_ = -1
    Left = 0
    Right = 1
    Up = 2
    Down = 3
    COUNT = 4

class ImGuiSortDirection_(Enum):    # imgui.h:1336
    """ A sorting direction"""
    None_ = 0
    Ascending = 1   # Ascending = 0->9, A->Z etc.
    Descending = 2  # Descending = 9->0, Z->A etc.

class ImGuiKey_(Enum):    # imgui.h:1345
    """ Keys value 0 to 511 are left unused as legacy native/opaque key values (< 1.87)
     Keys value >= 512 are named keys (>= 1.87)
    """
    # Keyboard
    None_ = 0
    Tab = 512                 # == ImGuiKey_NamedKey_BEGIN
    LeftArrow = 513
    RightArrow = 514
    UpArrow = 515
    DownArrow = 516
    PageUp = 517
    PageDown = 518
    Home = 519
    End = 520
    Insert = 521
    Delete = 522
    Backspace = 523
    Space = 524
    Enter = 525
    Escape = 526
    LeftCtrl = 527
    LeftShift = 528
    LeftAlt = 529
    LeftSuper = 530
    RightCtrl = 531
    RightShift = 532
    RightAlt = 533
    RightSuper = 534
    Menu = 535
    _0 = 536
    _1 = 537
    _2 = 538
    _3 = 539
    _4 = 540
    _5 = 541
    _6 = 542
    _7 = 543
    _8 = 544
    _9 = 545
    A = 546
    B = 547
    C = 548
    D = 549
    E = 550
    F = 551
    G = 552
    H = 553
    I = 554
    J = 555
    K = 556
    L = 557
    M = 558
    N = 559
    O = 560
    P = 561
    Q = 562
    R = 563
    S = 564
    T = 565
    U = 566
    V = 567
    W = 568
    X = 569
    Y = 570
    Z = 571
    F1 = 572
    F2 = 573
    F3 = 574
    F4 = 575
    F5 = 576
    F6 = 577
    F7 = 578
    F8 = 579
    F9 = 580
    F10 = 581
    F11 = 582
    F12 = 583
    Apostrophe = 584          # '
    Comma = 585               # ,
    Minus = 586               # -
    Period = 587              # .
    Slash = 588               # /
    Semicolon = 589           # ;
    Equal = 590               # =
    LeftBracket = 591         # [
    Backslash = 592           # \ (this text inhibit multiline comment caused by backslash)
    RightBracket = 593        # ]
    GraveAccent = 594         # `
    CapsLock = 595
    ScrollLock = 596
    NumLock = 597
    PrintScreen = 598
    Pause = 599
    Keypad0 = 600
    Keypad1 = 601
    Keypad2 = 602
    Keypad3 = 603
    Keypad4 = 604
    Keypad5 = 605
    Keypad6 = 606
    Keypad7 = 607
    Keypad8 = 608
    Keypad9 = 609
    KeypadDecimal = 610
    KeypadDivide = 611
    KeypadMultiply = 612
    KeypadSubtract = 613
    KeypadAdd = 614
    KeypadEnter = 615
    KeypadEqual = 616

    # Gamepad (some of those are analog values, 0.0 to 1.0)                              // NAVIGATION action
    GamepadStart = 617        # Menu (Xbox)          + (Switch)   Start/Options (PS) // --
    GamepadBack = 618         # View (Xbox)          - (Switch)   Share (PS)         // --
    GamepadFaceUp = 619       # Y (Xbox)             X (Switch)   Triangle (PS)      // -> ImGuiNavInput_Input
    GamepadFaceDown = 620     # A (Xbox)             B (Switch)   Cross (PS)         // -> ImGuiNavInput_Activate
    GamepadFaceLeft = 621     # X (Xbox)             Y (Switch)   Square (PS)        // -> ImGuiNavInput_Menu
    GamepadFaceRight = 622    # B (Xbox)             A (Switch)   Circle (PS)        // -> ImGuiNavInput_Cancel
    GamepadDpadUp = 623       # D-pad Up                                             // -> ImGuiNavInput_DpadUp
    GamepadDpadDown = 624     # D-pad Down                                           // -> ImGuiNavInput_DpadDown
    GamepadDpadLeft = 625     # D-pad Left                                           // -> ImGuiNavInput_DpadLeft
    GamepadDpadRight = 626    # D-pad Right                                          // -> ImGuiNavInput_DpadRight
    GamepadL1 = 627           # L Bumper (Xbox)      L (Switch)   L1 (PS)            // -> ImGuiNavInput_FocusPrev + ImGuiNavInput_TweakSlow
    GamepadR1 = 628           # R Bumper (Xbox)      R (Switch)   R1 (PS)            // -> ImGuiNavInput_FocusNext + ImGuiNavInput_TweakFast
    GamepadL2 = 629           # L Trigger (Xbox)     ZL (Switch)  L2 (PS) [Analog]
    GamepadR2 = 630           # R Trigger (Xbox)     ZR (Switch)  R2 (PS) [Analog]
    GamepadL3 = 631           # L Thumbstick (Xbox)  L3 (Switch)  L3 (PS)
    GamepadR3 = 632           # R Thumbstick (Xbox)  R3 (Switch)  R3 (PS)
    GamepadLStickUp = 633     # [Analog]                                             // -> ImGuiNavInput_LStickUp
    GamepadLStickDown = 634   # [Analog]                                             // -> ImGuiNavInput_LStickDown
    GamepadLStickLeft = 635   # [Analog]                                             // -> ImGuiNavInput_LStickLeft
    GamepadLStickRight = 636  # [Analog]                                             // -> ImGuiNavInput_LStickRight
    GamepadRStickUp = 637     # [Analog]
    GamepadRStickDown = 638   # [Analog]
    GamepadRStickLeft = 639   # [Analog]
    GamepadRStickRight = 640  # [Analog]

    # Keyboard Modifiers (explicitly submitted by backend via AddKeyEvent() calls)
    # - This is mirroring the data also written to io.KeyCtrl, io.KeyShift, io.KeyAlt, io.KeySuper, in a format allowing
    #   them to be accessed via standard key API, allowing calls such as IsKeyPressed(), IsKeyReleased(), querying duration etc.
    # - Code polling every keys (e.g. an interface to detect a key press for input mapping) might want to ignore those
    #   and prefer using the real keys (e.g. ImGuiKey_LeftCtrl, ImGuiKey_RightCtrl instead of ImGuiKey_ModCtrl).
    # - In theory the value of keyboard modifiers should be roughly equivalent to a logical or of the equivalent left/right keys.
    #   In practice: it's complicated; mods are often provided from different sources. Keyboard layout, IME, sticky keys and
    #   backends tend to interfere and break that equivalence. The safer decision is to relay that ambiguity down to the end-user...
    ModCtrl = 641
    ModShift = 642
    ModAlt = 643
    ModSuper = 644

    # End of list
    COUNT = 645               # No valid ImGuiKey is ever greater than this value

    # [Internal] Prior to 1.87 we required user to fill io.KeysDown[512] using their own native index + a io.KeyMap[] array.
    # We are ditching this method but keeping a legacy path for user code doing e.g. IsKeyPressed(MY_NATIVE_KEY_CODE)
    NamedKey_BEGIN = 512
    NamedKey_END = Literal[ImGuiKey_.COUNT]
    NamedKey_COUNT = Literal[ImGuiKey_.NamedKey_END] - Literal[ImGuiKey_.NamedKey_BEGIN]


class ImGuiModFlags_(Enum):    # imgui.h:1457
    """ Helper "flags" version of key-mods to store and compare multiple key-mods easily. Sometimes used for storage (e.g. io.KeyMods) but otherwise not much used in public API."""
    None_ = 0
    Ctrl = 1 << 0
    Shift = 1 << 1
    Alt = 1 << 2    # Menu
    Super = 1 << 3  # Cmd/Super/Windows key

class ImGuiNavInput_(Enum):    # imgui.h:1471
    """ Gamepad/Keyboard navigation
     Since >= 1.87 backends you generally don't need to care about this enum since io.NavInputs[] is setup automatically. This might become private/internal some day.
     Keyboard: Set io.ConfigFlags |= ImGuiConfigFlags_NavEnableKeyboard to enable. NewFrame() will automatically fill io.NavInputs[] based on your io.AddKeyEvent() calls.
     Gamepad:  Set io.ConfigFlags |= ImGuiConfigFlags_NavEnableGamepad to enable. Backend: set ImGuiBackendFlags_HasGamepad and fill the io.NavInputs[] fields before calling NewFrame(). Note that io.NavInputs[] is cleared by EndFrame().
     Read instructions in imgui.cpp for more details. Download PNG/PSD at http://dearimgui.org/controls_sheets.
    """
    # Gamepad Mapping
    Activate = 0    # Activate / Open / Toggle / Tweak value       // e.g. Cross  (PS4), A (Xbox), A (Switch), Space (Keyboard)
    Cancel = 1      # Cancel / Close / Exit                        // e.g. Circle (PS4), B (Xbox), B (Switch), Escape (Keyboard)
    Input = 2       # Text input / On-Screen keyboard              // e.g. Triang.(PS4), Y (Xbox), X (Switch), Return (Keyboard)
    Menu = 3        # Tap: Toggle menu / Hold: Focus, Move, Resize // e.g. Square (PS4), X (Xbox), Y (Switch), Alt (Keyboard)
    DpadLeft = 4    # Move / Tweak / Resize window (w/ PadMenu)    // e.g. D-pad Left/Right/Up/Down (Gamepads), Arrow keys (Keyboard)
    DpadRight = 5
    DpadUp = 6
    DpadDown = 7
    LStickLeft = 8  # Scroll / Move window (w/ PadMenu)            // e.g. Left Analog Stick Left/Right/Up/Down
    LStickRight = 9
    LStickUp = 10
    LStickDown = 11
    FocusPrev = 12  # Focus Next window (w/ PadMenu)               // e.g. L1 or L2 (PS4), LB or LT (Xbox), L or ZL (Switch)
    FocusNext = 13  # Focus Prev window (w/ PadMenu)               // e.g. R1 or R2 (PS4), RB or RT (Xbox), R or ZL (Switch)
    TweakSlow = 14  # Slower tweaks                                // e.g. L1 or L2 (PS4), LB or LT (Xbox), L or ZL (Switch)
    TweakFast = 15  # Faster tweaks                                // e.g. R1 or R2 (PS4), RB or RT (Xbox), R or ZL (Switch)

    # [Internal] Don't use directly! This is used internally to differentiate keyboard from gamepad inputs for behaviors that require to differentiate them.
    # Keyboard behavior that have no corresponding gamepad mapping (e.g. CTRL+TAB) will be directly reading from keyboard keys instead of io.NavInputs[].
    KeyLeft_ = 16   # Move left                                    // = Arrow keys
    KeyRight_ = 17  # Move right
    KeyUp_ = 18     # Move up
    KeyDown_ = 19   # Move down
    COUNT = 20

class ImGuiConfigFlags_(Enum):    # imgui.h:1501
    """ Configuration flags stored in io.ConfigFlags. Set by user/application."""
    None_ = 0
    NavEnableKeyboard = 1 << 0     # Master keyboard navigation enable flag. NewFrame() will automatically fill io.NavInputs[] based on io.AddKeyEvent() calls
    NavEnableGamepad = 1 << 1      # Master gamepad navigation enable flag. This is mostly to instruct your imgui backend to fill io.NavInputs[]. Backend also needs to set ImGuiBackendFlags_HasGamepad.
    NavEnableSetMousePos = 1 << 2  # Instruct navigation to move the mouse cursor. May be useful on TV/console systems where moving a virtual mouse is awkward. Will update io.MousePos and set io.WantSetMousePos=True. If enabled you MUST honor io.WantSetMousePos requests in your backend, otherwise ImGui will react as if the mouse is jumping around back and forth.
    NavNoCaptureKeyboard = 1 << 3  # Instruct navigation to not set the io.WantCaptureKeyboard flag when io.NavActive is set.
    NoMouse = 1 << 4               # Instruct imgui to clear mouse position/buttons in NewFrame(). This allows ignoring the mouse information set by the backend.
    NoMouseCursorChange = 1 << 5   # Instruct backend to not alter mouse cursor shape and visibility. Use if the backend cursor changes are interfering with yours and you don't want to use SetMouseCursor() to change mouse cursor. You may want to honor requests from imgui by reading GetMouseCursor() yourself instead.

    # User storage (to allow your backend/engine to communicate to code that may be shared between multiple projects. Those flags are NOT used by core Dear ImGui)
    IsSRGB = 1 << 20               # Application is SRGB-aware.
    IsTouchScreen = 1 << 21        # Application is using a touch screen instead of a mouse.

class ImGuiBackendFlags_(Enum):    # imgui.h:1517
    """ Backend capabilities flags stored in io.BackendFlags. Set by imgui_impl_xxx or custom backend."""
    None_ = 0
    HasGamepad = 1 << 0            # Backend Platform supports gamepad and currently has one connected.
    HasMouseCursors = 1 << 1       # Backend Platform supports honoring GetMouseCursor() value to change the OS cursor shape.
    HasSetMousePos = 1 << 2        # Backend Platform supports io.WantSetMousePos requests to reposition the OS mouse position (only used if ImGuiConfigFlags_NavEnableSetMousePos is set).
    RendererHasVtxOffset = 1 << 3  # Backend Renderer supports ImDrawCmd::VtxOffset. This enables output of large meshes (64K+ vertices) while still using 16-bit indices.

class ImGuiCol_(Enum):    # imgui.h:1527
    """ Enumeration for PushStyleColor() / PopStyleColor()"""
    Text = 0
    TextDisabled = 1
    WindowBg = 2                # Background of normal windows
    ChildBg = 3                 # Background of child windows
    PopupBg = 4                 # Background of popups, menus, tooltips windows
    Border = 5
    BorderShadow = 6
    FrameBg = 7                 # Background of checkbox, radio button, plot, slider, text input
    FrameBgHovered = 8
    FrameBgActive = 9
    TitleBg = 10
    TitleBgActive = 11
    TitleBgCollapsed = 12
    MenuBarBg = 13
    ScrollbarBg = 14
    ScrollbarGrab = 15
    ScrollbarGrabHovered = 16
    ScrollbarGrabActive = 17
    CheckMark = 18
    SliderGrab = 19
    SliderGrabActive = 20
    Button = 21
    ButtonHovered = 22
    ButtonActive = 23
    Header = 24                 # Header* colors are used for CollapsingHeader, TreeNode, Selectable, MenuItem
    HeaderHovered = 25
    HeaderActive = 26
    Separator = 27
    SeparatorHovered = 28
    SeparatorActive = 29
    ResizeGrip = 30             # Resize grip in lower-right and lower-left corners of windows.
    ResizeGripHovered = 31
    ResizeGripActive = 32
    Tab = 33                    # TabItem in a TabBar
    TabHovered = 34
    TabActive = 35
    TabUnfocused = 36
    TabUnfocusedActive = 37
    PlotLines = 38
    PlotLinesHovered = 39
    PlotHistogram = 40
    PlotHistogramHovered = 41
    TableHeaderBg = 42          # Table header background
    TableBorderStrong = 43      # Table outer and header borders (prefer using Alpha=1.0 here)
    TableBorderLight = 44       # Table inner borders (prefer using Alpha=1.0 here)
    TableRowBg = 45             # Table row background (even rows)
    TableRowBgAlt = 46          # Table row background (odd rows)
    TextSelectedBg = 47
    DragDropTarget = 48         # Rectangle highlighting a drop target
    NavHighlight = 49           # Gamepad/keyboard: current highlighted item
    NavWindowingHighlight = 50  # Highlight window when using CTRL+TAB
    NavWindowingDimBg = 51      # Darken/colorize entire screen behind the CTRL+TAB window list, when active
    ModalWindowDimBg = 52       # Darken/colorize entire screen behind a modal window, when one is active
    COUNT = 53

class ImGuiStyleVar_(Enum):    # imgui.h:1592
    """ Enumeration for PushStyleVar() / PopStyleVar() to temporarily modify the ImGuiStyle structure.
     - The enum only refers to fields of ImGuiStyle which makes sense to be pushed/popped inside UI code.
       During initialization or between frames, feel free to just poke into ImGuiStyle directly.
     - Tip: Use your programming IDE navigation facilities on the names in the _second column_ below to find the actual members and their description.
       In Visual Studio IDE: CTRL+comma ("Edit.GoToAll") can follow symbols in comments, whereas CTRL+F12 ("Edit.GoToImplementation") cannot.
       With Visual Assist installed: ALT+G ("VAssistX.GoToImplementation") can also follow symbols in comments.
     - When changing this enum, you need to update the associated internal table GStyleVarInfo[] accordingly. This is where we link enum values to members offset/type.
    """
    # Enum name --------------------- // Member in ImGuiStyle structure (see ImGuiStyle for descriptions)
    Alpha = 0                 # float     Alpha
    DisabledAlpha = 1         # float     DisabledAlpha
    WindowPadding = 2         # ImVec2    WindowPadding
    WindowRounding = 3        # float     WindowRounding
    WindowBorderSize = 4      # float     WindowBorderSize
    WindowMinSize = 5         # ImVec2    WindowMinSize
    WindowTitleAlign = 6      # ImVec2    WindowTitleAlign
    ChildRounding = 7         # float     ChildRounding
    ChildBorderSize = 8       # float     ChildBorderSize
    PopupRounding = 9         # float     PopupRounding
    PopupBorderSize = 10      # float     PopupBorderSize
    FramePadding = 11         # ImVec2    FramePadding
    FrameRounding = 12        # float     FrameRounding
    FrameBorderSize = 13      # float     FrameBorderSize
    ItemSpacing = 14          # ImVec2    ItemSpacing
    ItemInnerSpacing = 15     # ImVec2    ItemInnerSpacing
    IndentSpacing = 16        # float     IndentSpacing
    CellPadding = 17          # ImVec2    CellPadding
    ScrollbarSize = 18        # float     ScrollbarSize
    ScrollbarRounding = 19    # float     ScrollbarRounding
    GrabMinSize = 20          # float     GrabMinSize
    GrabRounding = 21         # float     GrabRounding
    TabRounding = 22          # float     TabRounding
    ButtonTextAlign = 23      # ImVec2    ButtonTextAlign
    SelectableTextAlign = 24  # ImVec2    SelectableTextAlign
    COUNT = 25

class ImGuiButtonFlags_(Enum):    # imgui.h:1624
    """ Flags for InvisibleButton() [extended in imgui_internal.h]"""
    None_ = 0
    MouseButtonLeft = 1 << 0    # React on left mouse button (default)
    MouseButtonRight = 1 << 1   # React on right mouse button
    MouseButtonMiddle = 1 << 2  # React on center mouse button

    # [Internal]
    MouseButtonMask_ = Literal[ImGuiButtonFlags_.MouseButtonLeft] | Literal[ImGuiButtonFlags_.MouseButtonRight] | Literal[ImGuiButtonFlags_.MouseButtonMiddle]
    MouseButtonDefault_ = Literal[ImGuiButtonFlags_.MouseButtonLeft]

class ImGuiColorEditFlags_(Enum):    # imgui.h:1637
    """ Flags for ColorEdit3() / ColorEdit4() / ColorPicker3() / ColorPicker4() / ColorButton()"""
    None_ = 0
    NoAlpha = 1 << 1            #              // ColorEdit, ColorPicker, ColorButton: ignore Alpha component (will only read 3 components from the input pointer).
    NoPicker = 1 << 2           #              // ColorEdit: disable picker when clicking on color square.
    NoOptions = 1 << 3          #              // ColorEdit: disable toggling options menu when right-clicking on inputs/small preview.
    NoSmallPreview = 1 << 4     #              // ColorEdit, ColorPicker: disable color square preview next to the inputs. (e.g. to show only the inputs)
    NoInputs = 1 << 5           #              // ColorEdit, ColorPicker: disable inputs sliders/text widgets (e.g. to show only the small preview color square).
    NoTooltip = 1 << 6          #              // ColorEdit, ColorPicker, ColorButton: disable tooltip when hovering the preview.
    NoLabel = 1 << 7            #              // ColorEdit, ColorPicker: disable display of inline text label (the label is still forwarded to the tooltip and picker).
    NoSidePreview = 1 << 8      #              // ColorPicker: disable bigger color preview on right side of the picker, use small color square preview instead.
    NoDragDrop = 1 << 9         #              // ColorEdit: disable drag and drop target. ColorButton: disable drag and drop source.
    NoBorder = 1 << 10          #              // ColorButton: disable border (which is enforced by default)

    # User Options (right-click on widget to change some of them).
    AlphaBar = 1 << 16          #              // ColorEdit, ColorPicker: show vertical alpha bar/gradient in picker.
    AlphaPreview = 1 << 17      #              // ColorEdit, ColorPicker, ColorButton: display preview as a transparent color over a checkerboard, instead of opaque.
    AlphaPreviewHalf = 1 << 18  #              // ColorEdit, ColorPicker, ColorButton: display half opaque / half checkerboard, instead of opaque.
    HDR = 1 << 19               #              // (WIP) ColorEdit: Currently only disable 0.0..1.0 limits in RGBA edition (note: you probably want to use ImGuiColorEditFlags_Float flag as well).
    DisplayRGB = 1 << 20        # [Display]    // ColorEdit: override _display_ type among RGB/HSV/Hex. ColorPicker: select any combination using one or more of RGB/HSV/Hex.
    DisplayHSV = 1 << 21        # [Display]    // "
    DisplayHex = 1 << 22        # [Display]    // "
    Uint8 = 1 << 23             # [DataType]   // ColorEdit, ColorPicker, ColorButton: _display_ values formatted as 0..255.
    Float = 1 << 24             # [DataType]   // ColorEdit, ColorPicker, ColorButton: _display_ values formatted as 0.0..1.0 floats instead of 0..255 integers. No round-trip of value via integers.
    PickerHueBar = 1 << 25      # [Picker]     // ColorPicker: bar for Hue, rectangle for Sat/Value.
    PickerHueWheel = 1 << 26    # [Picker]     // ColorPicker: wheel for Hue, triangle for Sat/Value.
    InputRGB = 1 << 27          # [Input]      // ColorEdit, ColorPicker: input and output data in RGB format.
    InputHSV = 1 << 28          # [Input]      // ColorEdit, ColorPicker: input and output data in HSV format.

    # Defaults Options. You can set application defaults using SetColorEditOptions(). The intent is that you probably don't want to
    # override them in most of your calls. Let the user choose via the option menu and/or call SetColorEditOptions() once during startup.
    DefaultOptions_ = Literal[ImGuiColorEditFlags_.Uint8] | Literal[ImGuiColorEditFlags_.DisplayRGB] | Literal[ImGuiColorEditFlags_.InputRGB] | Literal[ImGuiColorEditFlags_.PickerHueBar]

    # [Internal] Masks
    DisplayMask_ = Literal[ImGuiColorEditFlags_.DisplayRGB] | Literal[ImGuiColorEditFlags_.DisplayHSV] | Literal[ImGuiColorEditFlags_.DisplayHex]
    DataTypeMask_ = Literal[ImGuiColorEditFlags_.Uint8] | Literal[ImGuiColorEditFlags_.Float]
    PickerMask_ = Literal[ImGuiColorEditFlags_.PickerHueWheel] | Literal[ImGuiColorEditFlags_.PickerHueBar]
    InputMask_ = Literal[ImGuiColorEditFlags_.InputRGB] | Literal[ImGuiColorEditFlags_.InputHSV]

    # Obsolete names (will be removed)
    # ImGuiColorEditFlags_RGB = ImGuiColorEditFlags_DisplayRGB, ImGuiColorEditFlags_HSV = ImGuiColorEditFlags_DisplayHSV, ImGuiColorEditFlags_HEX = ImGuiColorEditFlags_DisplayHex  // [renamed in 1.69]

class ImGuiSliderFlags_(Enum):    # imgui.h:1682
    """ Flags for DragFloat(), DragInt(), SliderFloat(), SliderInt() etc.
     We use the same sets of flags for DragXXX() and SliderXXX() functions as the features are the same and it makes it easier to swap them.
    """
    None_ = 0
    AlwaysClamp = 1 << 4      # Clamp value to min/max bounds when input manually with CTRL+Click. By default CTRL+Click allows going out of bounds.
    Logarithmic = 1 << 5      # Make the widget logarithmic (linear otherwise). Consider using ImGuiSliderFlags_NoRoundToFormat with this if using a format-string with small amount of digits.
    NoRoundToFormat = 1 << 6  # Disable rounding underlying value to match precision of the display format string (e.g. %.3 values are rounded to those 3 digits)
    NoInput = 1 << 7          # Disable CTRL+Click or Enter key allowing to input text directly into the widget
    InvalidMask_ = 0x7000000F
    # [Internal] We treat using those bits as being potentially a 'float power' argument from the previous API that has got miscast to this enum, and will trigger an assert if needed.

    # Obsolete names (will be removed)

class ImGuiMouseButton_(Enum):    # imgui.h:1699
    """ Identify a mouse button.
     Those values are guaranteed to be stable and we frequently use 0/1 directly. Named enums provided for convenience.
    """
    Left = 0
    Right = 1
    Middle = 2
    COUNT = 5

class ImGuiMouseCursor_(Enum):    # imgui.h:1709
    """ Enumeration for GetMouseCursor()
     User code may request backend to display given cursor by calling SetMouseCursor(), which is why we have some cursors that are marked unused here
    """
    None_ = -1
    Arrow = 0
    TextInput = 1   # When hovering over InputText, etc.
    ResizeAll = 2   # (Unused by Dear ImGui functions)
    ResizeNS = 3    # When hovering over an horizontal border
    ResizeEW = 4    # When hovering over a vertical border or a column
    ResizeNESW = 5  # When hovering over the bottom-left corner of a window
    ResizeNWSE = 6  # When hovering over the bottom-right corner of a window
    Hand = 7        # (Unused by Dear ImGui functions. Use for e.g. hyperlinks)
    NotAllowed = 8  # When hovering something with disallowed interaction. Usually a crossed circle.
    COUNT = 9

class ImGuiCond_(Enum):    # imgui.h:1727
    """ Enumeration for ImGui::SetWindow***(), SetNextWindow***(), SetNextItem***() functions
     Represent a condition.
     Important: Treat as a regular enum! Do NOT combine multiple values using binary operators! All the functions above treat 0 as a shortcut to ImGuiCond_Always.
    """
    None_ = 0              # No condition (always set the variable), same as _Always
    Always = 1 << 0        # No condition (always set the variable)
    Once = 1 << 1          # Set the variable once per runtime session (only the first call will succeed)
    FirstUseEver = 1 << 2  # Set the variable if the object/window has no persistently saved data (no entry in .ini file)
    Appearing = 1 << 3     # Set the variable if the object/window is appearing after being hidden/inactive (or the first time)

#-----------------------------------------------------------------------------
# [SECTION] Helpers: Memory allocations macros, ImVector<>
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# IM_MALLOC(), IM_FREE(), IM_NEW(), IM_PLACEMENT_NEW(), IM_DELETE()
# We call C++ constructor on own allocated memory via the placement "new(ptr) Type()" syntax.
# Defining a custom placement new() with a custom parameter allows us to bypass including <new> which on some platforms complains when user has disabled exceptions.
#-----------------------------------------------------------------------------

class ImNewWrapper:    # imgui.h:1746
    pass
# This is only required so we can use the symmetrical new()

#-----------------------------------------------------------------------------
# ImVector<>
# Lightweight std::vector<>-like class to avoid dragging dependencies (also, some implementations of STL with debug enabled are absurdly slow, we bypass it so our code runs fast in debug).
#-----------------------------------------------------------------------------
# - You generally do NOT need to care or use this ever. But we need to make it available in imgui.h because some of our public structures are relying on it.
# - We use std-like naming convention here, which is a little unusual for this codebase.
# - Important: clear() frees memory, resize(0) keep the allocated buffer. We use resize(0) a lot to intentionally recycle allocated buffers across frames and amortize our costs.
# - Important: our implementation does NOT call C++ constructors/destructors, we treat everything as raw data! This is intentional but be extra mindful of that,
#   Do NOT use this class as a std::vector replacement in your own code! Many of the structures used by dear imgui can be safely initialized by a zero-memset.
#-----------------------------------------------------------------------------


#-----------------------------------------------------------------------------
# [SECTION] ImGuiStyle
#-----------------------------------------------------------------------------
# You may modify the ImGui::GetStyle() main instance during initialization and before NewFrame().
# During the frame, use ImGui::PushStyleVar(ImGuiStyleVar_XXXX)/PopStyleVar() to alter the main style values,
# and ImGui::PushStyleColor(ImGuiCol_XXX)/PopStyleColor() for colors.
#-----------------------------------------------------------------------------

class ImGuiStyle:    # imgui.h:1838
    Alpha:float                                              # Global alpha applies to everything in Dear ImGui.    # imgui.h:1840
    DisabledAlpha:float                                      # Additional alpha multiplier applied by BeginDisabled(). Multiply over current value of Alpha.    # imgui.h:1841
    WindowPadding:ImVec2                                     # Padding within a window.    # imgui.h:1842
    WindowRounding:float                                     # Radius of window corners rounding. Set to 0.0 to have rectangular windows. Large values tend to lead to variety of artifacts and are not recommended.    # imgui.h:1843
    WindowBorderSize:float                                   # Thickness of border around windows. Generally set to 0.0 or 1.0. (Other values are not well tested and more CPU/GPU costly).    # imgui.h:1844
    WindowMinSize:ImVec2                                     # Minimum window size. This is a global setting. If you want to constraint individual windows, use SetNextWindowSizeConstraints().    # imgui.h:1845
    WindowTitleAlign:ImVec2                                  # Alignment for title bar text. Defaults to (0.0,0.5) for left-aligned,vertically centered.    # imgui.h:1846
    WindowMenuButtonPosition:ImGuiDir                        # Side of the collapsing/docking button in the title bar (None/Left/Right). Defaults to ImGuiDir_Left.    # imgui.h:1847
    ChildRounding:float                                      # Radius of child window corners rounding. Set to 0.0 to have rectangular windows.    # imgui.h:1848
    ChildBorderSize:float                                    # Thickness of border around child windows. Generally set to 0.0 or 1.0. (Other values are not well tested and more CPU/GPU costly).    # imgui.h:1849
    PopupRounding:float                                      # Radius of popup window corners rounding. (Note that tooltip windows use WindowRounding)    # imgui.h:1850
    PopupBorderSize:float                                    # Thickness of border around popup/tooltip windows. Generally set to 0.0 or 1.0. (Other values are not well tested and more CPU/GPU costly).    # imgui.h:1851
    FramePadding:ImVec2                                      # Padding within a framed rectangle (used by most widgets).    # imgui.h:1852
    FrameRounding:float                                      # Radius of frame corners rounding. Set to 0.0 to have rectangular frame (used by most widgets).    # imgui.h:1853
    FrameBorderSize:float                                    # Thickness of border around frames. Generally set to 0.0 or 1.0. (Other values are not well tested and more CPU/GPU costly).    # imgui.h:1854
    ItemSpacing:ImVec2                                       # Horizontal and vertical spacing between widgets/lines.    # imgui.h:1855
    ItemInnerSpacing:ImVec2                                  # Horizontal and vertical spacing between within elements of a composed widget (e.g. a slider and its label).    # imgui.h:1856
    CellPadding:ImVec2                                       # Padding within a table cell    # imgui.h:1857
    TouchExtraPadding:ImVec2                                 # Expand reactive bounding box for touch-based system where touch position is not accurate enough. Unfortunately we don't sort widgets so priority on overlap will always be given to the first widget. So don't grow this too much!    # imgui.h:1858
    IndentSpacing:float                                      # Horizontal indentation when e.g. entering a tree node. Generally == (FontSize + FramePadding.x*2).    # imgui.h:1859
    ColumnsMinSpacing:float                                  # Minimum horizontal spacing between two columns. Preferably > (FramePadding.x + 1).    # imgui.h:1860
    ScrollbarSize:float                                      # Width of the vertical scrollbar, Height of the horizontal scrollbar.    # imgui.h:1861
    ScrollbarRounding:float                                  # Radius of grab corners for scrollbar.    # imgui.h:1862
    GrabMinSize:float                                        # Minimum width/height of a grab box for slider/scrollbar.    # imgui.h:1863
    GrabRounding:float                                       # Radius of grabs corners rounding. Set to 0.0 to have rectangular slider grabs.    # imgui.h:1864
    LogSliderDeadzone:float                                  # The size in pixels of the dead-zone around zero on logarithmic sliders that cross zero.    # imgui.h:1865
    TabRounding:float                                        # Radius of upper corners of a tab. Set to 0.0 to have rectangular tabs.    # imgui.h:1866
    TabBorderSize:float                                      # Thickness of border around tabs.    # imgui.h:1867
    TabMinWidthForCloseButton:float                          # Minimum width for close button to appears on an unselected tab when hovered. Set to 0.0 to always show when hovering, set to FLT_MAX to never show close button unless selected.    # imgui.h:1868
    ColorButtonPosition:ImGuiDir                             # Side of the color button in the ColorEdit4 widget (left/right). Defaults to ImGuiDir_Right.    # imgui.h:1869
    ButtonTextAlign:ImVec2                                   # Alignment of button text when button is larger than text. Defaults to (0.5, 0.5) (centered).    # imgui.h:1870
    SelectableTextAlign:ImVec2                               # Alignment of selectable text. Defaults to (0.0, 0.0) (top-left aligned). It's generally important to keep this left-aligned if you want to lay multiple items on a same line.    # imgui.h:1871
    DisplayWindowPadding:ImVec2                              # Window position are clamped to be visible within the display area or monitors by at least this amount. Only applies to regular windows.    # imgui.h:1872
    DisplaySafeAreaPadding:ImVec2                            # If you cannot see the edges of your screen (e.g. on a TV) increase the safe area padding. Apply to popups/tooltips as well regular windows. NB: Prefer configuring your TV sets correctly!    # imgui.h:1873
    MouseCursorScale:float                                   # Scale software rendered mouse cursor (when io.MouseDrawCursor is enabled). May be removed later.    # imgui.h:1874
    AntiAliasedLines:bool                                    # Enable anti-aliased lines/borders. Disable if you are really tight on CPU/GPU. Latched at the beginning of the frame (copied to ImDrawList).    # imgui.h:1875
    AntiAliasedLinesUseTex:bool                              # Enable anti-aliased lines/borders using textures where possible. Require backend to render with bilinear filtering (NOT point/nearest filtering). Latched at the beginning of the frame (copied to ImDrawList).    # imgui.h:1876
    AntiAliasedFill:bool                                     # Enable anti-aliased edges around filled shapes (rounded rectangles, circles, etc.). Disable if you are really tight on CPU/GPU. Latched at the beginning of the frame (copied to ImDrawList).    # imgui.h:1877
    CurveTessellationTol:float                               # Tessellation tolerance when using PathBezierCurveTo() without a specific number of segments. Decrease for highly tessellated curves (higher quality, more polygons), increase to reduce quality.    # imgui.h:1878
    CircleTessellationMaxError:float                         # Maximum error (in pixels) allowed when using AddCircle()/AddCircleFilled() or drawing rounded corner rectangles with no explicit segment count specified. Decrease for higher quality but more geometry.    # imgui.h:1879

    def __init__(self) -> None:                              # imgui.h:1882
        pass
    def ScaleAllSizes(self, scale_factor: float) -> None:    # imgui.h:1883
        pass

#-----------------------------------------------------------------------------
# [SECTION] ImGuiIO
#-----------------------------------------------------------------------------
# Communicate most settings and inputs/outputs to Dear ImGui using this structure.
# Access via ImGui::GetIO(). Read 'Programmer guide' section in .cpp file for general usage.
#-----------------------------------------------------------------------------

class ImGuiKeyData:    # imgui.h:1895
    """ [Internal] Storage used by IsKeyDown(), IsKeyPressed() etc functions.
     If prior to 1.87 you used io.KeysDownDuration[] (which was marked as internal), you should use GetKeyData(key)->DownDuration and not io.KeysData[key]->DownDuration.
    """
    Down:bool               # True for if key is down    # imgui.h:1897
    DownDuration:float      # Duration the key has been down (<0.0: not pressed, 0.0: just pressed, >0.0: time held)    # imgui.h:1898
    DownDurationPrev:float  # Last frame duration the key has been down    # imgui.h:1899
    AnalogValue:float       # 0.0..1.0 for gamepad values    # imgui.h:1900

class ImGuiIO:    # imgui.h:1903
    #------------------------------------------------------------------
    # Configuration                            // Default value
    #------------------------------------------------------------------

    ConfigFlags:ImGuiConfigFlags                                                                                                         # = 0              // See ImGuiConfigFlags_ enum. Set by user/application. Gamepad/keyboard navigation options, etc.    # imgui.h:1909
    BackendFlags:ImGuiBackendFlags                                                                                                       # = 0              // See ImGuiBackendFlags_ enum. Set by backend (imgui_impl_xxx files or custom backend) to communicate features supported by the backend.    # imgui.h:1910
    DisplaySize:ImVec2                                                                                                                   # <unset>          // Main display size, in pixels (generally == GetMainViewport()->Size). May change every frame.    # imgui.h:1911
    DeltaTime:float                                                                                                                      # = 1.0/60.0     // Time elapsed since last frame, in seconds. May change every frame.    # imgui.h:1912
    IniSavingRate:float                                                                                                                  # = 5.0           // Minimum time between saving positions/sizes to .ini file, in seconds.    # imgui.h:1913
    IniFilename:str                                                                                                                      # = "imgui.ini"    // Path to .ini file (important: default "imgui.ini" is relative to current working dir!). Set None to disable automatic .ini loading/saving or if you want to manually call LoadIniSettingsXXX() / SaveIniSettingsXXX() functions.    # imgui.h:1914
    LogFilename:str                                                                                                                      # = "imgui_log.txt"// Path to .log file (default parameter to ImGui::LogToFile when no file is specified).    # imgui.h:1915
    MouseDoubleClickTime:float                                                                                                           # = 0.30          // Time for a double-click, in seconds.    # imgui.h:1916
    MouseDoubleClickMaxDist:float                                                                                                        # = 6.0           // Distance threshold to stay in to validate a double-click, in pixels.    # imgui.h:1917
    MouseDragThreshold:float                                                                                                             # = 6.0           // Distance threshold before considering we are dragging.    # imgui.h:1918
    KeyRepeatDelay:float                                                                                                                 # = 0.250         // When holding a key/button, time before it starts repeating, in seconds (for buttons in Repeat mode, etc.).    # imgui.h:1919
    KeyRepeatRate:float                                                                                                                  # = 0.050         // When holding a key/button, rate at which it repeats, in seconds.    # imgui.h:1920
    UserData:Any                                                                                                                         # = None           // Store your own data for retrieval by callbacks.    # imgui.h:1921

    Fonts:ImFontAtlas                                                                                                                    # <auto>           // Font atlas: load, rasterize and pack one or more fonts into a single texture.    # imgui.h:1923
    FontGlobalScale:float                                                                                                                # = 1.0           // Global scale all fonts    # imgui.h:1924
    FontAllowUserScaling:bool                                                                                                            # = False          // Allow user scaling text of individual window with CTRL+Wheel.    # imgui.h:1925
    FontDefault:ImFont                                                                                                                   # = None           // Font to use on NewFrame(). Use None to uses Fonts->Fonts[0].    # imgui.h:1926
    DisplayFramebufferScale:ImVec2                                                                                                       # = (1, 1)         // For retina display or other situations where window coordinates are different from framebuffer coordinates. This generally ends up in ImDrawData::FramebufferScale.    # imgui.h:1927

    # Miscellaneous options
    MouseDrawCursor:bool                                                                                                                 # = False          // Request ImGui to draw a mouse cursor for you (if you are on a platform without a mouse cursor). Cannot be easily renamed to 'io.ConfigXXX' because this is frequently used by backend implementations.    # imgui.h:1930
    ConfigMacOSXBehaviors:bool                                                                                                           # = defined(__APPLE__) // OS X style: Text editing cursor movement using Alt instead of Ctrl, Shortcuts using Cmd/Super instead of Ctrl, Line/Text Start and End using Cmd+Arrows instead of Home/End, Double click selects by word instead of selecting whole text, Multi-selection in lists uses Cmd/Super instead of Ctrl.    # imgui.h:1931
    ConfigInputTrickleEventQueue:bool                                                                                                    # = True           // Enable input queue trickling: some types of events submitted during the same frame (e.g. button down + up) will be spread over multiple frames, improving interactions with low framerates.    # imgui.h:1932
    ConfigInputTextCursorBlink:bool                                                                                                      # = True           // Enable blinking cursor (optional as some users consider it to be distracting).    # imgui.h:1933
    ConfigDragClickToInputText:bool                                                                                                      # = False          // [BETA] Enable turning DragXXX widgets into text input with a simple mouse click-release (without moving). Not desirable on devices without a keyboard.    # imgui.h:1934
    ConfigWindowsResizeFromEdges:bool                                                                                                    # = True           // Enable resizing of windows from their edges and from the lower-left corner. This requires (io.BackendFlags & ImGuiBackendFlags_HasMouseCursors) because it needs mouse cursor feedback. (This used to be a per-window ImGuiWindowFlags_ResizeFromAnySide flag)    # imgui.h:1935
    ConfigWindowsMoveFromTitleBarOnly:bool                                                                                               # = False       // Enable allowing to move windows only when clicking on their title bar. Does not apply to windows without a title bar.    # imgui.h:1936
    ConfigMemoryCompactTimer:float                                                                                                       # = 60.0          // Timer (in seconds) to free transient windows/tables memory buffers when unused. Set to -1.0 to disable.    # imgui.h:1937

    #------------------------------------------------------------------
    # Platform Functions
    # (the imgui_impl_xxxx backend files are setting those up for you)
    #------------------------------------------------------------------

    # Optional: Platform/Renderer backend name (informational only! will be displayed in About Window) + User data for backend/wrappers to store their own stuff.
    BackendPlatformName:str                                                                                                              # = None    # imgui.h:1945
    BackendRendererName:str                                                                                                              # = None    # imgui.h:1946
    BackendPlatformUserData:Any                                                                                                          # = None           // User data for platform backend    # imgui.h:1947
    BackendRendererUserData:Any                                                                                                          # = None           // User data for renderer backend    # imgui.h:1948
    BackendLanguageUserData:Any                                                                                                          # = None           // User data for non C++ programming language backend    # imgui.h:1949

    # Optional: Access OS clipboard
    # (default to use native Win32 clipboard on Windows, otherwise uses a private clipboard. Override to access OS clipboard on other architectures)
    ClipboardUserData:Any                                                                                                                # imgui.h:1955


    #------------------------------------------------------------------
    # Input - Call before calling NewFrame()
    #------------------------------------------------------------------

    # Input Functions
    def AddKeyEvent(self, key: ImGuiKey, down: bool) -> None:                                                                            # imgui.h:1971
        """ Queue a new key down/up event. Key should be "translated" (as in, generally ImGuiKey_A matches the key end-user would use to emit an 'A' character)"""
        pass
    def AddKeyAnalogEvent(self, key: ImGuiKey, down: bool, v: float) -> None:                                                            # imgui.h:1972
        """ Queue a new key down/up event for analog values (e.g. ImGuiKey_Gamepad_ values). Dead-zones should be handled by the backend."""
        pass
    def AddMousePosEvent(self, x: float, y: float) -> None:                                                                              # imgui.h:1973
        """ Queue a mouse position update. Use -FLT_MAX,-FLT_MAX to signify no mouse (e.g. app not focused and not hovered)"""
        pass
    def AddMouseButtonEvent(self, button: int, down: bool) -> None:                                                                      # imgui.h:1974
        """ Queue a mouse button change"""
        pass
    def AddMouseWheelEvent(self, wh_x: float, wh_y: float) -> None:                                                                      # imgui.h:1975
        """ Queue a mouse wheel update"""
        pass
    def AddFocusEvent(self, focused: bool) -> None:                                                                                      # imgui.h:1976
        """ Queue a gain/loss of focus for the application (generally based on OS/platform focus of your window)"""
        pass
    def AddInputCharacter(self, c: int) -> None:                                                                                         # imgui.h:1977
        """ Queue a new character input"""
        pass
    def AddInputCharacterUTF16(self, c: ImWchar16) -> None:                                                                              # imgui.h:1978
        """ Queue a new character input from an UTF-16 character, it can be a surrogate"""
        pass
    def AddInputCharactersUTF8(self, str: str) -> None:                                                                                  # imgui.h:1979
        """ Queue a new characters input from an UTF-8 string"""
        pass

    def SetKeyEventNativeData(self, key: ImGuiKey, native_keycode: int, native_scancode: int, native_legacy_index: int = -1) -> None:    # imgui.h:1981
        """ [Optional] Specify index for legacy <1.87 IsKeyXXX() functions with native indices + specify native keycode, scancode."""
        pass
    def SetAppAcceptingEvents(self, accepting_events: bool) -> None:                                                                     # imgui.h:1982
        """ Set master flag for accepting key/mouse/text events (default to True). Useful if you have native dialog boxes that are interrupting your application loop/refresh, and you want to disable events being queued while your app is frozen."""
        pass
    def ClearInputCharacters(self) -> None:                                                                                              # imgui.h:1983
        """ [Internal] Clear the text input buffer manually"""
        pass
    def ClearInputKeys(self) -> None:                                                                                                    # imgui.h:1984
        """ [Internal] Release all keys"""
        pass

    #------------------------------------------------------------------
    # Output - Updated by NewFrame() or EndFrame()/Render()
    # (when reading from the io.WantCaptureMouse, io.WantCaptureKeyboard flags to dispatch your inputs, it is
    #  generally easier and more correct to use their state BEFORE calling NewFrame(). See FAQ for details!)
    #------------------------------------------------------------------

    WantCaptureMouse:bool                                                                                                                # Set when Dear ImGui will use mouse inputs, in this case do not dispatch them to your main game/application (either way, always pass on mouse inputs to imgui). (e.g. unclicked mouse is hovering over an imgui window, widget is active, mouse was clicked over an imgui window, etc.).    # imgui.h:1992
    WantCaptureKeyboard:bool                                                                                                             # Set when Dear ImGui will use keyboard inputs, in this case do not dispatch them to your main game/application (either way, always pass keyboard inputs to imgui). (e.g. InputText active, or an imgui window is focused and navigation is enabled, etc.).    # imgui.h:1993
    WantTextInput:bool                                                                                                                   # Mobile/console: when set, you may display an on-screen keyboard. This is set by Dear ImGui when it wants textual keyboard input to happen (e.g. when a InputText widget is active).    # imgui.h:1994
    WantSetMousePos:bool                                                                                                                 # MousePos has been altered, backend should reposition mouse on next frame. Rarely used! Set only when ImGuiConfigFlags_NavEnableSetMousePos flag is enabled.    # imgui.h:1995
    WantSaveIniSettings:bool                                                                                                             # When manual .ini load/save is active (io.IniFilename == None), this will be set to notify your application that you can call SaveIniSettingsToMemory() and save yourself. Important: clear io.WantSaveIniSettings yourself after saving!    # imgui.h:1996
    NavActive:bool                                                                                                                       # Keyboard/Gamepad navigation is currently allowed (will handle ImGuiKey_NavXXX events) = a window is focused and it doesn't use the ImGuiWindowFlags_NoNavInputs flag.    # imgui.h:1997
    NavVisible:bool                                                                                                                      # Keyboard/Gamepad navigation is visible and allowed (will handle ImGuiKey_NavXXX events).    # imgui.h:1998
    Framerate:float                                                                                                                      # Rough estimate of application framerate, in frame per second. Solely for convenience. Rolling average estimation based on io.DeltaTime over 120 frames.    # imgui.h:1999
    MetricsRenderVertices:int                                                                                                            # Vertices output during last call to Render()    # imgui.h:2000
    MetricsRenderIndices:int                                                                                                             # Indices output during last call to Render() = number of triangles * 3    # imgui.h:2001
    MetricsRenderWindows:int                                                                                                             # Number of visible windows    # imgui.h:2002
    MetricsActiveWindows:int                                                                                                             # Number of active windows    # imgui.h:2003
    MetricsActiveAllocations:int                                                                                                         # Number of active allocations, updated by MemAlloc/MemFree based on current context. May be off if you have multiple imgui contexts.    # imgui.h:2004
    MouseDelta:ImVec2                                                                                                                    # imgui.h:2005
    # Mouse delta. Note that this is zero if either current or previous position are invalid (-FLT_MAX,-FLT_MAX), so a disappearing/reappearing mouse won't have a huge delta.

    # Legacy: before 1.87, we required backend to fill io.KeyMap[] (imgui->native map) during initialization and io.KeysDown[] (native indices) every frame.
    # This is still temporarily supported as a legacy feature. However the new preferred scheme is for backend to call io.AddKeyEvent().

    #------------------------------------------------------------------
    # [Internal] Dear ImGui will maintain those fields. Forward compatibility not guaranteed!
    #------------------------------------------------------------------

    # Main Input State
    # (this block used to be written by backend, since 1.87 it is best to NOT write to those directly, call the AddXXX functions above instead)
    # (reading from those variables is fair game, as they are extremely unlikely to be moving anywhere)
    MousePos:ImVec2                                                                                                                      # Mouse position, in pixels. Set to ImVec2(-FLT_MAX, -FLT_MAX) if mouse is unavailable (on another screen, etc.)    # imgui.h:2021
    MouseDown:np.ndarray                                                                                                                 # ndarray[type=bool, size=5]  # Mouse buttons: 0=left, 1=right, 2=middle + extras (ImGuiMouseButton_COUNT == 5). Dear ImGui mostly uses left and right buttons. Others buttons allows us to track if the mouse is being used by your application + available to user as a convenience via IsMouse** API.    # imgui.h:2022
    MouseWheel:float                                                                                                                     # Mouse wheel Vertical: 1 unit scrolls about 5 lines text.    # imgui.h:2023
    MouseWheelH:float                                                                                                                    # Mouse wheel Horizontal. Most users don't have a mouse with an horizontal wheel, may not be filled by all backends.    # imgui.h:2024
    KeyCtrl:bool                                                                                                                         # Keyboard modifier down: Control    # imgui.h:2025
    KeyShift:bool                                                                                                                        # Keyboard modifier down: Shift    # imgui.h:2026
    KeyAlt:bool                                                                                                                          # Keyboard modifier down: Alt    # imgui.h:2027
    KeySuper:bool                                                                                                                        # Keyboard modifier down: Cmd/Super/Windows    # imgui.h:2028

    # Other state maintained from data above + IO function calls
    KeyMods:ImGuiModFlags                                                                                                                # Key mods flags (same as io.KeyCtrl/KeyShift/KeyAlt/KeySuper but merged into flags), updated by NewFrame()    # imgui.h:2032
    WantCaptureMouseUnlessPopupClose:bool                                                                                                # Alternative to WantCaptureMouse: (WantCaptureMouse == True && WantCaptureMouseUnlessPopupClose == False) when a click over None is expected to close a popup.    # imgui.h:2034
    MousePosPrev:ImVec2                                                                                                                  # Previous mouse position (note that MouseDelta is not necessary == MousePos-MousePosPrev, in case either position is invalid)    # imgui.h:2035
    MouseClickedTime:np.ndarray                                                                                                          # ndarray[type=double, size=5]  # Time of last click (used to figure out double-click)    # imgui.h:2037
    MouseClicked:np.ndarray                                                                                                              # ndarray[type=bool, size=5]  # Mouse button went from !Down to Down (same as MouseClickedCount[x] != 0)    # imgui.h:2038
    MouseDoubleClicked:np.ndarray                                                                                                        # ndarray[type=bool, size=5]  # Has mouse button been double-clicked? (same as MouseClickedCount[x] == 2)    # imgui.h:2039
    MouseClickedCount:np.ndarray                                                                                                         # ndarray[type=ImU16, size=5]  # == 0 (not clicked), == 1 (same as MouseClicked[]), == 2 (double-clicked), == 3 (triple-clicked) etc. when going from !Down to Down    # imgui.h:2040
    MouseClickedLastCount:np.ndarray                                                                                                     # ndarray[type=ImU16, size=5]  # Count successive number of clicks. Stays valid after mouse release. Reset after another click is done.    # imgui.h:2041
    MouseReleased:np.ndarray                                                                                                             # ndarray[type=bool, size=5]  # Mouse button went from Down to !Down    # imgui.h:2042
    MouseDownOwned:np.ndarray                                                                                                            # ndarray[type=bool, size=5]  # Track if button was clicked inside a dear imgui window or over None blocked by a popup. We don't request mouse capture from the application if click started outside ImGui bounds.    # imgui.h:2043
    MouseDownOwnedUnlessPopupClose:np.ndarray                                                                                            # ndarray[type=bool, size=5]  # Track if button was clicked inside a dear imgui window.    # imgui.h:2044
    MouseDownDuration:np.ndarray                                                                                                         # ndarray[type=float, size=5]  # Duration the mouse button has been down (0.0 == just clicked)    # imgui.h:2045
    MouseDownDurationPrev:np.ndarray                                                                                                     # ndarray[type=float, size=5]  # Previous time the mouse button has been down    # imgui.h:2046
    MouseDragMaxDistanceSqr:np.ndarray                                                                                                   # ndarray[type=float, size=5]  # Squared maximum distance of how much mouse has traveled from the clicking point (used for moving thresholds)    # imgui.h:2047
    PenPressure:float                                                                                                                    # Touch/Pen pressure (0.0 to 1.0, should be >0.0 only when MouseDown[0] == True). Helper storage currently unused by Dear ImGui.    # imgui.h:2050
    AppFocusLost:bool                                                                                                                    # Only modify via AddFocusEvent()    # imgui.h:2051
    AppAcceptingEvents:bool                                                                                                              # Only modify via SetAppAcceptingEvents()    # imgui.h:2052
    BackendUsingLegacyKeyArrays:ImS8                                                                                                     # -1: unknown, 0: using AddKeyEvent(), 1: using legacy io.KeysDown[]    # imgui.h:2053
    BackendUsingLegacyNavInputArray:bool                                                                                                 # 0: using AddKeyAnalogEvent(), 1: writing to legacy io.NavInputs[] directly    # imgui.h:2054
    InputQueueSurrogate:ImWchar16                                                                                                        # For AddInputCharacterUTF16()    # imgui.h:2055
    InputQueueCharacters:List[ImWchar]                                                                                                   # Queue of _characters_ input (obtained by platform backend). Fill using AddInputCharacter() helper.    # imgui.h:2056

    def __init__(self) -> None:                                                                                                          # imgui.h:2058
        pass

#-----------------------------------------------------------------------------
# [SECTION] Misc data structures
#-----------------------------------------------------------------------------

class ImGuiInputTextCallbackData:    # imgui.h:2074
    """ Shared state of InputText(), passed as an argument to your callback when a ImGuiInputTextFlags_Callback* flag is used.
     The callback function should return 0 by default.
     Callbacks (follow a flag name and see comments in ImGuiInputTextFlags_ declarations for more details)
     - ImGuiInputTextFlags_CallbackEdit:        Callback on buffer edit (note that InputText() already returns True on edit, the callback is useful mainly to manipulate the underlying buffer while focus is active)
     - ImGuiInputTextFlags_CallbackAlways:      Callback on each iteration
     - ImGuiInputTextFlags_CallbackCompletion:  Callback on pressing TAB
     - ImGuiInputTextFlags_CallbackHistory:     Callback on pressing Up/Down arrows
     - ImGuiInputTextFlags_CallbackCharFilter:  Callback on character inputs to replace or discard them. Modify 'EventChar' to replace or discard, or return 1 in callback to discard.
     - ImGuiInputTextFlags_CallbackResize:      Callback on buffer capacity changes request (beyond 'buf_size' parameter value), allowing the string to grow.
    """
    EventFlag:ImGuiInputTextFlags                                                # One ImGuiInputTextFlags_Callback*    // Read-only    # imgui.h:2076
    Flags:ImGuiInputTextFlags                                                    # What user passed to InputText()      // Read-only    # imgui.h:2077
    UserData:Any                                                                 # What user passed to InputText()      // Read-only    # imgui.h:2078

    # Arguments for the different callback events
    # - To modify the text buffer in a callback, prefer using the InsertChars() / DeleteChars() function. InsertChars() will take care of calling the resize callback if necessary.
    # - If you know your edits are not going to resize the underlying buffer allocation, you may modify the contents of 'Buf[]' directly. You need to update 'BufTextLen' accordingly (0 <= BufTextLen < BufSize) and set 'BufDirty'' to True so InputText can update its internal state.
    EventChar:ImWchar                                                            # Character input                      // Read-write   // [CharFilter] Replace character with another one, or set to zero to drop. return 1 is equivalent to setting EventChar=0;    # imgui.h:2083
    EventKey:ImGuiKey                                                            # Key pressed (Up/Down/TAB)            // Read-only    // [Completion,History]    # imgui.h:2084
    BufTextLen:int                                                               # Text length (in bytes)               // Read-write   // [Resize,Completion,History,Always] Exclude zero-terminator storage. In C land: == strlen(some_text), in C++ land: string.length()    # imgui.h:2086
    BufSize:int                                                                  # Buffer size (in bytes) = capacity+1  // Read-only    // [Resize,Completion,History,Always] Include zero-terminator storage. In C land == ARRAYSIZE(my_char_array), in C++ land: string.capacity()+1    # imgui.h:2087
    BufDirty:bool                                                                # Set if you modify Buf/BufTextLen!    // Write        // [Completion,History,Always]    # imgui.h:2088
    CursorPos:int                                                                #                                      // Read-write   // [Completion,History,Always]    # imgui.h:2089
    SelectionStart:int                                                           #                                      // Read-write   // [Completion,History,Always] == to SelectionEnd when no selection)    # imgui.h:2090
    SelectionEnd:int                                                             #                                      // Read-write   // [Completion,History,Always]    # imgui.h:2091

    # Helper functions for text manipulation.
    # Use those function to benefit from the CallbackResize behaviors. Calling those function reset the selection.
    def __init__(self) -> None:                                                  # imgui.h:2095
        pass
    def DeleteChars(self, pos: int, bytes_count: int) -> None:                   # imgui.h:2096
        pass
    def InsertChars(self, pos: int, text: str, text_end: str = None) -> None:    # imgui.h:2097
        pass

class ImGuiSizeCallbackData:    # imgui.h:2105
    """ Resizing callback data to apply custom constraint. As enabled by SetNextWindowSizeConstraints(). Callback is called during the next Begin().
     NB: For basic min/max size constraint on each axis you don't need to use the callback! The SetNextWindowSizeConstraints() parameters are enough.
    """
    UserData:Any        # Read-only.   What user passed to SetNextWindowSizeConstraints()    # imgui.h:2107
    Pos:ImVec2          # Read-only.   Window position, for reference.    # imgui.h:2108
    CurrentSize:ImVec2  # Read-only.   Current window size.    # imgui.h:2109
    DesiredSize:ImVec2  # Read-write.  Desired size, based on user's mouse position. Write to this field to restrain resizing.    # imgui.h:2110

class ImGuiPayload:    # imgui.h:2114
    """ Data payload for Drag and Drop operations: AcceptDragDropPayload(), GetDragDropPayload()"""
    # Members
    Data:Any                       # Data (copied and owned by dear imgui)    # imgui.h:2117
    DataSize:int                   # Data size    # imgui.h:2118

    # [Internal]
    SourceId:ImGuiID               # Source item id    # imgui.h:2121
    SourceParentId:ImGuiID         # Source parent id (if available)    # imgui.h:2122
    DataFrameCount:int             # Data timestamp    # imgui.h:2123
    Preview:bool                   # Set when AcceptDragDropPayload() was called and mouse has been hovering the target item (nb: handle overlapping drag targets)    # imgui.h:2125
    Delivery:bool                  # Set when AcceptDragDropPayload() was called and mouse button is released over the target item.    # imgui.h:2126

    def __init__(self) -> None:    # imgui.h:2128
        pass

class ImGuiTableColumnSortSpecs:    # imgui.h:2136
    """ Sorting specification for one column of a table (sizeof == 12 bytes)"""
    ColumnUserID:ImGuiID           # User id of the column (if specified by a TableSetupColumn() call)    # imgui.h:2138
    ColumnIndex:ImS16              # Index of the column    # imgui.h:2139
    SortOrder:ImS16                # Index within parent ImGuiTableSortSpecs (always stored in order starting from 0, tables sorted on a single criteria will always have a 0 here)    # imgui.h:2140

    def __init__(self) -> None:    # imgui.h:2143
        pass

class ImGuiTableSortSpecs:    # imgui.h:2150
    """ Sorting specifications for a table (often handling sort specs for a single column, occasionally more)
     Obtained by calling TableGetSortSpecs().
     When 'SpecsDirty == True' you can sort your data. It will be True with sorting specs have changed since last call, or the first time.
     Make sure to set 'SpecsDirty = False' after sorting, else you may wastefully sort your data every frame!
    """
    Specs:ImGuiTableColumnSortSpecs  # Pointer to sort spec array.    # imgui.h:2152
    SpecsCount:int                   # Sort spec count. Most often 1. May be > 1 when ImGuiTableFlags_SortMulti is enabled. May be == 0 when ImGuiTableFlags_SortTristate is enabled.    # imgui.h:2153
    SpecsDirty:bool                  # Set to True when specs have changed since last time! Use this to sort again, then clear the flag.    # imgui.h:2154

    def __init__(self) -> None:      # imgui.h:2156
        pass

#-----------------------------------------------------------------------------
# [SECTION] Helpers (ImGuiOnceUponAFrame, ImGuiTextFilter, ImGuiTextBuffer, ImGuiStorage, ImGuiListClipper, ImColor)
#-----------------------------------------------------------------------------

# Helper: Unicode defines

class ImGuiOnceUponAFrame:    # imgui.h:2173
    """ Helper: Execute a block of code at maximum once a frame. Convenient if you want to quickly create an UI within deep-nested code that runs multiple times every frame.
     Usage: static ImGuiOnceUponAFrame oaf; if (oaf) ImGui::Text("This will be called only once per frame");
    """
    def __init__(self) -> None:    # imgui.h:2175
        pass
    RefFrame:int                   # imgui.h:2176

class ImGuiTextFilter:    # imgui.h:2181
    """ Helper: Parse and apply text filters. In format "aaaaa[,bbbb][,ccccc]" """
    def __init__(self, default_filter: str = "") -> None:                            # imgui.h:2183
        pass
    def Draw(self, label: str = "Filter (inc,-exc)", width: float = 0.0) -> bool:    # imgui.h:2184
        """ Helper calling InputText+Build"""
        pass
    def PassFilter(self, text: str, text_end: str = None) -> bool:                   # imgui.h:2185
        pass
    def Build(self) -> None:                                                         # imgui.h:2186
        pass

    Filters:List[ImGuiTextRange]                                                     # imgui.h:2202
    CountGrep:int                                                                    # imgui.h:2203


class ImGuiStorage:    # imgui.h:2235
    """ Helper: Key->Value storage
     Typically you don't have to worry about this since a storage is held within each Window.
     We use it to e.g. store collapse state for a tree (Int 0/1)
     This is optimized for efficient lookup (dichotomy into a contiguous buffer) and rare insertion (typically tied to user interactions aka max once a frame)
     You can use it as custom user storage for temporary values. Declare your own storage if, for example:
     - You want to manipulate the open/close state of a particular sub-tree in your interface (tree node uses Int 0/1 to store their state).
     - You want to store custom debug data easily without adding or editing structures in your code (probably not efficient, but convenient)
     Types are NOT stored, so it is up to you to make sure your Key don't collide with different types.
    """

    Data:List[ImGuiStoragePair]                                                # imgui.h:2247

    def GetInt(self, key: ImGuiID, default_val: int = 0) -> int:               # imgui.h:2253
        pass
    def SetInt(self, key: ImGuiID, val: int) -> None:                          # imgui.h:2254
        pass
    def GetBool(self, key: ImGuiID, default_val: bool = False) -> bool:        # imgui.h:2255
        pass
    def SetBool(self, key: ImGuiID, val: bool) -> None:                        # imgui.h:2256
        pass
    def GetFloat(self, key: ImGuiID, default_val: float = 0.0) -> float:       # imgui.h:2257
        pass
    def SetFloat(self, key: ImGuiID, val: float) -> None:                      # imgui.h:2258
        pass
    def GetVoidPtr(self, key: ImGuiID) -> Any:                                 # imgui.h:2259
        """ default_val is None"""
        pass
    def SetVoidPtr(self, key: ImGuiID, val: Any) -> None:                      # imgui.h:2260
        pass

    # - Get***Ref() functions finds pair, insert on demand if missing, return pointer. Useful if you intend to do Get+Set.
    # - References are only valid until a new value is added to the storage. Calling a Set***() function or a Get***Ref() function invalidates the pointer.
    # - A typical use case where this is convenient for quick hacking (e.g. add storage during a live Edit&Continue session if you can't modify existing struct)
    #      float* pvar = ImGui::GetFloatRef(key); ImGui::SliderFloat("var", pvar, 0, 100.0); some_var += *pvar;
    def GetIntRef(self, key: ImGuiID, default_val: int = 0) -> int:            # imgui.h:2266
        pass
    def GetBoolRef(self, key: ImGuiID, default_val: bool = False) -> bool:     # imgui.h:2267
        pass
    def GetFloatRef(self, key: ImGuiID, default_val: float = 0.0) -> float:    # imgui.h:2268
        pass
    def GetVoidPtrRef(self, key: ImGuiID, default_val: Any = None) -> Any:     # imgui.h:2269
        pass

    def SetAllInt(self, val: int) -> None:                                     # imgui.h:2272
        """ Use on your own storage if you know only integer are being stored (open/close all tree nodes)"""
        pass

    def BuildSortByKey(self) -> None:                                          # imgui.h:2275
        """ For quicker full rebuild of a storage (instead of an incremental one), you may add all your contents and then sort once."""
        pass

class ImGuiListClipper:    # imgui.h:2298
    """ Helper: Manually clip large list of items.
     If you have lots evenly spaced items and you have a random access to the list, you can perform coarse
     clipping based on visibility to only submit items that are in view.
     The clipper calculates the range of visible items and advance the cursor to compensate for the non-visible items we have skipped.
     (Dear ImGui already clip items based on their bounds but: it needs to first layout the item to do so, and generally
      fetching/submitting your own data incurs additional cost. Coarse clipping using ImGuiListClipper allows you to easily
      scale using lists with tens of thousands of items without a problem)
     Usage:
       ImGuiListClipper clipper;
       clipper.Begin(1000);         // We have 1000 elements, evenly spaced.
       while (clipper.Step())
           for (int i = clipper.DisplayStart; i < clipper.DisplayEnd; i++)
               ImGui::Text("line number %d", i);
     Generally what happens is:
     - Clipper lets you process the first element (DisplayStart = 0, DisplayEnd = 1) regardless of it being visible or not.
     - User code submit that one element.
     - Clipper can measure the height of the first element
     - Clipper calculate the actual range of elements to display based on the current clipping rectangle, position the cursor before the first visible element.
     - User code submit visible elements.
     - The clipper also handles various subtleties related to keyboard/gamepad navigation, wrapping etc.
    """
    DisplayStart:int                                                               # First item to display, updated by each call to Step()    # imgui.h:2300
    DisplayEnd:int                                                                 # End of items to display (exclusive)    # imgui.h:2301
    ItemsCount:int                                                                 # [Internal] Number of items    # imgui.h:2302
    ItemsHeight:float                                                              # [Internal] Height of item after a first step and item submission can calculate it    # imgui.h:2303
    StartPosY:float                                                                # [Internal] Cursor position at the time of Begin() or after table frozen rows are all processed    # imgui.h:2304
    TempData:Any                                                                   # [Internal] Internal data    # imgui.h:2305

    def __init__(self) -> None:                                                    # imgui.h:2309
        """ items_count: Use INT_MAX if you don't know how many items you have (in which case the cursor won't be advanced in the final step)
         items_height: Use -1.0 to be calculated automatically on first step. Otherwise pass in the distance between your items, typically GetTextLineHeightWithSpacing() or GetFrameHeightWithSpacing().
        """
        pass
    def Begin(self, items_count: int, items_height: float = -1.0) -> None:         # imgui.h:2311
        pass
    def End(self) -> None:                                                         # imgui.h:2312
        """ Automatically called on the last call of Step() that returns False."""
        pass
    def Step(self) -> bool:                                                        # imgui.h:2313
        """ Call until it returns False. The DisplayStart/DisplayEnd fields will be set and you can process/draw those items."""
        pass

    def ForceDisplayRangeByIndices(self, item_min: int, item_max: int) -> None:    # imgui.h:2316
        """ Call ForceDisplayRangeByIndices() before first call to Step() if you need a range of items to be displayed regardless of visibility."""
        pass
    # item_max is exclusive e.g. use (42, 42+1) to make item 42 always visible BUT due to alignment/padding of certain items it is likely that an extra item may be included on either end of the display range.


# Helpers macros to generate 32-bit encoded colors
# User can declare their own format by #defining the 5 _SHIFT/_MASK macros in their imconfig file.

class ImColor:    # imgui.h:2349
    """ Helper: ImColor() implicitly converts colors to either ImU32 (packed 4x1 byte) or ImVec4 (4x1 float)
     Prefer using IM_COL32() macros if you want a guaranteed compile-time ImU32 for usage with ImDrawList API.
     **Avoid storing ImColor! Store either u32 of ImVec4. This is not a full-featured color class. MAY OBSOLETE.
     **None of the ImGui API are using ImColor directly but you can use it as a convenience to pass colors in either ImU32 or ImVec4 formats. Explicitly cast to ImU32 or ImVec4 if needed.
    """
    Value:ImVec4                                                                 # imgui.h:2351

    def __init__(self) -> None:                                                  # imgui.h:2353
        pass
    def __init__(self, r: float, g: float, b: float, a: float = 1.0) -> None:    # imgui.h:2354
        pass
    def __init__(self, col: ImVec4) -> None:                                     # imgui.h:2355
        pass
    def __init__(self, r: int, g: int, b: int, a: int = 255) -> None:            # imgui.h:2356
        pass
    def __init__(self, rgba: ImU32) -> None:                                     # imgui.h:2357
        pass

    # FIXME-OBSOLETE: May need to obsolete/cleanup those helpers.

#-----------------------------------------------------------------------------
# [SECTION] Drawing API (ImDrawCmd, ImDrawIdx, ImDrawVert, ImDrawChannel, ImDrawListSplitter, ImDrawListFlags, ImDrawList, ImDrawData)
# Hold a series of drawing commands. The user provides a renderer for ImDrawData which essentially contains an array of ImDrawList.
#-----------------------------------------------------------------------------

# The maximum line width to bake anti-aliased textures for. Build atlas with ImFontAtlasFlags_NoBakedLines to disable baking.

# ImDrawCallback: Draw callbacks for advanced uses [configurable type: override in imconfig.h]
# NB: You most likely do NOT need to use draw callbacks just to create your own widget or customized UI rendering,
# you can poke into the draw list for that! Draw callback may be useful for example to:
#  A) Change your GPU render state,
#  B) render a complex 3D scene inside a UI element without an intermediate texture/render target, etc.
# The expected behavior from your rendering function is 'if (cmd.UserCallback != None) { cmd.UserCallback(parent_list, cmd); } else { RenderTriangles() }'
# If you want to override the signature of ImDrawCallback, you can simply use e.g. '#define ImDrawCallback MyDrawCallback' (in imconfig.h) + update rendering backend accordingly.


class ImDrawCmd:    # imgui.h:2398
    """ Typically, 1 command = 1 GPU draw call (unless command is a callback)
     - VtxOffset: When 'io.BackendFlags & ImGuiBackendFlags_RendererHasVtxOffset' is enabled,
       this fields allow us to render meshes larger than 64K vertices while keeping 16-bit indices.
       Backends made for <1.71. will typically ignore the VtxOffset fields.
     - The ClipRect/TextureId/VtxOffset fields must be contiguous as we memcmp() them together (this is asserted for).
    """
    ClipRect:ImVec4                # 4*4  // Clipping rectangle (x1, y1, x2, y2). Subtract ImDrawData->DisplayPos to get clipping rectangle in "viewport" coordinates    # imgui.h:2400
    TextureId:ImTextureID          # 4-8  // User-provided texture ID. Set by user in ImfontAtlas::SetTexID() for fonts or passed to Image*() functions. Ignore if never using images or multiple fonts atlas.    # imgui.h:2401
    VtxOffset:int                  # 4    // Start offset in vertex buffer. ImGuiBackendFlags_RendererHasVtxOffset: always 0, otherwise may be >0 to support meshes larger than 64K vertices with 16-bit indices.    # imgui.h:2402
    IdxOffset:int                  # 4    // Start offset in index buffer.    # imgui.h:2403
    ElemCount:int                  # 4    // Number of indices (multiple of 3) to be rendered as triangles. Vertices are stored in the callee ImDrawList's vtx_buffer[] array, indices in idx_buffer[].    # imgui.h:2404
    UserCallbackData:Any           # 4-8  // The draw callback code can access this.    # imgui.h:2406

    def __init__(self) -> None:    # imgui.h:2408
        """ Also ensure our padding fields are zeroed"""
        pass


# Vertex layout

class ImDrawCmdHeader:    # imgui.h:2431
    """ [Internal] For use by ImDrawList"""
    ClipRect:ImVec4          # imgui.h:2433
    TextureId:ImTextureID    # imgui.h:2434
    VtxOffset:int            # imgui.h:2435

class ImDrawChannel:    # imgui.h:2439
    """ [Internal] For use by ImDrawListSplitter"""
    _CmdBuffer:List[ImDrawCmd]    # imgui.h:2441
    _IdxBuffer:List[ImDrawIdx]    # imgui.h:2442


class ImDrawListSplitter:    # imgui.h:2448
    """ Split/Merge functions are used to split the draw list into different layers which can be drawn into out of order.
     This is used by the Columns/Tables API, so items of each column can be batched together in a same draw call.
    """
    _Current:int                                                                     # Current channel number (0)    # imgui.h:2450
    _Count:int                                                                       # Number of active channels (1+)    # imgui.h:2451
    _Channels:List[ImDrawChannel]                                                    # Draw channels (not resized down so _Count might be < Channels.Size)    # imgui.h:2452

    def __init__(self) -> None:                                                      # imgui.h:2454
        pass
    def ClearFreeMemory(self) -> None:                                               # imgui.h:2457
        pass
    def Split(self, draw_list: ImDrawList, count: int) -> None:                      # imgui.h:2458
        pass
    def Merge(self, draw_list: ImDrawList) -> None:                                  # imgui.h:2459
        pass
    def SetCurrentChannel(self, draw_list: ImDrawList, channel_idx: int) -> None:    # imgui.h:2460
        pass

class ImDrawFlags_(Enum):    # imgui.h:2465
    """ Flags for ImDrawList functions
     (Legacy: bit 0 must always correspond to ImDrawFlags_Closed to be backward compatible with old API using a bool. Bits 1..3 must be unused)
    """
    None_ = 0
    Closed = 1 << 0                                               # PathStroke(), AddPolyline(): specify that shape should be closed (Important: this is always == 1 for legacy reason)
    RoundCornersTopLeft = 1 << 4                                  # AddRect(), AddRectFilled(), PathRect(): enable rounding top-left corner only (when rounding > 0.0, we default to all corners). Was 0x01.
    RoundCornersTopRight = 1 << 5                                 # AddRect(), AddRectFilled(), PathRect(): enable rounding top-right corner only (when rounding > 0.0, we default to all corners). Was 0x02.
    RoundCornersBottomLeft = 1 << 6                               # AddRect(), AddRectFilled(), PathRect(): enable rounding bottom-left corner only (when rounding > 0.0, we default to all corners). Was 0x04.
    RoundCornersBottomRight = 1 << 7                              # AddRect(), AddRectFilled(), PathRect(): enable rounding bottom-right corner only (when rounding > 0.0, we default to all corners). Wax 0x08.
    RoundCornersNone = 1 << 8                                     # AddRect(), AddRectFilled(), PathRect(): disable rounding on all corners (when rounding > 0.0). This is NOT zero, NOT an implicit flag!
    RoundCornersTop = Literal[ImDrawFlags_.RoundCornersTopLeft] | Literal[ImDrawFlags_.RoundCornersTopRight]
    RoundCornersBottom = Literal[ImDrawFlags_.RoundCornersBottomLeft] | Literal[ImDrawFlags_.RoundCornersBottomRight]
    RoundCornersLeft = Literal[ImDrawFlags_.RoundCornersBottomLeft] | Literal[ImDrawFlags_.RoundCornersTopLeft]
    RoundCornersRight = Literal[ImDrawFlags_.RoundCornersBottomRight] | Literal[ImDrawFlags_.RoundCornersTopRight]
    RoundCornersAll = Literal[ImDrawFlags_.RoundCornersTopLeft] | Literal[ImDrawFlags_.RoundCornersTopRight] | Literal[ImDrawFlags_.RoundCornersBottomLeft] | Literal[ImDrawFlags_.RoundCornersBottomRight]
    RoundCornersDefault_ = Literal[ImDrawFlags_.RoundCornersAll]  # Default to ALL corners if none of the _RoundCornersXX flags are specified.
    RoundCornersMask_ = Literal[ImDrawFlags_.RoundCornersAll] | Literal[ImDrawFlags_.RoundCornersNone]

class ImDrawListFlags_(Enum):    # imgui.h:2485
    """ Flags for ImDrawList instance. Those are set automatically by ImGui:: functions from ImGuiIO settings, and generally not manipulated directly.
     It is however possible to temporarily alter flags between calls to ImDrawList:: functions.
    """
    None_ = 0
    AntiAliasedLines = 1 << 0        # Enable anti-aliased lines/borders (*2 the number of triangles for 1.0 wide line or lines thin enough to be drawn using textures, otherwise *3 the number of triangles)
    AntiAliasedLinesUseTex = 1 << 1  # Enable anti-aliased lines/borders using textures when possible. Require backend to render with bilinear filtering (NOT point/nearest filtering).
    AntiAliasedFill = 1 << 2         # Enable anti-aliased edge around filled shapes (rounded rectangles, circles).
    AllowVtxOffset = 1 << 3          # Can emit 'VtxOffset > 0' to allow large meshes. Set when 'ImGuiBackendFlags_RendererHasVtxOffset' is enabled.

class ImDrawList:    # imgui.h:2503
    """ Draw command list
     This is the low-level list of polygons that ImGui:: functions are filling. At the end of the frame,
     all command lists are passed to your ImGuiIO::RenderDrawListFn function for rendering.
     Each dear imgui window contains its own ImDrawList. You can use ImGui::GetWindowDrawList() to
     access the current window draw list and draw custom primitives.
     You can interleave normal ImGui:: calls and adding primitives to the current draw list.
     In single viewport mode, top-left is == GetMainViewport()->Pos (generally 0,0), bottom-right is == GetMainViewport()->Pos+Size (generally io.DisplaySize).
     You are totally free to apply whatever transformation matrix to want to the data (depending on the use of the transformation you may want to apply it to ClipRect as well!)
     Important: Primitives are always added to the list and not culled (culling is done at higher-level by ImGui:: functions), if you use this API a lot consider coarse culling your drawn objects.
    """
    # This is what you have to render
    CmdBuffer:List[ImDrawCmd]                                                                                                                                                                                                                                     # Draw commands. Typically 1 command = 1 GPU draw call, unless the command is a callback.    # imgui.h:2506
    IdxBuffer:List[ImDrawIdx]                                                                                                                                                                                                                                     # Index buffer. Each command consume ImDrawCmd::ElemCount of those    # imgui.h:2507
    VtxBuffer:List[ImDrawVert]                                                                                                                                                                                                                                    # Vertex buffer.    # imgui.h:2508
    Flags:ImDrawListFlags                                                                                                                                                                                                                                         # Flags, you may poke into these to adjust anti-aliasing settings per-primitive.    # imgui.h:2509

    # [Internal, used while building lists]
    _VtxCurrentIdx:int                                                                                                                                                                                                                                            # [Internal] generally == VtxBuffer.Size unless we are past 64K vertices, in which case this gets reset to 0.    # imgui.h:2512
    _Data:ImDrawListSharedData                                                                                                                                                                                                                                    # Pointer to shared draw data (you can use ImGui::GetDrawListSharedData() to get the one from current ImGui context)    # imgui.h:2513
    _OwnerName:str                                                                                                                                                                                                                                                # Pointer to owner window's name for debugging    # imgui.h:2514
    _VtxWritePtr:ImDrawVert                                                                                                                                                                                                                                       # [Internal] point within VtxBuffer.Data after each add command (to avoid using the ImVector<> operators too much)    # imgui.h:2515
    _IdxWritePtr:ImDrawIdx                                                                                                                                                                                                                                        # [Internal] point within IdxBuffer.Data after each add command (to avoid using the ImVector<> operators too much)    # imgui.h:2516
    _ClipRectStack:List[ImVec4]                                                                                                                                                                                                                                   # [Internal]    # imgui.h:2517
    _TextureIdStack:List[ImTextureID]                                                                                                                                                                                                                             # [Internal]    # imgui.h:2518
    _Path:List[ImVec2]                                                                                                                                                                                                                                            # [Internal] current path building    # imgui.h:2519
    _CmdHeader:ImDrawCmdHeader                                                                                                                                                                                                                                    # [Internal] template of active commands. Fields should match those of CmdBuffer.back().    # imgui.h:2520
    _Splitter:ImDrawListSplitter                                                                                                                                                                                                                                  # [Internal] for channels api (note: prefer using your own persistent instance of ImDrawListSplitter!)    # imgui.h:2521
    _FringeScale:float                                                                                                                                                                                                                                            # [Internal] anti-alias fringe is scaled by this value, this helps to keep things sharp while zooming at vertex buffer content    # imgui.h:2522

    def __init__(self, shared_data: ImDrawListSharedData) -> None:                                                                                                                                                                                                # imgui.h:2525
        """ If you want to create ImDrawList instances, pass them ImGui::GetDrawListSharedData() or create and use your own ImDrawListSharedData (so you can use ImDrawList without ImGui)"""
        pass

    def PushClipRect(self, clip_rect_min: ImVec2, clip_rect_max: ImVec2, intersect_with_current_clip_rect: bool = False) -> None:                                                                                                                                 # imgui.h:2528
        """ Render-level scissoring. This is passed down to your render function but not used for CPU-side coarse clipping. Prefer using higher-level ImGui::PushClipRect() to affect logic (hit-testing and widget culling)"""
        pass
    def PushClipRectFullScreen(self) -> None:                                                                                                                                                                                                                     # imgui.h:2529
        pass
    def PopClipRect(self) -> None:                                                                                                                                                                                                                                # imgui.h:2530
        pass
    def PushTextureID(self, texture_id: ImTextureID) -> None:                                                                                                                                                                                                     # imgui.h:2531
        pass
    def PopTextureID(self) -> None:                                                                                                                                                                                                                               # imgui.h:2532
        pass

    # Primitives
    # - Filled shapes must always use clockwise winding order. The anti-aliasing fringe depends on it. Counter-clockwise shapes will have "inward" anti-aliasing.
    # - For rectangular primitives, "p_min" and "p_max" represent the upper-left and lower-right corners.
    # - For circle primitives, use "num_segments == 0" to automatically calculate tessellation (preferred).
    #   In older versions (until Dear ImGui 1.77) the AddCircle functions defaulted to num_segments == 12.
    #   In future versions we will use textures to provide cheaper and higher-quality circles.
    #   Use AddNgon() and AddNgonFilled() functions if you need to guaranteed a specific number of sides.
    def AddLine(self, p1: ImVec2, p2: ImVec2, col: ImU32, thickness: float = 1.0) -> None:                                                                                                                                                                        # imgui.h:2543
        pass
    def AddRect(self, p_min: ImVec2, p_max: ImVec2, col: ImU32, rounding: float = 0.0, flags: ImDrawFlags = 0, thickness: float = 1.0) -> None:                                                                                                                   # imgui.h:2544
        """ a: upper-left, b: lower-right (== upper-left + size)"""
        pass
    def AddRectFilled(self, p_min: ImVec2, p_max: ImVec2, col: ImU32, rounding: float = 0.0, flags: ImDrawFlags = 0) -> None:                                                                                                                                     # imgui.h:2545
        """ a: upper-left, b: lower-right (== upper-left + size)"""
        pass
    def AddRectFilledMultiColor(self, p_min: ImVec2, p_max: ImVec2, col_upr_left: ImU32, col_upr_right: ImU32, col_bot_right: ImU32, col_bot_left: ImU32) -> None:                                                                                                # imgui.h:2546
        pass
    def AddQuad(self, p1: ImVec2, p2: ImVec2, p3: ImVec2, p4: ImVec2, col: ImU32, thickness: float = 1.0) -> None:                                                                                                                                                # imgui.h:2547
        pass
    def AddQuadFilled(self, p1: ImVec2, p2: ImVec2, p3: ImVec2, p4: ImVec2, col: ImU32) -> None:                                                                                                                                                                  # imgui.h:2548
        pass
    def AddTriangle(self, p1: ImVec2, p2: ImVec2, p3: ImVec2, col: ImU32, thickness: float = 1.0) -> None:                                                                                                                                                        # imgui.h:2549
        pass
    def AddTriangleFilled(self, p1: ImVec2, p2: ImVec2, p3: ImVec2, col: ImU32) -> None:                                                                                                                                                                          # imgui.h:2550
        pass
    def AddCircle(self, center: ImVec2, radius: float, col: ImU32, num_segments: int = 0, thickness: float = 1.0) -> None:                                                                                                                                        # imgui.h:2551
        pass
    def AddCircleFilled(self, center: ImVec2, radius: float, col: ImU32, num_segments: int = 0) -> None:                                                                                                                                                          # imgui.h:2552
        pass
    def AddNgon(self, center: ImVec2, radius: float, col: ImU32, num_segments: int, thickness: float = 1.0) -> None:                                                                                                                                              # imgui.h:2553
        pass
    def AddNgonFilled(self, center: ImVec2, radius: float, col: ImU32, num_segments: int) -> None:                                                                                                                                                                # imgui.h:2554
        pass
    def AddText(self, pos: ImVec2, col: ImU32, text_begin: str, text_end: str = None) -> None:                                                                                                                                                                    # imgui.h:2555
        pass
    def AddText(self, font: ImFont, font_size: float, pos: ImVec2, col: ImU32, text_begin: str, text_end: str = None, wrap_width: float = 0.0, cpu_fine_clip_rect: ImVec4 = None) -> None:                                                                        # imgui.h:2556
        pass
    def AddPolyline(self, points: ImVec2, num_points: int, col: ImU32, flags: ImDrawFlags, thickness: float) -> None:                                                                                                                                             # imgui.h:2557
        pass
    def AddConvexPolyFilled(self, points: ImVec2, num_points: int, col: ImU32) -> None:                                                                                                                                                                           # imgui.h:2558
        pass
    def AddBezierCubic(self, p1: ImVec2, p2: ImVec2, p3: ImVec2, p4: ImVec2, col: ImU32, thickness: float, num_segments: int = 0) -> None:                                                                                                                        # imgui.h:2559
        """ Cubic Bezier (4 control points)"""
        pass
    def AddBezierQuadratic(self, p1: ImVec2, p2: ImVec2, p3: ImVec2, col: ImU32, thickness: float, num_segments: int = 0) -> None:                                                                                                                                # imgui.h:2560
        """ Quadratic Bezier (3 control points)"""
        pass

    # Image primitives
    # - Read FAQ to understand what ImTextureID is.
    # - "p_min" and "p_max" represent the upper-left and lower-right corners of the rectangle.
    # - "uv_min" and "uv_max" represent the normalized texture coordinates to use for those corners. Using (0,0)->(1,1) texture coordinates will generally display the entire texture.
    def AddImage(self, user_texture_id: ImTextureID, p_min: ImVec2, p_max: ImVec2, uv_min: ImVec2 = ImVec2(0, 0), uv_max: ImVec2 = ImVec2(1, 1), col: ImU32 = IM_COL32_WHITE) -> None:                                                                            # imgui.h:2566
        pass
    def AddImageQuad(self, user_texture_id: ImTextureID, p1: ImVec2, p2: ImVec2, p3: ImVec2, p4: ImVec2, uv1: ImVec2 = ImVec2(0, 0), uv2: ImVec2 = ImVec2(1, 0), uv3: ImVec2 = ImVec2(1, 1), uv4: ImVec2 = ImVec2(0, 1), col: ImU32 = IM_COL32_WHITE) -> None:    # imgui.h:2567
        pass
    def AddImageRounded(self, user_texture_id: ImTextureID, p_min: ImVec2, p_max: ImVec2, uv_min: ImVec2, uv_max: ImVec2, col: ImU32, rounding: float, flags: ImDrawFlags = 0) -> None:                                                                           # imgui.h:2568
        pass

    # Stateful path API, add points then finish with PathFillConvex() or PathStroke()
    # - Filled shapes must always use clockwise winding order. The anti-aliasing fringe depends on it. Counter-clockwise shapes will have "inward" anti-aliasing.
    def PathArcTo(self, center: ImVec2, radius: float, a_min: float, a_max: float, num_segments: int = 0) -> None:                                                                                                                                                # imgui.h:2577
        pass
    def PathArcToFast(self, center: ImVec2, radius: float, a_min_of_12: int, a_max_of_12: int) -> None:                                                                                                                                                           # imgui.h:2578
        """ Use precomputed angles for a 12 steps circle"""
        pass
    def PathBezierCubicCurveTo(self, p2: ImVec2, p3: ImVec2, p4: ImVec2, num_segments: int = 0) -> None:                                                                                                                                                          # imgui.h:2579
        """ Cubic Bezier (4 control points)"""
        pass
    def PathBezierQuadraticCurveTo(self, p2: ImVec2, p3: ImVec2, num_segments: int = 0) -> None:                                                                                                                                                                  # imgui.h:2580
        """ Quadratic Bezier (3 control points)"""
        pass
    def PathRect(self, rect_min: ImVec2, rect_max: ImVec2, rounding: float = 0.0, flags: ImDrawFlags = 0) -> None:                                                                                                                                                # imgui.h:2581
        pass

    # Advanced
    def AddCallback(self, callback: ImDrawCallback, callback_data: Any) -> None:                                                                                                                                                                                  # imgui.h:2584
        """ Your rendering function must check for 'UserCallback' in ImDrawCmd and call the function instead of rendering triangles."""
        pass
    def AddDrawCmd(self) -> None:                                                                                                                                                                                                                                 # imgui.h:2585
        """ This is useful if you need to forcefully create a new draw call (to allow for dependent rendering / blending). Otherwise primitives are merged into the same draw-call as much as possible"""
        pass
    def CloneOutput(self) -> ImDrawList:                                                                                                                                                                                                                          # imgui.h:2586
        """ Create a clone of the CmdBuffer/IdxBuffer/VtxBuffer."""
        pass

    # Advanced: Channels
    # - Use to split render into layers. By switching channels to can render out-of-order (e.g. submit FG primitives before BG primitives)
    # - Use to minimize draw calls (e.g. if going back-and-forth between multiple clipping rectangles, prefer to append into separate channels then merge at the end)
    # - FIXME-OBSOLETE: This API shouldn't have been in ImDrawList in the first place!
    #   Prefer using your own persistent instance of ImDrawListSplitter as you can stack them.
    #   Using the ImDrawList::ChannelsXXXX you cannot stack a split over another.

    # Advanced: Primitives allocations
    # - We render triangles (three vertices)
    # - All primitives needs to be reserved via PrimReserve() beforehand.
    def PrimReserve(self, idx_count: int, vtx_count: int) -> None:                                                                                                                                                                                                # imgui.h:2601
        pass
    def PrimUnreserve(self, idx_count: int, vtx_count: int) -> None:                                                                                                                                                                                              # imgui.h:2602
        pass
    def PrimRect(self, a: ImVec2, b: ImVec2, col: ImU32) -> None:                                                                                                                                                                                                 # imgui.h:2603
        """ Axis aligned rectangle (composed of two triangles)"""
        pass
    # Write vertex with unique index


    # [Internal helpers]
    def _ResetForNewFrame(self) -> None:                                                                                                                                                                                                                          # imgui.h:2616
        pass
    def _ClearFreeMemory(self) -> None:                                                                                                                                                                                                                           # imgui.h:2617
        pass
    def _PopUnusedDrawCmd(self) -> None:                                                                                                                                                                                                                          # imgui.h:2618
        pass
    def _TryMergeDrawCmds(self) -> None:                                                                                                                                                                                                                          # imgui.h:2619
        pass
    def _OnChangedClipRect(self) -> None:                                                                                                                                                                                                                         # imgui.h:2620
        pass
    def _OnChangedTextureID(self) -> None:                                                                                                                                                                                                                        # imgui.h:2621
        pass
    def _OnChangedVtxOffset(self) -> None:                                                                                                                                                                                                                        # imgui.h:2622
        pass
    def _CalcCircleAutoSegmentCount(self, radius: float) -> int:                                                                                                                                                                                                  # imgui.h:2623
        pass
    def _PathArcToFastEx(self, center: ImVec2, radius: float, a_min_sample: int, a_max_sample: int, a_step: int) -> None:                                                                                                                                         # imgui.h:2624
        pass
    def _PathArcToN(self, center: ImVec2, radius: float, a_min: float, a_max: float, num_segments: int) -> None:                                                                                                                                                  # imgui.h:2625
        pass

class ImDrawData:    # imgui.h:2631
    """ All draw data to render a Dear ImGui frame
     (NB: the style and the naming convention here is a little inconsistent, we currently preserve them for backward compatibility purpose,
     as this is one of the oldest structure exposed by the library! Basically, ImDrawList == CmdList)
    """
    Valid:bool                                             # Only valid after Render() is called and before the next NewFrame() is called.    # imgui.h:2633
    CmdListsCount:int                                      # Number of ImDrawList* to render    # imgui.h:2634
    TotalIdxCount:int                                      # For convenience, sum of all ImDrawList's IdxBuffer.Size    # imgui.h:2635
    TotalVtxCount:int                                      # For convenience, sum of all ImDrawList's VtxBuffer.Size    # imgui.h:2636
    DisplayPos:ImVec2                                      # Top-left position of the viewport to render (== top-left of the orthogonal projection matrix to use) (== GetMainViewport()->Pos for the main viewport, == (0.0) in most single-viewport applications)    # imgui.h:2638
    DisplaySize:ImVec2                                     # Size of the viewport to render (== GetMainViewport()->Size for the main viewport, == io.DisplaySize in most single-viewport applications)    # imgui.h:2639
    FramebufferScale:ImVec2                                # Amount of pixels for each unit of DisplaySize. Based on io.DisplayFramebufferScale. Generally (1,1) on normal display, (2,2) on OSX with Retina display.    # imgui.h:2640

    def __init__(self) -> None:                            # imgui.h:2643
        """ Functions"""
        pass
    def DeIndexAllBuffers(self) -> None:                   # imgui.h:2645
        """ Helper to convert all buffers from indexed to non-indexed, in case you cannot render indexed. Note: this is slow and most likely a waste of resources. Always prefer indexed rendering!"""
        pass
    def ScaleClipRects(self, fb_scale: ImVec2) -> None:    # imgui.h:2646
        """ Helper to scale the ClipRect field of each ImDrawCmd. Use if your final output buffer is at a different scale than Dear ImGui expects, or if there is a difference between your window resolution and framebuffer resolution."""
        pass

#-----------------------------------------------------------------------------
# [SECTION] Font API (ImFontConfig, ImFontGlyph, ImFontAtlasFlags, ImFontAtlas, ImFontGlyphRangesBuilder, ImFont)
#-----------------------------------------------------------------------------

class ImFontConfig:    # imgui.h:2653
    FontData:Any                   #          // TTF/OTF data    # imgui.h:2655
    FontDataSize:int               #          // TTF/OTF data size    # imgui.h:2656
    FontDataOwnedByAtlas:bool      # True     // TTF/OTF data ownership taken by the container ImFontAtlas (will delete memory itself).    # imgui.h:2657
    FontNo:int                     # 0        // Index of font within TTF/OTF file    # imgui.h:2658
    SizePixels:float               #          // Size in pixels for rasterizer (more or less maps to the resulting font height).    # imgui.h:2659
    OversampleH:int                # 3        // Rasterize at higher quality for sub-pixel positioning. Note the difference between 2 and 3 is minimal so you can reduce this to 2 to save memory. Read https://github.com/nothings/stb/blob/master/tests/oversample/README.md for details.    # imgui.h:2660
    OversampleV:int                # 1        // Rasterize at higher quality for sub-pixel positioning. This is not really useful as we don't use sub-pixel positions on the Y axis.    # imgui.h:2661
    PixelSnapH:bool                # False    // Align every glyph to pixel boundary. Useful e.g. if you are merging a non-pixel aligned font with the default font. If enabled, you can set OversampleH/V to 1.    # imgui.h:2662
    GlyphExtraSpacing:ImVec2       # 0, 0     // Extra spacing (in pixels) between glyphs. Only X axis is supported for now.    # imgui.h:2663
    GlyphOffset:ImVec2             # 0, 0     // Offset all glyphs from this font input.    # imgui.h:2664
    GlyphMinAdvanceX:float         # 0        // Minimum AdvanceX for glyphs, set Min to align font icons, set both Min/Max to enforce mono-space font    # imgui.h:2666
    GlyphMaxAdvanceX:float         # FLT_MAX  // Maximum AdvanceX for glyphs    # imgui.h:2667
    MergeMode:bool                 # False    // Merge into previous ImFont, so you can combine multiple inputs font into one ImFont (e.g. ASCII font + icons + Japanese glyphs). You may want to use GlyphOffset.y when merge font of different heights.    # imgui.h:2668
    FontBuilderFlags:int           # 0        // Settings for custom font builder. THIS IS BUILDER IMPLEMENTATION DEPENDENT. Leave as zero if unsure.    # imgui.h:2669
    RasterizerMultiply:float       # 1.0     // Brighten (>1.0) or darken (<1.0) font output. Brightening small fonts may be a good workaround to make them more readable.    # imgui.h:2670
    EllipsisChar:ImWchar           # -1       // Explicitly specify unicode codepoint of ellipsis character. When fonts are being merged first specified ellipsis will be used.    # imgui.h:2671

    # [Internal]
    DstFont:ImFont                 # imgui.h:2675

    def __init__(self) -> None:    # imgui.h:2677
        pass

class ImFontGlyph:    # imgui.h:2682
    """ Hold rendering data for one glyph.
     (Note: some language parsers may fail to convert the 31+1 bitfield members, in this case maybe drop store a single u32 or we can rework this)
    """
    AdvanceX:float  # Distance to next character (= data from font + ImFontConfig::GlyphExtraSpacing.x baked in)    # imgui.h:2687
    X0:float        # Glyph corners    # imgui.h:2688
    Y0:float        # Glyph corners    # imgui.h:2688
    X1:float        # Glyph corners    # imgui.h:2688
    Y1:float        # Glyph corners    # imgui.h:2688
    U0:float        # Texture coordinates    # imgui.h:2689
    V0:float        # Texture coordinates    # imgui.h:2689
    U1:float        # Texture coordinates    # imgui.h:2689
    V1:float        # Texture coordinates    # imgui.h:2689

class ImFontGlyphRangesBuilder:    # imgui.h:2694
    """ Helper to build glyph ranges from text/string data. Feed your application strings/characters to it then call BuildRanges().
     This is essentially a tightly packed of vector of 64k booleans = 8KB storage.
    """
    UsedChars:List[ImU32]                                          # Store 1-bit per Unicode code point (0=unused, 1=used)    # imgui.h:2696

    def __init__(self) -> None:                                    # imgui.h:2698
        pass
    def AddText(self, text: str, text_end: str = None) -> None:    # imgui.h:2703
        """ Add string (each character of the UTF-8 string are added)"""
        pass
    def AddRanges(self, ranges: ImWchar) -> None:                  # imgui.h:2704
        """ Add ranges, e.g. builder.AddRanges(ImFontAtlas::GetGlyphRangesDefault()) to force add all of ASCII/Latin+Ext"""
        pass
    def BuildRanges(self, out_ranges: List[ImWchar]) -> None:      # imgui.h:2705
        """ Output new ranges"""
        pass

class ImFontAtlasCustomRect:    # imgui.h:2709
    """ See ImFontAtlas::AddCustomRectXXX functions."""
    Width:int                      # Input    // Desired rectangle dimension    # imgui.h:2711
    Height:int                     # Input    // Desired rectangle dimension    # imgui.h:2711
    X:int                          # Output   // Packed position in Atlas    # imgui.h:2712
    Y:int                          # Output   // Packed position in Atlas    # imgui.h:2712
    GlyphID:int                    # Input    // For custom font glyphs only (ID < 0x110000)    # imgui.h:2713
    GlyphAdvanceX:float            # Input    // For custom font glyphs only: glyph xadvance    # imgui.h:2714
    GlyphOffset:ImVec2             # Input    // For custom font glyphs only: glyph display offset    # imgui.h:2715
    Font:ImFont                    # Input    // For custom font glyphs only: target font    # imgui.h:2716
    def __init__(self) -> None:    # imgui.h:2717
        pass

class ImFontAtlasFlags_(Enum):    # imgui.h:2722
    """ Flags for ImFontAtlas build"""
    None_ = 0
    NoPowerOfTwoHeight = 1 << 0  # Don't round the height to next power of two
    NoMouseCursors = 1 << 1      # Don't build software mouse cursors into the atlas (save a little texture memory)
    NoBakedLines = 1 << 2        # Don't build thick line textures into the atlas (save a little texture memory, allow support for point/nearest filtering). The AntiAliasedLinesUseTex features uses them, otherwise they will be rendered using polygons (more expensive for CPU/GPU).

class ImFontAtlas:    # imgui.h:2747
    """ Load and rasterize multiple TTF/OTF fonts into a same texture. The font atlas will build a single texture holding:
      - One or more fonts.
      - Custom graphics data needed to render the shapes needed by Dear ImGui.
      - Mouse cursor shapes for software cursor rendering (unless setting 'Flags |= ImFontAtlasFlags_NoMouseCursors' in the font atlas).
     It is the user-code responsibility to setup/build the atlas, then upload the pixel data into a texture accessible by your graphics api.
      - Optionally, call any of the AddFont*** functions. If you don't call any, the default font embedded in the code will be loaded for you.
      - Call GetTexDataAsAlpha8() or GetTexDataAsRGBA32() to build and retrieve pixels data.
      - Upload the pixels data into a texture within your graphics system (see imgui_impl_xxxx.cpp examples)
      - Call SetTexID(my_tex_id); and pass the pointer/identifier to your texture in a format natural to your graphics API.
        This value will be passed back to you during rendering to identify the texture. Read FAQ entry about ImTextureID for more details.
     Common pitfalls:
     - If you pass a 'glyph_ranges' array to AddFont*** functions, you need to make sure that your array persist up until the
       atlas is build (when calling GetTexData*** or Build()). We only copy the pointer, not the data.
     - Important: By default, AddFontFromMemoryTTF() takes ownership of the data. Even though we are not writing to it, we will free the pointer on destruction.
       You can set font_cfg->FontDataOwnedByAtlas=False to keep ownership of your data and it won't be freed,
     - Even though many functions are suffixed with "TTF", OTF data is supported just as well.
     - This is an old API and it is currently awkward for those and and various other reasons! We will address them in the future!
    """
    def __init__(self) -> None:                                                                                                                                                                                 # imgui.h:2749
        pass
    def AddFont(self, font_cfg: ImFontConfig) -> ImFont:                                                                                                                                                        # imgui.h:2751
        pass
    def AddFontDefault(self, font_cfg: ImFontConfig = None) -> ImFont:                                                                                                                                          # imgui.h:2752
        pass
    def AddFontFromFileTTF(self, filename: str, size_pixels: float, font_cfg: ImFontConfig = None, glyph_ranges: ImWchar = None) -> ImFont:                                                                     # imgui.h:2753
        pass
    def AddFontFromMemoryTTF(self, font_data: Any, font_size: int, size_pixels: float, font_cfg: ImFontConfig = None, glyph_ranges: ImWchar = None) -> ImFont:                                                  # imgui.h:2754
        """ Note: Transfer ownership of 'ttf_data' to ImFontAtlas! Will be deleted after destruction of the atlas. Set font_cfg->FontDataOwnedByAtlas=False to keep ownership of your data and it won't be freed."""
        pass
    def AddFontFromMemoryCompressedTTF(self, compressed_font_data: Any, compressed_font_size: int, size_pixels: float, font_cfg: ImFontConfig = None, glyph_ranges: ImWchar = None) -> ImFont:                  # imgui.h:2755
        """ 'compressed_font_data' still owned by caller. Compress with binary_to_compressed_c.cpp."""
        pass
    def AddFontFromMemoryCompressedBase85TTF(self, compressed_font_data_base85: str, size_pixels: float, font_cfg: ImFontConfig = None, glyph_ranges: ImWchar = None) -> ImFont:                                # imgui.h:2756
        """ 'compressed_font_data_base85' still owned by caller. Compress with binary_to_compressed_c.cpp with -base85 parameter."""
        pass
    def ClearInputData(self) -> None:                                                                                                                                                                           # imgui.h:2757
        """ Clear input data (all ImFontConfig structures including sizes, TTF data, glyph ranges, etc.) = all the data used to build the texture and fonts."""
        pass
    def ClearTexData(self) -> None:                                                                                                                                                                             # imgui.h:2758
        """ Clear output texture data (CPU side). Saves RAM once the texture has been copied to graphics memory."""
        pass
    def ClearFonts(self) -> None:                                                                                                                                                                               # imgui.h:2759
        """ Clear output font data (glyphs storage, UV coordinates)."""
        pass
    def Clear(self) -> None:                                                                                                                                                                                    # imgui.h:2760
        """ Clear all input and output."""
        pass

    # Build atlas, retrieve pixel data.
    # User is in charge of copying the pixels into graphics memory (e.g. create a texture with your engine). Then store your texture handle with SetTexID().
    # The pitch is always = Width * BytesPerPixels (1 or 4)
    # Building in RGBA32 format is provided for convenience and compatibility, but note that unless you manually manipulate or copy color data into
    # the texture (e.g. when using the AddCustomRect*** api), then the RGB pixels emitted will always be white (~75% of memory/bandwidth waste.
    def Build(self) -> bool:                                                                                                                                                                                    # imgui.h:2767
        """ Build pixels data. This is called automatically for you by the GetTexData*** functions."""
        pass

    #-------------------------------------------
    # Glyph Ranges
    #-------------------------------------------

    # Helpers to retrieve list of common Unicode ranges (2 value per range, values are inclusive, zero-terminated list)
    # NB: Make sure that your string are UTF-8 and NOT in your local code page. In C++11, you can create UTF-8 string literal using the u8"Hello world" syntax. See FAQ for details.
    # NB: Consider using ImFontGlyphRangesBuilder to build glyph ranges from textual data.
    def GetGlyphRangesDefault(self) -> ImWchar:                                                                                                                                                                 # imgui.h:2780
        """ Basic Latin, Extended Latin"""
        pass
    def GetGlyphRangesKorean(self) -> ImWchar:                                                                                                                                                                  # imgui.h:2781
        """ Default + Korean characters"""
        pass
    def GetGlyphRangesJapanese(self) -> ImWchar:                                                                                                                                                                # imgui.h:2782
        """ Default + Hiragana, Katakana, Half-Width, Selection of 2999 Ideographs"""
        pass
    def GetGlyphRangesChineseFull(self) -> ImWchar:                                                                                                                                                             # imgui.h:2783
        """ Default + Half-Width + Japanese Hiragana/Katakana + full set of about 21000 CJK Unified Ideographs"""
        pass
    def GetGlyphRangesChineseSimplifiedCommon(self) -> ImWchar:                                                                                                                                                 # imgui.h:2784
        """ Default + Half-Width + Japanese Hiragana/Katakana + set of 2500 CJK Unified Ideographs for common simplified Chinese"""
        pass
    def GetGlyphRangesCyrillic(self) -> ImWchar:                                                                                                                                                                # imgui.h:2785
        """ Default + about 400 Cyrillic characters"""
        pass
    def GetGlyphRangesThai(self) -> ImWchar:                                                                                                                                                                    # imgui.h:2786
        """ Default + Thai characters"""
        pass
    def GetGlyphRangesVietnamese(self) -> ImWchar:                                                                                                                                                              # imgui.h:2787
        """ Default + Vietnamese characters"""
        pass

    #-------------------------------------------
    # [BETA] Custom Rectangles/Glyphs API
    #-------------------------------------------

    # You can request arbitrary rectangles to be packed into the atlas, for your own purposes.
    # - After calling Build(), you can query the rectangle position and render your pixels.
    # - If you render colored output, set 'atlas->TexPixelsUseColors = True' as this may help some backends decide of prefered texture format.
    # - You can also request your rectangles to be mapped as font glyph (given a font + Unicode point),
    #   so you can render e.g. custom colorful icons and use them as regular glyphs.
    # - Read docs/FONTS.md for more details about using colorful icons.
    # - Note: this API may be redesigned later in order to support multi-monitor varying DPI settings.
    def AddCustomRectRegular(self, width: int, height: int) -> int:                                                                                                                                             # imgui.h:2800
        pass
    def AddCustomRectFontGlyph(self, font: ImFont, id: ImWchar, width: int, height: int, advance_x: float, offset: ImVec2 = ImVec2(0, 0)) -> int:                                                               # imgui.h:2801
        pass

    # [Internal]
    def GetMouseCursorTexData(self, cursor: ImGuiMouseCursor, out_offset: ImVec2, out_size: ImVec2, out_uv_border_0: ImVec2, out_uv_border_1: ImVec2, out_uv_fill_0: ImVec2, out_uv_fill_1: ImVec2) -> bool:    # imgui.h:2806
        pass

    #-------------------------------------------
    # Members
    #-------------------------------------------

    Flags:ImFontAtlasFlags                                                                                                                                                                                      # Build flags (see ImFontAtlasFlags_)    # imgui.h:2812
    TexID:ImTextureID                                                                                                                                                                                           # User data to refer to the texture once it has been uploaded to user's graphic systems. It is passed back to you during rendering via the ImDrawCmd structure.    # imgui.h:2813
    TexDesiredWidth:int                                                                                                                                                                                         # Texture width desired by user before Build(). Must be a power-of-two. If have many glyphs your graphics API have texture size restrictions you may want to increase texture width to decrease height.    # imgui.h:2814
    TexGlyphPadding:int                                                                                                                                                                                         # Padding between glyphs within texture in pixels. Defaults to 1. If your rendering method doesn't rely on bilinear filtering you may set this to 0 (will also need to set AntiAliasedLinesUseTex = False).    # imgui.h:2815
    Locked:bool                                                                                                                                                                                                 # Marked as Locked by ImGui::NewFrame() so attempt to modify the atlas will assert.    # imgui.h:2816

    # [Internal]
    # NB: Access texture data via GetTexData*() calls! Which will setup a default font for you.
    TexReady:bool                                                                                                                                                                                               # Set when texture was built matching current font input    # imgui.h:2820
    TexPixelsUseColors:bool                                                                                                                                                                                     # Tell whether our texture data is known to use colors (rather than just alpha channel), in order to help backend select a format.    # imgui.h:2821
    TexWidth:int                                                                                                                                                                                                # Texture width calculated during Build().    # imgui.h:2824
    TexHeight:int                                                                                                                                                                                               # Texture height calculated during Build().    # imgui.h:2825
    TexUvScale:ImVec2                                                                                                                                                                                           # = (1.0/TexWidth, 1.0/TexHeight)    # imgui.h:2826
    TexUvWhitePixel:ImVec2                                                                                                                                                                                      # Texture coordinates to a white pixel    # imgui.h:2827
    Fonts:List[ImFont]                                                                                                                                                                                          # Hold all the fonts returned by AddFont*. Fonts[0] is the default font upon calling ImGui::NewFrame(), use ImGui::PushFont()/PopFont() to change the current font.    # imgui.h:2828
    CustomRects:List[ImFontAtlasCustomRect]                                                                                                                                                                     # Rectangles for packing custom texture data into the atlas.    # imgui.h:2829
    ConfigData:List[ImFontConfig]                                                                                                                                                                               # Configuration data    # imgui.h:2830

    # [Internal] Font builder
    FontBuilderIO:ImFontBuilderIO                                                                                                                                                                               # Opaque interface to a font builder (default to stb_truetype, can be changed to use FreeType by defining IMGUI_ENABLE_FREETYPE).    # imgui.h:2834
    FontBuilderFlags:int                                                                                                                                                                                        # Shared flags (for all fonts) for custom font builder. THIS IS BUILD IMPLEMENTATION DEPENDENT. Per-font override is also available in ImFontConfig.    # imgui.h:2835

    # [Internal] Packing data
    PackIdMouseCursors:int                                                                                                                                                                                      # Custom texture rectangle ID for white pixel and mouse cursors    # imgui.h:2838
    PackIdLines:int                                                                                                                                                                                             # Custom texture rectangle ID for baked anti-aliased lines    # imgui.h:2839

    # [Obsolete]
    #typedef ImFontAtlasCustomRect    CustomRect;         // OBSOLETED in 1.72+
    #typedef ImFontGlyphRangesBuilder GlyphRangesBuilder; // OBSOLETED in 1.67+

class ImFont:    # imgui.h:2848
    """ Font runtime data and rendering
     ImFontAtlas automatically loads a default embedded font for you when you call GetTexDataAsAlpha8() or GetTexDataAsRGBA32().
    """
    # Members: Hot ~20/24 bytes (for CalcTextSize)
    IndexAdvanceX:List[float]                                                                                                                                                                              # 12-16 // out //            // Sparse. Glyphs->AdvanceX in a directly indexable way (cache-friendly for CalcTextSize functions which only this this info, and are often bottleneck in large UI).    # imgui.h:2851
    FallbackAdvanceX:float                                                                                                                                                                                 # 4     // out // = FallbackGlyph->AdvanceX    # imgui.h:2852
    FontSize:float                                                                                                                                                                                         # 4     // in  //            // Height of characters/line, set during loading (don't change after loading)    # imgui.h:2853

    # Members: Hot ~28/40 bytes (for CalcTextSize + render loop)
    IndexLookup:List[ImWchar]                                                                                                                                                                              # 12-16 // out //            // Sparse. Index glyphs by Unicode code-point.    # imgui.h:2856
    Glyphs:List[ImFontGlyph]                                                                                                                                                                               # 12-16 // out //            // All glyphs.    # imgui.h:2857
    FallbackGlyph:ImFontGlyph                                                                                                                                                                              # 4-8   // out // = FindGlyph(FontFallbackChar)    # imgui.h:2858

    # Members: Cold ~32/40 bytes
    ContainerAtlas:ImFontAtlas                                                                                                                                                                             # 4-8   // out //            // What we has been loaded into    # imgui.h:2861
    ConfigData:ImFontConfig                                                                                                                                                                                # 4-8   // in  //            // Pointer within ContainerAtlas->ConfigData    # imgui.h:2862
    ConfigDataCount:int                                                                                                                                                                                    # 2     // in  // ~ 1        // Number of ImFontConfig involved in creating this font. Bigger than 1 when merging multiple font sources into one ImFont.    # imgui.h:2863
    FallbackChar:ImWchar                                                                                                                                                                                   # 2     // out // = FFFD/'?' // Character used if a glyph isn't found.    # imgui.h:2864
    EllipsisChar:ImWchar                                                                                                                                                                                   # 2     // out // = '...'    // Character used for ellipsis rendering.    # imgui.h:2865
    DotChar:ImWchar                                                                                                                                                                                        # 2     // out // = '.'      // Character used for ellipsis rendering (if a single '...' character isn't found)    # imgui.h:2866
    DirtyLookupTables:bool                                                                                                                                                                                 # 1     // out //    # imgui.h:2867
    Scale:float                                                                                                                                                                                            # 4     // in  // = 1.      // Base font scale, multiplied by the per-window font scale which you can adjust with SetWindowFontScale()    # imgui.h:2868
    Ascent:float                                                                                                                                                                                           # 4+4   // out //            // Ascent: distance from top to bottom of e.g. 'A' [0..FontSize]    # imgui.h:2869
    Descent:float                                                                                                                                                                                          # 4+4   // out //            // Ascent: distance from top to bottom of e.g. 'A' [0..FontSize]    # imgui.h:2869
    MetricsTotalSurface:int                                                                                                                                                                                # 4     // out //            // Total surface in pixels to get an idea of the font rasterization/texture cost (not exact, we approximate the cost of padding between glyphs)    # imgui.h:2870

    def __init__(self) -> None:                                                                                                                                                                            # imgui.h:2874
        """ Methods"""
        pass
    def FindGlyph(self, c: ImWchar) -> ImFontGlyph:                                                                                                                                                        # imgui.h:2876
        pass
    def FindGlyphNoFallback(self, c: ImWchar) -> ImFontGlyph:                                                                                                                                              # imgui.h:2877
        pass

    # 'max_width' stops rendering after a certain width (could be turned into a 2 size). FLT_MAX to disable.
    # 'wrap_width' enable automatic word-wrapping across multiple lines to fit into given width. 0.0 to disable.
    def CalcWordWrapPositionA(self, scale: float, text: str, text_end: str, wrap_width: float) -> str:                                                                                                     # imgui.h:2885
        pass
    def RenderChar(self, draw_list: ImDrawList, size: float, pos: ImVec2, col: ImU32, c: ImWchar) -> None:                                                                                                 # imgui.h:2886
        pass
    def RenderText(self, draw_list: ImDrawList, size: float, pos: ImVec2, col: ImU32, clip_rect: ImVec4, text_begin: str, text_end: str, wrap_width: float = 0.0, cpu_fine_clip: bool = False) -> None:    # imgui.h:2887
        pass

    # [Internal] Don't use!
    def BuildLookupTable(self) -> None:                                                                                                                                                                    # imgui.h:2890
        pass
    def ClearOutputData(self) -> None:                                                                                                                                                                     # imgui.h:2891
        pass
    def GrowIndex(self, new_size: int) -> None:                                                                                                                                                            # imgui.h:2892
        pass
    def AddGlyph(self, src_cfg: ImFontConfig, c: ImWchar, x0: float, y0: float, x1: float, y1: float, u0: float, v0: float, u1: float, v1: float, advance_x: float) -> None:                               # imgui.h:2893
        pass
    def AddRemapChar(self, dst: ImWchar, src: ImWchar, overwrite_dst: bool = True) -> None:                                                                                                                # imgui.h:2894
        """ Makes 'dst' character/glyph points to 'src' character/glyph. Currently needs to be called AFTER fonts have been built."""
        pass
    def SetGlyphVisible(self, c: ImWchar, visible: bool) -> None:                                                                                                                                          # imgui.h:2895
        pass
    def IsGlyphRangeUnused(self, c_begin: int, c_last: int) -> bool:                                                                                                                                       # imgui.h:2896
        pass

#-----------------------------------------------------------------------------
# [SECTION] Viewports
#-----------------------------------------------------------------------------

class ImGuiViewportFlags_(Enum):    # imgui.h:2904
    """ Flags stored in ImGuiViewport::Flags, giving indications to the platform backends."""
    None_ = 0
    IsPlatformWindow = 1 << 0   # Represent a Platform Window
    IsPlatformMonitor = 1 << 1  # Represent a Platform Monitor (unused yet)
    OwnedByApp = 1 << 2         # Platform Window: is created/managed by the application (rather than a dear imgui backend)

class ImGuiViewport:    # imgui.h:2919
    """ - Currently represents the Platform Window created by the application which is hosting our Dear ImGui windows.
     - In 'docking' branch with multi-viewport enabled, we extend this concept to have multiple active viewports.
     - In the future we will extend this concept further to also represent Platform Monitor and support a "no main platform window" operation mode.
     - About Main Area vs Work Area:
       - Main Area = entire viewport.
       - Work Area = entire viewport minus sections used by main menu bars (for platform windows), or by task bar (for platform monitor).
       - Windows are generally trying to stay within the Work Area of their host viewport.
    """
    Flags:ImGuiViewportFlags       # See ImGuiViewportFlags_    # imgui.h:2921
    Pos:ImVec2                     # Main Area: Position of the viewport (Dear ImGui coordinates are the same as OS desktop/native coordinates)    # imgui.h:2922
    Size:ImVec2                    # Main Area: Size of the viewport.    # imgui.h:2923
    WorkPos:ImVec2                 # Work Area: Position of the viewport minus task bars, menus bars, status bars (>= Pos)    # imgui.h:2924
    WorkSize:ImVec2                # Work Area: Size of the viewport minus task bars, menu bars, status bars (<= Size)    # imgui.h:2925

    # Platform/Backend Dependent Data
    PlatformHandleRaw:Any          # None* to hold lower-level, platform-native window handle (under Win32 this is expected to be a HWND, unused for other platforms)    # imgui.h:2928

    def __init__(self) -> None:    # imgui.h:2930
        pass

    # Helpers

#-----------------------------------------------------------------------------
# [SECTION] Platform Dependent Interfaces
#-----------------------------------------------------------------------------

class ImGuiPlatformImeData:    # imgui.h:2942
    """ (Optional) Support for IME (Input Method Editor) via the io.SetPlatformImeDataFn() function."""
    WantVisible:bool               # A widget wants the IME to be visible    # imgui.h:2944
    InputPos:ImVec2                # Position of the input cursor    # imgui.h:2945
    InputLineHeight:float          # Line height    # imgui.h:2946

    def __init__(self) -> None:    # imgui.h:2948
        pass

#-----------------------------------------------------------------------------
# [SECTION] Obsolete functions and types
# (Will be removed! Read 'API BREAKING CHANGES' section in imgui.cpp for details)
# Please keep your copy of dear imgui up to date! Occasionally set '#define IMGUI_DISABLE_OBSOLETE_FUNCTIONS' in imconfig.h to stay ahead.
#-----------------------------------------------------------------------------

# <Namespace ImGui>
# </Namespace ImGui>


#-----------------------------------------------------------------------------



# Include imgui_user.h at the end of imgui.h (convenient for user to only explicitly include vanilla imgui.h)


# </litgen_stub>

# fmt: on
