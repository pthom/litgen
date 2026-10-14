# Changelog

## [Unreleased]

- Default values: nothing is translated inside a C++ string literal any more. A printf format such as `"%.3f"` was published as `"%.3"` in the stubs (its `3f` was taken for a float literal)
- `codemanip.code_utils.append_regex(current, *extra)`: typed helper to extend a regex option (replaces `options.xxx__regex += "|..."`, which does not type-check since these options may also hold a matcher function)
- Custom bindings: new placeholder `LG_CPP_CLASS_NAME` (C++ class name with template arguments), so that custom class bindings can be written for template specializations
- `member_exclude_by_name_and_class__regex`: document that it also applies to methods (it already did), with tests
- Generated stub files are formatted with black in memory and written only when their content changes (their mtime is preserved otherwise, which matters when a build system depends on them)
- nanobind: require nanobind >= 3.0.1, and emit `NB_TRAMPOLINE(Base)` without the size argument (deprecated in nanobind 3)
- C buffers: a 1D array with zero or one element is accepted whatever its stride (a contiguous single-element view such as `a[:, 0]` was rejected)
- `fn_params_text_end_names__regex` (off by default): a "text end" param (`const char* text, const char* text_end`) leaves the Python signature, and receives its default value or the end of the text. A Python string could not point inside the text, so C++ read from an unrelated address
- Stubs: a comment-only line that contains a `#` (a URL anchor, for example) is no longer aligned as an end-of-line comment: the rest of the line was pushed to the column of the block's other comments
- Stubs: the main module's custom bindings are between `# <custom_bindings>` and `# </custom_bindings>`, as a submodule between its markers: a doc generator can tell them from the stubs generated from the headers

## [0.22.0] - 2025-11-27

- Can publish functions that return a pointer to pointer
- Improved doc
- added gil_scoped_release support to functions using a regex (thanks to @gfabiano)

## New Contributors
- @gfabiano made their first contribution in https://github.com/pthom/litgen/pull/37


## [0.21.0] - 2025-09-09

### Added
- **Custom bindings API**:
  You can now manually extend the generated bindings without modifying your C++ headers.
  - `LitgenOptions.custom_bindings.add_custom_code_to_class(...)`
  - `LitgenOptions.custom_bindings.add_custom_code_to_submodule(...)`
  - `LitgenOptions.custom_bindings.add_custom_code_to_main_module(...)`
  This allows you to inject extra methods, functions, or properties into classes, namespaces, or the main module.
  Placeholders (`LG_CLASS`, `LG_SUBMODULE`, `LG_MODULE`) are available in `pydef_code` and are replaced automatically.
  See the manual section **"Manually add custom bindings"** for details and examples.

- Added `customize-class-bases-option` feature (thanks @jnastarot, #26)

### Changed
- All options ending with the `__regex` suffix in `LitgenOptions` (e.g. `fn_exclude_by_name__regex`)
  now accept either:
  - a regex string (`str`), or
  - a callable (`Callable[[str], bool]`).
  This gives more flexibility when filtering functions, classes, or members.

### Fixed
- Enums can now derive from `enum.IntEnum` or `enum.IntFlag`
- Added `.none()` to arguments when `std::optional` is used
- Do not publish function implementations containing `::`
- Fixed case when a return value had a reference (#26, @jnastarot)

## New Contributors
- @jnastarot made their first contribution in https://github.com/pthom/litgen/pull/26

**Full Changelog**: https://github.com/pthom/litgen/compare/v0.20.0...v0.21.0
