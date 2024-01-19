from __future__ import annotations
import copy
from typing import Optional

from codemanip import code_utils

from srcmlcpp.cpp_types import CppFunctionDecl

from litgen.internal.adapted_types import AdaptedFunction


CppOperatorName = str
PythonOperatorName = str

# TODO: spaceship operator "<=>": "three way comparison" (need to split adapted_function in three!)


def _cpp_operator_unsupported_message(cpp_operator_name: CppOperatorName) -> Optional[str]:
    known_unsupported: dict[CppOperatorName, str] = {
        "++": 'increment operator not available in python (use "+=1" ?)',
        "--": 'decrement operator not available in python (use "-=1" ?)',
        "=": "operator= not supported in python. Consider using copy.copy or copy.deepcopy",
    }
    if cpp_operator_name in known_unsupported:
        return known_unsupported[cpp_operator_name]
    else:
        return None


def _cpp_to_python_operator_one_param(cpp_operator_name: CppOperatorName) -> Optional[PythonOperatorName]:
    known_conversions: dict[CppOperatorName, PythonOperatorName] = {
        "+": "__add__",
        "-": "__sub__",
        "*": "__mul__",
        "/": "__truediv__",
        "%": "__mod__",
        "[]": "__getitem__",
        "<": "__lt__",
        "<=": "__le__",
        "==": "__eq__",
        "!=": "__ne__",
        ">": "__gt__",
        ">=": "__ge__",
        "+=": "__iadd__",
        "-=": "__isub__",
        "*=": "__imul__",
        "/=": "__itruediv__",
        "%=": "__imod__",
        "<=>": "<=>",  # Specific case handled separately
    }
    if cpp_operator_name in known_conversions.keys():
        return known_conversions[cpp_operator_name]
    else:
        return None


def _cpp_to_python_operator_zero_param(cpp_operator_name: CppOperatorName) -> Optional[PythonOperatorName]:
    known_conversions: dict[CppOperatorName, PythonOperatorName] = {
        "-": "__neg__",  # Unary minus (negation)
        "+": "__pos__",  # Unary plus
        "bool": "__bool__",
    }
    if cpp_operator_name in known_conversions.keys():
        return known_conversions[cpp_operator_name]
    else:
        return None


def raise_if_unsupported_operator(cpp_function_decl: CppFunctionDecl) -> None:
    if not cpp_function_decl.is_operator():
        return
    if not cpp_function_decl.is_method():
        cpp_function_decl.raise_exception("operators are supported only when implemented as a member functions")

    operator_name = cpp_function_decl.operator_name()

    unsupported_message = _cpp_operator_unsupported_message(operator_name)
    if unsupported_message is not None:
        cpp_function_decl.raise_exception(unsupported_message)

    if operator_name == "()":
        return

    nb_parameters = len(cpp_function_decl.parameter_list.parameters)
    if nb_parameters == 0:
        if _cpp_to_python_operator_zero_param(operator_name) is None:
            cpp_function_decl.raise_exception(f'Unsupported zero param "operator {operator_name}"')
    elif nb_parameters == 1:
        if _cpp_to_python_operator_one_param(operator_name) is None:
            cpp_function_decl.raise_exception(f'Unsupported one param "operator {operator_name}"')
    else:
        cpp_function_decl.raise_exception(f'Unsupported "operator {operator_name}" (only 0 or 1 params are accepted')


def cpp_to_python_operator_name(cpp_function_decl: CppFunctionDecl) -> str:
    assert cpp_function_decl.is_operator() and cpp_function_decl.is_method()
    raise_if_unsupported_operator(cpp_function_decl)

    operator_name = cpp_function_decl.operator_name()

    if operator_name == "()":
        return "__call__"

    nb_parameters = len(cpp_function_decl.parameter_list.parameters)
    if nb_parameters == 0:
        r = _cpp_to_python_operator_zero_param(operator_name)
        assert r is not None
        return r
    elif nb_parameters == 1:
        r = _cpp_to_python_operator_one_param(operator_name)
        assert r is not None
        return r
    else:
        raise AssertionError("Logic Error in cpp_to_python_operator_name")


def is_spaceship_operator(adapted_function: AdaptedFunction) -> bool:
    if not adapted_function.cpp_adapted_function.is_operator():
        return False
    if not adapted_function.is_method():
        return False
    r = adapted_function.cpp_adapted_function.operator_name() == "<=>"
    return r


def cpp_split_spaceship_operator(adapted_spaceship_operator: AdaptedFunction) -> list[AdaptedFunction]:
    assert is_spaceship_operator(adapted_spaceship_operator)

    r: list[AdaptedFunction] = []

    def make_cmp(cpp_operator_name: str, test_to_run: str) -> AdaptedFunction:
        f = copy.deepcopy(adapted_spaceship_operator)
        f.cpp_adapted_function.return_type.typenames = ["bool"]
        f.cpp_adapted_function.function_name = f"operator{cpp_operator_name}"
        f.cpp_adapter_code = code_utils.unindent_code(
            f"""
        auto cmp = [&self](auto&& other) -> bool {{
            return self.operator<=>(other) {test_to_run};
        }};
        """,
            flag_strip_empty_lines=True,
        )
        f.lambda_to_call = "cmp"
        return f

    r.append(make_cmp("<", " < 0"))
    r.append(make_cmp("<=", " <= 0"))
    r.append(make_cmp("==", " == 0"))
    r.append(make_cmp(">=", " >= 0"))
    r.append(make_cmp(">", " > 0"))

    return r
