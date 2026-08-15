"""
Pre-generation validation hook.

Runs BEFORE the template is rendered. Validates the identifiers the bake will use to
name the distribution/folder and the import surface (package directory + module file).

**D1 — check, do not transform.** This hook validates what the user typed. It never
rewrites, slugifies, or auto-corrects a value; a bad value is a loud, non-zero-exit
abort with a corrective message, never a silent fix-up. See
.claude/specs/project-conventions.md §1.

Two casings, two regexes:
- `projectIdentifier` (distribution name + top-level folder) must be lowercase
  kebab-case: PyPI/repo/folder convention, not an import surface.
- `packageName` / `moduleName` (the `import` surface) must be PEP-8 snake_case:
  hyphens are not legal Python identifiers.

camelCase remains the house style for *tooling* identifiers (cookiecutter keys, test
function names, Makefile targets); it is not allowed for any of the three generated
identifiers validated here.
"""

import re
import sys

# Lowercase kebab-case: letters/digits, hyphen-separated words, no leading/trailing
# hyphen, no underscore, no uppercase.
KEBAB_CASE_REGEX = r"^[a-z0-9]+(-[a-z0-9]+)*$"

# PEP-8 snake_case: lowercase letters, digits, underscores; no leading digit, no hyphen,
# no uppercase. A single character is allowed (e.g. a one-letter module).
SNAKE_CASE_REGEX = r"^[a-z_][a-z0-9_]*$"

KEBAB_CASE_IDENTIFIERS = {
    "projectIdentifier": "{{ cookiecutter.projectIdentifier }}",
}

SNAKE_CASE_IDENTIFIERS = {
    "packageName": "{{ cookiecutter.packageName }}",
    "moduleName": "{{ cookiecutter.moduleName }}",
}

errors = []

for variable, value in KEBAB_CASE_IDENTIFIERS.items():
    if not re.match(KEBAB_CASE_REGEX, value):
        corrected = value.replace("_", "-").lower()
        errors.append(
            f"ERROR: {variable}={value!r} is not a valid kebab-case identifier.\n"
            f"       Allowed pattern: {KEBAB_CASE_REGEX}\n"
            f"       Use lowercase letters, digits, and hyphens only "
            f"(no underscores, no uppercase, no leading/trailing hyphen).\n"
            f"       Did you mean {corrected!r}?"
        )

for variable, value in SNAKE_CASE_IDENTIFIERS.items():
    if not re.match(SNAKE_CASE_REGEX, value):
        errors.append(
            f"ERROR: {variable}={value!r} is not a valid PEP-8 snake_case identifier.\n"
            f"       Allowed pattern: {SNAKE_CASE_REGEX}\n"
            f"       Use lowercase letters, digits, and underscores only "
            f"(no hyphens, no uppercase, no leading digit). e.g. my_package"
        )

if errors:
    print("\n\n".join(errors), file=sys.stderr)
    # Exit to cancel project generation.
    sys.exit(1)
