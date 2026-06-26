"""
Pre-generation validation hook.

Runs BEFORE the template is rendered. Validates that the identifiers which become an
importable surface — the distribution name, the package directory, and the module file —
are PEP-8 snake_case. A non-zero exit aborts the bake.

camelCase remains the house style for *tooling* identifiers (cookiecutter keys, test
function names, Makefile targets); it is intentionally NOT allowed for these generated
identifiers, which PyPI consumers `import`. See .claude/specs/project-conventions.md §1.
"""

import re
import sys

# PEP-8 snake_case: lowercase letters, digits, underscores; no leading digit, no hyphen,
# no uppercase. A single character is allowed (e.g. a one-letter module).
SNAKE_CASE_REGEX = r"^[a-z_][a-z0-9_]*$"

# Each generated identifier that must be a legal, importable snake_case name.
IDENTIFIERS = {
    "projectIdentifier": "{{ cookiecutter.projectIdentifier }}",
    "packageName": "{{ cookiecutter.packageName }}",
    "moduleName": "{{ cookiecutter.moduleName }}",
}

errors = []
for variable, value in IDENTIFIERS.items():
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
