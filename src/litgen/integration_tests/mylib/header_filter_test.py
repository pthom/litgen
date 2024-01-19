from __future__ import annotations
import lg_mylib


def test_header_filter():
    # assert "add_c_array2" not in dir(lg_mylib)
    assert "obscure_function" not in dir(
        lg_mylib,
    )
