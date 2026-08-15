# Project Conventions — Resolved Decisions

Durable verdicts distilled from closed action-plans. These are settled; do **not**
re-litigate without a new explicit decision. Companion to
`.claude/specs/devops-makefile-principles.md` and `.claude/GAPS.md`. Each section notes the
GAPS § it resolves and the source plan (now removed).

> Two-halves reminder: "root" = template tooling that runs in *this* repo; "template" =
> files under `{{cookiecutter.projectIdentifier}}/` that render into a new project. Most
> conventions apply to **both** halves and the Makefile is kept byte-identical, so per-half
> differences live in **config**, not recipe args.

---

## 1. Naming convention — two layers (GAPS §2, plan 02)

**Verdict (revised 2026-08-14, plan 17 — supersedes the 2026-06-25 two-layer split, which
itself superseded "keep camelCase everywhere").** The 2026-06-25 revision was right that the
import surface must be snake_case, but wrong to put the *distribution name* in that same layer.
There are **three** layers, not two:

- **Distribution layer → lowercase kebab-case.** `projectIdentifier` — the distribution name,
  the generated project folder, and the GitHub repo slug — is **kebab-case**
  (`python-boilerplate`). Enforced by `pre_gen_project.py` (regex `^[a-z0-9]+(-[a-z0-9]+)*$`).
- **Import layer → PEP-8 snake_case.** `packageName` and `moduleName` — what consumers
  `import` — stay **snake_case** (`my_package`, `my_module`). Enforced by the same hook
  (regex `^[a-z_][a-z0-9_]*$`). This is not stylistic: hyphens are not legal Python
  identifiers, so `import my-package` is a syntax error.
- **Tooling layer → camelCase (house style, kept).** The cookiecutter variable **keys**
  themselves (`projectIdentifier`, `packageName`, `moduleName`), `test*` function names
  (`testBakeWithDefaults`), and some Makefile targets stay camelCase ("Nick's workflow").
  These are internal tooling names, never an import surface. Ruff `N`/pep8-naming stays omitted
  (§4) so these don't fail CI.

**Why kebab for the distribution name:** hyphens are the conventional spelling for a Python
distribution; underscores are legal but unconventional. The 2026-06-25 text justified the
snake_case distribution name as following "PEP 8 / PEP 503" — **that was a misapplication.**
PEP 8 governs the *import* identifier, and PEP 503 defines *normalization equivalence* (pip
treats `python-boilerplate` and `python_boilerplate` as the same project). Neither expresses a
preference for underscores in a distribution name. That bad reasoning is what produced the
defect plan 17 fixed.

**Why camelCase is still excluded from both generated layers:** `import myPackage` surprises
consumers and fights PyPI norms; the house style only ever made sense for tooling-internal
names.

### One name, three surfaces

The generated **folder name**, `pyproject [project].name`, and the **GitHub repo slug** are all
the same string — `projectIdentifier`. `ghIdentifier` composes from it, so every GitHub URL
inherits it. This is load-bearing, not incidental: `git clone` creates a directory named after
the repo, so if these diverged a contributor would land in a differently-named directory than
the one the bake produced. `tests/testBakeProject.py::testGithubUrlsMatchFolderName` guards it.

### D1 — check, do not transform

**The bake validates what the user typed; it never rewrites it.** A bad identifier is a loud,
non-zero-exit abort with a corrective message ("Did you mean 'my-project'?"), never a silent
fix-up. The suggestion in the error text is display-only and is never applied.

This is a standing rule, recorded so a future change doesn't reintroduce auto-correction.
Cookiecutter ≥2.x registers `SlugifyExtension` in `default_extensions`, so a `slugify` filter is
available with no `_extensions` key and no new dependency — deriving `projectIdentifier` from
`projectName` is *easy*, which is exactly why this rule is written down. It was rejected: slugify
silently flattens concatenated CamelCase (`py-foundationTools` → `py-foundationtools`, word
breaks lost), and a name the user did not choose is worse than an error they can act on.

Corollary: `projectName` (prompt 4) is **headings-only**. It does not set the folder name and is
not derived from — the hyphenated folder/dist name is typed independently at `projectIdentifier`
(prompt 5).

**Discoverability:** per-prompt help lives in the `cookiecutter.json` `__prompts__` block
(cookiecutter ≥2.2) so guidance shows during the interactive walkthrough; a quick-reference
table of all variables lives in the root README.

---

## 2. Python version policy (GAPS §3, §7, §8, plan 04)

**Verdict — canonical set:** default **3.13**, support floor **3.10**.

- `requires-python = ">=3.10"` (both halves).
- `.python-version` = `3.13` (both halves; template now ships one for parity).
- `.env`: `DEFAULT_PYTHON=3.13`, `PYTHONS=3.10 3.11 3.12 3.13`. Makefile `?=` fallbacks match.
- `classifiers` advertise 3.10–3.13.
- CI test matrix runs 3.10/3.11/3.12 (+ default).

**tomllib-floor pattern.** `tomllib` is stdlib only on ≥3.11, but the floor is 3.10. `make
version` therefore tries `tomllib` and falls back to `grep`/`cut`, dependency-free:

```make
version:
	@$(PYTHON) -c "import tomllib; print(tomllib.load(open('pyproject.toml','rb'))['project']['version'])" 2>/dev/null \
		|| grep -m1 '^version' pyproject.toml | cut -d'"' -f2
```

Principle: tooling that must run on the support floor cannot assume floor-incompatible stdlib —
guard with a no-dep fallback rather than raising the floor or adding a dependency.

---

## 3. Branch model — `dev`/`prod` (GAPS §4, plan 06)

**Verdict.** Two-branch model: `dev` (integration) and `prod` (released). No `master`/`main`
in user-facing docs or automation.

- CI (`ci.yml`) runs on PRs targeting `dev`/`prod`.
- `tag-on-prod.yml` auto-creates a `v<version>` tag when `pyproject.toml`'s version changes on
  a push to `prod`.
- README and the generated `[project.urls].changelog` point at `prod`.

Release flow: bump version → merge to `prod` → `tag-on-prod.yml` tags `v<version>` →
`publish.yml` (§5) promotes the tagged build.

---

## 4. Lint & typecheck stack (GAPS §3, §6, plan 03)

**Verdict.** **ruff** (lint + format) + **mypy `--strict`**. black/pylint removed; `.pylintrc`
deleted (both halves).

**Config-only per-half path resolution (the §6 trick).** The Makefile is byte-identical across
halves, so `ruff check .` / `mypy .` run with **no path args** and resolve scope from each
half's `pyproject.toml`:

- Root half: `[tool.ruff] src = ["hooks","tests"]`, `[tool.mypy] files = ["hooks","tests"]`
  (this repo has no `src/`).
- Template half: `src`/`files = ["src","tests"]` (generated projects use a `src/` layout).

`target-version = "py310"` / `python_version = "3.10"` (the support floor, §2). Lint selection
starts at `["E","F","I","UP","B"]`; **pep8-naming (`N`) is intentionally omitted** so the
camelCase house style (§1) never fails CI.

**Makefile quality targets (plan 11).**

- `uv-lint` → `ruff check $(PY_ALL)` — read-only; non-zero exit for CI.
- `uv-format` → `ruff format $(PY_ALL)` **then** `ruff check --fix --unsafe-fixes $(PY_ALL)`.
  **`--unsafe-fixes` is intentional and load-bearing here** — it is relied upon after the
  2026-06-25 findings and is marked `# KEEP` in the recipe. **Do not strip it** in cleanup/refactor
  passes (removing it has regressed this target before). There is **no** separate `uv-lintFix`
  target; fixing happens through `uv-format`.
- `uv-typecheck` → `mypy …`; `uv-fullCheck` composes `uv-lint uv-typecheck uv-test`.

**Decision D1 — `ty` is OUT.** Astral's preview type-checker is pre-release; `uv-typecheck-ty`
was removed from `.PHONY` (it had no recipe) and is not part of `uv-fullCheck`. A comment marks it
deferred; revisit when it stabilizes.

**Per-half path scoping → `PY_*` vars in `.env`, not config.** The targets read `$(PY_SRC)` /
`$(PY_ALL)`. The Makefile defaults to `PY_SRC ?= hooks` (root has no `src/`); the **template
`.env` overrides `PY_SRC=src`**. So the two `.env` files differ but the Makefile stays
byte-identical (see the two-halves note below). This supersedes the original "resolve via ruff/mypy
config per half" idea.

*Note:* landing the ruff/mypy config surfaced real pre-existing lint debt in `hooks/`+`tests/`
(unused imports, `assert False`, pointless comparisons). That cleanup is separate from the config.

---

## 5. Release auth — CI-owned, scaffolded (GAPS §4, §5, §7, plan 13)

**Verdict.** Publishing is owned by CI, not the Makefile (per the shared `operations/ci-cd.md`
spec: single authoritative pipeline path, no out-of-band deploys).

- `make release` **refuses** local upload and prints the CI-driven procedure; `make
  release-test` allows a TestPyPI dry-run gated on a clean tree.
- `.github/workflows/publish.yml` is shipped as a **guarded scaffold** (`on: push: tags: v*`)
  that fails loudly until the user wires PyPI auth (Trusted Publishing recommended, or a
  `PYPI_API_TOKEN` secret). Left intentionally for the user to implement.

---

## 6. Dependency model — module declares names, requirements file pins (GAPS §5, §7)

**BKM.** This is the one production-tested model; many other arrangements have been tried over the
years and largely failed. It is non-negotiable for this repo and the generated projects:

1. **Only the application layer pins versions.** A library/module/template never pins.
2. **Module-level pinning causes dependency conflicts** — so `pyproject.toml` declares dependency
   **names only**, never versions.
3. **The requirements file is the only place for git-based dependency pointers**
   (`pkg @ git+https://…`, `-e git+…`). A git URL in `pyproject.toml` is a module-deployment
   disaster.
4. **The Makefile leans on the requirements file for BOTH pip and uv workflows** — every install
   path runs `-r requirements.txt` (or a sibling requirements file), then the editable self-install
   (`-e ".[dev]"` / `-e "."`).
5. **`pyproject.toml` maintains only the module/dependency names** — no version pins, no git URLs.

**Requirement files** (all hand-authored — never `uv pip compile`-generated; committed except the
local overlay):

- `requirements.txt` — base install/test pointers; git-based pointers live here.
- `requirements-release.txt` — tag-pinned release set (`make uv-sync-release`).
- `requirements-local.txt` — per-machine local editable sibling overrides (`make uv-sync-local`);
  **gitignored**, never read by CI/release.

**`uv` runs through the pip interface only** (`uv pip …`), which never writes a lockfile; uv's
*project* interface (`uv sync`/`uv lock`) is not used. **No `uv.lock`** (gitignored both halves) and
**no `lock`/compile target**. `installDev` does not pass `--break-system-packages`/`--force-reinstall`
— use a venv.

This **supersedes** `devops-makefile-principles.md` Lesson 1 **and** the global
`makefile-devops-approach.md` Lesson 1: the pinned set is **authored**, not generated, and pinning is
an application-layer concern. Where any of them disagree, **this BKM wins**.

---

## 7. Generated-project defaults & test surface (GAPS §4, plans 07, 08)

**pyproject defaults.** A freshly baked `pyproject.toml` is publishable-shaped, not empty:

- `keywords` seeded from context (`{{ packageName }}`, `python`, `package`).
- `classifiers` include Development Status, Intended Audience, MIT license, OS-Independent, and
  `Programming Language :: Python :: 3.10`–`3.13` — the version rows **track the §2 canonical
  matrix** (keep in sync).
- `dependencies` left **empty with a guiding comment** (a fresh library has no runtime deps;
  when added, declare **names only — never pins or git URLs** per §6; those go in
  `requirements*.txt`). Dev deps live in the `[dev]` extra (names only).

**Test surface (non-vacuous smoke test).**

- The package `__init__.py` exposes `__version__ = "{{ cookiecutter.version }}"`; the module
  ships a `hello()` sentinel. The generated `test{{ moduleName }}.py` imports both and asserts.
- `[tool.pytest.ini_options] pythonpath = ["src"]` lets `pytest` / `make test` import the
  `src/`-layout package **without an install**, so a fresh checkout tests green immediately.
- Root bake tests prove it: `testBakeAndRunTests` and `testGeneratedModuleIsImportable` run the
  baked suite and assert exit 0; `testBakeRejects*` assert the snake_case hook (§1) aborts bad
  bakes. (The earlier `runInsideDir(...) == 0` no-op assertion was fixed to a real `assert`.)

---

## 8. Version bump & changelog roll (GAPS §3, plan 05)

**Verdict.** A version bump and its changelog entry move **together, in one commit**.

- `bump-patch`/`bump-minor`/`bump-major` are a **static pattern rule** (`bump-patch bump-minor
  bump-major: bump-%:`) sharing one recipe — `$*` is the part. The standalone generic `bump-%`
  rule and the three duplicated bodies were collapsed into this.
- The recipe runs `bumpversion <part>` (config `commit = true`, so it commits the `pyproject.toml`
  version edit), then a `roll_changelog` define rewrites `HISTORY.md`: an `awk` step inserts a
  fresh `## [<version>] - <YYYY-MM-DD>` section immediately under the `## [Unreleased]` anchor
  (Keep-a-Changelog), folding the accumulated notes into the new version and leaving `[Unreleased]`
  empty. It then `git add HISTORY.md && git commit --amend --no-edit` to fold the changelog into
  bump2version's commit.
- Mechanism **(B)** from the plan (recipe-owned, real `date +%F`) was chosen over a
  `[bumpversion:file:HISTORY.md]` section (which can't inject a real date). `.bumpversion.cfg`
  stays focused on the version string only.
- Both halves; the Makefile is byte-identical so the recipe is the same. Verified via dry-run: the
  `[Unreleased]` header empties and notes reappear under the dated section.

---

## 9. Multi-repo co-development (GAPS §7)

**Verdict.** Per §6, local editable sibling repos are handled through a **requirements file**, not
through `pyproject.toml` (no `[tool.uv.sources]`, no path/git overrides in the manifest — those are a
module-deployment disaster).

- A per-machine **`requirements-local.txt`** holds `-e ../sibling` editable lines. **`make
  uv-sync-local`** creates the venv, installs `-r requirements-local.txt`, then the editable package
  (`-e ".[dev]"`). The file is **gitignored** and never read by CI/release; a solo checkout simply
  doesn't have one.

The generated `CONTRIBUTING.md` documents this under "Co-developing with sibling repositories."

---

## Note on the two halves

The Makefiles **are byte-identical** across halves again (verified: `diff Makefile
{{cookiecutter.projectIdentifier}}/Makefile` is empty). Per-half differences live entirely in
**`.env`**, the user-editable surface the Makefile `include`s:

- Path scoping: the Makefile defaults `PY_SRC ?= hooks` (root has no `src/`); the **template
  `.env` sets `PY_SRC=src`** (generated projects use a `src/` layout). The recipes read
  `$(PY_SRC)`/`$(PY_ALL)`, so the same Makefile lints the right tree in each half.
- The release recipes are identical too: both defer PyPI upload to CI (the old `RELEASE_ENABLED`
  gate and grep `VERSION` var were removed from **both** halves; plan 13/14 template port is done).

This is the cleaner realization of the original "config, not recipe args" aspiration — the
divergence is one `.env` line, not a forked Makefile.
