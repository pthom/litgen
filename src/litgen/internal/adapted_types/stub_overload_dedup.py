"""Deduplication of overloaded functions with identical Python signatures in stubs."""
from __future__ import annotations

from typing import Sequence

from litgen.internal.adapted_types.adapted_element import AdaptedElement


def dedup_stub_lines(elements: Sequence[AdaptedElement]) -> list[tuple[AdaptedElement, list[str]]]:
    """Deduplicate overloads and generate stub lines for each surviving element.

    C++ overloads on int vs unsigned int (or int vs size_t) map to identical
    Python signatures. This function:
    1. Skips duplicates (keeps the first occurrence)
    2. Strips the @overload decorator from functions that end up as the sole
       survivor of their overload group (mypy requires at least 2 overloads)

    Returns a list of (element, stub_lines) pairs for surviving elements.
    Callers handle spacing and progress bar as needed.
    """
    from litgen.internal.adapted_types.adapted_function import AdaptedFunction

    # First pass: determine which elements survive and count overloads per name
    emitted_signatures: set[str] = set()
    survivors: list[AdaptedElement] = []
    for elem in elements:
        if isinstance(elem, AdaptedFunction) and elem.is_overloaded:
            sig = elem.stub_python_signature()
            if sig in emitted_signatures:
                continue
            emitted_signatures.add(sig)
        survivors.append(elem)

    # Second pass: generate stub lines and count surviving overloads per name.
    # Functions that produce empty stub output (e.g., excluded templates) don't count.
    generated: list[tuple[AdaptedElement, list[str]]] = []
    overload_counts: dict[str, int] = {}
    for elem in survivors:
        element_lines = elem.stub_lines()
        generated.append((elem, element_lines))

        has_content = any(line.strip() for line in element_lines)
        if isinstance(elem, AdaptedFunction) and elem.is_overloaded and has_content:
            name = elem._stub_function_name_python()
            overload_counts[name] = overload_counts.get(name, 0) + 1

    # Names where only one overload survived: strip @overload
    singleton_overloads = {name for name, count in overload_counts.items() if count <= 1}

    # Third pass: strip @overload from singletons
    result: list[tuple[AdaptedElement, list[str]]] = []
    for elem, element_lines in generated:
        if (
            isinstance(elem, AdaptedFunction)
            and elem.is_overloaded
            and elem._stub_function_name_python() in singleton_overloads
        ):
            element_lines = [line for line in element_lines if line.strip() != "@overload"]
        result.append((elem, element_lines))

    return result
