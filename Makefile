.PHONY: clean clean-test clean-pyc clean-build docs help test test-in-tmp-venv \
	venv-install-temp-env-from-setup venv-run-pytest-in-tmp-env venv-cleanup-tmp-env \
	dist release install dev-install flushpip build version

.DEFAULT_GOAL := help



# Python one-liner to open a file in the browser
define BROWSER_PYSCRIPT
import os, webbrowser, sys
from urllib.request import pathname2url
webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

# Python one-liner to print help for Makefile targets
define PRINT_HELP_PYSCRIPT
import re, sys
for line in sys.stdin:
    match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
    if match:
        target, help = match.groups()
        print("%-20s -> %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

VERSION=v$(shell grep -m 1 version pyproject.toml | tr -s ' ' | tr -d '"' | tr -d "'" | cut -d' ' -f3)
PYTHON := python3
BROWSER := $(PYTHON) -c "$$BROWSER_PYSCRIPT"
PIP := $(PYTHON) -m pip
VENV := $(VENV)



help:  ## Show this help
	@$(PYTHON) -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: clean-build clean-pyc clean-test  ## Remove all build, test, coverage, and Python artifacts

clean-build:  ## Remove build artifacts
	rm -rf build/ dist/ .eggs/
	find . -name '*.egg-info' -exec rm -rf {} +
	find . -name '*.egg' -exec rm -rf {} +

clean-pyc:  ## Remove Python file artifacts
	find . \( -name '*.pyc' -o -name '*.pyo' -o -name '*~' \) -exec rm -f {} +
	find . -name '__pycache__' -exec rm -rf {} +

clean-test:  ## Remove test and coverage artifacts
	rm -f .coverage
	rm -rf htmlcov/ .pytest_cache

test:  ## Run tests quickly with the default Python
	pytest

test-in-tmp-venv: clean venv-install-temp-env-from-setup venv-run-pytest-in-tmp-env venv-cleanup-tmp-env  ## Create temp venv, install deps, run tests, cleanup

venv-install-temp-env-from-setup: venv-cleanup-tmp-env  ## Create temp venv in $(VENV) and install dev dependencies
	$(PYTHON) -m venv $(VENV)
	. $(VENV)/bin/activate; which $(PYTHON); $(PIP) install ".[personal_repos,develop]"
	@echo "Virtual env can be activated with 'source $(VENV)/bin/activate'"

venv-run-pytest-in-tmp-env:  ## Run pytest inside temp virtual environment
	. $(VENV)/bin/activate && \
	which $(PYTHON) && \
	$(PYTHON) -m pytest

venv-cleanup-tmp-env:  ## Remove temp virtual environment
	rm -rf $(VENV) || true

dist: clean  ## Build source and wheel package
	$(PYTHON) -m build
	ls -l dist


build:  ## Build the project, useful for checking that packaging is correct
	rm -rf build
	rm -rf dist
	$(PYTHON) -m build

version:  ## Print the current version of the project
	@echo "Current version is $(VERSION)"

tag:  ## Tag the current version in git and put to github
	echo "Tagging version $(VERSION)"
	git tag -a $(VERSION) -m "Creating version $(VERSION)"
	git push origin $(VERSION)	

release: dist  ## Package and upload a release to PyPI
	twine upload dist/*

install: clean  ## Install the package in editable mode
	$(PIP) install -e .

dev-install: clean  ## Install development dependencies
	$(PIP) install -e .[develop]

docs:  ## Build HTML documentation with Sphinx
	sphinx-build -b html docs/ docs/_build/html
	@echo "Documentation built in docs/_build/html"

flushpip: SHELL := /bin/bash
flushpip:  ## Uninstall all packages from current pip environment
	$(PIP) uninstall -y -r <($(PIP) freeze)
