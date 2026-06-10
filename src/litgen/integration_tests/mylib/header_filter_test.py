from __future__ import annotations
import lg_mylib


def test_header_filter():
    # assert "add_c_array2" not in dir(lg_mylib)
    assert "obscure_function" not in dir(
        lg_mylib,
    )


def test_header_filter_if_expression():
    # `#if MACRO` / `#if defined(MACRO)` regions are filtered like `#ifdef`:
    # the macro name in the condition is matched against header_filter_acceptable__regex.

    # OBSCURE_OPTION is not acceptable => `#if OBSCURE_OPTION` region is not exported
    assert "obscure_function_in_if" not in dir(lg_mylib)

    # HEADER_FILTER_ACCEPTABLE_IF is acceptable => both `#if` forms are exported
    assert lg_mylib.filter_acceptable_if_function() == 44
    assert lg_mylib.filter_acceptable_defined_function() == 45


def test_header_filter_else_branch_is_dropped():
    # The `#else` branch of an accepted region is inactive: only the primary branch is
    # exported, the `#else` body is dropped.
    assert lg_mylib.else_branch_primary() == 46
    assert "else_branch_secondary" not in dir(lg_mylib)
