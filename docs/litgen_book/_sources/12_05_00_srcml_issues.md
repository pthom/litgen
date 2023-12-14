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
