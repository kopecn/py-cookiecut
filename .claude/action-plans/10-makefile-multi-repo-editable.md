# 10 — Makefile: multi-repo editable siblings

**Source:** GAPS §7 (Multi-repo editable, Lesson 4) · **Half:** both · **Decisions needed:** minor · **Risk:** medium

Companion: `.claude/specs/devops-makefile-principles.md` (Lesson 4).

## Problem

Co-developing sibling repos (`py-foundationTools`, `py-cvTools`, `py-MathTools`, `py-robotTools`,
`py-machineVisionTools`, …): a project must import siblings from **local editable working trees**
during dev, while CI/release uses **pinned index versions**. Need a first-class way to SWAP a dep
between "local editable path" and "pinned index" per dependency.

## Verdict (from Lesson 4)

- **Recommended path:** uv workspaces / `[tool.uv.sources]`
  (`{ path = "../repoB", editable = true }`) — one resolver across member repos, declarative local
  sources, switchable by profile/env.
- **Fallback:** a documented file-overlay convention (`-e ../sibling` lines) + Make targets, marked
  inferior (precedence pitfalls, per-machine paths).
- A template should ship **the hook** (overlay + `editable-local`/`sync-local` targets) AND
  **recommend** `[tool.uv.sources]`.

## Decision (minor)

**D1 — overlay file format & location.** e.g. `requirements-local.txt` (gitignored,
per-machine) holding `-e ../sibling` lines, vs an env-var list of sibling paths consumed by the
target. Default: a gitignored `requirements-local.txt` overlay + an env override for paths.

## Steps

1. **Document `[tool.uv.sources]` as the recommended path** in the generated project's README /
   a `CONTRIBUTING` "co-development" section: show the `{ path = "../repoB", editable = true }`
   form and how to toggle it per profile/env so CI stays on pinned index versions.
2. **Ship the overlay hook (fallback):**
   - `editable-local` → install sibling repos as editable from the overlay
     (`uv pip install -e <path>` per sibling, paths from `requirements-local.txt` or an env var).
   - `sync-local` → `uv-sync` (Plan 09) **then** apply the editable overlay on top, so the locked
     env is the base and local siblings override specific packages.
   - Accept sibling paths as arguments / from `.env` (document the sibling repo list).
3. **Keep CI clean:** the overlay file is gitignored and never used by `release`/CI targets — those
   resolve from the committed lock only. Make this explicit in comments.
4. Byte-identical Makefile constraint: targets must no-op gracefully when no overlay exists (a
   solo repo with no siblings checked out should still `make sync-local` == `make uv-sync`).
5. Add a `.gitignore` entry for the overlay file in both halves.

## Files affected

- `Makefile` (both halves) — `editable-local`, `sync-local`
- `{{cookiecutter.projectIdentifier}}/pyproject.toml` — optional commented `[tool.uv.sources]`
  example block
- `.gitignore` (both halves) — ignore `requirements-local.txt`
- README / CONTRIBUTING (both halves) — co-development docs
- `.env` (both halves) — optional sibling-path list

## Acceptance criteria

- D1 recorded.
- `[tool.uv.sources]` workflow is documented as the recommended approach.
- `editable-local` / `sync-local` exist, accept sibling paths, layer editable installs over the
  locked env, and no-op cleanly when no overlay is present.
- Overlay file is gitignored and provably unused by CI/release paths.
