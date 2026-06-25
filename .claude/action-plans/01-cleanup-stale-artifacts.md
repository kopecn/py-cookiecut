# 01 — Cleanup stale on-disk artifacts — ✅ DONE (2026-06-25)

**Source:** GAPS §1 · **Half:** root only · **Decisions needed:** none · **Risk:** trivial

## Status — CLOSED (2026-06-25)

`build/` and stray `.DS_Store` removed (both untracked). **`py_cookiecut.egg-info/` turned out to
be _tracked_** despite `.gitignore` listing `*.egg-info/` — it had been force-committed. Corrected
the root cause, not just the symptom: `git rm -r --cached py_cookiecut.egg-info` (untrack) then
deleted from disk, so the gitignore rule now actually holds. No `.gitignore` edits needed (`build/`,
`*.egg-info/`, `.DS_Store` all already present). The repeatable cleanup already exists in the
`clean`/`clean-build`/`clean-artifacts`/`clean-test` targets (Plan 09 base).

## Problem

Build/IDE leftovers sit on disk in the repo root. They are already gitignored (so not tracked)
but pollute the working tree, confuse `make clean`, and get copied into `build/lib/` snapshots.

Targets:
- `build/lib/hooks/` — byte-identical copy of `hooks/`, leftover from `python -m build`.
- `py_cookiecut.egg-info/` — packaging metadata leftover.
- `.DS_Store` — macOS Finder cruft.

## Pre-checks

- Confirm each path is gitignored and **not** tracked before deleting:
  `git ls-files --error-unmatch build/lib py_cookiecut.egg-info .DS_Store` should fail for each.
- Confirm `hooks/` is the real source and `build/lib/hooks/` is the copy (diff them); delete the
  copy, never the source.

## Steps

1. Delete the three paths from disk:
   - `rm -rf build/ py_cookiecut.egg-info/`
   - `find . -name .DS_Store -not -path './.git/*' -delete`
2. Verify `.gitignore` already covers them (it does: `build/`, `*.egg-info/`, `.DS_Store`). Add
   any missing pattern rather than re-deleting later.
3. Make this repeatable: the future `make clean` family (Plan 09) must remove `build/`, `dist/`,
   `*.egg-info/`, `__pycache__/`, and tool caches. This plan's manual deletion is a stopgap until
   those targets exist — wire the same paths into `cleanBuild`/`cleanArtifacts`.

## Files affected

- Disk only (no tracked files). Possibly `.gitignore` if a pattern is missing.

## Acceptance criteria

- [x] `build/`, `py_cookiecut.egg-info/`, and stray `.DS_Store` files are gone from the working tree.
- [x] No untracked cruft remains; `py_cookiecut.egg-info/` is now **untracked** (was committed —
  fixed via `git rm --cached`, so the existing gitignore rule holds going forward).
- [x] Cleanup paths are folded into the Plan 09 `clean*` targets so this never accrues by hand.
