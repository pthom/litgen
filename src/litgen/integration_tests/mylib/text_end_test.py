from __future__ import annotations
import lg_mylib


def test_text_end():
    assert lg_mylib.text_end_length("Hello") == 5
    assert lg_mylib.text_end_length("é") == 2  # bytes, in UTF-8
    assert lg_mylib.text_end_length_optional("Hello") == -1  # text_end receives its default value (nullptr)
