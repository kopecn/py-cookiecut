# History

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.0.3] - 2026-09-08

### Added
- `HISTORY.md` changelog (this file) plus a documented changelog BKM in `CONTRIBUTING.md`.
- `flake8` linting configuration (root and template `.flake8`) and a flake8 step in CI.
- `docs/branching strategy.md` documenting the feat/bugfix/hotfix → dev → prod workflow.

### Changed
- Consolidated root and template `.gitignore` files (added `.ruff_cache/`, `uv.lock`;
  moved Sphinx build output to `docs/sphinx/_build/`).
- Refined `project-conventions` spec and the root/template `Makefile` and `pyproject.toml`
  for fleet toolchain alignment.

## [0.0.2] - 2026-08-14

### Added
- Generated-project GitHub Actions workflows: `ci.yml`, `publish.yml`, and `tag-on-prod.yml`.
- Template scaffolding: `CODEOWNERS`, `.editorconfig`, `.vscode/extensions.json`,
  `.python-version`, and `.bumpversion.cfg`.

### Changed
- Rebuilt the template against latest best-known-methods: expanded generated `Makefile`
  and `pyproject.toml`, and broadened `pre_gen_project.py` validation and the bake tests.
- Consolidated split `requirements_dev.txt`/`requirements_prod.txt` into `requirements.txt`.

### Removed
- Template `.pylintrc` (superseded by the current lint toolchain).

## [0.0.1] - 2026-06-22

### Added
- Initial Cookiecutter template (forked from `cookiecutter-pypackage`): `src/` layout,
  pre/post-gen hooks, `pytest-cookies` bake tests, and a generated-project `Makefile`.

[Unreleased]: https://github.com/kopecn/py-cookiecut/compare/v0.0.3...HEAD
[0.0.3]: https://github.com/kopecn/py-cookiecut/compare/v0.0.2...v0.0.3
[0.0.2]: https://github.com/kopecn/py-cookiecut/compare/v0.0.1...v0.0.2
[0.0.1]: https://github.com/kopecn/py-cookiecut/releases/tag/v0.0.1
