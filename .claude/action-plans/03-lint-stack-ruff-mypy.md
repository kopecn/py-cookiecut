# 03 — Lint stack: ruff + mypy config, drop pylintrc

**Source:** GAPS §3 (lint stack), §6 (per-half paths) · **Half:** both · **Decisions needed:** minor · **Risk:** low

## Problem

Toolchain is already decided: **ruff** (lint + format) + **mypy --strict**; black/pylint were
removed from the `[dev]` extra. What remains:
- No `[tool.ruff]` / `[tool.mypy]` config in either `pyproject.toml`.
- Obsolete `.pylintrc` still on disk in **both halves** (`./.pylintrc` and
  `{{cookiecutter.projectIdentifier}}/.pylintrc`).
- The two halves must lint **different paths** (GAPS §6): root code lives in `hooks/` + `tests/`
  (no `src/`); template code lives in `src/`. The Makefile is intentionally byte-identical, so
  the path difference MUST be expressed in per-half **config**, not in recipe arguments.

## Key constraint (the §6 trick)

Because the Makefile is identical across halves, `make lint` must resolve the right paths from
config alone. Achieve this with ruff/mypy's own file discovery + per-half config:
- Run `ruff check .` / `mypy .` (no explicit paths) and let each half's `pyproject.toml` define
  `include`/`exclude` (ruff) and `files`/`packages` (mypy).
- Root config targets `hooks`, `tests`. Template config targets `src` (+ optionally `tests`).

## Steps

1. **Root `pyproject.toml`** — add:
   - `[tool.ruff]`: `target-version` aligned with Plan 04 floor; `line-length`; `src = ["hooks",
     "tests"]`; a sensible `[tool.ruff.lint]` rule selection (`E,F,I,UP,B` to start). Note the
     repo's **non-standard `test*` (not `test_*`) naming** — do not add rules that would fight the
     camelCase convention (e.g. configure `pep8-naming`/`N` leniently or omit it).
   - `[tool.mypy]`: `strict = true`; `files = ["hooks", "tests"]`; `python_version` per Plan 04.
2. **Template `pyproject.toml`** — add the analogous blocks but pathed at `src` (and `tests`):
   `[tool.ruff] src = ["src", "tests"]`; `[tool.mypy] files = ["src", "tests"]`. Remember the
   body is Jinja — keep `{{ }}` out of these static blocks unless a value is genuinely templated.
3. **Delete `.pylintrc`** in both halves.
4. **Naming-convention coherence:** the project uses camelCase intentionally. Ensure ruff lint
   rules don't flag it as errors that break CI — disable/relax `N` (pep8-naming) or scope it.
5. Defer **ty (preview)** explicitly (it belongs to Plan 11 / GAPS G5 `uv-typecheck-ty`); leave a
   `# TODO(G5): decide ty in/out` marker rather than configuring it now.

## Files affected

- `pyproject.toml` (root) — add `[tool.ruff]`, `[tool.mypy]`
- `{{cookiecutter.projectIdentifier}}/pyproject.toml` — add the same, pathed at `src`
- Delete `./.pylintrc` and `{{cookiecutter.projectIdentifier}}/.pylintrc`

## Acceptance criteria

- `ruff check .` and `mypy .` run clean-ish from each half using **config-only** path resolution
  (no path args), respecting §6's per-half difference.
- No `.pylintrc` remains in either half; black/pylint absent from `[dev]` (already true).
- camelCase identifiers do not produce lint errors that would fail CI.
- Plan 11 can wire `uv-lint`/`uv-format`/`uv-typecheck` against this config with identical recipes.
