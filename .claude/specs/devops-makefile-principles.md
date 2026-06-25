# DevOps Makefile — Principles (Lessons Learned)

Forward-looking principles for the `py-cookiecut` Makefile. These are the distilled lessons we
are choosing to design around — the WHY behind each decision, plus the verdict on the best way
to do it. Companion to `.claude/plans/nearly-all-of-the-jaunty-sloth.md` and `.claude/GAPS.md`.

Per-command reasoning is appended as we finalize each target in the command-by-command pass.

---

## Lesson 1 — Single source of truth for dependencies (pip ⇄ uv convergence)

**Problem.** pip's native input is `requirements.txt`; uv prefers `pyproject.toml` + a lockfile.
For both backends to produce identical environments, they must converge on one artifact.

**Why it's hard.** Installing `-r requirements.txt` *and* `-e ".[dev]"` resolves dependencies
from two places → drift and version conflicts. Hand-maintained requirements files drift from
pyproject. Private indexes need a fully resolved, pinned set for reproducible builds.

**Verdict — the best way.** pyproject.toml is the **only authored source of truth**;
`requirements.txt` is a **generated lockfile**: `uv pip compile pyproject.toml --extra dev -o
requirements.txt`. Both pip and uv install from the generated file → true convergence, zero
drift, reproducible. The self-install becomes `-e . --no-deps` (deps already locked). A `lock`
target owns regeneration; the lockfile is committed.

**Principle.** pyproject = authored truth. `requirements.txt` = generated lock (ship a
minimal/empty starter in the template; `make lock` populates it). Both paths: `-r
requirements.txt` then `-e . --no-deps`. No hand-edited requirements files.

---

## Lesson 2 — Flushing an environment is genuinely hard

**Problem.** "Reset my environment" rarely works first try; stale state keeps importing.

**Why it's hard.** State hides in many places: the venv dir, `site-packages`
`.pth`/`.egg-link` editable pointers, `__pycache__`/`*.pyc`, `.egg-info`/`.eggs`, `build/`/`dist/`,
the **global** package-manager cache, managed Python installs, the lockfile, and tool caches
(`.mypy_cache`/`.pytest_cache`/`.ruff_cache`). A partial clean leaves a poisoned env that
silently imports stale code. Editable installs are the worst offenders (dangling pointers).

**Verdict — the best way.** Graduated targets with explicit blast radius
(clean → flush-envs → flush-cache → flush-pythons → nuke). **The reliable flush primitive is
`rm -rf` the venv directory**, never per-package uninstall (fragile: system-managed pkgs, broken
editables, ordering). If per-package uninstall is ever *needed*, that's a symptom that a
non-deletable (system) env got polluted — the real fix is "always work in a deletable venv."
Separate "remove generated artifacts" from "remove the committed lock."

**Principle.** Graduated flush targets; venv deletion is the workhorse; never rely on
per-package uninstall for correctness; routine `clean` must NOT delete a committed lockfile.

---

## Lesson 3 — Forced package refreshes are painful

**Problem.** After changing a local/editable dependency, the env keeps serving old code.

**Why it's hard.** Wheel caches mean a same-version rebuild won't reinstall without
`--force-reinstall`. `-e .` doesn't re-resolve deps when pyproject changes. `--force-reinstall`
without `--no-deps` reinstalls the whole tree (slow, clobbers pins); with `--no-deps` it skips
deps (may miss new ones). Installing into an externally-managed Python (needing
`--break-system-packages`) makes all of this worse.

**Verdict — the best way.** Don't fight the tools. **`uv pip sync requirements.txt` makes the
env EXACTLY match the lock** (adds missing, removes stragglers) — fast, no force-reinstall. For
targeted local-version churn, `uv pip install --reinstall-package <name>` refreshes one package.
A pip `--force-reinstall` path survives only as a documented, inferior fallback. Use a venv so
`--break-system-packages` is never needed.

**Principle.** Prefer `uv pip sync` (exact match) over `install --force-reinstall`;
`--reinstall-package` for targeted refresh; keep a pip fallback documented as inferior; venvs
mean no `--break-system-packages`.

---

## Lesson 4 — Plural co-development with editable installs across repos

**Problem.** Co-developing sibling repos (here: `py-foundationTools`, `py-cvTools`, `py-MathTools`,
`py-robotTools`, `py-machineVisionTools`, …) — repo A must import B/C from your local working
trees (editable), live, while CI/release uses pinned index versions. You need to SWAP a dep
between "local editable path" and "pinned index" per dependency.

**Why it's hard.** Overlay files of `-e ../sibling` lines have precedence pitfalls (last `-e`
wins, partial overrides), are hand-maintained per machine (paths differ), and pip has no shared
resolver across repos → version conflicts surface late.

**Verdict — the best way.** **uv workspaces / `[tool.uv.sources]`**
(`{ path = "../repoB", editable = true }`) are first-class: one resolver across member repos,
declarative local sources, switchable by profile/env. A file-overlay convention is an acceptable
fallback when uv sources aren't usable, but is inferior. A template should ship the HOOK (a
documented overlay + an `editable-local`/`sync-local` target) AND recommend `[tool.uv.sources]`.

**Principle.** First-class support for "swap these deps to local editable siblings": a documented
overlay convention + targets, with uv `[tool.uv.sources]`/workspaces as the recommended path.
Editable targets accept sibling paths.

---

## Cross-cutting verdict

Most environment pain comes from **not having a lock/compile step and not always using a
deletable venv**. Adopt the lessons (graduated flush, OS-aware install, lock-as-truth); reject
the workarounds that fight tooling (hand-maintained requirements, per-package uninstall,
force-reinstall gymnastics, `--break-system-packages`). uv's `compile`/`sync`/`sources` collapse
three of the four pain points when used properly.
