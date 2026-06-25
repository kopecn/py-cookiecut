# 08 — Generated smoke test

**Source:** GAPS §4 (test asserts nothing) · **Half:** template body · **Decisions needed:** no · **Risk:** low

## Problem

The generated test `{{cookiecutter.projectIdentifier}}/tests/test{{cookiecutter.moduleName}}.py`
has a commented-out import and a `test_content()` that asserts nothing:

```python
import pytest
# from {{ cookiecutter.projectIdentifier }} import {{ cookiecutter.moduleName }}

def test_content():
    """Sample pytest test function."""
```

This passes vacuously and gives baked projects a false sense of coverage. It should actually
import the generated module and assert something real, so `make test` inside a fresh project is
meaningful — and so the **bake tests** (`tests/testBakeProject.py`) verify the generated suite
runs green.

## Approach

Provide a minimal but real smoke test that imports the rendered package/module and asserts on a
trivially-true property the template guarantees (e.g. a `__version__` or a sentinel function the
template ships).

## Steps

1. Decide what the generated module exposes. Cheapest reliable surface: have the template's
   `src/{{cookiecutter.packageName}}/{{cookiecutter.moduleName}}.py` define a `__version__`
   (rendered from `{{ cookiecutter.version }}`) and/or a trivial function. Confirm what the
   current template module actually ships and align the import path with the Plan 02 naming
   verdict.
2. Rewrite the test to:
   - Use a **real, uncommented import** of the generated module via the correct package path.
   - Assert something concrete (e.g. `module.__version__ == "<expected>"`, or that a known
     callable returns the expected value).
   - Use the repo's non-standard `test*` function naming (the pytest config matches `test*`).
     Prefer `testSmoke`/`testImport`-style names to match "Nick's workflow" camelCase, but keep
     pytest discovery working (`python_functions = ["test*"]`).
3. Drop the unused `import pytest` unless a fixture/raises is actually used.
4. Remove the `if __name__ == "__main__"` manual-run block (pytest is the runner) unless there's a
   reason to keep it.
5. **Extend `tests/testBakeProject.py`** (root) to bake and then run `pytest` *inside* the baked
   project and assert it passes — this is the real guard that the generated test is non-vacuous.
   Use the existing `runInsideDir`/`checkOutputInsideDir` helpers.

## Files affected

- `{{cookiecutter.projectIdentifier}}/tests/test{{cookiecutter.moduleName}}.py`
- Possibly `{{cookiecutter.projectIdentifier}}/src/{{cookiecutter.packageName}}/{{cookiecutter.moduleName}}.py` (expose `__version__`/a callable)
- `tests/testBakeProject.py` (root) — assert the baked suite runs green
- Cross-ref Plan 02 (import path naming)

## Acceptance criteria

- The generated test imports the real module and makes a non-trivial assertion.
- `make test` (or `pytest`) inside a freshly baked project passes and is meaningful.
- A root bake test confirms the generated suite runs and passes.
