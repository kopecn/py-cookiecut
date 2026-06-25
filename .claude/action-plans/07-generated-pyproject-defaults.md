# 07 — Generated pyproject defaults

**Source:** GAPS §4 (empty keywords/classifiers/dependencies/urls) · **Half:** template body · **Decisions needed:** minor · **Risk:** low

## Problem

The generated `{{cookiecutter.projectIdentifier}}/pyproject.toml` ships **empty**
`keywords = []`, `classifiers = []`, `dependencies = []`, and a `[project.urls]` that only has
bugs/changelog/homepage. A freshly baked project should be publishable-shaped without the user
hand-filling boilerplate. (The `[project.urls]` block is actually populated — the real gaps are
keywords, classifiers, and dependencies.)

## Approach

Fill each empty block with sensible **templated** defaults that render from existing
`cookiecutter.json` variables, keeping anything genuinely project-specific minimal.

## Steps

1. **classifiers** — provide a default set mirroring the root project's, but with version rows
   driven by the canonical matrix from **Plan 04** (keep them in sync). Include at minimum:
   `Development Status`, `Intended Audience :: Developers`, `License :: OSI Approved :: MIT
   License`, `Programming Language :: Python :: 3` + per-version rows, `Operating System ::
   OS Independent`. Honor the camelCase verdict from Plan 02 only insofar as it affects naming,
   not classifiers.
2. **keywords** — seed from template context: e.g. `["{{ cookiecutter.packageName }}", "python",
   "package"]`. Keep short; it's a starting point.
3. **dependencies** — keep the runtime list **empty by default** (a fresh package has no runtime
   deps) but add a comment showing the expected format, OR seed nothing and rely on the `[dev]`
   extra (already populated). Decision: prefer an explicit empty list with a guiding comment over
   inventing deps. (Minor decision — default to empty-with-comment.)
4. **license classifier vs `license` field** — ensure the MIT `license = {text = "MIT"}` and the
   MIT classifier agree (and match the shipped `LICENSE`).
5. Keep the static blocks free of stray Jinja: only `{{ }}` where a value is genuinely derived.
6. Re-bake and confirm the rendered `pyproject.toml` is valid TOML and `python -m build` succeeds
   (ties into Plan 13's `validateBuild`).

## Files affected

- `{{cookiecutter.projectIdentifier}}/pyproject.toml`
- Cross-ref Plan 04 (classifier version rows) and Plan 02 (naming).

## Acceptance criteria

- Baked `pyproject.toml` has non-empty `keywords` and `classifiers`, an intentional
  `dependencies` policy (empty + comment), and agreeing license metadata.
- Rendered file is valid TOML; `python -m build` produces an sdist/wheel without metadata warnings
  about missing classifiers.
- Classifier version rows match Plan 04's canonical matrix.
