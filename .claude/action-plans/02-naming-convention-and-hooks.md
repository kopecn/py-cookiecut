# 02 — Naming convention + hook validation

**Source:** GAPS §2 · **Half:** root (hooks) + template body · **Decisions needed:** YES · **Risk:** medium

## Problem

Two coupled issues:

1. **camelCase package/module names.** The template ships `packageName=myPackage`,
   `moduleName=myModule`. camelCase is intentional for *tooling* identifiers ("Nick's workflow"),
   but for an importable **package/module** it violates PEP 8 and PyPI import norms
   (`import myPackage`). Need an explicit verdict.
2. **`pre_gen_project.py` lies and under-validates.** Current regex `^[_a-zA-Z][_a-zA-Z0-9]+$`
   only *rejects `-`*; it never enforces that `_` was used, yet the error says "use `_` instead."
   It also validates **only `projectIdentifier`**, not `packageName`/`moduleName`.

## Decision required (blocking)

**D1 — naming policy.** Pick one:
- **(A) Keep camelCase everywhere** (deliberate deviation; document loudly in generated README +
  CLAUDE.md). Simplest; consistent with stated "Nick's workflow."
- **(B) camelCase for tooling, lowercase for the importable package/module.** Generated package
  becomes e.g. `my_package`/`my_module` (or `mypackage`). Aligns with PEP 8 / import norms.
- **(C) Hybrid:** keep camelCase `projectIdentifier` (the project/dist name) but lowercase the
  import surface (`packageName`/`moduleName`).

> Recommendation: **(C)** — distribution/project name can be camelCase, but the *import surface*
> should be lowercase to avoid surprising consumers. Surface this via `AskUserQuestion` before
> implementing. The rest of this plan assumes the validation work, which is needed under any
> verdict.

## Steps

### Hook validation rewrite (`hooks/pre_gen_project.py`)
1. Define separate validators:
   - `projectIdentifier`: must be a legal module name. Keep `^[_a-zA-Z][_a-zA-Z0-9]+$` (rejects
     `-`, leading digit). Fix the **message** to match reality: it rejects hyphens and other
     illegal chars — don't claim it rewrites to `_`.
   - `packageName` and `moduleName`: validate against the policy chosen in D1. If (B)/(C), enforce
     lowercase + underscores (e.g. `^[a-z_][a-z0-9_]*$`); if (A), the module regex.
2. Emit a **specific** error per offending variable (name + value + what was expected), then
   `sys.exit(1)`.
3. Keep messages copy-pasteable: show the exact allowed pattern.

### Template body
4. If D1 ≠ (A): update `cookiecutter.json` defaults (`packageName`, `moduleName`) to lowercase
   examples, and verify templated paths still resolve:
   `src/{{cookiecutter.packageName}}/{{cookiecutter.moduleName}}.py`.
5. Grep the template body for hardcoded `myPackage`/`myModule` references and re-point them.

### Tests
6. Add `tests/testBakeProject.py` cases:
   - bake with a hyphenated `projectIdentifier` → bake **fails** (hook exits non-zero).
   - bake with an illegal `packageName`/`moduleName` → bake **fails**.
   - bake with valid values → succeeds and the expected `src/.../*.py` path exists.

## Files affected

- `hooks/pre_gen_project.py`
- `cookiecutter.json` (if D1 ≠ A)
- `{{cookiecutter.projectIdentifier}}/...` references to package/module names
- `tests/testBakeProject.py`
- Generated `README.md` / docs note if (A) is chosen (document the deliberate deviation)

## Acceptance criteria

- D1 recorded in `GAPS.md` and this plan.
- Hook validates all three identifiers, with messages that match actual behavior.
- New bake tests cover both reject and accept paths and pass.
- A clean bake produces import paths consistent with the chosen policy.
