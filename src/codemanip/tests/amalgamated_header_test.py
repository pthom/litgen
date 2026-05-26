from __future__ import annotations
import os
import tempfile

import pytest

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


def test_angle_includes_are_external_by_default() -> None:
    # Default (only_quoted_includes_are_local=True): quoted includes are inlined,
    # angle-bracket includes (system headers) are left as external #include lines.
    # This is the no-prefix case (e.g. Dear ImGui).
    with tempfile.TemporaryDirectory() as d:
        _write(os.path.join(d, "local.h"), "// LOCAL INLINED\n")
        _write(os.path.join(d, "main.h"), '#include <vector>\n#include "local.h"\nint m();\n')
        content = amalgamated_header.amalgamation_content(_make_options(d, "main.h"))
        assert "// LOCAL INLINED" in content  # quoted include was inlined
        assert "#include <vector>" in content  # system include kept as external (not inlined / no crash)


def test_angle_local_includes_when_option_disabled() -> None:
    # With only_quoted_includes_are_local=False and a prefix, a prefix-matching
    # angle-bracket include is treated as local and inlined (requires the
    # angle-bracket path extraction to work).
    with tempfile.TemporaryDirectory() as d:
        os.makedirs(os.path.join(d, "mylib"))
        _write(os.path.join(d, "mylib", "foo.h"), "// FOO INLINED\n")
        _write(os.path.join(d, "main.h"), "#include <mylib/foo.h>\nint m();\n")
        options = _make_options(d, "main.h")
        options.local_includes_startwith = "mylib/"
        options.only_quoted_includes_are_local = False
        content = amalgamated_header.amalgamation_content(options)
        assert "// FOO INLINED" in content


def test_empty_prefix_with_angle_local_enabled_raises() -> None:
    # An empty prefix combined with only_quoted_includes_are_local=False would
    # classify every system include (<vector>, ...) as local: reject it early.
    with tempfile.TemporaryDirectory() as d:
        _write(os.path.join(d, "main.h"), "int m();\n")
        options = _make_options(d, "main.h")
        options.local_includes_startwith = ""
        options.only_quoted_includes_are_local = False
        with pytest.raises(ValueError, match="only_quoted_includes_are_local"):
            amalgamated_header.amalgamation_content(options)
