# Plan 15 — PR #2 review findings

Source: `/review` of PR #2 (`feat/rebuild-for-latest-bkms` → `dev`) on 2026-06-28, plus a
live CI failure observed on the `test-python` job. Most findings touch **both halves**
(root tooling + `{{cookiecutter.projectIdentifier}}/` template body); each notes which.

Greenfield rules apply: prefer decisive replacement. Tick boxes here and in `GAPS.md` as
items land. Legend: `[ ]` open · `[~]` in progress · `[x]` done.

---

## A. CI matrix guard hard-fails (both halves) — **DONE (2026-06-28)**

- [x] CI's narrowed `PYTHONS="3.10 3.11 3.12"` tripped the Makefile's global
      `DEFAULT_PYTHON ∈ PYTHONS` guard (default stayed `3.13`), exiting 2 on every run.
      **Fix:** keep `3.13` in the matrix (`PYTHONS="3.10 3.11 3.12 3.13"`); `lint-typecheck`
      installs `3.13`. Both `ci.yml` halves byte-identical.
      - [ ] Follow-up (optional): scope the guard to only targets that read `DEFAULT_PYTHON`,
            so a narrowed matrix can't trip a target that ignores it.

---

## B. `.gitignore` trailing inline comments break ignore patterns (both halves) — **OPEN**

- [ ] Git treats `#` as a comment **only at line start**; appended text becomes part of the
      pattern. The consolidated `.gitignore` has many trailing-comment lines that now match
      nothing: `*.egg-info/ # Generic wheel/package info folders`, `.cleanroom-venv/   # …`,
      `.vscode/        # …`, `.idea/`, `*.iml`, `local_settings.py # …`, `*.spec`, `.Python`,
      `MANIFEST`, `db.sqlite3`, `instance/`, `storage/*`, `*.log`. **Fix:** move every `#`
      comment to its own line (pattern alone on the line). This is the root cause of finding C.

## C. `py_cookiecut.egg-info/` build artifacts committed (root) — **OPEN**

- [ ] `PKG-INFO`, `SOURCES.txt`, `requires.txt`, `top_level.txt`, `dependency_links.txt` are
      tracked again, contradicting GAPS §1 (untracked twice). Re-entered because `*.egg-info/`
      is dead (finding B). **Fix:** `git rm -r --cached py_cookiecut.egg-info/` and confirm the
      repaired ignore rule holds. (`requirements_dev.txt` was even renamed *into*
      `egg-info/requires.txt` — drop that too.)

## D. `tag-on-prod.yml` "Skip if pyproject didn't change" fails the run (both halves) — **OPEN**

- [ ] `git diff --quiet HEAD^ HEAD -- pyproject.toml && exit 1 || exit 0`: when pyproject is
      unchanged, `--quiet` exits 0 → `exit 1` → the step (and job) **fails** instead of skipping.
      Every push to `prod` without a version bump shows a red run. **Fix:** emit a step output
      and gate later steps with `if:`, rather than `exit 1`.

## E. `uv-sync-release` reads an uncommitted `requirements-release.txt` (both halves) — **OPEN**

- [ ] `.gitignore` comment + spec §6 say `requirements-release.txt` is **committed**, but it is
      not in the repo. `make uv-sync-release` aborts immediately ("No such file"). **Fix:** ship a
      starter `requirements-release.txt` (both halves), mirroring the committed `requirements.txt`.

## F. uv quality/test targets use `uv run` (project interface), bypassing requirements + BKM — **OPEN**

- [ ] `UV := uv run --extra dev` is uv's *project* interface: it resolves from `pyproject.toml`
      and auto-syncs the env (writing `uv.lock` — why `clean-build` does `rm -f uv.lock`),
      ignoring `requirements*.txt`. So `uv-lint`/`uv-typecheck`/`uv-test` run in an env that omits
      requirements-file deps; `uv-test` runs `uv-sync` (installs them via `uv pip`) then `uv run`
      can re-sync and drop them. Contradicts spec §6 "uv pip only / no `uv.lock` / every install
      path leans on the requirements file." Latent today (requirements is comment-only). **Fix:**
      run the quality/test tools through the `uv pip`-built `.venv` (e.g. `uv run --no-sync …` or
      invoke `.venv/bin/<tool>`), keeping uv on the pip interface.

## G. `uv-test-all` matrix env skips `-r requirements.txt` (both halves) — **OPEN**

- [ ] Each matrix env does only `uv pip install -e ".[dev]"`, never the requirements file —
      same divergence as F at the matrix layer. A git-pointer/pinned dep declared (per the BKM)
      only in `requirements.txt` is absent under CI. **Fix:** add `uv pip install -r requirements.txt`
      before the editable install in the matrix loop.

## H. `roll_changelog` doesn't update Keep-a-Changelog compare links (both halves) — **OPEN**

- [ ] The `awk` inserts the dated section but leaves the footer `[Unreleased]: …/compare/vX…HEAD`
      / `[X]: …/releases/tag/vX` links pointing at the prior version, and adds no fresh
      `### Added` stub under `[Unreleased]` — contradicting the CONTRIBUTING instructions.
      **Fix:** extend the recipe to rewrite the compare links and seed an empty `[Unreleased]`.

---

## Severity order

A (fixed) and B/C are the blockers (B is the root cause of C). D is user-visible CI noise on
`prod`. E breaks a documented target out of the box. F/G are latent BKM-consistency
correctness issues (harmless only while deps are empty). H is a changelog-hygiene defect.
