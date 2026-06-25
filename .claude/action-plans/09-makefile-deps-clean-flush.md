# 09 — Makefile: dependency SoT, clean, flush, refresh

**Source:** GAPS §5, §7 (Item 1, Clean, Flush/nuke, Refresh) · **Half:** both (Makefile is byte-identical) · **Decisions needed:** YES · **Risk:** medium

Companion: `.claude/specs/devops-makefile-principles.md` (Lessons 1–3).

## Scope

The first three groupings of the command-by-command Makefile pass:
1. **Dependency single-source-of-truth** (Lesson 1) — `lock`, rewrite `uv-sync` + `installDev`.
2. **Clean** (Lesson 2 base) — `cleanBuild` / `cleanArtifacts` / `cleanTest`.
3. **Flush/nuke** (Lesson 2) — graduated venv/cache/python destruction.
4. **Refresh** (Lesson 3) — exact-match resync.

These targets are currently `# TODO(Gx)` stubs in the scaffold.

## Decisions required (blocking)

- **D1 — compile-as-lock?** Treat `requirements.txt` as a **generated lockfile** via
  `uv pip compile pyproject.toml --extra dev -o requirements.txt` (Lesson 1 verdict = yes).
- **D2 — `uv pip sync` vs `uv pip install`?** Lesson 3 verdict = **sync** (exact match).
- **D3 — commit the generated `requirements.txt` / `uv.lock`?** Lesson 1 verdict = commit the
  lock. Decide whether to also use `uv.lock` or stick to compiled `requirements.txt` only.

> The spec already states the verdicts (yes / sync / commit). Confirm D1–D3 explicitly, then build
> to them. The template ships a **minimal starter** `requirements.txt`; `make lock` populates it.

## Steps

### Group 1 — dependency SoT (Lesson 1)
1. Add **`lock`**: `uv pip compile pyproject.toml --extra dev -o requirements.txt` (the only place
   the lock is regenerated).
2. Rewrite **`uv-sync`** → `uv pip sync requirements.txt` then `uv pip install -e . --no-deps`
   (deps already locked; self-install adds the package only).
3. Rewrite **`installDev`** → `-r requirements.txt` then `-e . --no-deps`. **Drop**
   `--break-system-packages` and `--force-reinstall` (Lesson 3 — venvs make them unnecessary).
4. pyproject is the **only** authored source; never hand-edit `requirements.txt`.

### Group 2 — clean (Lesson 2 base)
5. `cleanBuild` → remove `build/`, `dist/`, `*.egg-info/` (folds in Plan 01's manual deletions).
6. `cleanArtifacts` → remove `__pycache__/`, `*.pyc`, `.eggs/`.
7. `cleanTest` → remove `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`.
8. **Invariant:** routine `clean*` MUST NOT delete a committed lockfile (`requirements.txt` /
   `uv.lock`). Keep lock removal exclusively in the flush/nuke tier.

### Group 3 — flush/nuke (Lesson 2)
9. Graduated targets with explicit blast radius:
   - `uv-clean` (artifacts), `uv-flush-cache` (`uv cache clean` / tool caches),
   - `uv-flush-envs` → `rm -rf .venv .venvs/*` (the **reliable primitive** — never per-package
     uninstall), `uv-flush-pythons`, `uv-flush-everything`, `uv-nuke`; pip `nuke`/`list`.
10. Venv deletion is the workhorse; do **not** implement per-package uninstall for correctness.

### Group 4 — refresh (Lesson 3)
11. `uv-refresh` → `uv pip sync requirements.txt` (adds missing, removes stragglers); targeted
    churn via `uv pip install --reinstall-package <name>`.
12. pip `refresh` survives only as a **documented, inferior** `--force-reinstall` fallback.

### Cross-cutting
13. Because the Makefile is byte-identical across halves, every target above must work in BOTH the
    root repo (no `src/`) and a generated project (`src/` layout) without per-half args. Verify by
    baking and running the targets inside the baked project.
14. `set -euo pipefail` / shell concerns (§5) are mostly moot here (no release recipes yet) — apply
    `.ONESHELL` + strict shell only where a recipe has multi-line logic that needs it.

## Files affected

- `Makefile` (both halves) — fill the stub recipes above
- `requirements.txt` (both halves) — becomes a generated lock (starter shipped)
- `pyproject.toml` (both) — confirmed as the only authored dep source
- Cross-ref Plan 01 (clean paths), Plan 10 (editable siblings build on `uv-sync`)

## Acceptance criteria

- D1–D3 recorded in `GAPS.md`.
- `make lock` regenerates `requirements.txt` from pyproject; `make installDev`/`make uv-sync`
  produce identical environments from that one artifact (no `-r` + `-e .[dev]` double-resolve).
- `clean*` never removes the committed lock; the flush tier does, with documented blast radius.
- No `--break-system-packages` anywhere; venv deletion is the flush primitive.
- All targets run from both halves (verified inside a baked project).
