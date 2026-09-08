---
last_updated: 2026-08-28
semver: 1.0.0
author: Nicholas Bergantz
status: active
---

# Plan 15 — remaining repository-review findings

The original review contained eight independent findings. A–D are fixed in the current
tree; they are not prerequisites for the remaining work.

## Open candidates

### E — missing release requirements file

`uv-sync-release` reads committed `requirements-release.txt`, but neither template half
contains it. Decide the intended starter content, add it to both halves, and bake-test
its presence. Do not redesign dependency policy.

### F — quality commands can resync away installed requirements

Quality/test targets use `uv run --no-project` after `uv pip` sync. Prove the failure
with a dependency available only through `requirements.txt`, then use the smallest
no-resync invocation that preserves the existing environment. Apply to both Makefiles.

### G — matrix tests omit requirements

Each `uv-test-all` environment installs `.[dev]` without first installing
`requirements.txt`. Add that one missing step in both halves and cover ordering in the
bake tests.

### H — changelog compare links drift

`roll_changelog` creates a release section but does not update Keep-a-Changelog footer
links. Add a focused fixture test, update only the link/empty-Unreleased behavior, and
apply it to both Makefiles.

Each candidate is a separate change unless the user explicitly groups them. Run the
focused bake test and normal repository gate for the candidate being changed.
