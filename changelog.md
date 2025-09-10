# Changelog

## [Unreleased]

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

### Changed
- All options ending with the `__regex` suffix in `LitgenOptions` (e.g. `fn_exclude_by_name__regex`)
  now accept either:
  - a regex string (`str`), or
  - a callable (`Callable[[str], bool]`).
  This gives more flexibility when filtering functions, classes, or members.
