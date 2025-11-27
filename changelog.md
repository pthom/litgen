# Changelog

## [Unreleased]

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
