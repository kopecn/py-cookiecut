# Action Plans — Index

Per-gap implementation plans derived from [`.claude/GAPS.md`](../GAPS.md). Each plan is
self-contained: it states the source gap, the open decisions, the concrete steps, the files
touched in **both halves** (template tooling vs. template body), and acceptance criteria.

Greenfield rules apply: prefer decisive replacement over backward-compat patching. When a plan
resolves or supersedes a GAPS item, tick the box in `GAPS.md` and note it here.

> **Two-halves reminder.** "Root" = template tooling that runs in *this* repo. "Template" =
> files under `{{cookiecutter.projectIdentifier}}/` that render into a new project. Most plans
> touch both; each plan calls out which.

> **🎉 All plans are now CLOSED and their files removed (2026-06-26).** Every durable verdict lives
> in [`../specs/project-conventions.md`](../specs/project-conventions.md) (§1–§9) and the resolution
> details are ticked in [`../GAPS.md`](../GAPS.md). This index is kept as the historical record of
> what was decided and where it landed. New work should open a fresh plan or update GAPS directly.

| # | Plan | Landed in | GAPS § |
|---|------|-----------|--------|
| 01 | Cleanup stale on-disk artifacts | GAPS §1 (build/, .DS_Store, egg-info untracked — incl. 2026-06-26 regression re-fix) | §1 |
| 02 | Naming convention + hook validation | spec §1 (PEP-8 snake_case generated names; camelCase tooling keys; hook enforces) | §2 |
| 03 | Lint/typecheck stack | spec §4 (ruff + mypy config) | §3, §6 |
| 04 | Python version policy | spec §2 (3.13 default / 3.10 floor; tomllib→grep) | §3, §7, §8 |
| 05 | bump2version HISTORY auto-roll | spec §8 (bump-% rolls HISTORY into the bump commit) | §3 |
| 06 | Branch model | spec §3 (dev/prod) | §4 |
| 07 | Generated pyproject defaults | spec §7 (publishable-shaped) | §4 |
| 08 | Generated smoke test | spec §7 (non-vacuous + bake assertions) | §4 |
| 09 | Dependency SoT, clean, flush, refresh | spec §6 (**BKM: pyproject names-only; requirements file pins; both pip+uv lean on it; no `uv.lock`/`lock`**) | §5, §7 |
| 10 | Multi-repo editable siblings | spec §9 (`requirements-local.txt` + `make uv-sync-local`; no `[tool.uv.sources]`) | §7 |
| 11 | Makefile quality targets | spec §4 (lint/format split; `--unsafe-fixes` KEPT; ty OUT; PY_SRC via .env) | §3, §6, §7 |
| 12 | Makefile test targets | GAPS §7 Test (uv-test ensures sync; matrix; clean-room) | §7 |
| 13 | Release auth | spec §5 (publish.yml scaffolded; CI-owned) | §5, §7 |
| 14 | Version/git orphan cleanup | spec §4 note (VERSION var gone; checkCleanGit wired; floor fallback) | §7 |

## Outcome

All 14 plans resolved. The two halves' Makefiles are **byte-identical** again (per-half scope lives
in `.env`: `PY_SRC=src` for the template). The dependency model is the **BKM** (spec §6): the module
manifest declares **names only**, the **requirements file holds pins + git pointers** and is what
every install path (pip and uv) leans on, **only the application layer pins**, and there is no
`uv.lock`/`lock` target. This **supersedes** the earlier "ranges, no committed lock" decision and
`devops-makefile-principles.md` Lesson 1 — spec §6 (BKM) wins.

## Progress notes

- **Makefile-tier cluster closed (05, 11, 14; most of 12) → spec — 2026-06-26.** `bump-{patch,
  minor,major}` collapsed to a static pattern rule that auto-rolls `HISTORY.md` into the bump
  commit (spec §8). Quality targets split cleanly: `uv-lint` (read-only), `uv-lintFix` (safe
  `--fix`, **`--unsafe-fixes` removed**), `uv-format` (format only); duplicate `uv-fullCheck`
  removed; **ty decided OUT (D1)** and dropped from `.PHONY` (spec §4). Per-half path scoping moved
  off forked Makefiles onto **`.env`** (`template .env: PY_SRC=src`) — the two Makefiles are
  **byte-identical again** (verified `diff` empty; baked project lints `src tests`, root lints
  `hooks tests`). Plan 14 confirmed fully ported to the template half (VERSION var gone,
  `checkCleanGit` wired, tomllib→grep floor fallback). All 10 bake tests green. Plans 05/11/14
  deleted; 12 left open for only the `uv-test` ensure-synced item, which is really a plan-09
  dependency.

- **Naming cluster closed (02, 07, 08) → spec — 2026-06-26.** The naming verdict was **reversed**:
  generated identifiers (`projectIdentifier`/`packageName`/`moduleName` *values*) are now **PEP-8
  snake_case**, while camelCase is retained only for tooling *keys* and `test*`/Makefile names
  (spec §1). `hooks/pre_gen_project.py` rewritten to validate all three identifiers against
  `^[a-z_][a-z0-9_]*$` and abort the bake per-variable. `cookiecutter.json` `__prompts__` + a root
  README variable table give discoverability. **07/08:** generated `pyproject.toml` is now
  publishable-shaped (keywords/classifiers tracking the §2 matrix; deps empty-with-comment) and the
  baked project ships a non-vacuous smoke test (`__version__` + `hello()` sentinel, `pythonpath =
  ["src"]` so it tests without install). Root bake suite grew to **10 tests, all green** —
  `testGeneratedModuleIsImportable` + three `testBakeRejects*` lock in the hook. Plan files 02/07/08
  deleted; learnings in spec §1 and §7.

- **Cross-cutting decisions resolved & applied — 2026-06-25.** User settled the five gating
  decisions; all applied to code and the verdicts migrated to
  [`../specs/project-conventions.md`](../specs/project-conventions.md). Closed + deleted plans
  **03, 04, 06, 13**. **02** verdict = keep camelCase (hook validation impl still open). **09**
  verdict = no `uv.lock` committed / stay on `uv pip` + gitignore (broader Makefile dep work
  still open). Concrete changes: `.env`+`.python-version`+Makefile fallbacks → 3.13 default /
  3.10–3.13 matrix; `make version` tomllib→grep fallback (runs on 3.10 floor); `[tool.ruff]`+
  `[tool.mypy]` added to both pyprojects (config-only per-half paths, `N` omitted for camelCase);
  README + generated changelog URL → dev/prod; `uv.lock` gitignored both halves; guarded
  `publish.yml` scaffold added both halves. Verified: `make -s version`→0.0.2, DEFAULT_PYTHON
  guard passes, `ruff check .` runs via config (surfaced 7 real pre-existing lint findings — no
  camelCase false positives).

- **Low-hanging cleanup — 2026-06-25.** **Plan 01 CLOSED:** removed `build/` + `.DS_Store`
  (untracked); `py_cookiecut.egg-info/` was discovered **tracked** (force-committed despite
  `.gitignore`) — untracked via `git rm --cached` + deleted so the ignore rule holds. **Plan 03
  step 3:** deleted both tracked `.pylintrc` files (`git rm`); pylint/black already gone from `[dev]`
  (Plan 03 stays open for the ruff/mypy config). **Plan 14 root half:** steps 1–2 done as part of the
  Plan 13 alignment (VERSION var deleted, `checkCleanGit` wired into `release-test`); open: template
  half + tomllib floor (Plan 04).
- **Plan 09 (flush/nuke) — pip `nuke` + `list` done, root half, 2026-06-24.** Both have real
  recipes (the `uv-flush-*` tier remains stubs). Code-reviewed: `nuke`'s `name==version`
  uninstall verified working; added a header comment flagging it as the **inferior pip fallback**
  (per-package uninstall against the ambient interp — Lesson 2 says prefer `uv-flush-envs` /
  venv deletion) and retitled its docstring. `list` switched to `$(PIP)`/`$(HR)` for consistency.
  **Flagged, not fixed:** `list` greps `.venv-py*` (matches what `uv-test-all` actually creates),
  but sibling `list-uv` greps `.venvs/*/` (matches the unimplemented GAPS §7 naming) — reconcile
  matrix-env naming when that tier lands. GAPS §7 Flush/nuke box stays open (uv- targets pending).
- **Plan 13 (build & release) — root half COMPLETE, 2026-06-24.** `build` (`clean-build` →
  `$(PYTHON) -m build`); `validateBuild` (`twine check`); `release-test` (TestPyPI, gated on
  `checkCleanGit`, prints `make -s version`); `release` **defers to CI** — refuses local upload and
  exits 1, printing the tag-driven procedure. **D1 resolved → defer-to-CI, mandated by the
  shared-memory `operations/ci-cd.md` spec** ("single authoritative pipeline path; no out-of-band
  deploys") — not a judgment call. **Both `uv-build` and `uv-validateBuild` removed** (installer-
  agnostic; dead `.PHONY` entry cleared). Orphans cleared: grep `VERSION` var deleted, `checkCleanGit`
  now consumed by `release-test`, `RELEASE_ENABLED` removed from Makefile + `.env`. **Shell-strictness
  decided: NO global `.ONESHELL`** (file-global; would flip `installDev`'s leading-`-`; release recipes
  are single-command + Make-sequenced → already fail-fast). **New gap surfaced:** publish-on-tag
  workflow (`publish.yml`) doesn't exist — `tag-on-prod.yml` only tags. Still open: template half;
  D2 auth-env docs; `make -s version` needs Python ≥3.11 (tomllib).
- **Plan 11 (quality targets) — root half done, 2026-06-24.** Defined `UV` + per-half `PY_*`
  path vars in the root `Makefile`; `uv-lint`/`uv-lintFix`/`uv-format`/`uv-typecheck`/`uv-test`
  now expand correctly (verified by `make -n`). **Superseded the §6 path-free/config-only design**
  in favor of explicit `PY_*` vars (Makefiles now differ per half by those vars), which decouples
  path-scoping from Plan 03. Still open: template-half `PY_SRC=src` override, ty decision (D1),
  Plan 03 strictness/ruff-rule config. *(GAPS §6 wording — "resolve via ruff/mypy config per half"
  — is now stale; the chosen mechanism is `PY_*` vars.)*
