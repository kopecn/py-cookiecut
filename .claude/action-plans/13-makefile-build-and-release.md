# 13 — Makefile: build & release

**Source:** GAPS §7 (Build & release), §5 (`set -euo pipefail`/shell) · **Half:** both · **Decisions needed:** YES (publish auth/flow) · **Risk:** high (outward-facing: publishes to PyPI)

## Scope

Fill the build/release stubs: `build` / `uv-build`, `validateBuild` / `uv-validateBuild`,
`release-test` (TestPyPI), `release` (PyPI). Reconcile the deferred `set -euo pipefail` / shell
concern (§5) here, since these are the first genuinely multi-step, side-effecting recipes.

## Decisions required (blocking — these publish artifacts)

- **D1 — release trigger model.** Tagging is owned by `.github/workflows/tag-on-prod.yml` (auto
  `v<version>` on push to the release branch — Plan 06). Decide whether `make release` **publishes
  locally** (twine upload) or only **prepares/validates** and lets CI publish on tag. Recommend:
  CI publishes on tag; `make release-test` does the local TestPyPI dry run.
- **D2 — auth.** TestPyPI/PyPI credentials via API tokens in `~/.pypirc` or env
  (`TWINE_USERNAME=__token__` / `TWINE_PASSWORD`). Never hardcode. Document the expected env.
- **D3 — version source.** Derive the release version from `make -s version` (tomllib, Plan 14),
  not the orphaned grep-based `VERSION` make-var (Plan 14 deletes it).

## Steps

1. `build` / `uv-build` → clean build dir first (`cleanBuild`, Plan 09), then
   `python -m build` (or `uv build`) producing sdist + wheel into `dist/`.
2. `validateBuild` / `uv-validateBuild` → `twine check dist/*`; optionally install the built wheel
   into a throwaway venv and import it (smoke). Ties to Plan 12's clean-room pattern.
3. `release-test` → build + validate + `twine upload --repository testpypi dist/*`. Gate on
   `checkCleanGit` (Plan 14 — strict `git status --porcelain`) so you never publish a dirty tree.
4. `release` → per D1: either `twine upload dist/*` to PyPI **or** a guard that refuses local
   upload and points at the tag-driven CI flow. Gate on `checkCleanGit` + on being on the release
   branch (Plan 06).
5. **Shell hygiene (§5):** these multi-line recipes need `.ONESHELL:` + `SHELL := bash` +
   `.SHELLFLAGS := -euo pipefail -c` so a failed step aborts the recipe (no half-published
   releases). Apply specifically to build/release recipes.
6. Version coherence: `release`/`release-test` read `make -s version` (Plan 14), enabling deletion
   of the orphaned `VERSION` grep var.
7. **Confirm-before-publish:** since `release` is outward-facing and hard to reverse, the recipe
   should require an explicit confirmation or a `CONFIRM=1` style guard, and print the
   target index/version before uploading.

## Files affected

- `Makefile` (both halves) — build/release recipes + shell-strictness directives
- README / CONTRIBUTING — document the release flow, required env tokens, and the tag-driven CI path
- Cross-ref Plan 06 (release branch), Plan 09 (cleanBuild), Plan 14 (`version`, `checkCleanGit`)

## Acceptance criteria

- D1–D3 recorded in `GAPS.md`.
- `make build` produces a valid sdist+wheel; `make validateBuild` passes `twine check`.
- `make release-test` uploads to **TestPyPI** only, gated on a clean git tree and token auth.
- `make release` either publishes to PyPI behind an explicit confirmation **or** defers to CI per
  D1 — never silently double-publishes alongside `tag-on-prod`.
- Release recipes abort on first failed step (`set -euo pipefail` via `.ONESHELL`).
- No remaining dependence on the orphaned grep `VERSION` var.
