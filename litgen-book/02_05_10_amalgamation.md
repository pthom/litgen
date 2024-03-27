# Headers amalgamation

Litgen processes files individually, and if a subclass is defined in a different file than its parent, inherited members may not be correctly bound.
Sometimes it is worthwhile to first generate an `Amalgamation Header` for a library before generating bindings for it.
An amalgamation header is a single header file that includes all the public headers of a library.

## Amalgamation utility

`litgen` provides a utility function `write_amalgamate_header_file` to generate an Amalgamation header file.
It is available in the `codemanip.amalgamated_header` module.

```python
from codemanip import amalgamated_header
```

And its API is as follows:
```python
@dataclass
class AmalgamationOptions:
    base_dir: str                     # The base directory of the headers
    local_includes_startwith: str     # Only headers whose name begin with this string should be included
    include_subdirs: list[str]        # Include only headers in these subdirectories

    main_header_file: str             # The main header file
    dst_amalgamated_header_file: str  # The destination file

def write_amalgamate_header_file(options: AmalgamationOptions) -> None:
    ...
```

`write_amalgamate_header_file` takes an `AmalgamationOptions` object as an argument and generates an Amalgamation header file.
It will include all the headers whose name starts with `local_includes_startwith` in the `base_dir` directory
and its subdirectories given in `include_subdirs`.

Note: it will include any file only once: if a file was already included by another file, it will not be included again.

## A concrete example

Let's take an example with the [Hello ImGui](https://github.com/pthom/hello_imgui) library.

This library is a C++ library
that wraps the [Dear ImGui](https://github.com/ocornut/imgui) library and provides additional functionalities.
Its bindings are generated using the `litgen` library, and are available in [Dear ImGui Bundle](https://pthom.github.io/imgui_bundle/introduction.html).

It has a directory structure as shown below.

```
src
├── CMakeLists.txt
├── hello_imgui
│     ├── CMakeLists.txt
│     ├── app_window_params.h
│     ├── hello_imgui.h           -->  ( hello_imgui.h is the main header, included by users
│     ├── imgui_window_params.h          it "#include" all other public API headers )
│     ├── ... (other headers)
│     │
│     ├── internal
│     │     ├── borderless_movable.cpp
│     │     ├── borderless_movable.h
│     │     ├── clock_seconds.cpp
│     │     ├── clock_seconds.h
│     │     ├── ... (other headers and c++ files)
│     │     ├── ... (not part of the public API)
```

And its main header file `hello_imgui.h` looks like this:

````cpp
#pragma once

#if defined(__ANDROID__) && defined(HELLOIMGUI_USE_SDL2)
// We need to include SDL, so that it can instantiate its main function under Android
#include "SDL.h"   // This include should *not* be in the amalgamation header
#endif

#include "hello_imgui/dpi_aware.h"             // Only headers whose name begin with
#include "hello_imgui/hello_imgui_assets.h"    // "hello_imgui" should be included
#include "hello_imgui/hello_imgui_error.h"     // in the amalgamation header
#include "hello_imgui/hello_imgui_logger.h"
#include "hello_imgui/image_from_asset.h"
#include "hello_imgui/imgui_theme.h"
#include "hello_imgui/hello_imgui_font.h"
#include "hello_imgui/runner_params.h"
#include "hello_imgui/hello_imgui_widgets.h"

#include <string>   // Other includes can be included as usual
#include <cstddef>
#include <cstdint>

... (other includes)
````

The code to generate the Amalgamation header file is as follows:

```python
from codemanip import amalgamated_header

options = amalgamated_header.AmalgamationOptions()
options.base_dir = hello_imgui_src_dir                # The base directory of the headers
options.local_includes_startwith = "hello_imgui/"     # Only headers whose name begin with "hello_imgui" should be included
options.include_subdirs = ["hello_imgui"]             # Include only headers in the hello_imgui directory
options.main_header_file = "hello_imgui.h"            # The main header file
options.dst_amalgamated_header_file = PYDEF_DIR + "/hello_imgui_amalgamation.h"  # The destination file

amalgamated_header.write_amalgamate_header_file(options)

```

And the generated Amalgamation header file `hello_imgui_amalgamation.h` will look like this:

```cpp
// THIS FILE WAS GENERATED AUTOMATICALLY. DO NOT EDIT.

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       hello_imgui.h                                                                          //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////

#if defined(__ANDROID__) && defined(HELLOIMGUI_USE_SDL2)
// We need to include SDL, so that it can instantiate its main function under Android
#include "SDL.h"
#endif


//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       hello_imgui/dpi_aware.h included by hello_imgui.h                                      //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#include "imgui.h"

namespace HelloImGui
{
... (content of hello_imgui/dpi_aware.h)
}
... (other includes)
```
