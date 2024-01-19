#include "api_marker.h"

#include <cstddef>
#include <cstdint>

struct Color4
{
    // The constructor params will automatically be "adapted" into std::array<uint8_t, 4>
    MY_API Color4(const uint8_t _rgba[4])
    {
        for (size_t i = 0; i < 4; ++i)
            rgba[i] = _rgba[i];
    }

    // This member will be stored as a modifiable numpy array
    uint8_t rgba[4];
};
