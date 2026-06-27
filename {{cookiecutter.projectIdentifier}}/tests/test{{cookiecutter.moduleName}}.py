"""Smoke tests for {{ cookiecutter.packageName }}.

These import the real package (resolved via `pythonpath = ["src"]` in pyproject, so they
run without an install) and assert concrete behavior — a meaningful starting point, not a
vacuous placeholder.
"""

from {{ cookiecutter.packageName }} import __version__
from {{ cookiecutter.packageName }}.{{ cookiecutter.moduleName }} import hello


def testVersionIsExposed() -> None:
    """The package exposes its version, matching the baked value."""
    assert __version__ == "{{ cookiecutter.version }}"


def testHelloReturnsGreeting() -> None:
    """The sentinel function returns a non-empty greeting naming the package."""
    greeting = hello()
    assert "{{ cookiecutter.packageName }}" in greeting
