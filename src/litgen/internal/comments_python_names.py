"""In a stub, the C++ names in backticks become their Python names (see comments_python_names_in_backticks).
The pass runs on the whole stub, where backticks are found in comments and docstrings.

    `RunnerParams.callbacks.ShowMenus`       -> `RunnerParams.callbacks.show_menus`
    `HelloImGui::GetRunnerParams()`          -> `hello_imgui.get_runner_params()`  (with comments_python_modules)
    `ImGui::GetStyle().FontScaleDpi`         -> `imgui.get_style().font_scale_dpi` (another module: its names are checked)
    `HelloImGui::Run(const RunnerParams&)`   -> unchanged (C++ type syntax)

All or nothing: a text in backticks with a name that cannot be converted stays as is, never half converted.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from codemanip import code_utils

if TYPE_CHECKING:
    from litgen.internal.context.litgen_context import LitgenContext


_TEXT_IN_BACKTICKS = re.compile(r"`([^`\n]+)`")
# C++ that a Python name cannot replace: a declaration (a name after a type: `string prefName`), a statement (`;{}`)
_CPP_ONLY_SYNTAX = re.compile(r"->|&|\*|<|;|\{|\}|\bconst\b|\bstd::|[A-Za-z_]\w*\s+[A-Za-z_]")
# A chain of names: HelloImGui::GetRunnerParams, RunnerParams.callbacks.ShowMenus, ImGui::GetStyle().FontScaleDpi
_NAME_CHAIN = re.compile(r"[A-Za-z_]\w*(?:(?:::|\(\)\.|\.)[A-Za-z_]\w*)*")
_CHAIN_SEPARATOR = re.compile(r"(::|\(\)\.|\.)")
_DEFINED_NAME = re.compile(r"^\s*(?:def|class)\s+(\w+)", re.MULTILINE)
_ASSIGNED_NAME = re.compile(r"^\s*(\w+)\s*[:=]", re.MULTILINE)


def _is_camel_case(name: str) -> bool:
    return re.search(r"[a-z][A-Z]", name) is not None


def python_names_in_stub(stub_file: str) -> set[str]:
    """The names a stub defines (functions, classes, fields, enum values), for comments_python_names_of_other_modules.
    A superset: a docstring line such as "Returns:" counts too."""
    with open(stub_file, encoding="utf-8") as f:
        code = f.read()
    return set(_DEFINED_NAME.findall(code)) | set(_ASSIGNED_NAME.findall(code))


def python_names_in_backticks(lg_context: LitgenContext, stub_code: str) -> str:
    options = lg_context.options
    # With the custom bindings, which litgen did not adapt. Not the assigned names: a param of a signature written on
    # several lines (`runner_params: RunnerParams,`) would turn the type `RunnerParams` into `runner_params`
    functions_and_classes_in_this_stub = set(_DEFINED_NAME.findall(stub_code))

    def python_name(name: str, module: str | None, must_be_known: bool) -> str | None:
        """The Python name of a C++ name, or None if it cannot be converted"""
        names_of_other_module = options.comments_python_names_of_other_modules.get(module or "")
        if names_of_other_module is not None:
            for candidate in (code_utils.to_snake_case(name), name):  # a function or a field, or a class
                if candidate in names_of_other_module:
                    return candidate
            return None
        known = lg_context.python_names.get(name, "")
        if known == "":  # a name litgen did not adapt: a custom binding may define it
            if code_utils.to_snake_case(name) in functions_and_classes_in_this_stub:
                return code_utils.to_snake_case(name)
            return None if must_be_known or _is_camel_case(name) else name
        if known == name + "_":  # escaped since it is a Python name: in a comment, it may well be that one (`id(obj)`)
            return name
        return known  # None when the name has two Python forms

    def convert_chain(chain: str, is_call: bool, has_other_names: bool) -> str | None:
        parts = _CHAIN_SEPARATOR.split(chain)
        names, separators = parts[0::2], parts[1::2]
        is_lone_word = not separators and not is_call and not _is_camel_case(chain)
        if is_lone_word and chain not in lg_context.enum_value_names:
            # A lone word (`Render`, `size`) stays: it may be prose. An enum value (`Metal`) converts.
            # Next to other names, a capitalized word must convert, or `Begin/EndPlot` would become `Begin/end_plot`
            if not has_other_names or chain[0].islower() or chain in ("True", "False", "None"):
                return chain

        module = None
        if separators[:1] == ["::"] and names[0] in options.comments_python_modules:
            module = options.comments_python_modules[names[0]]
            names, separators = names[1:], separators[1:]
        converted: list[str] = []
        for i, name in enumerate(names):
            # a name with a module, before a "::" (`return_value_policy::reference`), or a lone word here, must be known
            must_be_known = module is not None or separators[i : i + 1] == ["::"] or is_lone_word
            python = python_name(name, module, must_be_known)
            if python is None:
                return None
            converted.append(python)
        r = converted[0]
        for separator, name in zip(separators, converted[1:]):
            r += ("." if separator == "::" else separator) + name
        return f"{module}.{r}" if module is not None else r

    def convert_text(match: re.Match[str]) -> str:
        text = match.group(1)
        if _CPP_ONLY_SYNTAX.search(text):
            return match.group(0)
        converted, position = "", 0
        chains = list(_NAME_CHAIN.finditer(text))
        for chain in chains:
            is_call = text[chain.end() : chain.end() + 1] == "("
            python = convert_chain(chain.group(0), is_call, has_other_names=len(chains) > 1)
            if python is None:
                return match.group(0)
            converted += text[position : chain.start()] + python
            position = chain.end()
        return "`" + converted + text[position:] + "`"

    return _TEXT_IN_BACKTICKS.sub(convert_text, stub_code)
