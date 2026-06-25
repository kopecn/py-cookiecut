# 01 — Cleanup stale on-disk artifacts

**Source:** GAPS §1 · **Half:** root only · **Decisions needed:** none · **Risk:** trivial

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

- `build/`, `py_cookiecut.egg-info/`, and stray `.DS_Store` files are gone from the working tree.
- `git status` shows no new tracked changes from the deletion (they were ignored).
- The cleanup paths are folded into the Plan 09 `clean*` targets so this never accrues by hand.
