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

## 1. Naming convention — camelCase is KEPT (GAPS §2, plan 02)

**Verdict.** camelCase package/module names (`myPackage`, `myModule`), cookiecutter keys,
test function names (`testBakeWithDefaults`), and Makefile targets are the **deliberate house
convention** ("Nick's workflow"). This intentionally deviates from PEP 8 — match it, do not
"fix" it. Tooling must accommodate it (see §4: ruff `N`/pep8-naming is omitted).

*Still open (impl, not decision):* `hooks/pre_gen_project.py` validation message/regex
alignment and validating `packageName`/`moduleName`, not just `projectIdentifier`.

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
