# Changelog

## [Unreleased]

## [0.21.0] - WIP Unreleased

### Changed
- `RegexOrMatcher` inside `LitgenOptions`:
  All options ending with the `__regex` suffix can now be either a regex string (`str`),
  or a callable `Callable[[str], bool]`
