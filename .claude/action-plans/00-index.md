# Action Plans — Index

Per-gap implementation plans derived from [`.claude/GAPS.md`](../GAPS.md). Each plan is
self-contained: it states the source gap, the open decisions, the concrete steps, the files
touched in **both halves** (template tooling vs. template body), and acceptance criteria.

Greenfield rules apply: prefer decisive replacement over backward-compat patching. When a plan
resolves or supersedes a GAPS item, tick the box in `GAPS.md` and note it here.

> **Two-halves reminder.** "Root" = template tooling that runs in *this* repo. "Template" =
> files under `{{cookiecutter.projectIdentifier}}/` that render into a new project. Most plans
> touch both; each plan calls out which.

| # | Plan | GAPS § | Blocking decisions? |
|---|------|--------|---------------------|
| 01 | [Cleanup stale on-disk artifacts](./01-cleanup-stale-artifacts.md) | §1 | No |
| 02 | [Naming convention + hook validation](./02-naming-convention-and-hooks.md) | §2 | **Yes** — camelCase verdict |
| 03 | [Lint stack: ruff + mypy config, drop pylintrc](./03-lint-stack-ruff-mypy.md) | §3, §6 | Minor |
| 04 | [Python version reconciliation](./04-python-version-reconciliation.md) | §3, §7, §8 | **Yes** — canonical version set |
| 05 | [bump2version HISTORY auto-roll](./05-bumpversion-history-followup.md) | §3 | No |
| 06 | [Branch-naming model](./06-branch-naming-model.md) | §4 | **Yes** — pick branch model |
| 07 | [Generated pyproject defaults](./07-generated-pyproject-defaults.md) | §4 | Minor |
| 08 | [Generated smoke test](./08-generated-smoke-test.md) | §4 | No |
| 09 | [Makefile: dependency SoT, clean, flush, refresh](./09-makefile-deps-clean-flush.md) | §5, §7 | **Yes** — lock/commit policy |
| 10 | [Makefile: multi-repo editable siblings](./10-makefile-multi-repo-editable.md) | §7 | Minor |
| 11 | [Makefile: quality targets](./11-makefile-quality-targets.md) | §3, §6, §7 | No (after 03) |
| 12 | [Makefile: test targets](./12-makefile-test-targets.md) | §7 | No |
| 13 | [Makefile: build & release](./13-makefile-build-and-release.md) | §5, §7 | **Yes** — TestPyPI/PyPI auth |
| 14 | [Makefile: version/git orphan cleanup](./14-makefile-version-git-cleanup.md) | §7 | No (after 04) |

## Suggested execution order

1. **Decide the cross-cutting things first** (they unblock the rest):
   - 02 camelCase verdict, 04 canonical Python set, 06 branch model, 09 lock/commit policy.
2. **Mechanical cleanup**: 01, 03, 05.
3. **Template body correctness**: 07, 08.
4. **Makefile command-by-command pass** (build order): 09 → 10 → 11 → 12 → 13 → 14.

Plans 03, 11, and the ruff/mypy config are intertwined: 03 lands the *config*; 11 wires the
*Makefile targets* that consume it. Do 03 before 11.
