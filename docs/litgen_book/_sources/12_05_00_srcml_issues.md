# srcML - C++ parsing advices

srcML parses C++ 14 code into XML:
* it will *never* fail to construct an XML tree from C++ code
* it will *always* regenerate the exact same original C++ code from the XML tree

However, there are corner cases where the XML tree is not what you would expect. See some gotchas below:

## Don't use `={}` as function's default parameter value

See [related issue](https://github.com/srcML/srcML/issues/1833)

```cpp
void Foo(int v = {} );
```
is parsed as a declaration statement, whereas 

```cpp
void Foo(int v = 0 );
```
is correctly parsed as a function declaration.


