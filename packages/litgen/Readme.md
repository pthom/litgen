# litgen: Main Python package that generates bindings

Note about function arrow-return type notation:
-----------------------------------------------
Arrow return notation function are correctly exported, including their return type.
For example,
````cpp
auto my_pow(double a, double b) -> double
````
Will result in:
```python
def my_pow(a: float, b: float) -> float:
pass
````

Note about function inferred return type notation:
-----------------------------------------------
Functions with an inferred return type are correctly exported,
however the published return type is unknown and will be marked as "Any"
For example,
````cpp
auto my_pow(double a, double b)
````
Will result in:
```python
def my_pow(a: float, b: float) -> Any:
pass
````


Note about mixing auto return and API markers
---------------------------------------------
Mixing API marker and auto return type is not supported. Such function would not be exported!

````cpp
    MY_API auto my_modulo(int a, int b)
    MY_API auto my_pow(double a, double b) -> double
````
