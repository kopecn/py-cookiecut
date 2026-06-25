# 06 — Branch-naming model

**Source:** GAPS §4 (branch naming unresolved) · **Half:** both · **Decisions needed:** YES · **Risk:** medium

## Problem

Branch names are inconsistent across the repo, which breaks CI triggers and release tagging:
- New CI workflows trigger on `dev` / `prod`.
- `tag-on-prod.yml` tags `v<version>` on push to `prod`.
- Old `tag`/`release`/README text references `master`.
- The actual repo uses `development` / `main`.

One model must be chosen and applied everywhere consistently, in **both** halves.

## Decision required (blocking)

**D1 — the branch model.** Pick one pair (integration branch → release branch):
- **(A) `main` + `prod`.** `main` = integration/default; `prod` = release line that triggers
  tagging. Matches the repo's actual default (`main`) and the existing `tag-on-prod.yml`. Minimal
  churn. **Recommended.**
- **(B) `dev` + `prod`.** Matches the new CI `on:` triggers but requires renaming the repo default
  away from `main`.
- **(C) `development` + `main`.** Matches current actual repo branches but contradicts the CI and
  tagging workflows (would need `tag-on-main`).

> Recommendation: **(A)** — least surprising (`main` is already default), and `tag-on-prod.yml`
> already encodes `prod` as the release line. Confirm via `AskUserQuestion`.

## Steps (assuming verdict A)

1. **Inventory every branch reference** before editing:
   `grep -rIn -E 'master|development|\bdev\b|\bprod\b|main' .github Makefile readme.md README.md "{{cookiecutter.projectIdentifier}}"`
   (exclude `.git/`). Build the full hit list so nothing is missed.
2. **CI workflows (both halves):** set `on: push`/`pull_request` branches to the chosen
   integration branch; confirm `tag-on-prod.yml` triggers on the chosen release branch. These are
   under `_copy_without_render` so `${{ }}` is safe — edit them as literal YAML.
3. **Makefile `tag`/`release`:** note `tag` was **AXED** (GAPS G8 — tagging owned by
   `tag-on-prod.yml`). Ensure `release`/`release-test` (Plan 13) push to / gate on the chosen
   release branch, not `master`.
4. **README/docs:** replace `master` and any stale branch names with the chosen model in both
   halves.
5. **CODEOWNERS / branch-protection docs:** verify they reference the chosen branches.
6. Document the model once, authoritatively (generated project README + CONTRIBUTING), so users of
   the template know the dev→release flow.

## Files affected

- `.github/workflows/*.yml` (both halves)
- `Makefile` (both halves) — `release`/`release-test` branch refs
- `readme.md` (root), `{{cookiecutter.projectIdentifier}}/README.md`, CONTRIBUTING (both halves)
- `.github/CODEOWNERS` (both halves) — if it references branches

## Acceptance criteria

- D1 recorded in `GAPS.md`.
- A single branch model is used consistently across CI, Makefile, README, and CONTRIBUTING in
  both halves; `grep` finds no stray `master`/contradictory names.
- CI triggers and `tag-on-prod` fire on the intended branches (verified by reading the resolved
  workflow YAML after a bake).
