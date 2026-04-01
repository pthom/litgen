# srcML - C++ parsing advices

srcML parses C++ 14 code into XML:
* it will *never* fail to construct an XML tree from C++ code
* it will *always* regenerate the exact same original C++ code from the XML tree

However, there are corner cases where the XML tree is not what you would expect.
See some gotchas below.


## srcML

### Don't use `={}` as function's default parameter value

See [related issue](https://github.com/srcML/srcML/issues/1833)

```cpp
void Foo(int v = {} );
```
is parsed as a declaration statement, whereas

```cpp
void Foo(int v = 0 );
```
is correctly parsed as a function declaration.


### Note about mixing auto return and API markers
Mixing API marker and auto return type is not supported.

 Such functions will not be parsed correctly!

```cpp
    MY_API auto my_modulo(int a, int b)
    MY_API auto my_pow(double a, double b) -> double
```


## Python bindings

### Note about function arrow-return type notation:

Arrow return notation function are correctly exported to python, including their return type.
For example,
```cpp
auto my_pow(double a, double b) -> double
```
Will result in:
```python
def my_pow(a: float, b: float) -> float:
pass
```

### Note about function inferred return type notation:

Functions with an inferred return type are correctly exported to python, however the published return type is unknown and will be marked as "Any"
For example,
```cpp
auto my_pow(double a, double b)
```
Will result in:
```python
def my_pow(a: float, b: float) -> Any:
pass
```


## Why litgen uses srcML instead of libclang

### srcML's strengths for binding generation

**Fragment parsing** — srcML can parse a single line like `std::string foo(int a, std::string& b);` and return a structured AST instantly. No includes, no compilation context needed. This is heavily used in litgen's tests and internal processing.

**No compilation environment required** — Users just point at a header file. No `compile_commands.json`, no `-I` flags, no need to resolve transitive dependencies. This keeps the tool accessible and easy to use.

**Comment and layout preservation** — Comments are first-class nodes in srcML's XML output. This is essential for generating `.pyi` stubs with accurate docstrings.

**Preprocessor visibility** — srcML preserves `#ifdef` branches as-is, allowing litgen to see all conditional paths. Clang evaluates preprocessor directives and only exposes the resolved view.

### What libclang would require

- A valid compilation setup for every header (include paths, defines, system headers)
- `std::string` wouldn't even resolve without `#include <string>` — partial code fails or produces incomplete ASTs
- Wrapping fragments in dummy translation units with appropriate preambles
- Reimplementing comment extraction (possible but less natural)

### What libclang would gain

- Full type resolution and template instantiation
- Better handling of complex C++ (deeply nested templates, SFINAE, concepts)
- Active maintenance and C++ standard evolution support

### Why the tradeoff favors srcML

For binding generation from **curated public headers** — which are designed to be human-readable and typically avoid deep template metaprogramming — srcML's lightweight, syntax-oriented approach is a better fit. The full semantic analysis that Clang provides is rarely needed in this context.

Switching to Clang would be a significant migration with worse ergonomics for a marginal accuracy gain on litgen's actual use cases.

Howvever, this means we have to deal with some quirks as shown in this page. 
