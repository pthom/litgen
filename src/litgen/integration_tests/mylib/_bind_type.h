#pragma once
#include "api_marker.h"

MY_API bool bindings_with_nanobind()
{
#ifdef BINDINGS_WITH_NANOBIND
    return true;
#else
    return false;
#endif
}

MY_API bool bindings_with_pybind()
{
#ifdef BINDINGS_WITH_PYBIND
    return true;
#else
    return false;
#endif
}
