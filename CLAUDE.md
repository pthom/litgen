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
litgen-book/      # Jupyter-based documentation
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
- Generated code is **not** GPL-licensed even though litgen itself is GPL-3.

## PRs

- Target branch: `main`
- Run `just integration_tests` before opening a PR
