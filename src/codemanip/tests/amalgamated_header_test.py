from __future__ import annotations
import os
import tempfile

from codemanip import amalgamated_header


def _make_options(base_dir: str, main_header_file: str) -> amalgamated_header.AmalgamationOptions:
    options = amalgamated_header.AmalgamationOptions()
    options.base_dir = base_dir
    options.local_includes_startwith = ""
    options.main_header_file = main_header_file
    return options


def _write(path: str, content: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def test_relative_main_header_in_base_dir() -> None:
    with tempfile.TemporaryDirectory() as d:
        _write(os.path.join(d, "foo.h"), "// foo content\n")
        content = amalgamated_header.amalgamation_content(_make_options(d, "foo.h"))
        assert "// foo content" in content


def test_absolute_main_header_file() -> None:
    # An absolute main_header_file must be used as-is, even when base_dir
    # does not contain it (this is the feature added by PR #41).
    with tempfile.TemporaryDirectory() as d:
        foo = os.path.join(d, "foo.h")
        _write(foo, "// foo content\n")
        options = _make_options(os.path.join(d, "does_not_exist"), foo)
        content = amalgamated_header.amalgamation_content(options)
        assert "// foo content" in content


def test_relative_header_found_in_subdir() -> None:
    with tempfile.TemporaryDirectory() as d:
        os.makedirs(os.path.join(d, "sub"))
        _write(os.path.join(d, "sub", "foo.h"), "// sub content\n")
        options = _make_options(d, "foo.h")
        options.include_subdirs = ["sub"]
        content = amalgamated_header.amalgamation_content(options)
        assert "// sub content" in content


def test_absolute_include_subdir() -> None:
    with tempfile.TemporaryDirectory() as d:
        abs_sub = os.path.join(d, "abs_sub")
        os.makedirs(abs_sub)
        _write(os.path.join(abs_sub, "foo.h"), "// abs sub content\n")
        options = _make_options(d, "foo.h")
        options.include_subdirs = [abs_sub]  # absolute search dir
        content = amalgamated_header.amalgamation_content(options)
        assert "// abs sub content" in content


def test_base_dir_takes_precedence_over_subdir() -> None:
    # When the same relative path exists in both base_dir and a subdir,
    # base_dir wins (the first matching directory in the search order).
    with tempfile.TemporaryDirectory() as d:
        os.makedirs(os.path.join(d, "sub"))
        _write(os.path.join(d, "foo.h"), "// from base\n")
        _write(os.path.join(d, "sub", "foo.h"), "// from sub\n")
        options = _make_options(d, "foo.h")
        options.include_subdirs = ["sub"]
        content = amalgamated_header.amalgamation_content(options)
        assert "// from base" in content
        assert "// from sub" not in content
