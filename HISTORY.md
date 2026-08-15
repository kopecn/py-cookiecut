# History

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `.claude/CLAUDE.md` operating spec and `.claude/GAPS.md` refactor backlog.
- `HISTORY.md` changelog (this file) plus a documented changelog BKM in `CONTRIBUTING.md`.

### Changed
- Consolidated root and template `.gitignore` files (added `.ruff_cache/`, `uv.lock`;
  moved Sphinx build output to `docs/sphinx/_build/`).

## [0.0.1] - 2025-08-16

### Added
- Initial Cookiecutter template (forked from `cookiecutter-pypackage`): `src/` layout,
  pre/post-gen hooks, `pytest-cookies` bake tests, and a generated-project `Makefile`.

[Unreleased]: https://github.com/kopecn/py-cookiecut/compare/v0.0.1...HEAD
[0.0.1]: https://github.com/kopecn/py-cookiecut/releases/tag/v0.0.1
