# 11 — Makefile: quality targets

**Source:** GAPS §7 (Quality / G5), §6 (per-half paths), §3 (ruff config) · **Half:** both · **Decisions needed:** ty in/out · **Risk:** low

**Depends on Plan 03** (which lands the `[tool.ruff]` / `[tool.mypy]` config). This plan wires the
Makefile targets that consume that config.

## Scope

Fill the `# TODO(G5)` quality stubs: `uv-lint`, `uv-lintFix`, `uv-format`, `uv-typecheck`,
`uv-typecheck-ty` (decision), `uv-fullCheck`.

## Key constraint (the §6 trick, recap)

The Makefile is byte-identical across halves but the halves lint **different paths** (root:
`hooks/`+`tests/`; template: `src/`). Targets therefore must **not** pass explicit paths —
they run `ruff`/`mypy` with no path args and rely on each half's `pyproject.toml` config (Plan 03)
to scope discovery. This is the whole reason Plan 03 must land first.

## Steps

1. `uv-format` → `uv run ruff format .` (or `ruff format` against config). Formatting only.
2. `uv-lint` → `uv run ruff check .` (read-only; non-zero exit on findings for CI).
3. `uv-lintFix` → `uv run ruff check --fix .` (applies safe autofixes).
4. `uv-typecheck` → `uv run mypy .` with `--strict` already set via `[tool.mypy]` (Plan 03), so the
   recipe stays path-free.
5. `uv-typecheck-ty` — **Decision D1: ty in or out?** ty is preview (GAPS defers it). Default:
   ship the target as an **opt-in stub** (`# TODO: ty preview`) or a thin `uv run ty check .`
   guarded as experimental. Do not make it part of `uv-fullCheck` until it's stable.
6. `uv-fullCheck` → `lint` + `typecheck` + `test` (test target from Plan 12). Compose, don't
   duplicate recipe bodies. Order: format-check/lint → typecheck → test.
7. Ensure a synced env exists first (depend on / document `uv-sync` from Plan 09) so quality
   targets don't run against a stale or empty env.
8. Verify both halves: run `make uv-lint`/`uv-typecheck` in the root (lints `hooks`+`tests`) and
   inside a baked project (lints `src`), confirming the config-only path resolution works.

## Files affected

- `Makefile` (both halves) — quality recipes
- (Config itself lives in Plan 03's `[tool.ruff]`/`[tool.mypy]` blocks — not re-added here)

## Acceptance criteria

- D1 (ty in/out) recorded.
- `make uv-lint`/`uv-format`/`uv-typecheck` run path-free and hit the correct files in **each**
  half via config alone (§6 satisfied).
- `make uv-fullCheck` composes lint+typecheck+test and returns non-zero on any failure.
- camelCase identifiers don't trip lint failures (depends on Plan 03 rule config).
