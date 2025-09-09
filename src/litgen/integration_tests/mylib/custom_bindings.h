#ifdef EXPLANATIONS
/*

## Introduction: about custom bindings

This code demonstrates how to add custom bindings to a C++ class and namespace using Litgen.
We will be adding custom methods to the `RootCustom::Foo` class and a custom function to the `RootCustom` namespace below.
```cpp
namespace RootCustom
{
    struct Foo
    {
        int mValue = 0;
    };
}
```

## Configuration for custom bindings

The following options are set in the Litgen configuration to add custom bindings.

**Notes:**
- We use LG_CLASS, LG_SUBMODULE, and LG_MODULE macros to refer to the current class, submodule, and module respectively.
- When adding a function to a  "namespace (C++)/submodule (Python)", ensure to use @staticmethod in the stub
  (since, for convenience only, the submodule is shown as a class in the stub)


```python
    options.custom_bindings.add_custom_bindings_to_class(
        qualified_class="RootCustom::Foo",
        stub_code='''
            def get_value(self) -> int:
                """Get the value"""
                ...
            def set_value(self, value: int) -> None:
                """Set the value"""
                ...
        ''',
        pydef_code="""
            LG_CLASS.def("get_value", [](const RootCustom::Foo& self){ return self.mValue; });
            LG_CLASS.def("set_value", [](RootCustom::Foo& self, int value){ self.mValue = value; });
        """,
    )
    options.custom_bindings.add_custom_bindings_to_submodule(
        qualified_namespace="RootCustom",
        stub_code='''
        @staticmethod
        def foo_namespace_function() -> int:
            """A custom function in the submodule"""
            ...
        ''',
        pydef_code="""
        // Example of adding a custom function to the submodule
        LG_SUBMODULE.def("foo_namespace_function", [](){ return 53; });
        """,
    )

    # options.custom_bindings.add_custom_bindings_to_main_module(
    #     stub_code='''
    #     def global_function() -> int:
    #         """A custom function in the global namespace"""
    #         ...
    #     ''',
    #     pydef_code="""
    #     // Example of adding a custom function to the main module
    #     LG_MODULE.def("global_function", [](){ return 64; });
    #     """,
    # )
```


**Resulting bindings:**

```python
# <submodule root_custom>
class root_custom:  # Proxy class that introduces typings for the *submodule* root_custom
    pass  # (This corresponds to a C++ namespace. All method are static!)

    class Foo:
        m_value: int = 0
        def __init__(self, m_value: int = 0) -> None:
            """Auto-generated default constructor with named params"""
            pass
        def get_value(self) -> int:
            """Get the value"""
            ...
        def set_value(self, value: int) -> None:
            """Set the value"""
            ...
    @staticmethod
    def foo_namespace_function() -> int:
        """A custom function in the submodule"""
        ...

# </submodule root_custom>
# def global_function() -> int:
```
*/
#endif  // EXPLANATIONS

namespace RootCustom
{
    struct Foo
    {
        int mValue = 0;
    };
}
