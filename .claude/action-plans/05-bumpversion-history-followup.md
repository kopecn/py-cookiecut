# 05 — bump2version HISTORY auto-roll

**Source:** GAPS §3 (bump2version follow-up) · **Half:** both · **Decisions needed:** no · **Risk:** low

## Problem

`bump2version` config (`.bumpversion.cfg`) already exists in both halves and bumps the version in
`pyproject.toml` (`commit = True`, `tag = False`, verified via dry-run). Follow-up: on release,
also auto-roll the `HISTORY.md` `[Unreleased]` header so the changelog tracks the new version
instead of being hand-edited every time.

## Approach

bump2version can manage multiple files in one config via additional `[bumpversion:file:...]`
sections, each with its own `search`/`replace`. Use this to rewrite the changelog header during a
bump.

Two viable mechanisms:
- **(A) Header rewrite via a `[bumpversion:file:HISTORY.md]` section.** `search`/`replace` turns the
  `## [Unreleased]` line into `## [Unreleased]\n\n## [{new_version}] - <date>`. bump2version
  supports `{new_version}`; it does **not** natively inject the date, so the date either stays a
  placeholder or is filled by a follow-up step.
- **(B) A small `pre`/post bump hook** (Makefile `bump-%` recipe wraps bumpversion, then a tiny
  `python`/`sed` step inserts a dated section). More flexible (real date), slightly more moving
  parts.

> Recommendation: **(B)** wired into the existing `bump-%` Makefile target (Plan 14 / GAPS G8
> already owns `bump-patch/minor/major` + `bump-%`). Keeps `.bumpversion.cfg` focused on the
> version string and lets the recipe own changelog formatting (incl. the real date via
> `$(shell date +%F)`).

## Steps

1. Confirm `HISTORY.md` uses a stable, machine-matchable header convention in both halves
   (e.g. Keep-a-Changelog `## [Unreleased]`). Normalize if it doesn't.
2. Implement the roll in the `bump-%` recipe (Plan 14): after `bumpversion <part>` succeeds,
   insert `## [<new_version>] - <YYYY-MM-DD>` immediately under `## [Unreleased]`, leaving
   `[Unreleased]` empty for the next cycle. Derive `<new_version>` from `make -s version` (post
   bump) and the date from `date +%F`.
3. Ensure the changelog edit is included in the bumpversion commit (or amended into it) so version
   + changelog move together.
4. Keep this **out** of `.bumpversion.cfg` unless verdict A is chosen; if A, add the file section
   and accept a placeholder date.
5. Apply identically in both halves (root tooling + generated project).

## Files affected

- `Makefile` (both halves) — `bump-%` recipe gains the changelog-roll step
- `.bumpversion.cfg` (both halves) — only if verdict A
- `HISTORY.md` (both halves) — header convention normalization if needed

## Acceptance criteria

- Running a bump moves the version **and** opens a fresh dated changelog section, leaving
  `[Unreleased]` empty.
- The changelog change is part of the same commit as the version bump.
- Behavior is identical in root and generated projects (verified by a bake + dry-run bump).
