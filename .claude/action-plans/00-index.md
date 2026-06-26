# Action Plans — Index

Per-gap implementation plans derived from [`.claude/GAPS.md`](../GAPS.md). Each plan is
self-contained: it states the source gap, the open decisions, the concrete steps, the files
touched in **both halves** (template tooling vs. template body), and acceptance criteria.

Greenfield rules apply: prefer decisive replacement over backward-compat patching. When a plan
resolves or supersedes a GAPS item, tick the box in `GAPS.md` and note it here.

> **Two-halves reminder.** "Root" = template tooling that runs in *this* repo. "Template" =
> files under `{{cookiecutter.projectIdentifier}}/` that render into a new project. Most plans
> touch both; each plan calls out which.

> **Closed plans are removed; their durable verdicts live in
> [`../specs/project-conventions.md`](../specs/project-conventions.md).** Plans 03/04/06/13 are
> done and deleted (2026-06-25); 02 and 09 had their *decisions* settled (recorded in that spec)
> but keep open files because implementation work remains.

| # | Plan | GAPS § | Blocking decisions? |
|---|------|--------|---------------------|
| 01 | [Cleanup stale on-disk artifacts](./01-cleanup-stale-artifacts.md) ✅ | §1 | No |
| 02 | [Naming convention + hook validation](./02-naming-convention-and-hooks.md) | §2 | ✅ decided (keep camelCase) — hook impl open |
| 03 | ✅ **CLOSED** → spec §4 (ruff+mypy config landed) | §3, §6 | — |
| 04 | ✅ **CLOSED** → spec §2 (3.13 default / 3.10 floor) | §3, §7, §8 | — |
| 05 | [bump2version HISTORY auto-roll](./05-bumpversion-history-followup.md) | §3 | No |
| 06 | ✅ **CLOSED** → spec §3 (dev/prod model) | §4 | — |
| 07 | [Generated pyproject defaults](./07-generated-pyproject-defaults.md) | §4 | Minor |
| 08 | [Generated smoke test](./08-generated-smoke-test.md) | §4 | No |
| 09 | [Makefile: dependency SoT, clean, flush, refresh](./09-makefile-deps-clean-flush.md) | §5, §7 | ✅ uv.lock decided (spec §6) — Makefile impl open |
| 10 | [Makefile: multi-repo editable siblings](./10-makefile-multi-repo-editable.md) | §7 | Minor |
| 11 | [Makefile: quality targets](./11-makefile-quality-targets.md) | §3, §6, §7 | No (after 03) |
| 12 | [Makefile: test targets](./12-makefile-test-targets.md) | §7 | No |
| 13 | ✅ **CLOSED** → spec §5 (publish.yml scaffolded) | §5, §7 | — |
| 14 | [Makefile: version/git orphan cleanup](./14-makefile-version-git-cleanup.md) | §7 | No (after 04) |

## Suggested execution order

1. **Decide the cross-cutting things first** (they unblock the rest):
   - 02 camelCase verdict, 04 canonical Python set, 06 branch model, 09 lock/commit policy.
2. **Mechanical cleanup**: 01, 03, 05.
3. **Template body correctness**: 07, 08.
4. **Makefile command-by-command pass** (build order): 09 → 10 → 11 → 12 → 13 → 14.

Plans 03, 11, and the ruff/mypy config are intertwined: 03 lands the *config*; 11 wires the
*Makefile targets* that consume it. Do 03 before 11.

## Progress notes

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
