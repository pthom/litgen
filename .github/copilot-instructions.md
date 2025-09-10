# AI contributor guide for this repository (litgen)

This repo hosts litgen, a C++→Python bindings generator built on srcML, plus helper libs. Use these notes to navigate, build, test, and extend consistently.

## What this project does (quick summary)
- Generates Python bindings from C++ headers with either pybind11 or nanobind.
- Produces two artifacts per API surface:
  - C++ binding code (to compile into a Python extension)
  - Python stubs (.pyi) with accurate signatures and docs for IDEs
- Uses srcML to parse C++14 while preserving comments and preprocessor, enabling high-fidelity doc transfer.


## Project map and entry points
- Python packages (under `src/`):
  - `litgen/` — core generator: options, parsing/orchestration, code emission. Key: `options.py`, `litgen_generator.py`, `cli/`, `integration_tests/`.
  - `codemanip/` — code utilities. Key: `amalgamated_header.py` (see “Amalgamation”).
  - `srcmlcpp/` — srcML wrappers and helpers. Key: `cli/srcmlcpp_cli.py`, `srcml_wrapper.py`.
- CLI scripts (declared in `pyproject.toml`):
  - `litgen-cli` → `litgen.cli.litgen_cli:main`
  - `srcmlcpp-cli` → `srcmlcpp.cli.srcmlcpp_cli:main`

## Build, test, docs (local)
- Python ≥ 3.10. Create venv, then:
  - Install dev deps: `just install_requirements_dev`
  - Editable install: `just install_litgen_editable`
  - Lint/type/format: `just black`, `just mypy`
  - Run all checks (mypy/black/ruff/pytest): `./ci_scripts/devel/run_all_checks.sh`
  - Build docs (JupyterBook): `just docs` → `litgen-book/`

## CI expectations
- Workflow `.github/workflows/pip.yml` runs on macOS/Ubuntu/Windows:
  - `just install_requirements_dev` → `just install_litgen_editable` → `just black` → `just mypy` → integration tests (both backends).

## Integration tests and backends
- Location: `src/litgen/integration_tests/` ("mylib").
- Recipes:
  - Pybind11 flow: `just integration_tests_pybind`
  - Nanobind flow: `just integration_tests_nanobind`
  - Both: `just integration_tests`
- Backend toggle used by scripts:
  - `LITGEN_USE_NANOBIND=OFF` → pybind11
  - `LITGEN_USE_NANOBIND=ON` → nanobind
- Pytest targets in `pytest.ini`: `src/litgen`, `src/codemanip`, `src/srcmlcpp`.

## Amalgamation (important for multi-header APIs)
- If classes span multiple headers, inherited members can be missed. Generate a single “amalgamation header”.
- Use `codemanip.amalgamated_header.write_amalgamate_header_file(AmalgamationOptions)` with: `base_dir`, `local_includes_startwith`, `include_subdirs`, `main_header_file`, `dst_amalgamated_header_file`.
- See `litgen-book/02_05_10_amalgamation.md` for rationale and example.

## srcML parsing gotchas that affect bindings
- Don’t use default params like `={}`; use concrete values (e.g., `= 0`).
- Avoid mixing API visibility markers with `auto` return types (parsing breaks).
- Arrow returns (`auto f(...) -> T`) map to Python annotations; inferred `auto` returns become `typing.Any`.
- Details: `litgen-book/12_05_00_srcml_issues.md`.

## Conventions and packaging
- Black (line length 120), Ruff, Mypy are enforced (see `pyproject.toml`, `requirements-dev.txt`).
- Packaging: Hatchling; wheels include `src/litgen`, `src/codemanip`, `src/srcmlcpp` via `[tool.hatch.build.targets.wheel].packages`.
- Docs live in `litgen-book/`; PDF/site built via `generate_litgen_book.sh`.

## Where to implement
- New generator options/behavior: `src/litgen/options.py`, `src/litgen/litgen_generator.py`; tests under `src/litgen/tests/`.
- Code manipulation helpers: `src/codemanip/`; tests under `src/codemanip/tests/`.
- srcML integration/CLI: `src/srcmlcpp/`; tests under `src/srcmlcpp/tests/`.
- Changes should keep both pybind11 and nanobind flows green (`just integration_tests`).

If something’s unclear, say which area you’re touching; we’ll extend these notes with concrete examples from that code path.
