---
last_updated: 2026-08-28
semver: 1.0.0
author: Nicholas Bergantz
status: active
---

# Plan 16 — finish verification of pip recoverability

## Requested outcome

After `make nuke`, the pip fallback remains recoverable, and the clean-room install
uses the same requirements-first dependency path as other installs.

## Already implemented in both Makefiles

- `nuke` preserves `setuptools` and `wheel` and prints recovery commands.
- `pip-bootstrap` rebuilds pip plus the build backend.
- `check-pip` checks only `ensurepip` and gates only `cleanRoomBootstrap`.
- the clean room installs `requirements.txt` before non-editable `.[dev]`.
- build and twine commands run through uv rather than an unrelated ambient interpreter.
- the root and template Makefiles are byte-identical.

The long investigation transcript remains in git history. The explicitly requested
foundation back-port is complete and archived there as action plan 24; this local plan
does not duplicate its checklist.

## Remaining work

1. Add bake-level dry-run tests for the exclusions, bootstrap target, ensurepip-only
   guard, and requirements-before-package ordering.
2. Correct `.claude/GAPS.md` where it still calls build/validation
   installer-agnostic.
3. Add one concise note to `devops-makefile-principles.md`: Python 3.12 stopped
   bundling setuptools in `ensurepip`, so destructive package flushes must preserve or
   document recovery of the build backend.
4. Verify the Makefiles remain identical and run the repository gate.

Do not repeat the completed foundation back-port, guard unrelated install targets,
vendor wheels, or redesign the Makefile.
