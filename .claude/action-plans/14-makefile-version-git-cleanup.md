# 14 — Makefile: version/git orphan cleanup

**Source:** GAPS §7 (G8 orphans) · **Half:** both · **Decisions needed:** no · **Risk:** low

**Depends on Plan 04** (Python floor decides the tomllib question) and feeds Plan 13 (release uses
`make version`).

## Problem

G8 (version/git/util) is mostly DONE: `help`, `bump-patch/minor/major` + `bump-%`, `version` (via
`tomllib`), `checkCleanGit`, `open-github`. The `tag` target was **AXED** (owned by
`tag-on-prod.yml`). That removal left two orphans plus a latent floor bug:

1. **Orphaned `checkCleanGit`** — no consumer now that `tag` is gone. Keep it as a standalone
   guard and wire it as the prereq for `release`/`release-test` (Plan 13).
2. **Orphaned `VERSION` make-var** — the header grep-based, `v`-prefixed `VERSION` var is now
   UNUSED (`version` target uses tomllib). Converge everything on the tomllib `version` target,
   then **delete** the `VERSION` var.
3. **tomllib floor bug** — `make version` needs Python ≥3.11; `requires-python>=3.10` would break
   it on 3.10. Resolved by Plan 04 (raise floor to 3.11) **or** a `tomli` fallback. Implement
   whichever Plan 04 chooses.

## Status — root half DONE (2026-06-25)

Steps 1–2 complete in the **root** Makefile (done as part of the Plan 13 release alignment):
`checkCleanGit` is now the prereq for `release-test`; the orphaned grep `VERSION` var is deleted and
`release-test`/`release` read `$(MAKE) -s version`. **Still open:** the template-half Makefile
(step 5) and the tomllib floor (step 3, blocked on Plan 04's floor decision).

## Steps

1. [x] **Wire `checkCleanGit`** as the prerequisite for `release`/`release-test` (Plan 13). Strict
   (`git status --porcelain` must be empty); stays a reusable guard. *(root — wired into
   `release-test`; `release` defers to CI so needs no clean-tree gate.)*
2. [x] **Delete the `VERSION` grep var:** confirmed nothing referenced it; release recipes repointed
   to `$(MAKE) -s version` (tomllib); the `VERSION := $(shell grep ...)` line removed. *(root)*
3. **tomllib floor** (mirror Plan 04 verdict):
   - Verdict A (floor 3.11): no recipe change — just confirm `make version` runs on the floor.
   - Verdict B (keep 3.10): make the `version` recipe try `tomllib` then fall back to `tomli`, and
     ensure `tomli` is in `[dev]` conditionally (`tomli; python_version < "3.11"`).
4. [x] Verify `make version` returns the bare version (used by Plan 05 changelog roll and Plan 13
   release) and `make -s version` is clean for command substitution. *(root — verified via release
   `make -n`.)*
5. Apply in the **template half** (still pending — the two Makefiles diverged per Plan 11/13, so this
   is no longer a byte-identical copy; port the same VERSION-var deletion + `checkCleanGit` wiring).

## Files affected

- `Makefile` (both halves) — delete `VERSION` var, wire `checkCleanGit`, maybe `version` fallback
- `pyproject.toml` (both) — `tomli` conditional dep only under verdict B
- Cross-ref Plan 04 (floor), Plan 13 (release prereq), Plan 05 (changelog uses `version`)

## Acceptance criteria

- The orphaned grep `VERSION` var is gone; all version reads go through the tomllib `version`
  target.
- `checkCleanGit` is consumed by `release`/`release-test` and remains a strict standalone guard.
- `make version` works on the canonical Python floor (no tomllib ImportError) in both halves.
