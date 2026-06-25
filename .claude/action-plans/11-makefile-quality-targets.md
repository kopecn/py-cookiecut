# 11 — Makefile: quality targets

**Source:** GAPS §7 (Quality / G5), §6 (per-half paths), §3 (ruff config) · **Half:** both · **Decisions needed:** ty in/out · **Risk:** low

**Depends on Plan 03** (which lands the `[tool.ruff]` / `[tool.mypy]` config). This plan wires the
Makefile targets that consume that config.

## Status — root half done (2026-06-24)

**Design divergence (decided):** we did **not** take the path-free / config-only route below.
Instead the root `Makefile` now defines explicit, per-half path vars and a tool runner:

```make
PY_SRC ?= hooks          # template half overrides → src
PY_TESTS ?= tests
PY_EXAMPLES ?=
PY_ALL ?= $(PY_SRC) $(PY_TESTS) $(PY_EXAMPLES)
UV := uv run             # run tools in the uv-managed .venv ([dev] extra)
```

Consequence: the Makefile is **no longer byte-identical across halves** (the §6 trick is
superseded — paths are scoped by `PY_*` vars, not by `pyproject` config). This **decouples path
scoping from Plan 03**; Plan 03 is still needed for `mypy --strict` strictness and ruff rule
selection, but is no longer a hard blocker for the targets to run.

Verified by dry-run (`make -n`): `uv-lint`→`uv run ruff check hooks tests`,
`uv-lintFix`→`uv run ruff check --fix hooks tests`, `uv-format`→`uv run ruff format hooks tests`,
`uv-typecheck`→`uv run mypy hooks tests`, `uv-test`→`uv run pytest`.

**Still open:** template-half `PY_*` overrides (`src`); ty decision (D1); Plan 03 config
(strictness + camelCase-safe ruff rules); end-to-end run against a synced env (Plan 09).

## Scope

Fill the `# TODO(G5)` quality stubs: `uv-lint`, `uv-lintFix`, `uv-format`, `uv-typecheck`,
`uv-typecheck-ty` (decision), `uv-fullCheck`.

## Key constraint (the §6 trick) — SUPERSEDED

> Original design: byte-identical Makefile across halves, targets pass **no** explicit paths and
> rely on each half's `pyproject.toml` config to scope discovery. **Superseded** by the Status
> note above: we scope per-half via explicit `PY_*` vars instead, so the Makefiles differ by
> those vars. Kept here for provenance.

## Steps

- [x] 1. `uv-format` → `$(UV) ruff format $(PY_ALL)` (formatting only). *(root)*
- [x] 2. `uv-lint` → `$(UV) ruff check $(PY_ALL)` (read-only; non-zero exit for CI). *(root)*
- [x] 3. `uv-lintFix` → `$(UV) ruff check --fix $(PY_ALL)` (safe autofixes). *(root)*
- [~] 4. `uv-typecheck` → `$(UV) mypy $(PY_SRC) $(PY_TESTS) $(PY_EXAMPLES)`. Wired + expands; still
  needs `--strict` via `[tool.mypy]` (Plan 03).
- [ ] 5. `uv-typecheck-ty` — **Decision D1: ty in or out?** Still in `.PHONY` with **no recipe**.
  ty is preview (GAPS defers it). Default: opt-in stub / experimental `$(UV) ty check`; not part
  of `uv-fullCheck` until stable.
- [x] 6. `uv-fullCheck` → composes `uv-lint uv-typecheck uv-test` (no duplicated bodies).
- [ ] 7. Ensure a synced env exists first (depend on / document `uv-sync` from Plan 09).
- [~] 8. Verify both halves: root verified by `make -n` (lints `hooks`+`tests`). **Template half
  not yet done** — needs `PY_SRC=src` override + bake verification.

## Files affected

- `Makefile` (both halves) — quality recipes
- (Config itself lives in Plan 03's `[tool.ruff]`/`[tool.mypy]` blocks — not re-added here)

## Acceptance criteria

- [ ] D1 (ty in/out) recorded.
- [~] `make uv-lint`/`uv-format`/`uv-typecheck` hit the correct files in **each** half. Root: via
  `PY_*` vars (`hooks`+`tests`) — done. Template: pending `PY_SRC=src` override. *(§6 satisfied by
  per-half `PY_*` vars, not config-only.)*
- [x] `make uv-fullCheck` composes lint+typecheck+test and returns non-zero on any failure.
- [ ] camelCase identifiers don't trip lint failures (depends on Plan 03 rule config).
