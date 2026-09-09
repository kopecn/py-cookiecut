---
last_updated: 2026-09-07
semver: 1.0.0
author: Nicholas Bergantz
status: active
---

# Plan 18 — Align the generated-repo fleet to the pip / flake8 / black first-class toolchain

## Requested outcome

Every repo already generated from this cookiecutter runs the same first-class toolchain the template now ships: **pip / flake8 / black first-class, uv / ruff / ty second-class**, with a green first-class gate (`make fullCheck` = flake8 + mypy + pytest).

## Scope — repos in this migration

Pending (5): `py-clerical-tools`, `py-machineVisionTools`, `py-MathTools`, `py-robotTools`, `py-textBookReduciton`.

Reference implementations, already aligned (use as the diff to copy): `py-foundationTools`, `py-cookiecut` (both halves).

This plan is the **explicit exception** to the index's standing rule against sibling-repo work — the task names these repos directly.

## Standard being applied

Already landed in the template and the two reference repos:

- Lint = **flake8** (+ `flake8-bugbear` for the `B` checks); format = **black**; typecheck = **mypy**. `ruff` and `ty` stay installed but **second-class** — available, not wired into any gate.
- flake8 `select = E, F, B`. The `W` series is not enforced (ruff never selected it, and enabling it floods `W293` on schema-generated models). ruff's `I` (isort) and `UP` (pyupgrade) have no flake8 equivalent and are **dropped** in the swap.

## Uniform changes (identical per repo — scriptable)

1. Add `.flake8`: `select = E, F, B`, `max-line-length = 100`, `extend-ignore = E203, E704, W503`, standard excludes. (`E704` ignore is what silences the `@overload` stub false positive.)
2. `pyproject.toml`: dev deps gain `flake8`, `flake8-bugbear`, `black`; `ruff`/`ty` retained as second-class; add `[tool.black]` (`line-length = 100`, `target-version = ["py310"]`).
3. `Makefile` (both halves stay byte-identical): repoint `uv-lint` → flake8 and `uv-format` → black; add first-class `lint` / `format` / `typecheck` / `fullCheck`; update the help header and `.PHONY`.
4. `.claude/CLAUDE.md`: flip the primary-path / linting-and-formatting language to pip / flake8 / black first-class.
5. Only where a repo has schema codegen: repoint `run_ruff` → `run_black` in `schema/scripts/reuse/codegen.sh` and its callers, and the `codegen-all` format step. (`py-foundationTools` needed this; check each repo — several may have no `schema/`.)

## Per-repo tail (not scriptable — verify each repo to green)

6. Run black once to reformat to the new formatter — expect a formatting-only diff (black ≠ ruff format).
7. Run flake8 and triage residual findings. Expect the same classes seen in `py-foundationTools`: `B014` redundant exception types (fix — behavior-preserving where the extra types subclass a kept one), and stray `E501` / `E402` in tests (fix, or per-file-ignore in `.flake8`).
8. Install the new dev deps into the repo's env (`make uv-sync` or `make installDev`) before the gate can resolve flake8/black.
9. Confirm the gate is green; **commit nothing without review** — each repo likely carries pre-existing uncommitted WIP unrelated to this migration.

## Remaining work

1. Decide the migration mechanism and its home (idempotent `align-toolchain.sh` in `py-cookiecut/scripts/migrations/`, vs. global tooling, vs. inline hand-edits) — **open user decision.**
2. Apply the uniform changes (1–5) to the 5 repos, then per-repo triage (6–9) to green.
3. Decide whether CI should move off the uv runner to the first-class pip `make fullCheck`. Deferred in the reference repos: CI still uses `setup-uv` + `make uv-fullCheck`, which now runs flake8/black. Separate decision from this migration.
4. Update this plan's `status` and the index row as each repo lands.

## Non-goals / boundaries

- Do not refactor or re-flow a repo's own code beyond what making the new gate green requires.
- Do not run `codegen-all` as part of this migration unless a repo's generated tree actually fails the gate.
- Do not change CI runners in this pass (item 3 tracks that separately).
- `UP` / pyupgrade modernization is intentionally lost in the swap — not a defect to chase.
