# DevOps Makefile — Principles (Lessons Learned)

Forward-looking principles for the `py-cookiecut` Makefile. These are the distilled lessons we
are choosing to design around — the WHY behind each decision, plus the verdict on the best way
to do it. Companion to `.claude/plans/nearly-all-of-the-jaunty-sloth.md` and `.claude/GAPS.md`.

Per-command reasoning is appended as we finalize each target in the command-by-command pass.

---

## Lesson 1 — Module declares names; the requirements file pins (BKM)

**Problem.** pip's native input is `requirements.txt`; uv can use `pyproject.toml` and/or a
requirements file. For both backends to produce identical environments they must lean on the same
artifact — and a library must not over-constrain its consumers.

**Why it's hard.** Pinning versions inside a *library's* `pyproject.toml` propagates conflicts into
every downstream application that depends on it. Putting git-based pointers in `pyproject.toml`
breaks deployment. Resolving from two places at once drifts.

**Verdict — the one model that works in production** (every other arrangement tried over the years
has largely failed):

1. **Only the application layer pins versions.** A library/module/template never pins.
2. **Module-level pinning causes dependency conflicts** → `pyproject.toml` declares dependency
   **names only**, never versions.
3. **The requirements file is the only place for git-based dependency pointers**; a git URL in
   `pyproject.toml` is a module-deployment disaster.
4. **The Makefile leans on the requirements file for BOTH pip and uv** — `-r requirements.txt` then
   the editable self-install (`-e ".[dev]"` / `-e "."`).
5. **`pyproject.toml` maintains only the module/dependency names.**

`requirements.txt` is **hand-authored and committed** (NOT `uv pip compile`-generated); siblings
`requirements-release.txt` (tag-pinned) and `requirements-local.txt` (gitignored, local editable
overrides) follow the same shape. `uv` runs through its **pip interface** only — no `uv.lock`, no
`lock`/compile target.

**Principle.** pyproject = names. requirements file(s) = pins + git pointers + the thing every
install path leans on. Pinning is an application-layer concern, not a library's.

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

**Verdict — the best way.** Per Lesson 1, local editable siblings go through a **requirements file**,
not the manifest: a per-machine **`requirements-local.txt`** of `-e ../sibling` lines, installed by
**`make uv-sync-local`** on top of the normal env. `[tool.uv.sources]` / path overrides in
`pyproject.toml` are **rejected** — putting local/git resolution in the manifest is the
module-deployment disaster Lesson 1 warns about. The overlay is gitignored and never read by
CI/release.

**Principle.** "Swap these deps to local editable siblings" is a `requirements-local.txt` +
`uv-sync-local` concern, never a manifest concern.

---

## Cross-cutting verdict

Adopt the lessons: **names-in-manifest / pins-in-requirements** (Lesson 1), graduated flush,
OS-aware install, always work in a deletable venv. The requirements file is **authored** and is what
every install path (pip and uv) leans on; pinning lives at the application layer, never in a
library's `pyproject.toml`. Reject the workarounds that fight tooling (per-package uninstall for
correctness, force-reinstall gymnastics, `--break-system-packages`, git URLs / version pins in the
manifest).
