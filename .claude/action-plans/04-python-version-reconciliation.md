# 04 — Python version reconciliation

**Source:** GAPS §3 (`.python-version` vs `requires-python`), §7 (tomllib floor), §8 (config sources) · **Half:** both · **Decisions needed:** YES · **Risk:** medium

## Problem

Python-version sources contradict each other across the repo:

| Source | Value |
|---|---|
| `.python-version` | `3.13` |
| `.env` `DEFAULT_PYTHON` | `3.14` |
| `.env` `PYTHONS` | `3.10 3.11 3.12 3.14` |
| root `pyproject.toml` `requires-python` | `>=3.10` |
| template `pyproject.toml` `requires-python` | `>= 3.10` |
| root `classifiers` | enumerate 3.10–3.13 |
| Makefile fallback (per GAPS) | `3.10 3.11 3.12` |

Plus a latent bug (GAPS §7): `make version` uses `tomllib`, which is **stdlib only on ≥3.11**.
With `requires-python>=3.10`, `make version` breaks on a 3.10 interpreter.

## Decision required (blocking)

**D1 — canonical floor + matrix.** Pick the support floor and the test matrix, then make every
source agree. Two coherent options:
- **(A) Floor 3.11.** `requires-python = ">=3.11"`; matrix `3.11 3.12 3.13 3.14`;
  `.python-version = 3.13` (or 3.14). Fixes the tomllib bug for free. **Recommended.**
- **(B) Keep floor 3.10.** Then `make version` MUST gain a `tomli` fallback (try `tomllib`,
  except `ImportError` import `tomli`), and add `tomli; python_version < "3.11"` to `[dev]`.

> Recommendation: **(A)**. Raising the floor to 3.11 removes the tomllib special-case entirely and
> 3.10 is near end of its support window. Confirm via `AskUserQuestion` before editing.

## Steps (assuming verdict A; note B-deltas inline)

1. Set the **canonical set** in `.env` as the single human-authored source: `DEFAULT_PYTHON` (one
   value, must be in `PYTHONS`) and `PYTHONS` (space-separated, unquoted — the format is
   load-bearing for Make; keep the existing comment).
2. Align `.python-version` to `DEFAULT_PYTHON` (or the highest stable in the matrix).
3. Set `requires-python` to the floor in **both** `pyproject.toml` files (note: template currently
   has a stray space `">= 3.10"` — normalize to `">=3.11"`).
4. Regenerate `classifiers`:
   - Root: enumerate the chosen matrix (Plan 07 owns the template's classifier defaults).
   - Keep the enumerated versions in sync with `PYTHONS`.
5. Align the Makefile fallback `PYTHONS` default (used when `.env` is absent) to the same set.
6. **tomllib:** verdict A → no change needed (`make version` is safe on ≥3.11). Verdict B → add the
   `tomli` fallback in the `version` recipe and the `[dev]` conditional dep.
7. Sanity bake: generate a project and confirm the rendered `requires-python`, `.python-version`,
   and `.env` agree.

## Files affected

- `.env`, `{{cookiecutter.projectIdentifier}}/.env`
- `.python-version`, `{{cookiecutter.projectIdentifier}}/.python-version` (if present; create in
  template if missing so generated projects pin too)
- `pyproject.toml` (root) — `requires-python`, `classifiers`
- `{{cookiecutter.projectIdentifier}}/pyproject.toml` — `requires-python`
- `Makefile` (both halves) — fallback `PYTHONS`; `version` recipe only if verdict B
- Cross-ref Plan 14 (orphaned `VERSION` var / tomllib note) and Plan 07 (classifier defaults)

## Acceptance criteria

- D1 recorded in `GAPS.md`.
- Every version source lists the same floor and matrix; no contradictions remain.
- `make version` works on the declared floor interpreter (no tomllib ImportError).
- A fresh bake produces internally-consistent version metadata.
