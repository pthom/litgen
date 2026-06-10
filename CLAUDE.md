# litgen — Claude Code Guide

When helping users with coding tasks, please follow these guidelines to ensure high-quality, maintainable code.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.
- If a solution becomes complex (multiple cascading changes, need for workarounds), STOP and explain the difficulty. Present options rather than plowing ahead.

**If you encounter an API in the codebase which is awkward to use**
- Do not circumvent it with a hack. Instead, surface the issue and ask for clarification or improvement.
- The same goes for code smells or patterns that seem out of place. Don't just "make it work" - stop implementing, then communicate the underlying problem so it can be addressed properly in collaboration with the user.

**Before implementing a solution, wait for the user to finish evaluating alternatives.**


## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.



---

## 5. Project-specific guidance

### What this project is

**litgen** is an automatic Python bindings generator for C++ libraries using pybind11 or nanobind.
It parses C++ headers via `srcml` (XML-based C++ parser), adapts the AST, and generates both
`.cpp` pydef files and `.pyi` stub files. It is the engine behind the Python bindings of
[Dear ImGui Bundle](https://github.com/pthom/imgui_bundle).

## Project structure

```
src/
  litgen/         # Main package: options, generation pipeline, CLI
    internal/     # Core logic (not public API)
      adapted_types/          # AST node wrappers (AdaptedFunction, AdaptedClass, …)
      adapt_function_params/  # Per-parameter transformation rules
    tests/                    # Unit tests
    integration_tests/        # End-to-end C++ build tests (pybind11 + nanobind)
  srcmlcpp/       # C++ XML parsing layer (wraps srcml)
  codemanip/      # Low-level code/string manipulation utilities
docs/book/        # Jupyter Book v2 documentation
```

## Common commands (always use just recipes)

```sh
just install_requirements_dev      # install dev deps
just install_litgen_editable        # install litgen in editable mode
just black                          # check formatting
just mypy                           # type-check
just integration_tests_pybind       # build C++ + run tests (pybind11)
just integration_tests_nanobind     # build C++ + run tests (nanobind)
just integration_tests              # both
just pytest pybind|nanobind         # run pytest only (skip C++ rebuild)
```

## Before committing

1. Run `just integration_tests` — both pybind11 and nanobind paths must pass.
2. Run `just mypy` — strict mypy must pass with no new errors.
3. Run `just black` — formatting must be clean.

Pre-commit hooks enforce black, ruff, and mypy automatically on `git commit`.

## Code quality standards

- **mypy strict** (`disallow_untyped_defs`, `disallow_any_generics`, etc.) — never introduce
  new `# type: ignore` without a comment explaining why.
- **black** formatting — never hand-format; let black decide.
- **Conventional commits** — prefix messages with `fix:`, `feat:`, `docs:`, etc.

## Sensitive / complex areas — proceed carefully

### `src/litgen/internal/adapted_types/adapted_function.py` and `adapted_class.py`
Cyclomatic complexity ~180 and ~167 respectively. These are the core of the generation
pipeline. Changes here can silently affect many generated bindings. Always run
`just integration_tests` after touching these files. Explain architectural rationale
for any non-trivial change.

### `src/litgen/options.py`
759-line configuration class. Every option affects generated output. When adding or
changing options, update the inline docstring and add a test that exercises the option.

## Architecture notes

- The pipeline is: **C++ header → srcmlcpp parse → AdaptedXxx wrappers → code generation**
- `AdaptedFunction`, `AdaptedClass`, `AdaptedEnum` etc. each know how to emit both
  pydef C++ code and `.pyi` stub lines.
- Both pybind11 and nanobind are supported; many internal paths branch on
  `options.bind_library` (`BindLibraryType.pybind11` vs `BindLibraryType.nanobind`).
  When editing a generator, you usually must update **both** branches. They diverge on
  numpy dtype introspection: pybind uses `dtype().char_()`, nanobind uses
  `dtype().code` + `dtype().bits`.
- **Per-parameter adapters** (`internal/adapt_function_params/`) are the most useful
  mental model for parameter binding. Each adapter transforms a param in three
  coordinated places: `new_visible_interface_param` (the visible Python signature),
  `lambda_input` (the conversion code inside the generated lambda), and
  `adapted_inner_param` (the value passed to the real C++ call). To change how a param
  type is bound, you typically touch all three.
- Code is generated by **string templates** (`code_utils.replace_in_string`,
  manual `_i_` indentation), not an AST. The emitted C++ is not validated until the
  integration tests compile it — so always run `just integration_tests` after touching
  a generator.
- Generated code is **not** GPL-licensed even though litgen itself is GPL-3.

## Generated files & regeneration

- **Never hand-edit generated files.** Change the generator and regenerate. Generated
  outputs include: `integration_tests/_pydef_pybind11/`, `_pydef_nanobind/`,
  `_stubs/lg_mylib/`, the `mylib_amalgamation/`, and downstream libraries'
  `pybind_*.cpp` (e.g. in imgui_bundle).
- Regenerate mylib with `python src/litgen/integration_tests/autogenerate_mylib.py
  no_generate_file_by_file [pybind|nanobind]` (no flavor → both, nanobind then pybind).
- The two backends expose slightly different Python APIs (multiple inheritance,
  vectorize), so **each backend owns its own committed `.pyi` stub** — there is no shared
  stub. Package stubs: `_stubs/lg_mylib/__init__.pybind.pyi` and `__init__.nano.pyi`;
  per-file splits: `mylib/*.h.pybind.pyi` and `*.h.nano.pyi`. The active
  `_stubs/lg_mylib/__init__.pyi` imported by the package is a **generated copy** of the
  selected backend's stub (written by `autogenerate_mylib` and by `use.py` on switch); it
  is **gitignored**. Because nothing is shared, each backend regenerates independently and
  order is irrelevant — `build_integration_tests_pybind`/`_nanobind` each run
  `autogenerate_mylib.py [pybind|nanobind]` file-by-file.

## Test layers

- **Golden-string unit tests** (`assert_are_codes_equal`) under `tests/` pin the exact
  generated code. Fast, no compilation. Good for asserting a generator change.
- **Runtime integration tests** under `integration_tests/mylib` require a compiled
  `lg_mylib`; they do **not even collect** without it. Each `pip install -e .` builds
  **one** backend (selected by `LITGEN_USE_NANOBIND=ON|OFF`); switch the active backend
  with `python -m lg_mylib.use <pybind|nanobind>` and rebuild to test the other.
  `just integration_tests` does the full both-backend build + run.
- **When a change alters generated output or parsing behavior, a golden unit test is not
  enough.** Also add or extend a **runtime mylib integration test** (pick the matching
  header, e.g. `header_filter_test.h` for preprocessor filtering, and assert behavior in
  the matching `*_test.py`) and update the relevant `docs/book` notebook example. In the
  integration header, accepted C++ must actually compile (e.g. the guarding macro is
  defined) and rejected C++ must be compiled out — otherwise the generated pydef
  references a nonexistent symbol and the build breaks.

## Documentation (`docs/book`, Jupyter Book v2 / MyST)

- Notebooks are **literate**: `litgen_demo.demo(options, cpp_code)` runs litgen live and
  renders the generated bindings inline, so an example *is* its own demonstration.
- To refresh one example without churning the whole `.ipynb`, execute the notebook and
  copy back **only** the changed cell's outputs (keeps the diff scoped). Pre-commit
  hooks exclude `docs/`. Preview with `just doc_serve_interactive`.

## PRs

- Target branch: `main`
- Run `just integration_tests` before opening a PR
