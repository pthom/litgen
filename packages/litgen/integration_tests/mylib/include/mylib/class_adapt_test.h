#include "mylib/api_marker.h"

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


/*
For info, here is the generated python stub:
--------------------------------------------

````python
class Color4:
    def __init__(self, _rgba: List[int]) -> None:
        pass

    rgba: np.ndarray  # ndarray[type=uint8_t, size=4]
````

And the generated pydef:
------------------------

````cpp
    auto pyClassColor4 =
        py::class_<Color4>
            (m, "Color4", "")
        .def(py::init(
            [](const std::array<uint8_t, 4>& _rgba) -> std::unique_ptr<Color4>
            {
                auto ctor_wrapper = [](const uint8_t _rgba[4]) ->  std::unique_ptr<Color4>
                {
                    return std::make_unique<Color4>(_rgba);
                };
                auto ctor_wrapper_adapt_fixed_size_c_arrays = [&ctor_wrapper](const std::array<uint8_t, 4>& _rgba) -> std::unique_ptr<Color4>
                {
                    auto r = ctor_wrapper(_rgba.data());
                    return r;
                };

                return ctor_wrapper_adapt_fixed_size_c_arrays(_rgba);
            }),     py::arg("_rgba"))
        .def_property("rgba",
            [](Color4 &self) -> pybind11::array
            {
                auto dtype = pybind11::dtype(pybind11::format_descriptor<uint8_t>::format());
                auto base = pybind11::array(dtype, {4}, {sizeof(uint8_t)});
                return pybind11::array(dtype, {4}, {sizeof(uint8_t)}, self.rgba, base);
            }, [](Color4& self) {},
            "")
        ;

````

 */
