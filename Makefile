.PHONY: clean cleanTest cleanArtifacts cleanBuild docs help test testInEnv \
	testInEnvInstallFromSetup testInEnvRunPytest testInEnvCleanup \
	dist release install devInstall flushPip build version tag

.DEFAULT_GOAL := help

VERSION=v$(shell grep -m 1 version pyproject.toml | tr -s ' ' | tr -d '"' | tr -d "'" | cut -d' ' -f3)
PYTHON := python3
PIP := $(PYTHON) -m pip
VENV := /tmp/pipTest

help:  ## Show this help
	@awk 'BEGIN {FS = ":.*?## "}; /^[a-zA-Z0-9_-]+:.*?## / {printf "%-30s -> %s\n", $$1, $$2}' $(MAKEFILE_LIST)

clean: cleanBuild cleanArtifacts cleanTest  ## Remove all build, test, coverage, and Python artifacts

cleanBuild:  ## Remove build artifacts
	rm -rf build/ dist/ .eggs/
	find . -name '*.egg-info' -exec rm -rf {} +
	find . -name '*.egg' -exec rm -rf {} +

cleanArtifacts:  ## Remove Python file artifacts
	find . \( -name '*.pyc' -o -name '*.pyo' -o -name '*~' \) -exec rm -f {} +
	find . -name '__pycache__' -exec rm -rf {} +

cleanTest:  ## Remove test and coverage artifacts
	rm -f .coverage
	rm -rf htmlcov/ .pytest_cache

test:  ## Run tests quickly with the default Python
	pytest

testInEnv: clean testInEnvInstallFromSetup testInEnvRunPytest testInEnvCleanup  ## Create temp venv, install deps, run tests, cleanup

testInEnvInstallFromSetup: testInEnvCleanup  ## Create temp venv in $(VENV) and install dev dependencies
	$(PYTHON) -m venv $(VENV) && \
	. $(VENV)/bin/activate && \
	which python3 && \
	$(PYTHON) -m pip install ".[personal_repos,develop]"
	@echo "Virtual env can be activated with 'source $(VENV)/bin/activate'"

testInEnvRunPytest:  ## Run pytest inside temp virtual environment
	. $(VENV)/bin/activate && \
	which $(PYTHON) && \
	$(PYTHON) -m pytest

testInEnvCleanup:  ## Remove temp virtual environment
	rm -rf $(VENV) || true

dist: clean  ## Build source and wheel package
	$(PYTHON) -m build
	ls -l dist

build:  ## Build the project, useful for checking that packaging is correct
	rm -rf build dist
	$(PYTHON) -m build

version:  ## Print the current version of the project
	@echo "Current version is $(VERSION)"

tag:  ## Tag the current version in git and push to github
	echo "Tagging version $(VERSION)"
	git tag -a $(VERSION) -m "Creating version $(VERSION)"
	git push origin $(VERSION)	

release: dist  ## Package and upload a release to PyPI
	twine upload dist/*

install: clean  ## Install the package in editable mode
	$(PIP) install -e .

devInstall: clean  ## Install development dependencies
	$(PIP) install -e .[develop]

docs:  ## Build HTML documentation with Sphinx
	sphinx-build -b html docs/ docs/_build/html
	@echo "Documentation built in docs/_build/html"

flushpip: SHELL := /bin/bash
flushpip:  ## Uninstall all packages from current pip environment
	$(PIP) uninstall -y -r <($(PIP) freeze)
