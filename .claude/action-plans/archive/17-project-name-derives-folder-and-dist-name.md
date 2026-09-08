---
last_updated: 2026-08-28
semver: 1.0.0
author: Nicholas Bergantz
status: complete
---

# Plan 17 — generated-project naming (completed record)

The lasting decisions are:

- `projectIdentifier` is typed by the user and validated as lowercase kebab-case;
- it supplies the generated folder, distribution name, and GitHub repository slug;
- the hook validates and never rewrites input;
- `packageName` and `moduleName` remain snake_case import identifiers;
- `projectName` is free-form display text used only in headings;
- generated tests use `tests/test_<moduleName>.py`.

The current hook, template, tests, and documentation implement these decisions. This
completed plan authorizes no further naming transformation, compatibility alias, or
derived-name machinery.
