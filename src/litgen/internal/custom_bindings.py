from dataclasses import dataclass
from typing import Dict, List
from srcmlcpp.cpp_types.scope.cpp_scope import CppScope
from codemanip import code_utils


@dataclass
class _StringReplacement:
    target: str
    replacement: str


class CustomBindings:
    """
    Manage user-defined custom bindings for classes, namespaces, and the main module.

    Litgen normally generates bindings automatically from C++ headers, but sometimes
    you may want to extend the API with extra methods or functions that are not
    present in the C++ code. `CustomBindings` lets you do this **without modifying
    your C++ headers**.

    You can attach:
      * extra methods/properties to a C++ **class**,
      * free functions to a **namespace** (shown as a Python submodule),
      * free functions to the **main module**.

    Each injection consists of:
      * **stub code** (Python declarations added to the generated ``.pyi`` file),
      * **pydef code** (C++ binding code inserted into the generated binding .cpp file).

    Placeholders are available inside `pydef_code`:
      * ``LG_CLASS`` → the current ``py::class_`` / ``nb::class_`` object.
      * ``LG_SUBMODULE`` → the current submodule (for a C++ namespace).
      * ``LG_MODULE`` → the main Python module object.

    **Note about `pydef_code` syntax:**:
      * You can use either **pybind11** or **nanobind** syntax in `pydef_code`, depending on which backend you are using.
      * Since the `pydef_code` is inserted into a function, limit yourself to statements that are valid **inside a function**: no function/class definitions, no `#include`. Use **lambdas** for small helpers.
      * When writing lambdas, **fully qualify C++ types** if the class/namespace isn’t open (e.g. `const RootNs::Foo& self`).
      * Argument helpers differ by backend (`py::arg` vs `nb::arg`). Use the one matching your active backend.

    Example:
        >>> options = litgen.LitgenOptions()
        >>> # Add custom methods to a class
        >>> options.custom_bindings.add_custom_bindings_to_class(
        ...     qualified_class="RootCustom::Foo",
        ...     stub_code='''
        ...         def get_value(self) -> int: ...
        ...         def set_value(self, value: int) -> None: ...
        ...     ''',
        ...     pydef_code='''
        ...         LG_CLASS.def("get_value", [](const RootCustom::Foo& self){ return self.mValue; });
        ...         LG_CLASS.def("set_value", [](RootCustom::Foo& self, int value){ self.mValue = value; });
        ...     ''',
        ... )
        >>> # Add a free function to a namespace
        >>> options.custom_bindings.add_custom_bindings_to_submodule(
        ...     qualified_namespace="RootCustom",
        ...     stub_code='''
        ...         @staticmethod
        ...         def foo_namespace_function() -> int: ...
        ...     ''',
        ...     pydef_code="LG_SUBMODULE.def(\"foo_namespace_function\", [](){ return 53; });",
        ... )
        >>> # Add a global function to the main module
        >>> options.custom_bindings.add_custom_bindings_to_main_module(
        ...     stub_code="def global_function() -> int: ...",
        ...     pydef_code="LG_MODULE.def(\"global_function\", [](){ return 64; });",
        ... )
    """

    # Holds custom binding code to be added to specific classes or namespaces
    _custom_binding_pydefs: Dict[CppScope, List[str]]
    _custom_binding_stubs: Dict[CppScope, List[str]]

    def add_custom_bindings_to_class(
        self,
        qualified_class: str,
        stub_code: str | None,
        pydef_code: str | None,
    ) -> None:
        """
        Add custom binding code to a specific C++ class.

        This lets you extend the generated Python bindings with extra methods,
        properties, or static methods on an existing class, **without modifying
        the C++ headers**.

        Args:
            qualified_class: Fully qualified C++ class name
                (e.g. ``"RootNs::Foo"``).
            stub_code: Python stub declarations to be inserted into the
                generated ``.pyi`` file. These should be written in normal
                Python syntax with type annotations.
            pydef_code: Custom binding code in C++ (pybind11/nanobind syntax).
                You can use the placeholder ``LG_CLASS`` to refer to the bound
                ``py::class_`` / ``nb::class_`` object.

        Example:
            >>> options.custom_bindings.add_custom_bindings_to_class(
            ...     qualified_class="RootNs::Foo",
            ...     stub_code='''
            ...         def get_value(self) -> int: ...
            ...         def set_value(self, value: int) -> None: ...
            ...     ''',
            ...     pydef_code='''
            ...         LG_CLASS.def("get_value", [](const RootNs::Foo& self){ return self.mValue; });
            ...         LG_CLASS.def("set_value", [](RootNs::Foo& self, int value){ self.mValue = value; });
            ...     ''',
            ... )
        """
        self._do_add_custom_bindings(qualified_class, stub_code, pydef_code)

    def add_custom_bindings_to_submodule(
        self,
        qualified_namespace: str,
        stub_code: str | None,
        pydef_code: str | None,
    ) -> None:
        """
        Add custom binding code to a C++ namespace (exposed as a Python submodule).

        Args:
            qualified_namespace: Fully qualified C++ namespace
                (e.g. ``"RootNs"``).
            stub_code: Python stub declarations to be inserted in the proxy
                class representing this submodule in the generated ``.pyi``.
                **Functions here should be marked ``@staticmethod``.**
            pydef_code: Custom binding code in C++ (pybind11/nanobind syntax).
                Use the placeholder ``LG_SUBMODULE`` to refer to the submodule
                object.

        Example:
            >>> options.custom_bindings.add_custom_bindings_to_submodule(
            ...     qualified_namespace="RootNs",
            ...     stub_code='''
            ...         @staticmethod
            ...         def foo_namespace_function() -> int: ...
            ...     ''',
            ...     pydef_code='''
            ...         LG_SUBMODULE.def("foo_namespace_function", [](){ return 53; });
            ...     ''',
            ... )
        """
        self._do_add_custom_bindings(qualified_namespace, stub_code, pydef_code)

    def add_custom_bindings_to_main_module(
        self,
        stub_code: str | None,
        pydef_code: str | None,
    ) -> None:
        """
        Add custom binding code to the top-level Python module.

        Args:
            stub_code: Python stub declarations to be inserted into the
                generated ``.pyi`` at module level.
            pydef_code: Custom binding code in C++ (pybind11/nanobind syntax).
                Use the placeholder ``LG_MODULE`` to refer to the main module
                object.

        Example:
            >>> options.custom_bindings.add_custom_bindings_to_main_module(
            ...     stub_code='''
            ...         def global_function() -> int: ...
            ...     ''',
            ...     pydef_code='''
            ...         LG_MODULE.def("global_function", [](){ return 64; });
            ...     ''',
            ... )
        """
        self._do_add_custom_bindings("", stub_code, pydef_code)

    def __init__(self) -> None:
        self._custom_binding_pydefs = {}
        self._custom_binding_stubs = {}

    def _get_custom_bindings_ref(self, is_pydef: bool) -> Dict[CppScope, List[str]]:
        return self._custom_binding_pydefs if is_pydef else self._custom_binding_stubs

    def _do_add_cleaned_code(
        self,
        qualified_scope: str,
        code: str | None,
        is_pydef: bool = False
    ) -> None:
        if code is None:
            return
        code = code_utils.unindent_code(code)
        code = code_utils.strip_first_and_last_lines_if_empty(code)

        custom_binding_codes = self._get_custom_bindings_ref(is_pydef)
        scope = CppScope.from_string(qualified_scope)
        if scope not in custom_binding_codes:
            custom_binding_codes[scope] = []
        custom_binding_codes[scope].append(code)

    def _do_add_custom_bindings(
        self,
        qualified_scope: str,
        stub_code: str | None,
        pydef_code: str | None,
    ) -> None:
        self._do_add_cleaned_code(qualified_scope, stub_code, is_pydef=False)
        self._do_add_cleaned_code(qualified_scope, pydef_code, is_pydef=True)

    def _make_custom_code(self,
                          scope: CppScope,
                          is_pydef: bool,
                          replacements: List[_StringReplacement]) -> str | None:
        custom_binding_codes = self._get_custom_bindings_ref(is_pydef)
        if scope not in custom_binding_codes:
            return None

        custom_codes = custom_binding_codes[scope]
        codes = []
        for custom_code in custom_codes:
            codes.append(custom_code)

        result = "\n".join(codes)
        for r in replacements:
            result = result.replace(r.target, r.replacement)
        if not result.startswith("\n"):
            result = "\n" + result
        if not result.endswith("\n"):
            result = result + "\n"
        return result

    def _pub_make_class_custom_code(
            self,
            qualified_class_name: str,
            pydef_class_var_name: str,
            is_pydef: bool
    ) -> str | None:
        replacements = [_StringReplacement("LG_CLASS", pydef_class_var_name)]
        qual_class_scope = CppScope.from_string(qualified_class_name)
        result = self._make_custom_code(
            qual_class_scope,
            is_pydef=is_pydef,
            replacements=replacements
        )
        return result

    def _pub_make_submodule_custom_code(
            self,
            qualified_class_name: str,
            pydef_submodule_var_name: str,
            is_pydef: bool
    ) -> str | None:
        replacements = [_StringReplacement("LG_SUBMODULE", pydef_submodule_var_name)]
        qual_class_scope = CppScope.from_string(qualified_class_name)
        result = self._make_custom_code(
            qual_class_scope,
            is_pydef=is_pydef,
            replacements=replacements
        )
        return result

    def _pub_make_main_module_custom_code(
            self,
            pydef_main_module_var_name: str,
            is_pydef: bool
    ) -> str | None:
        replacements = [_StringReplacement("LG_MODULE", pydef_main_module_var_name)]
        qual_class_scope = CppScope.from_string("")
        result = self._make_custom_code(
            qual_class_scope,
            is_pydef=is_pydef,
            replacements=replacements
        )
        return result
