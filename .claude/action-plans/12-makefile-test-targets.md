# 12 — Makefile: test targets

**Source:** GAPS §7 (Test / G4) · **Half:** both · **Decisions needed:** no · **Risk:** low

## Scope

Fill the `# TODO(G4)` test stubs: `test`, `uv-test`, `uv-test-all` / `uv-test-matrix`,
`testInEnv*`.

## Constraints / lessons baked in

- **No fresh-env no-op:** `uv-test` must ensure the env is **synced first** (Plan 09 `uv-sync`),
  otherwise it silently tests an empty/stale env. Depend on or invoke sync before pytest.
- **Matrix uses per-version venvs:** `uv-test-matrix` runs against `.venvs/<ver>` for each version
  in `$(PYTHONS)` (canonical set from Plan 04). Venv-per-version, created/destroyed deletably
  (Lesson 2 — deletable venvs).
- **Clean-room** `testInEnv*` uses the throwaway `$(VENV)` (`.cleanroom-venv` per `.env`), kept
  distinct from `.venv` so it never nukes the dev env (the `.env` comment already says this).
- Byte-identical Makefile: in the **root** half `make test` runs the **bake tests**
  (`tests/testBakeProject.py`, non-standard `test*` discovery); in a **generated** project the same
  target runs that project's own `tests/`. The recipe must be generic enough to do both (run pytest
  against `tests/`, let pyproject's `[tool.pytest.ini_options]` scope it).

## Steps

1. `test` → `pytest` (relies on `[tool.pytest.ini_options]`: `testpaths`, `python_files=test*.py`,
   `python_functions=test*`). Path-free so it works in both halves.
2. `uv-test` → ensure sync (Plan 09), then `uv run pytest`. Document the sync dependency so it's
   never a no-op on a fresh checkout.
3. `uv-test-all` / `uv-test-matrix` → loop `$(PYTHONS)`:
   - `uv python install <ver>` (idempotent), create `.venvs/<ver>`, sync the lock into it, run
     pytest. Fail the whole target if any version fails.
   - Tear down or reuse `.venvs/<ver>` per the flush policy (Plan 09).
4. `testInEnv` → build a fresh `$(VENV)` clean-room, install (lock + `-e . --no-deps`), run tests,
   teardown (`rm -rf $(VENV)`) on exit. `testInEnv*` variants (e.g. per-version) layer on the
   matrix loop.
5. Wire into `uv-fullCheck` (Plan 11) — `test` is the final stage.
6. Verify: root `make test` runs the bake tests green (currently 6/6 per GAPS); baked-project
   `make test` runs the generated smoke test (Plan 08) green.

## Files affected

- `Makefile` (both halves) — test recipes
- Cross-ref Plan 04 (`PYTHONS`), Plan 09 (sync/flush), Plan 08 (generated smoke test), Plan 11
  (`uv-fullCheck`)

## Acceptance criteria

- `make test` is path-free and green in both halves.
- `make uv-test` never runs against an unsynced env (no false-green no-op).
- `uv-test-matrix` exercises every version in `$(PYTHONS)` via deletable per-version venvs and
  fails if any version fails.
- `testInEnv` uses the distinct clean-room venv and tears it down on exit.
