# GAPS & Refactor Backlog

Living list of known defects, inconsistencies, and intended changes for the `py-cookiecut`
rip-and-tear. This is **greenfield** — no downstream consumers to protect, so prefer
decisive replacement. Check items off and add new ones as the refactor proceeds.

Legend: `[ ]` open · `[~]` in progress · `[x]` done

---

## 1. Stale / on-disk artifacts (cleanup)

- [x] `build/` (incl. `build/lib/hooks/`) — leftover from `python -m build`. **Deleted (2026-06-25).**
- [x] `py_cookiecut.egg-info/` — build leftover. **Was actually TRACKED** (force-committed despite
      `.gitignore`); untracked via `git rm --cached` + deleted (2026-06-25), so the ignore rule now holds.
      **Regressed and re-untracked 2026-06-26** (an editable install/build had re-staged the 5
      metadata files into the index); `git rm -r --cached` again — `.gitignore` `*.egg-info/` (line 43)
      now holds and the dir is ignored on disk.
      **Regressed a third time and fixed at the ROOT CAUSE 2026-06-28 (plan 15 B/C):** the
      `*.egg-info/` rule had a trailing inline comment (`*.egg-info/ # …`), which git folds into
      the pattern so it matched nothing — that's why the dir kept re-tracking. All trailing-comment
      patterns in both halves' `.gitignore` were moved to their own lines, then
      `git rm -r --cached py_cookiecut.egg-info/`. Verified the repaired rule ignores the dir.
- [x] `.DS_Store` on disk (gitignored). **Deleted (2026-06-25).**

## 2. Naming-convention enforcement (the big decision)

- [x] **REVERSED (2026-06-25): two-layer split, not "camelCase everywhere".** The earlier
      "KEEP camelCase" verdict was superseded by an explicit new decision. *Generated*
      identifiers (the **values** for `projectIdentifier`/`packageName`/`moduleName` → dist
      name, import package, module file) are now **PEP-8 snake_case** (`python_boilerplate`,
      `my_package`, `my_module`); *tooling* identifiers (cookiecutter **keys**, `test*`
      function names, Makefile targets) stay camelCase. See
      `.claude/specs/project-conventions.md` §1. `cookiecutter.json` defaults + `__prompts__`
      teach this; the root README has a quick-reference table. Ruff `N` stays omitted (§4) so
      the camelCase tooling layer doesn't fail CI.
- [x] `pre_gen_project.py` **rewritten (2026-06-25)**: validates `projectIdentifier`,
      `packageName`, AND `moduleName` against `^[a-z_][a-z0-9_]*$` (hard-fails on hyphens,
      uppercase, leading digits) with a per-variable error message. Stale "use `_` instead"
      message and single-variable scope both resolved.

## 3. Tooling drift / contradictions

- [x] Lint stack: **ruff** (lint+format) + **mypy --strict**; black/pylint removed; `.pylintrc`
      deleted. `[tool.ruff]`/`[tool.mypy]` config **added to both pyprojects (2026-06-25)** with
      config-only per-half path resolution (root→`hooks,tests`; template→`src,tests`), `py310`
      floor, `N` omitted for camelCase. See `.claude/specs/project-conventions.md` §4. ty (preview)
      deferred to G5. *(Surfaced 7 real pre-existing lint findings in hooks/tests — cleanup is
      separate.)*
- [x] `requirements_dev.txt` / `requirements_prod.txt` — **deleted**.
- [x] Dev-dependency 3-way duplication — **consolidated**: pyproject `[dev]` extra (renamed
      from `develop`) is the source; a minimal `requirements.txt` starter is shipped; Makefile
      `installDev`/`uv-sync` install `-r requirements.txt` + `-e ".[dev]"`. NOTE: extra renamed
      `develop`→`dev` in both pyprojects to match recipes.
- [x] `.python-version` (3.13) vs `requires-python` (>=3.10) — **RECONCILED (2026-06-25)**:
      canonical set is default 3.13 / floor 3.10 (see §8 and `.claude/specs/project-conventions.md`
      §2). `.env`, `.python-version`, Makefile fallbacks aligned; template now ships `.python-version`.
- [x] `personal_repos = []` empty optional-dependency group — **removed** from both pyprojects.
- [x] `bump2version` config added: `.bumpversion.cfg` in root and template, bumping the
      version in `pyproject.toml` (`commit = True`, `tag = False`). Verified the search/replace
      matches via dry-run.
  - [x] Follow-up **DONE (2026-06-26, plan 05):** `bump-{patch,minor,major}` (now a static
        pattern rule sharing one recipe) auto-rolls `HISTORY.md` — an `awk` step opens a fresh
        dated `## [<version>] - <date>` section under `## [Unreleased]` (Keep-a-Changelog
        anchor), folding accumulated notes into it, then `git commit --amend --no-edit` lands the
        changelog in the same commit as the version bump. Both halves (Makefile byte-identical).

## 4. Template gaps (missing promised features)

- [x] **CI added** — `.github/workflows/ci.yml` + `tag-on-prod.yml` (release tag on push to
      `prod`) + `.github/CODEOWNERS` in BOTH halves.
      RESOLVED: dev/prod is the chosen model (see §4 branch-naming, below).
- [x] **Jinja-collision FIXED canonically:** `cookiecutter.json` now has
      `"_copy_without_render": [".github/workflows/*"]` so workflow files (full of GitHub
      `${{ }}` expressions) are copied verbatim and never break the bake. CODEOWNERS lives in
      `.github/` (not `workflows/`) so its `{{ cookiecutter.githubUsername }}` still renders.
      → Workflows may now contain `${{ }}` freely; the old `{% raw %}` workaround is unnecessary.
      (`testMakeHelp` assertion updated to match the new "make targets" help banner.)
- [x] `make docs` / sphinx target — **dropped** from the new Makefile (no docs/ toolchain).
- [x] **Branch naming — DECIDED (2026-06-25): `dev`/`prod`.** Applied across CI (already),
      `tag-on-prod.yml`, README release step, and generated changelog URL. No `master`/`main` in
      user-facing docs/automation. See `.claude/specs/project-conventions.md` §3.
- [x] Generated `pyproject.toml` empty blocks — **FILLED (2026-06-25)**: templated `keywords`
      (`packageName`, python, package); `classifiers` (Alpha, MIT, OS-Independent, Python 3.10–3.13
      matching §8); `dependencies` kept empty-with-comment (library declares ranges). `[project.urls]`
      was already populated.
- [x] Generated smoke test — **REAL (2026-06-25)**: package `__init__` exposes `__version__`;
      module ships a `hello()` sentinel; `test{{moduleName}}.py` imports both and asserts. Added
      `pythonpath = ["src"]` so `pytest`/`make test` work on a fresh checkout without install. Root
      bake tests (`testBakeAndRunTests`, `testGeneratedModuleIsImportable`) run the baked suite green;
      fixed the prior no-op `== 0` assertion.

## 5. Makefile hygiene

- [x] `.PHONY` — regenerated from the final target set in the new Makefile (both halves).
- [x] `release` shell/`set -euo pipefail` concern — **resolved (root, 2026-06-24): decided AGAINST
      global `.ONESHELL`.** It's file-global (would flip `installDev`'s leading-`-` to whole-recipe
      error-ignore) and the release recipes are single-command targets sequenced by Make's prereq
      chain, which already fails fast. Revisit only if a multi-line side-effecting recipe is added.
- [x] Root vs template Makefile — decision: **intentionally identical** (uses `$(notdir
      $(CURDIR))` + reads pyproject, no per-half vars). Kept byte-identical via the scaffold.
- [x] `testMakeHelp` — now PASSES (new help text matches); confirmed in bake run (6/6 green).

> See `.claude/plans/nearly-all-of-the-jaunty-sloth.md` for the full Makefile reconstruction
> plan and `.claude/specs/devops-makefile-principles.md` for the lessons driving recipe design.
> Recipe bodies are being filled grouping-by-grouping; many targets are `# TODO(Gx)` stubs.

## 6. Root vs. template `lint`/`format`/`typecheck` targets

- [x] **RESOLVED (2026-06-26).** Root code lives in `hooks/`+`tests/` (no `src/`); template code
      lives in `src/`. Per-half scoping is done with explicit `PY_*` Make vars, **not** ruff/mypy
      config: the Makefile defaults `PY_SRC ?= hooks` (root) and the **template `.env` overrides
      `PY_SRC=src`**, so the two `.env` files differ while the Makefile stays byte-identical.
      Verified: a baked project's `make -n uv-lint`/`uv-typecheck` scan `src tests`; the root's scan
      `hooks tests`. (The earlier "resolve via ruff/mypy config per half" plan is superseded.)

## 7. Makefile recipe backlog (command-by-command pass)

Scaffold is in place; these targets are still `# TODO` stubs. Bake in the lessons from
`.claude/specs/devops-makefile-principles.md` as each is implemented. **It may or may not be a
better implementation — critique each.** Grouped in build order:

- [x] **Item 1 — dependency model (BKM) DONE (2026-06-28).** The one production-tested model:
      **`pyproject.toml` declares dependency NAMES ONLY** (no version pins, no git URLs); **only the
      application layer pins**; module-level pins cause conflicts. **The requirements file is the only
      place for git-based pointers**, and **every install path — pip AND uv — leans on it**:
      `uv-sync`/`uv-sync-headless`/`uv-sync-dev`/`uv-sync-release`/`uv-sync-local`/`uv-bootstrap`/
      `uv-refresh`/`uv-test-all` and pip `installDev`/`refresh` all run `-r requirements*.txt` then the
      editable self-install (`-e ".[dev]"` / `-e "."`). `requirements.txt` is **hand-authored &
      committed** (NOT `uv pip compile`-generated); `requirements-release.txt` (tag-pinned) is also
      committed; `requirements-local.txt` (local editable overrides) is **gitignored**. `uv` runs
      through its **pip interface** only — **no `uv.lock`** (gitignored), **no `lock`/compile target**.
      `installDev` dropped `--break-system-packages`/`--force-reinstall` (use a venv). **Supersedes the
      earlier "ranges, no committed lock" decision and `devops-makefile-principles.md` Lesson 1.** See
      spec §6.
- [x] **Clean (G6 base) DONE.** `clean-build` / `clean-artifacts` / `clean-test` remove only
      build/cache/test artifacts. They never touch the authored `requirements*.txt` (those are source,
      not generated). `clean-build` removes any stray `uv.lock` (never committed). No committed
      lockfile exists to protect (Item 1).
- [x] **Flush/nuke (G6, Lesson 2) DONE.** `uv-flush-cache`, `uv-flush-envs` (rm -rf
      `.venv` + `.venvs/*` + `.venv-py*`), `uv-flush-pythons`, `uv-flush-everything` (= `clean` +
      `uv-flush-envs` + `uv-flush-cache`), `uv-nuke`, pip `nuke`/`list` — all have real recipes
      (verified `make -n`). The separate `uv-clean` was folded into the base `clean` tier (`uv.lock`
      removal now lives in `clean-build`). Venv-deletion is the primitive; the graduated targets have
      explicit blast radius. pip `nuke` is documented as the inferior fallback.
- [x] **Refresh (G7, Lesson 3) DONE (2026-06-28).** "refresh" = reinstall from the requirements file
      then upgrade the editable dev install. `uv-refresh` → `uv cache clean` + `uv pip install -r
      requirements.txt` + `uv pip install --upgrade -e ".[dev]"`; pip `refresh` is the inferior fallback
      (`$(PIP) install -r requirements.txt` + `--upgrade -e ".[dev]"`). Targeted churn is still
      available ad-hoc via `uv pip install --reinstall-package <name>`.
- [x] **Multi-repo editable (Lesson 4) DONE (2026-06-28).** Per the BKM, local editable siblings go
      through a **requirements file**, never the manifest. **`requirements-local.txt`** holds the
      `-e ../sibling` lines; **`make uv-sync-local`** installs it then the editable package. It is
      **gitignored** (both halves); CI/release never read it. `[tool.uv.sources]` / path overrides in
      `pyproject.toml` are **rejected** (manifest must stay names-only). The earlier
      `editable-local`/`sync-local`/`LOCAL_OVERLAY` overlay machinery and the `[tool.uv.sources]`
      commented example were **removed**. (Also fixed the stale CONTRIBUTING setup steps:
      `mkvirtualenv`/`setup.py develop` → `make dev`; `make lint`/`test-all` → `make uv-fullCheck`;
      Python "3.12 and 3.13" → "3.10 through 3.13".)
- [x] **Quality (G5) DONE (2026-06-26, plan 11).** `uv-lint` (read-only `ruff check`), `uv-format`
      (`ruff format` **then** `ruff check --fix --unsafe-fixes` — `--unsafe-fixes` is **intentional /
      `# KEEP`**, do not strip), `uv-typecheck` (`mypy`), `uv-fullCheck` (composes
      lint+typecheck+test; prior duplicate recipe line removed). No separate `uv-lintFix` (fixing is
      via `uv-format`). **ty decided OUT (D1)** — `uv-typecheck-ty` removed from `.PHONY` (no recipe);
      a comment marks it deferred. Paths scoped per half via `PY_*`/`.env` (see §6).
      `[tool.ruff]`/`[tool.mypy]` config + `.pylintrc` deletion already landed (§3).
- [x] **Test (G4) DONE (2026-06-26, plan 12).** `test` (path-free `pytest`), `uv-test` (now
      **depends on `uv-sync`** so a fresh checkout never tests an empty/stale `.venv` — the
      acceptance "no false-green no-op" is met), `uv-test-all`/`uv-test-matrix` (`.venvs/<ver>`,
      consistent with `list-uv`/`uv-flush-envs`; per-version env activates `.venvs/<ver>` then
      `uv pip install -e ".[dev]"` + `python -m pytest`), `testInEnv*` (clean-room `$(VENV)`).
      Applied to both halves. *Deferred (optional, not blocking):* `uv run --python X` to avoid
      per-version reinstall at matrix scale.
  - [x] **Onboarding entrypoint (review adoption):** added `make dev` / `make setup` aliases
        (→ `uv-sync`) so first-time setup is one command. Both halves.
- [~] **Build & release.** DONE (root, 2026-06-24): `build` (no `uv-build`); `validateBuild` (no
      `uv-validateBuild` — both installer-agnostic, dead `.PHONY` entry removed); `release-test`
      (TestPyPI, gated on `checkCleanGit`, prints `make -s version`); `release` **defers to CI**
      (refuses local upload, exits 1) per the shared-memory `operations/ci-cd.md` spec — *single
      authoritative pipeline path, no out-of-band deploys*. `RELEASE_ENABLED` gate removed from
      Makefile + `.env`. Shell-strictness resolved (§5: no global `.ONESHELL`).
      DONE (2026-06-25): **`publish.yml` added as a guarded SCAFFOLD** in both halves
      (`on: push: tags: 'v*'`, fails loudly until PyPI auth wired — Trusted Publishing or
      `PYPI_API_TOKEN`). D2 auth documented in the scaffold header. **Plan 13 CLOSED** →
      `.claude/specs/project-conventions.md` §5. Implementing the upload steps is left to the user.
- [~] **Version/git/util (G8).** DONE: `help` banner; `bump-patch/minor/major` + `bump-%`
      (`BUMPVERSION := bumpversion --allow-dirty`, kebab-case — deliberate); `version` via
      `tomllib` (`$(PYTHON) -c "import tomllib; ..."`); `checkCleanGit` via
      `git status --porcelain` (strict); `open-github` (OS-aware: macOS `open` / Linux
      `xdg-open`, default browser, derives URL from first remote). **`tag` AXED** — tagging is
      owned by `.github/workflows/tag-on-prod.yml` (auto `v<version>` on push to `prod`), so a
      manual `make tag` is redundant/double-tags. G8 complete.
  - [x] **Orphaned by removing `tag` — RESOLVED (root, 2026-06-24):** (a) `checkCleanGit` now has a
        consumer — it gates `release-test`. (b) the grep `VERSION` make-var was **deleted**;
        `release-test`/`release` derive the version from `$(MAKE) -s version` (tomllib).
  - [x] **tomllib needs Python ≥3.11** but floor is 3.10 — **RESOLVED (2026-06-25)**: `make
        version` now tries `tomllib` and falls back to `grep`/`cut` (dependency-free), so it runs
        on a 3.10 interpreter. Both halves. See `.claude/specs/project-conventions.md` §2.

## 8. Config reconciliation

- [x] Python version sources disagree — **RESOLVED (2026-06-25)**. Canonical set: **default
      3.13, floor 3.10**. Aligned: `.env` (`DEFAULT_PYTHON=3.13`, `PYTHONS=3.10 3.11 3.12 3.13`),
      `.python-version`=3.13 (both halves, template now ships one), Makefile `?=` fallbacks,
      `requires-python>=3.10`, classifiers 3.10–3.13. See `.claude/specs/project-conventions.md` §2.
