---
last_updated: 2026-08-10
semver: 0.0.3
author: Nicholas Bergantz
status: active
---

# Plan 16 — pip-half bootstrap & recoverability

Source: FA `docs/FAs/2026-07-28-pip-install-editable-fails-clean-environment.md`
(py-foundationTools), investigated 2026-07-28.

> **Mirrored plan.** This file exists in two repos by explicit decision (D4):
> `py-cookiecut/.claude/action-plans/16-pip-half-bootstrap-recoverability.md` and
> `py-foundationTools/.claude/action-plan/24-pip-half-bootstrap-recoverability.md`.
> py-cookiecut is where tracks A–F land; py-foundationTools receives track G.
> Keep both in sync when ticking boxes.

> **Two-halves reminder.** "Root" = tooling that runs in py-cookiecut itself.
> "Template" = files under `{{cookiecutter.projectIdentifier}}/`. The Makefiles are
> byte-identical; every Makefile step below lands in **both halves**.

Legend: `[ ]` open · `[~]` in progress · `[x]` done.

---

## Problem

`make nuke` on Python ≥3.12 leaves the ambient interpreter unable to install
anything — including itself — and the Makefile offers no way back. The pip
fallback half has no bootstrap target, no guard, and no documented inverse, while
the uv half has `check-uv` → `install-uv` → `uv-bootstrap` and `uv-nuke` that
prints its own recovery command.

## Evidence / Investigation Findings

**E1 — `ensurepip` seeds pip only.**
`/Library/Frameworks/Python.framework/Versions/3.13/lib/python3.13/ensurepip/_bundled/`
contains exactly one wheel: `pip-25.1.1-py3-none-any.whl`. Every `python3 -m venv`
therefore produces an environment with **no build backend**, so any PEP-517 build
in it must reach PyPI. This is what makes `make testInEnv` silently network-bound.

**E2 — `make nuke` became self-destructive at Python 3.12.** In
`pip/_internal/commands/freeze.py`:

```python
def _should_suppress_build_backends() -> bool:
    return sys.version_info < (3, 12)          # freeze.py:12-13

def _dev_pkgs() -> AbstractSet[str]:
    pkgs = {"pip"}
    if _should_suppress_build_backends():
        pkgs |= {"setuptools", "distribute", "wheel"}   # freeze.py:19-20

    return pkgs
```

Below 3.12, `pip freeze` hid `setuptools`/`wheel`; at ≥3.12 it lists them.
`Makefile:465` pipes `$(PIP) freeze --exclude-editable` into `pip uninstall`, so
`nuke` now removes the build backend it used to preserve. **This — not the
Python.org installer — is the root cause the FA is looking for.** `pip` itself is
still protected (always in `_dev_pkgs`).

**E3 — the uv half is unaffected.** Verified offline against a scratch venv:

```
$ VIRTUAL_ENV=<scratch> uv pip install --offline -e .
Resolved 1 package in 9ms
   Building pyfoundationtools @ file:///…/py-foundationTools
      Built pyfoundationtools @ file:///…/py-foundationTools
Installed 1 package in 1ms
```

`uv cache dir` carries `setuptools-83.0.0`, and py-foundationTools'
`.github/workflows/ci-cd.yml` invokes only `uv-bootstrap-pythons` / `uv-bootstrap` /
`uv-fullCheck` / `uv-test-all`. CI was never at risk. The FA's *"all project tooling
becomes unavailable"* is overstated — `make uv-fullCheck` still works throughout.

**E4 — `build`/`twine` are wired to the wrong interpreter (live bug, independent
of the FA).** `Makefile:427-437` runs `$(PYTHON) -m build` and `$(PYTHON) -m twine`
against *ambient* python3, but both are declared in
`[project.optional-dependencies].dev`, which installs into `.venv`. Confirmed:
`python3 -c "import build"` → `ModuleNotFoundError` while `build` sits in the dev
extra. `make build` cannot have worked on a machine that only ran `make uv-sync`.

**E5 — one Makefile, three copies.** `py-cookiecut/Makefile` and
`{{cookiecutter.projectIdentifier}}/Makefile` are byte-identical (`diff` → empty).
py-foundationTools' copy diverges only by `MYPY_PKGS` (Makefile:46), `codegen-all`
(Makefile:501-511), and a commented-out `$(UV)` in `uv-format` (Makefile:282-288).
Fixes land in the cookiecutter and back-port.

**E6 — workflow drift in py-foundationTools.** `make release` (Makefile:441-450)
prints a procedure citing `.github/workflows/tag-on-prod.yml` and a publish-on-tag
workflow. Neither exists — the repo has only `ci-cd.yml`. py-cookiecut ships
`ci.yml` + `publish.yml` + `tag-on-prod.yml` in **both** halves. The printed
release procedure is currently fiction.

**E7 — `--exclude` is available.** `pip freeze --exclude <package>` confirmed
present in pip 25.1.1; the flag has existed since pip 21.2, comfortably below any
interpreter in `PYTHONS`.

**E8 — the boundary is 3.12, measured (not inferred).** E1/E2 were verified
against 3.13 only; 3.11 is in `PYTHONS`, so the boundary is load-bearing.
Measured `ensurepip._bundled/` contents plus a real `venv` from each:

| Python | ensurepip bundles | `setuptools.build_meta` in fresh venv | `_should_suppress_build_backends()` | pre-fix `nuke` |
|---|---|---|---|---|
| 3.10 | pip + setuptools | importable | `True` | safe |
| 3.11 | pip + setuptools | importable | `True` | safe |
| 3.12 | pip only | **missing** | `False` | **destructive** |
| 3.13 | pip only | **missing** | `False` | **destructive** |

Both halves flip at 3.12: it removed setuptools from the `ensurepip` bundle
(E1) *and* pip correspondingly stopped suppressing build backends in `freeze`
(E2). One upstream change, two faces.

**E9 — the ambient build backend is irrelevant to the clean room.** On a machine
whose `python3` has no `setuptools` at all, the clean-room sequence run by hand
(`python3 -m venv`, `pip install -r requirements.txt`, `pip install ".[dev]"`)
**succeeds** — pip provisions setuptools into an isolated build env from PyPI.
Offline it fails regardless of the ambient backend. There is therefore no
true-positive case for guarding the clean room on `setuptools.build_meta`; see
D5.

**E10 — the A1 exclusion verified by round trip (2026-08-10, py-foundationTools).**
Dry-run greps for `--exclude setuptools` prove nothing on a machine whose ambient
interpreter has already lost its build backend: there is nothing for the
exclusion to protect, so `nuke` passes vacuously. Measured properly by planting
the backend first:

| step | command | result |
|---|---|---|
| 0 | ambient state | `setuptools`, `wheel` both absent |
| 1 | `make pip-bootstrap` | installs `setuptools 84.0.0`, `wheel 0.47.0`; `build_meta` importable |
| 2 | `pip freeze --exclude-editable` | lists `setuptools==84.0.0`, `wheel==0.47.0` → **the unguarded pipeline would delete both** |
| 3 | `… --exclude setuptools --exclude wheel` | 0 build-backend entries reach `pip uninstall` |
| 4 | `make nuke` (real) | both **survive**; `build_meta` still importable |
| 5 | `make testInEnv` | 345 passed in the clean room |

Step 2 is the one that makes the test non-vacuous — it shows the exclusion is
load-bearing rather than merely present. Any bake test for A1 (track E1) must
plant the backend first or it asserts nothing.

## Decisions

| # | Decision | Rationale |
|---|---|---|
| **D1** | Add `pip-bootstrap`; do **not** gate `installDev`/`e`/`refresh`/`build` on a build-backend guard. | User call. `nuke` gets an inverse; the install targets keep failing loudly on their own terms rather than growing a guard layer. |
| **D2** | `check-pip` is still authored, but wired **only** to the clean-room. | Reconciles D1 with D3 — D3's fix needs the guard, D1 says the install targets don't get it. Scope it precisely; do not creep it onto `installDev`/`e`/`refresh`/`build`. |
| **D3** | `testInEnv` stays on `python3 -m venv` + pip. | The target's entire purpose is validating the real pip packaging path. Swapping it to uv duplicates `uv-test-all` and deletes the only pip-install coverage. |
| **D4** | Mirror this plan into both repos. | User call, accepting two sources of truth; mitigated by the cross-reference header. |
| **D5** | **(2026-08-10, supersedes C1 as originally written.)** `check-pip` asserts `ensurepip` only; it does **not** assert `setuptools.build_meta` on the ambient interpreter. | Forced by E9. The original C1 shipped in py-foundationTools and blocked `make testInEnv` on a repo where the identical sequence succeeded by hand — a false negative. The `build_meta` assertion is only meaningful for `--no-build-isolation` ambient installs, which D1 deliberately leaves ungated. |
| **D6** | The clean room installs `-r requirements.txt` before the package (track H). | The plan audited the clean room for *bootstrap* but never for *dependency resolution*. `pyproject.toml` is names-only by BKM, so `".[dev]"` alone cannot resolve a git-pointer sibling. Surfaced by a real py-MathTools failure, not by this plan. |

## Risks

- **`ensurepip --upgrade` fails on externally-managed interpreters** (Homebrew,
  Debian) with `error: externally-managed-environment`. `pip-bootstrap` must say so
  in its help text and name `make uv-bootstrap` as the alternative.
- **Track D makes `build`/`validateBuild` uv-dependent.** GAPS §7 records them as
  deliberately "installer-agnostic"; that claim is being reversed, and it needs
  writing down rather than silently contradicting.
- **D1 leaves raw tracebacks in place.** `make e` on a nuked interpreter still dies
  on `BackendUnavailable`. Mitigated only by A2's echo — accepted.
- **Mirrored files drift** (D4, acknowledged).

## Implementation Steps

### A. Make `nuke` recoverable — py-cookiecut, both halves
- [ ] A1 — `nuke` (Makefile:465): add `--exclude setuptools --exclude wheel` to the
      `$(PIP) freeze --exclude-editable` pipeline.
- [ ] A2 — `nuke` closing echo prints the inverse, mirroring `uv-nuke:373`:
      `Run 'make pip-bootstrap' (network) or 'make uv-bootstrap' (offline-capable) to rebuild.`
- [ ] A3 — comment above `nuke` citing `freeze.py:12-20` and the 3.12 behavior
      change, so the exclusions are not "cleaned up" by a later refactor pass.

### B. `pip-bootstrap` — py-cookiecut, both halves
- [ ] B1 — new target under `##@ PIP · Install`; add to `.PHONY` (Makefile:4-17).
- [ ] B2 — recipe: `$(PYTHON) -m ensurepip --upgrade` then
      `$(PIP) install --upgrade setuptools wheel`. Help text carries
      `(NETWORK REQUIRED)`. Any comment stating the boundary MUST say **3.12**
      — measured, see "Boundary is 3.12" below. This track originally supplied
      no version and the executing agent guessed 3.11, wrongly.
- [ ] B3 — recipe echoes the externally-managed-interpreter caveat and points at
      `make uv-bootstrap`. Does **not** install `build`/`twine` — the `[dev]` extra
      owns those, and track D moves them onto uv.

### C. `check-pip`, scoped to the clean-room (D2) — py-cookiecut, both halves
- [ ] C1 — **REVISED 2026-08-10, see D5.** `check-pip` guard target modelled on
      `check-uv:177`, asserting **only** `$(PYTHON) -m ensurepip --version`
      succeeds; on failure name `make pip-bootstrap` and `make uv-sync`.
      It MUST NOT assert `setuptools.build_meta` imports on the ambient
      interpreter — the clean room installs into `$(VENV)` under PEP-517 build
      isolation, which provisions its own setuptools from PyPI, so the ambient
      backend is never consulted. The original wording produced a false
      negative that blocked a clean room which then succeeded when run by hand.
- [ ] C2 — wire as a prereq of `cleanRoomBootstrap` (renamed 2026-08-10 from
      `testInEnvInstallFromSetup`; locate by name, not line) **only**.
      Leave `installDev`/`e`/`refresh`/`build` ungated per D1 — add an inline
      comment recording that this is deliberate.
- [ ] C3 — `NETWORK REQUIRED` comment on the clean-room recipe citing E1
      (ensurepip seeds pip only since 3.12 → build isolation must reach PyPI).
      Note explicitly that a backend-less *ambient* interpreter does not change
      this either way — which is why C1 does not guard on it.

### D. Fix the build/release interpreter (E4) — py-cookiecut, both halves
- [ ] D1 — `build` (Makefile:429): `$(PYTHON) -m build` → `$(UV) --with build python -m build`.
- [ ] D2 — `validateBuild` (Makefile:433): → `$(UV) --with twine twine check dist/*`.
- [ ] D3 — `release-test` (Makefile:437): → `$(UV) --with twine twine upload --repository testpypi dist/*`.
- [ ] D4 — add `check-uv` as a prereq of `build` and `validateBuild`.
- [ ] D5 — record the reversal of the "installer-agnostic" claim in
      `.claude/specs/project-conventions.md`.

### E. Regression tests — py-cookiecut only
- [ ] E1 — `testBakeNukePreservesBuildBackend`: bake, run `make -n nuke`, assert the
      output contains `--exclude setuptools`.
- [ ] E2 — `testBakePipBootstrapExists`: `make -n pip-bootstrap` exits 0.
- [ ] E3 — `testBakeCleanRoomGuarded`: `make -n testInEnv` resolves `check-pip`.
      Assert the guard checks `ensurepip` and does **not** grep for
      `setuptools.build_meta`, or the bake suite freezes the C1 defect in.
- [ ] E5 — `testBakeCleanRoomInstallsRequirements`: `make -n testInEnv` shows
      `pip install -r requirements.txt` **before** `pip install ".[dev]"` (track H).
- [ ] E4 — re-green `testMakeHelp` (`tests/testBakeProject.py:150`) against the new
      help text.

### F. Docs — py-cookiecut
- [ ] F1 — `.claude/specs/devops-makefile-principles.md`: add **Lesson 5 — the
      bootstrap layer is not part of the distribution**. Problem: ensurepip seeds
      pip only since 3.12 and `pip freeze` stopped suppressing build backends.
      Verdict: every flush target must state its own inverse; the pip half is a
      documented-inferior fallback that cannot self-heal offline.
- [ ] F2 — `.claude/GAPS.md` §7: extend the Flush/nuke item with the 3.12 caveat;
      correct the build/validateBuild "installer-agnostic" note per D5.

### H. Clean room must obey the dependency BKM — py-cookiecut, both halves
- [x] H1 — `cleanRoomBootstrap`: install `-r requirements.txt` **before**
      `pip install ".[dev]"`. **DONE 2026-08-10** (both halves, `diff` empty).
      `pyproject.toml` is names-only by BKM, so `".[dev]"` alone makes pip
      resolve bare names against PyPI — fatal for any unpublished sibling
      (`No matching distribution found`). Every other install path in the
      Makefile already did this; the clean room was the sole violator of a rule
      the file states in its own dependency-model comment. Keep `".[dev]"`
      NON-editable — validating the real packaging path is the target's purpose.
- [ ] H2 — back-port H1 to py-foundationTools and py-MathTools. **DONE
      2026-08-10** for both, outside this plan's numbering.

### I. Name the clean-room steps honestly — all repos
- [x] I1 — the `testInEnv*` sub-steps promised testing and did not deliver it:
      `testInEnvInstallFromSetup` only creates the venv and installs, and
      `testInEnvCleanup` only deletes it. A user read the name, ran the target,
      and correctly reported "I don't see any testing". Renamed 2026-08-10 to
      say what they do — `cleanRoomBootstrap`, `cleanRoomCleanup`,
      `cleanRoomPytest` — matching the `pip-bootstrap` / `uv-bootstrap`
      vocabulary already in the file and the `.cleanroom-venv` it manages.
      `testInEnv` keeps its name: it is the public entry point and it does run
      tests. `cleanRoomBootstrap`'s help text now says "runs NO tests" outright.
      **DONE** in py-cookiecut (both halves), py-foundationTools, py-MathTools.

### G. Back-port — py-foundationTools
- [ ] G1 — apply tracks A–D to `Makefile`, preserving the three local divergences
      (E5): `MYPY_PKGS`, `codegen-all`, the `uv-format` comment block.
- [ ] G2 — copy `tag-on-prod.yml` + `publish.yml` from the template half (E6).
- [ ] G3 — reconcile `ci-cd.yml` against the template's `ci.yml`: pick one name,
      keep this repo's uv-target job set.
- [ ] G4 — amend `docs/FAs/2026-07-28-pip-install-editable-fails-clean-environment.md`:
      Root Cause → E1 + E2 with the `freeze.py:12-20` citation; add E3 as a
      "blast radius" finding; replace the "switch to Homebrew python" remediation
      (it treats a symptom) with `make pip-bootstrap`; `status: open` → `closed`.
- [x] G5 — create `.claude/action-plan/` (named in `CLAUDE.md:71`, absent since
      commit `e0a9bb7` archived 00–23 to `.claude/archive/action-plan/`) and land
      this plan there as `24-pip-half-bootstrap-recoverability.md`. **DONE 2026-07-28.**
- [ ] G6 — `make uv-fullCheck` green in both repos.

## Acceptance

- [ ] `make -n nuke` shows `--exclude setuptools --exclude wheel`; a real `nuke`
      followed by `make pip-bootstrap` restores an installable interpreter.
- [ ] `make build` and `make validateBuild` succeed on a checkout whose only setup
      was `make uv-sync`.
- [ ] ~~`make testInEnv` fails fast with an actionable message on a backend-less
      interpreter instead of a `BackendUnavailable` traceback.~~ **WITHDRAWN
      2026-08-10 — this criterion was false.** A backend-less ambient
      interpreter does not break the clean room (build isolation provisions its
      own setuptools), so "fails fast" here is a false negative, not a feature.
      Replaced by: `make testInEnv` **succeeds** on a backend-less ambient
      interpreter, and fails fast only when `ensurepip` is genuinely absent.
- [ ] `make testInEnv` resolves a git/path-pointer dependency carried in
      `requirements.txt` (track H).
- [ ] py-cookiecut's bake suite green, including E1–E4.
- [ ] Both Makefile halves still byte-identical (`diff` → empty).
- [ ] `make uv-fullCheck` green in py-cookiecut and py-foundationTools.

## Out of Scope

- Guarding `installDev`/`e`/`refresh`/`build` (D1 — explicitly declined).
- Vendoring wheels for a fully offline `pip-bootstrap`; `make uv-bootstrap` already
  covers offline via uv's cache (E3).
- Wiring `ty` into `uv-fullCheck` (decision D1 in the Makefile header stands).
- Implementing `publish.yml`'s upload steps — still user-owned per GAPS §7.
