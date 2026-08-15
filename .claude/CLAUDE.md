# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## ⚠️ Project status: GREENFIELD — rip-and-tear in progress

This repository is being **significantly refactored**. Treat existing structure as
**provisional, not load-bearing**. We are intentionally tearing out and replacing large
portions of the template tooling and the generated-project template. Do **not** preserve
legacy patterns for backward-compatibility reasons — there are no downstream consumers to
protect yet. Prefer decisive replacement over incremental patching.

The current known defects and intended changes are tracked in [`GAPS.md`](./GAPS.md) in this
directory. Read it before starting work; update it as items are resolved or added.

## What this repository is

`py-cookiecut` is a **Cookiecutter template** — a meta-project that *generates* Python
package projects. It originated as a fork of Audrey Roy's `cookiecutter-pypackage`.

There are two distinct halves; keep them mentally separate:

| Layer | Path | Role |
|---|---|---|
| **Template tooling** | root `pyproject.toml`, `Makefile`, `tests/`, `hooks/`, `cookiecutter.json` | The machinery that *bakes* and *tests* the template. Runs in *this* repo. |
| **The template body** | `{{cookiecutter.projectIdentifier}}/` | The files that get rendered into a *new* user project. Jinja-templated; does not run here. |

`cookiecutter.json` is the variable contract between the two halves. The variable **keys** use
**camelCase** (`projectIdentifier`, `packageName`, `moduleName`) — a tooling-internal house
style — and derived values (`pypiUsername`, `ghIdentifier`) reference earlier keys via Jinja.
The **values** split by role: `projectIdentifier` (distribution name + project folder + GitHub
repo slug) is **kebab-case** (`python-boilerplate`), while `packageName`/`moduleName` (the
import surface) are **PEP-8 snake_case** (`my_package`, `my_module`). See
`.claude/specs/project-conventions.md` §1. Per-prompt guidance lives in the `__prompts__` block.

### Generation lifecycle (how a bake actually works)

1. `hooks/pre_gen_project.py` runs **before** rendering — validates `projectIdentifier` is
   kebab-case (regex `^[a-z0-9]+(-[a-z0-9]+)*$`; rejects underscores and uppercase) and that
   `packageName`/`moduleName` are PEP-8 snake_case (regex `^[a-z_][a-z0-9_]*$`; rejects hyphens,
   uppercase, leading digits). Emits a per-variable error and exits non-zero to abort the bake.
   **D1: it validates only — it never rewrites a value.**
2. Cookiecutter renders `{{cookiecutter.projectIdentifier}}/` with the resolved variables,
   including templated *paths* (`src/{{cookiecutter.packageName}}/{{cookiecutter.moduleName}}.py`).
3. `hooks/post_gen_project.py` runs **after** rendering (currently only prints a success message).

The generated project uses a **`src/` layout**.

### How the template is tested

`tests/testBakeProject.py` is the real test surface. It uses `pytest-cookies` to bake the
template into a temp dir, then asserts on the output and runs `pytest`/`make` *inside* the
baked project. Key helpers: `bakeInTempDir` (bakes + cleans up), `runInsideDir` /
`checkOutputInsideDir` (shell out from within the baked project). When you change the
template body, these tests are what catch breakage — extend them rather than testing by hand.

## Commands

All commands run from the repo root. The `Makefile` loads `.env` (`PYTHON=python3`,
`VENV=/tmp/pipTest`) and exports it.

```bash
make help            # list documented targets
make devInstall      # editable install + dev deps (pytest, pylint, black, mypy, ...)
make test            # run the bake tests (pytest)
make lint            # pylint src/   (NOTE: this repo has no src/ — see GAPS.md)
make format          # black src/
make typecheck       # mypy src/
make fullCheck       # lint + typecheck + test
make build           # build sdist/wheel to validate packaging
make testInEnv       # full clean-room: fresh venv, install, run tests, teardown
```

Run a single test:

```bash
pytest tests/testBakeProject.py::testBakeWithDefaults
pytest -k testMakeHelp
```

Test config (root `pyproject.toml`): `testpaths = ["tests/*"]`, and pytest is configured to
discover `test*.py` files and `test*` functions (note the **non-standard** `test*` glob, not
`test_*`).

> Many `Makefile` targets (`lint`, `format`, `typecheck`, `docs`) assume directories/tools
> that don't match this repo's actual layout — they are inherited from the generated-project
> Makefile. See `GAPS.md` before relying on them.

## Conventions specific to this project

- **Three naming layers** (see `.claude/specs/project-conventions.md` §1): *tooling*
  identifiers are camelCase house style ("Nick's workflow") — cookiecutter variable **keys**,
  `test*` function names (`testBakeWithDefaults`), Makefile targets. The *distribution* layer
  (`projectIdentifier` → dist name, project folder, GitHub repo slug) is **kebab-case**
  (`python-boilerplate`). The *import* layer (`packageName`/`moduleName`) is **PEP-8
  snake_case** (`my_package`, `my_module`). Don't conflate them: a camelCase key can carry a
  kebab-case or snake_case value depending on its layer.
- **One name, three surfaces.** The generated folder, `pyproject [project].name`, and the GitHub
  repo slug are all `projectIdentifier`. `git clone` names a directory after the repo, so these
  must not diverge; `testGithubUrlsMatchFolderName` guards it.
- **`projectName` is headings-only.** It does not set the folder name — that is
  `projectIdentifier`, typed separately.
- When editing files under `{{cookiecutter.projectIdentifier}}/`, remember the content is
  **Jinja**, not final Python. `{{ ... }}` and `{% ... %}` are template directives. A file
  that looks broken in isolation may be correct post-render.
- The root `Makefile` and the template's `Makefile` are near-duplicates today. Changing one
  does not change the other — decide deliberately which layer a change belongs to.
