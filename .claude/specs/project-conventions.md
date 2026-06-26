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

**Verdict (revised 2026-06-25 — supersedes the earlier "keep camelCase everywhere").** Split
the two layers that were previously conflated:

- **Generated identifiers → PEP-8 snake_case.** The *values* a user supplies for
  `projectIdentifier`, `packageName`, `moduleName` — i.e. the distribution name, the import
  package, and the module file — are **lowercase snake_case** (`python_boilerplate`,
  `my_package`, `my_module`). This is what the import surface and PyPI consumers see, so it
  follows PEP 8 / PEP 503. The `cookiecutter.json` defaults and `__prompts__` already teach
  this; `pre_gen_project.py` enforces it (regex `^[a-z_][a-z0-9_]*$`).
- **Tooling identifiers → camelCase (house style, kept).** The cookiecutter variable **keys**
  themselves (`projectIdentifier`, `packageName`, `moduleName`), `test*` function names
  (`testBakeWithDefaults`), and some Makefile targets stay camelCase ("Nick's workflow").
  These are internal tooling names, never an import surface. Ruff `N`/pep8-naming stays omitted
  (§4) so these don't fail CI.

**Why:** camelCase as an importable package (`import myPackage`) surprises consumers and fights
PyPI norms; the deliberate house style only ever made sense for tooling-internal names.

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
camelCase house style (§1) never fails CI. `ty` (preview type-checker) is deferred — `# TODO(G5)`.

*Note:* landing this config surfaced real pre-existing lint debt in `hooks/`+`tests/` (unused
imports, `assert False`, pointless comparisons). That cleanup is separate from the config.

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

## 6. Lockfile policy — no `uv.lock` committed (GAPS §5, §7, plan 09 decision)

**Verdict.** This is a library/template: declare version ranges (`requires-python`), do **not**
commit a lockfile. `uv.lock` is only written by uv's *project* interface (`uv sync`/`uv lock`);
the *pip* interface (`uv pip install`/`sync`/`compile`) never writes one — so stay on `uv pip`.
`uv.lock` is gitignored (both halves) as belt-and-suspenders.

*Still open (impl, not decision):* the broader plan-09 Makefile work — `lock` target,
`uv-sync`/`installDev` rewrite, clean/flush/refresh — and the separate question of whether a
generated `requirements.txt` lock (via `uv pip compile`, per devops-makefile-principles Lesson 1)
is committed. The *uv.lock* verdict above is settled regardless of that.

---

## 7. Generated-project defaults & test surface (GAPS §4, plans 07, 08)

**pyproject defaults.** A freshly baked `pyproject.toml` is publishable-shaped, not empty:

- `keywords` seeded from context (`{{ packageName }}`, `python`, `package`).
- `classifiers` include Development Status, Intended Audience, MIT license, OS-Independent, and
  `Programming Language :: Python :: 3.10`–`3.13` — the version rows **track the §2 canonical
  matrix** (keep in sync).
- `dependencies` left **empty with a guiding comment** (a fresh library has no runtime deps;
  declare ranges, not pins, when added). Dev deps live in the `[dev]` extra.

**Test surface (non-vacuous smoke test).**

- The package `__init__.py` exposes `__version__ = "{{ cookiecutter.version }}"`; the module
  ships a `hello()` sentinel. The generated `test{{ moduleName }}.py` imports both and asserts.
- `[tool.pytest.ini_options] pythonpath = ["src"]` lets `pytest` / `make test` import the
  `src/`-layout package **without an install**, so a fresh checkout tests green immediately.
- Root bake tests prove it: `testBakeAndRunTests` and `testGeneratedModuleIsImportable` run the
  baked suite and assert exit 0; `testBakeRejects*` assert the snake_case hook (§1) aborts bad
  bakes. (The earlier `runInsideDir(...) == 0` no-op assertion was fixed to a real `assert`.)

---

## Note on the two halves (correction)

The Makefiles are **no longer byte-identical** across halves (an earlier aspiration). Per-half
path scoping is done with explicit `PY_*` vars (`PY_SRC=hooks` root / `PY_SRC=src` template), and
the release recipes differ (root defers to CI; the template still carries a `RELEASE_ENABLED`
gate pending the plan-13/14 template-half port). The ruff/mypy `files`/`src` config (§4) still
encodes per-half paths too; where both exist, the recipe's explicit `PY_*` paths win.
