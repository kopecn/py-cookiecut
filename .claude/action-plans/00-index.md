---
last_updated: 2026-08-14
semver: 0.0.2
author: Nicholas Bergantz
status: active
---

# Action Plans — Index

Per-gap implementation plans derived from [`.claude/GAPS.md`](../GAPS.md). Each open plan is
self-contained: source gap, open decisions, concrete steps, files touched in **both halves**
(template tooling vs. template body), and acceptance criteria.

Greenfield rules apply: prefer decisive replacement over backward-compat patching. When a plan
resolves a GAPS item, tick the box in `GAPS.md`.

> **Two-halves reminder.** "Root" = template tooling that runs in *this* repo. "Template" =
> files under `{{cookiecutter.projectIdentifier}}/` that render into a new project.

## Closed plans (01–14) — historical map

Files removed (2026-06-26). Every durable verdict lives in
[`../specs/project-conventions.md`](../specs/project-conventions.md) (§1–§9) and each gap is
ticked in [`../GAPS.md`](../GAPS.md). Table kept as the record of where each plan landed.

| # | Plan | Landed in spec § / GAPS § |
|---|------|---------------------------|
| 01 | Cleanup stale on-disk artifacts | GAPS §1 |
| 02 | Naming convention + hook validation | spec §1 / GAPS §2 |
| 03 | Lint/typecheck stack (ruff + mypy) | spec §4 / GAPS §3, §6 |
| 04 | Python version policy (3.13/3.10) | spec §2 / GAPS §3, §7, §8 |
| 05 | bump2version HISTORY auto-roll | spec §8 / GAPS §3 |
| 06 | Branch model (dev/prod) | spec §3 / GAPS §4 |
| 07 | Generated pyproject defaults | spec §7 / GAPS §4 |
| 08 | Generated smoke test | spec §7 / GAPS §4 |
| 09 | Dependency SoT, clean, flush, refresh | spec §6 (**BKM**) / GAPS §5, §7 |
| 10 | Multi-repo editable siblings | spec §9 / GAPS §7 |
| 11 | Makefile quality targets | spec §4 / GAPS §3, §6, §7 |
| 12 | Makefile test targets | GAPS §7 |
| 13 | Release auth | spec §5 / GAPS §5, §7 |
| 14 | Version/git orphan cleanup | spec §4 note / GAPS §7 |

**Key outcome:** the two halves' Makefiles are **byte-identical** (per-half scope lives in
`.env`: `PY_SRC=src` for the template). The dependency model is the **BKM** (spec §6) — module
manifest declares names only, the requirements file holds pins + git pointers and every install
path leans on it, only the application layer pins, no `uv.lock`/`lock` target. This supersedes
the earlier "ranges, no committed lock" decision and `devops-makefile-principles.md` Lesson 1.

## Open plans

Each plan's frontmatter (`status`, `tracks_done` / `tracks_partial` / `tracks_open`) is the
source of truth for its state; this table is a derived summary — keep it in sync.

When a plan's tracks and acceptance criteria are all ticked, set `status: complete` and move
the file to `.claude/archive/action-plans/`, leaving its row here pointing at the new path.

| # | Plan | Status | Done | Open |
|---|------|--------|------|------|
| 15 | [PR #2 review findings](15-pr2-review-findings.md) | active | A, B, C | D, E, F, G, H |
| 16 | [pip-half bootstrap & recoverability](16-pip-half-bootstrap-recoverability.md) | active | I (G, H partial) | A, B, C, D, E, F |
| 17 | [kebab folder & dist name (check, don't transform)](17-project-name-derives-folder-and-dist-name.md) | active | — | A, B, C, D, E, F |
