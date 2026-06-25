# GAPS & Refactor Backlog

Living list of known defects, inconsistencies, and intended changes for the `py-cookiecut`
rip-and-tear. This is **greenfield** — no downstream consumers to protect, so prefer
decisive replacement. Check items off and add new ones as the refactor proceeds.

Legend: `[ ]` open · `[~]` in progress · `[x]` done

---

## 1. Stale / on-disk artifacts (cleanup)

- [ ] `build/lib/hooks/` — byte-identical copy of `hooks/`, leftover from `python -m build`.
      Gitignored but present on disk; delete.
- [ ] `py_cookiecut.egg-info/` — build leftover, gitignored but on disk; delete.
- [ ] `.DS_Store` on disk (gitignored); delete.

## 2. Naming-convention enforcement (the big decision)

- [ ] Template forces **camelCase** package/module names (`myPackage`, `myModule`), which
      violates PEP 8 / PyPI import norms. Decide: keep as deliberate convention, or switch
      generated packages to lowercase while keeping camelCase for tooling. **Decision needed.**
- [ ] `pre_gen_project.py` error message says "use `_` instead" but the regex
      `^[_a-zA-Z][_a-zA-Z0-9]+$` only *rejects `-`* — it never enforces that `_` was used.
      Align message with actual validation (and validate `packageName`/`moduleName` too, not
      just `projectIdentifier`).

## 3. Tooling drift / contradictions

- [~] Lint stack: toolchain decided = **ruff** (lint+format) + **mypy --strict**; black/pylint
      removed from the `[dev]` extra. STILL TODO: add `[tool.ruff]` config to pyproject and
      delete the obsolete `.pylintrc` (both halves). ty (preview) deferred to G5.
- [x] `requirements_dev.txt` / `requirements_prod.txt` — **deleted**.
- [x] Dev-dependency 3-way duplication — **consolidated**: pyproject `[dev]` extra (renamed
      from `develop`) is the source; a minimal `requirements.txt` starter is shipped; Makefile
      `installDev`/`uv-sync` install `-r requirements.txt` + `-e ".[dev]"`. NOTE: extra renamed
      `develop`→`dev` in both pyprojects to match recipes.
- [ ] `.python-version` pins **3.13** but `requires-python = ">=3.10"`. Reconcile.
- [x] `personal_repos = []` empty optional-dependency group — **removed** from both pyprojects.
- [x] `bump2version` config added: `.bumpversion.cfg` in root and template, bumping the
      version in `pyproject.toml` (`commit = True`, `tag = False`). Verified the search/replace
      matches via dry-run.
  - [ ] Follow-up: consider having bump2version also auto-roll the `HISTORY.md`
        `[Unreleased]` header on release.

## 4. Template gaps (missing promised features)

- [x] **CI added** — `.github/workflows/ci.yml` + `tag-on-prod.yml` (release tag on push to
      `prod`) + `.github/CODEOWNERS` in BOTH halves.
      OPEN: triggers on `[dev, prod]` — reconcile branch names (see below).
- [x] **Jinja-collision FIXED canonically:** `cookiecutter.json` now has
      `"_copy_without_render": [".github/workflows/*"]` so workflow files (full of GitHub
      `${{ }}` expressions) are copied verbatim and never break the bake. CODEOWNERS lives in
      `.github/` (not `workflows/`) so its `{{ cookiecutter.githubUsername }}` still renders.
      → Workflows may now contain `${{ }}` freely; the old `{% raw %}` workaround is unnecessary.
      (`testMakeHelp` assertion updated to match the new "make targets" help banner.)
- [x] `make docs` / sphinx target — **dropped** from the new Makefile (no docs/ toolchain).
- [ ] **Branch naming unresolved across the repo:** new CI triggers on `dev`/`prod`; old
      `tag`/`release`/README reference `master`; actual repo uses `development`/`main`.
      Pick ONE model and apply to CI, Makefile `tag`/`release`, and README.
- [ ] Generated `pyproject.toml` ships empty `keywords`, `classifiers`, `dependencies`, and
      `[project.urls]` blocks — fill with sensible defaults or template them.
- [ ] Generated test (`test{{moduleName}}.py`) has commented-out imports and a `test_content()`
      that asserts nothing. Provide a real smoke test.

## 5. Makefile hygiene

- [x] `.PHONY` — regenerated from the final target set in the new Makefile (both halves).
- [~] `release` shell/`set -euo pipefail` concern — moot until release recipes are written
      (currently TODO); revisit when implementing `release`/`release-test` in the command pass.
- [x] Root vs template Makefile — decision: **intentionally identical** (uses `$(notdir
      $(CURDIR))` + reads pyproject, no per-half vars). Kept byte-identical via the scaffold.
- [x] `testMakeHelp` — now PASSES (new help text matches); confirmed in bake run (6/6 green).

> See `.claude/plans/nearly-all-of-the-jaunty-sloth.md` for the full Makefile reconstruction
> plan and `.claude/specs/devops-makefile-principles.md` for the lessons driving recipe design.
> Recipe bodies are being filled grouping-by-grouping; many targets are `# TODO(Gx)` stubs.

## 6. Root vs. template `lint`/`format`/`typecheck` targets

- [~] Root quality targets must lint the right paths: root code lives in `hooks/`+`tests/`
      (no `src/`); template code lives in `src/`. When implementing `uv-lint`/`uv-typecheck`
      (G5), make the target paths correct for EACH half (they're not identical here even though
      the Makefile is). Resolve via ruff/mypy config (`[tool.ruff]`, `[tool.mypy]`) per half.

## 7. Makefile recipe backlog (command-by-command pass)

Scaffold is in place; these targets are still `# TODO` stubs. Bake in the lessons from
`.claude/specs/devops-makefile-principles.md` as each is implemented. **It may or may not be a
better implementation — critique each.** Grouped in build order:

- [ ] **Item 1 — dependency SoT (Lesson 1).** Add `lock` (`uv pip compile`); rewrite `uv-sync`
      (→ `uv pip sync` + `-e . --no-deps`) and `installDev` (`-r requirements.txt` + `-e . --no-deps`,
      drop `--break-system-packages`/`--force-reinstall`). DECISIONS PENDING: compile-as-lock y/n;
      `uv pip sync` vs `uv pip install`; commit generated `requirements.txt`/`uv.lock` y/n.
- [ ] **Clean (G6 base).** `cleanBuild` / `cleanArtifacts` / `cleanTest` — must NOT delete a
      committed lockfile (Lesson 2).
- [ ] **Flush/nuke (G6, Lesson 2).** `uv-clean`, `uv-flush-cache`, `uv-flush-envs` (rm -rf
      `.venv` + `.venvs/*`), `uv-flush-pythons`, `uv-flush-everything`, `uv-nuke`, pip `nuke`/`list`.
      Venv-deletion is the primitive; no per-package uninstall for correctness.
- [ ] **Refresh (G7, Lesson 3).** `uv-refresh` via `uv pip sync` / `--reinstall-package`; pip
      `refresh` as documented inferior fallback.
- [ ] **Multi-repo editable (Lesson 4).** Add `editable-local`/`sync-local` overlay convention
      + document `[tool.uv.sources]`/workspaces for sibling repos (py-foundationTools, py-cvTools,
      py-MathTools, py-robotTools, py-machineVisionTools, …).
- [ ] **Quality (G5).** `uv-lint`/`uv-lintFix`/`uv-format` (ruff), `uv-typecheck` (mypy --strict),
      `uv-typecheck-ty` (decide ty in/out), `uv-fullCheck`. Add `[tool.ruff]`/`[tool.mypy]` config;
      correct paths per half (see §6); delete `.pylintrc`.
- [ ] **Test (G4).** `test`, `uv-test` (ensure synced env first — no fresh-env no-op), `uv-test-all`
      / `uv-test-matrix` (`.venvs/<ver>`), `testInEnv*`.
- [ ] **Build & release.** `build`/`uv-build`, `validateBuild`/`uv-validateBuild`, `release-test`
      (TestPyPI), `release` (PyPI). Reconcile `set -euo pipefail`/shell (§5).
- [~] **Version/git/util (G8).** DONE: `help` banner; `bump-patch/minor/major` + `bump-%`
      (`BUMPVERSION := bumpversion --allow-dirty`, kebab-case — deliberate); `version` via
      `tomllib` (`$(PYTHON) -c "import tomllib; ..."`); `checkCleanGit` via
      `git status --porcelain` (strict); `open-github` (OS-aware: macOS `open` / Linux
      `xdg-open`, default browser, derives URL from first remote). **`tag` AXED** — tagging is
      owned by `.github/workflows/tag-on-prod.yml` (auto `v<version>` on push to `prod`), so a
      manual `make tag` is redundant/double-tags. G8 complete.
  - [ ] **Orphaned by removing `tag`:** (a) `checkCleanGit` has no consumer now — kept as a
        standalone guard / future `release` prereq. (b) header `VERSION` make-var (grep,
        `v`-prefixed) is now UNUSED — `version` target uses tomllib. Converge: have `release`/
        `release-test` derive from tomllib (`make -s version`); then delete the `VERSION` var.
  - [ ] **tomllib needs Python ≥3.11** but `requires-python = ">=3.10"`. `make version` breaks
        on a 3.10 interpreter. Resolve via §8 (raise floor to 3.11) or add a `tomli` fallback.

## 8. Config reconciliation

- [ ] Python version sources disagree: `.python-version`=3.13, `.env` `DEFAULT_PYTHON=3.14` /
      `PYTHONS=3.10 3.11 3.12 3.14`, `requires-python>=3.10`, Makefile fallback `3.10 3.11 3.12`.
      Pick the canonical set and align `.python-version` + Makefile fallback to `.env`.
