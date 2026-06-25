# 13 — Makefile: build & release

**Source:** GAPS §7 (Build & release), §5 (`set -euo pipefail`/shell) · **Half:** both · **Decisions needed:** YES (publish auth/flow) · **Risk:** high (outward-facing: publishes to PyPI)

## Scope

Fill the build/release stubs: `build` / `uv-build`, `validateBuild` / `uv-validateBuild`,
`release-test` (TestPyPI), `release` (PyPI). Reconcile the deferred `set -euo pipefail` / shell
concern (§5) here, since these are the first genuinely multi-step, side-effecting recipes.

## Status — `build` done, root half (2026-06-24)

**Decided: building is consolidated into the single bare `build` target — there is no
`uv-build`.** Rationale: `python -m build` is installer-agnostic, so a uv-specific build adds no
value. `uv-build` was **removed** (dropped from `.PHONY`); `uv-validateBuild` now depends on
`build`. Implementation:

```make
build: clean-build  ## Build sdist+wheel ($(PYTHON) -m build)
	$(PYTHON) -m build
```

Composes on `clean-build` (Plan 09) rather than an inline `rm -rf` — DRY, and `clean-build` is a
superset (also clears `.eggs/`, `*.egg-info`). Verified by `make -n build` (cleans then builds).
`build`/`twine` are already in the `[dev]` extra.

## Status — `validateBuild`/`release-test`/`release` done, root half (2026-06-24)

Remaining root recipes implemented and aligned to the shared-memory `operations/ci-cd.md` spec:

- **`validateBuild: build`** → `twine check dist/*` (single bare target; **no `uv-validateBuild`** —
  twine-check is installer-agnostic, same rationale as the dropped `uv-build`. The dead
  `uv-validateBuild` `.PHONY` entry was removed).
- **`release-test: checkCleanGit validateBuild`** → TestPyPI upload, now **gated on a clean tree**
  (gives `checkCleanGit` its consumer) and prints `v$(make -s version)` for traceability.
- **`release: validateBuild`** → **refuses local upload and exits 1**, printing the CI-driven
  procedure (bump → merge/push to `prod` → `tag-on-prod.yml` tags → publish-on-tag workflow). This
  resolves **D1 = defer to CI**, mandated (not merely recommended) by `ci-cd.md`: *"The pipeline is
  the single authoritative path to production. No manual, out-of-band deploys."*
- Orphaned grep **`VERSION` make-var deleted**; `RELEASE_ENABLED` gate **removed** from Makefile and
  `.env` (dead once `release` defers to CI).

Verified by `make -n release-test` / `make -n release` and `make help`.

**Shell-strictness (§5 / step 5) decision: do NOT set global `.ONESHELL`.** Make's `.ONESHELL` is
file-global, not per-recipe, and would change `-`/`@` modifier semantics (e.g. `installDev` leads
with `-`, which under `.ONESHELL` would make the *entire* recipe error-ignored). The release recipes
are single-command targets sequenced by Make's prereq chain (`build → validateBuild → release-test`),
which already fails fast — so per-recipe `set -euo pipefail` adds nothing here. Revisit only if a
genuinely multi-line side-effecting recipe is added.

**Still open:** the **publish-on-tag workflow does not exist yet** — `tag-on-prod.yml` only creates
the tag; nothing uploads to PyPI on that tag. Add a `publish.yml` (`on: push: tags: 'v*'`). Also:
template half; D2 (auth env) documentation; `make -s version` needs Python ≥3.11 (tomllib — GAPS §7).

## Decisions (resolved)

- **D1 — release trigger model. RESOLVED → defer to CI.** Decided by `ci-cd.md` (single authoritative
  pipeline path; no out-of-band deploys). `make release` refuses local upload; `make release-test`
  is the local TestPyPI dry run.
- **D2 — auth.** TestPyPI/PyPI credentials via API tokens in `~/.pypirc` or env
  (`TWINE_USERNAME=__token__` / `TWINE_PASSWORD`). Never hardcode. **Still TODO:** document the
  expected env (README/CONTRIBUTING) — only `release-test` needs local TestPyPI auth now.
- **D3 — version source. RESOLVED.** Release recipes derive the version from `$(MAKE) -s version`
  (tomllib, Plan 14); the orphaned grep `VERSION` make-var is **deleted**.

## Steps

1. [x] `build` → `clean-build` (Plan 09) then `$(PYTHON) -m build` → sdist+wheel in `dist/`.
   **`uv-build` removed** (consolidated into `build`; see Status). *(root half)*
2. [x] `validateBuild` → `twine check dist/*`. **No `uv-validateBuild`** (installer-agnostic; dead
   `.PHONY` entry removed). Optional wheel-import smoke deferred (ties to Plan 12). *(root half)*
3. [x] `release-test` → build + validate + `twine upload --repository testpypi dist/*`, gated on
   `checkCleanGit` (strict `git status --porcelain`). Prints `v$(make -s version)`. *(root half)*
4. [x] `release` → **per D1 (resolved → defer to CI):** refuses local upload, exits 1, and prints
   the tag-driven CI procedure. No release-branch guard needed (CI owns the publish). *(root half)*
5. [x] **Shell hygiene (§5): decided NOT to set global `.ONESHELL`** — it's file-global (would flip
   `installDev`'s leading-`-` to whole-recipe error-ignore) and the release recipes are
   single-command targets sequenced by Make's prereq chain, which already fails fast. See Status.
6. [x] Version coherence: `release-test`/`release` read `$(MAKE) -s version` (Plan 14); orphaned
   grep `VERSION` var **deleted**.
7. [x] **Confirm-before-publish — N/A under D1:** `release` no longer uploads, so no `CONFIRM=`
   guard is needed. `release-test` (TestPyPI dry-run) is gated on `checkCleanGit` + prints version.

## Files affected

- `Makefile` (both halves) — build/release recipes + shell-strictness directives
- README / CONTRIBUTING — document the release flow, required env tokens, and the tag-driven CI path
- Cross-ref Plan 06 (release branch), Plan 09 (cleanBuild), Plan 14 (`version`, `checkCleanGit`)

## Acceptance criteria

- [x] D1–D3 recorded (here + GAPS §7). D1→defer-to-CI, D3→tomllib `version`; D2 (auth env docs) open.
- [x] `make build` produces a valid sdist+wheel; `make validateBuild` passes `twine check`. *(root)*
- [~] `make release-test` uploads to **TestPyPI** only, gated on a clean git tree. **Token auth
  (D2) not yet documented.** *(root)*
- [x] `make release` **defers to CI** per D1 — refuses local upload, so cannot double-publish
  alongside `tag-on-prod`. *(root)*
- [x] Fail-fast satisfied by Make's prereq sequencing (decided against global `.ONESHELL`; see §5
  note in Status).
- [x] No remaining dependence on the orphaned grep `VERSION` var (deleted).
- [ ] **New gap:** publish-on-tag workflow (`publish.yml`, `on: push: tags: 'v*'`) — referenced by
  `release` but does not exist yet. Template half also pending.
