# Quickstart

This page shows how to get results with litgen **in 5 minutes**, without setting up a full repo.
You will generate Python stub code and C++ binding code from a simple header.

To actually compile and import the bindings, please use the [Litgen Template](https://github.com/pthom/litgen_template).

---

## Step 1: Install litgen

```bash
pip install litgen
```

or, for the latest development version:

```bash
pip install "litgen@git+https://github.com/pthom/litgen"
```

---

## Step 2: Write a small C++ header

```cpp
// file: mylib.h
#pragma once

inline int add(int a, int b) { return a + b; }

struct Point {
    int x = 0;
    int y = 0;
};
```

---

## Step 3: Run litgen

```python
# file: generate.py
import litgen

options = litgen.LitgenOptions()
gen = litgen.generate_code_for_file(options, "mylib.h")

print("===================================")
print("=== Generated stub code (.pyi) ===")
print("===================================")
print(gen.stub_code)
print()
print("===================================")
print("=== Generated pydef code (.cpp) ===")
print("===================================")
print(gen.pydef_code)
```

Run it:

```bash
python generate.py
```

---

## Step 4: Inspect the output

**Stub file (Python declarations, `.pyi`):**

```python
def add(a: int, b: int) -> int:
    pass

class Point:
    x: int = 0
    y: int = 0
    def __init__(self, x: int = 0, y: int = 0) -> None:
        """Auto-generated default constructor with named params"""
        pass
```

**Pydef file (C++ binding code, `.cpp`):**

```cpp
m.def("add",
    add, py::arg("a"), py::arg("b"));


auto pyClassPoint =
    py::class_<Point>
        (m, "Point", "")
    .def(py::init<>([](
    int x = 0, int y = 0)
    {
        auto r_ctor_ = std::make_unique<Point>();
        r_ctor_->x = x;
        r_ctor_->y = y;
        return r_ctor_;
    })
    , py::arg("x") = 0, py::arg("y") = 0
    )
    .def_readwrite("x", &Point::x, "")
    .def_readwrite("y", &Point::y, "")
    ;
```

*(exact output may vary depending on options and backend)*

---

## Step 5: A small tweak (optional)

You can adjust `LitgenOptions` to control what gets generated.
For example, to exclude functions whose name starts with `_`:

```python
options.fn_exclude_by_name__regex = r"^_"
```

Or to add a custom method, add this before calling `generate_code_for_file`:

```python
options.custom_bindings.add_custom_bindings_to_class(
    "Point",
    stub_code="def norm(self) -> float: ...",
    pydef_code="LG_CLASS.def(\"norm\", [](const Point& p){ return sqrt(p.x*p.x + p.y*p.y); });"
)
```

and you will get this stub:

```python
class Point:
    x: int = 0
    y: int = 0
    def __init__(self, x: int = 0, y: int = 0) -> None:
        """Auto-generated default constructor with named params"""
        pass

    def norm(self) -> float: ...
```

---

## Next steps

You now know how to generate stubs and C++ binding code.

To **compile** these bindings into an importable Python module (with CMake, scikit-build, packaging, CI, etc.), please use the [Litgen Template](https://github.com/pthom/litgen_template).

Continue reading the [User Guide](https://pthom.github.io/litgen) for more details on how to customize the generation.
