#include "api_marker.h"

//
// Pointer params that accept None: with options.fn_params_pointer_accept_none__regex = r"^accept_none_", the pointer
// params of the matching functions accept None (with nanobind, a pointer param refuses None unless it has a default).
//
// The following functions will be exported with the following python signatures:
// -->    def accept_none_value_or(point: Optional[PointAcceptNone], default_value: int) -> int:
// -->    class PointAcceptNone:
// -->        def accept_none_add(self, other: Optional[PointAcceptNone]) -> int:
//
struct PointAcceptNone
{
    int value = 0;
    MY_API int accept_none_add(const PointAcceptNone* other) const { return other ? value + other->value : value; }
};

MY_API inline int accept_none_value_or(const PointAcceptNone* point, int default_value)
{
    return point ? point->value : default_value;
}
