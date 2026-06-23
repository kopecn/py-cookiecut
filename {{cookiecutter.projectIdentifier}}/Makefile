# ============================================================================
# CONFIG
# ============================================================================
.PHONY: help version checkCleanGit bumpPatch bumpMinor bumpMajor tag open-github \
	clean cleanBuild cleanArtifacts cleanTest \
	check-uv install-uv list-uv \
	uv-bootstrap-pythons uv-bootstrap uv-sync uv-sync-headless uv-editable uv-refresh \
	uv-lint uv-lintFix uv-format uv-typecheck uv-typecheck-ty uv-fullCheck \
	uv-test uv-test-all uv-test-matrix \
	uv-build uv-validateBuild \
	uv-clean uv-flush-cache uv-flush-envs uv-flush-pythons uv-flush-everything uv-nuke \
	uv-lifecycle-test \
	installDev editable refresh \
	test testInEnvCleanup testInEnvInstallFromSetup testInEnvRunPytest testInEnv \
	build validateBuild release-test release \
	nuke list

.DEFAULT_GOAL := help

# Load .env file if it exists
ifneq (,$(wildcard .env))
    include .env
    export
endif

# Defaults (overridable via .env — the user-editable surface). Keep in sync with .env.
PYTHONS ?= 3.10 3.11 3.12 3.14
DEFAULT_PYTHON ?= 3.14
PYTHON ?= python3
VENV ?= .cleanroom-venv

# Derived
PIP := $(PYTHON) -m pip
REPO := $(notdir $(CURDIR))
UNAME_S := $(shell uname -s)
HR := ========================================

# Guard: DEFAULT_PYTHON must be one of the versions we test against.
ifeq ($(filter $(DEFAULT_PYTHON),$(PYTHONS)),)
    $(error DEFAULT_PYTHON ($(DEFAULT_PYTHON)) is not in PYTHONS ($(PYTHONS)) — fix .env)
endif
VERSION = v$(shell grep -m 1 'version' pyproject.toml | tr -s ' ' | tr -d '"' | tr -d "'" | cut -d'=' -f2 | xargs)

# ============================================================================
# HELP
# ============================================================================
help:  ## Show this help
	@echo "$(REPO) — make targets   (bare = pip · uv-… = uv path)"
	@echo "config: DEFAULT_PYTHON=$(DEFAULT_PYTHON)  PYTHONS=$(PYTHONS)"
	@echo ""
	@awk 'BEGIN {FS = ":.*?## "} \
		/^##@ / {printf "\n\033[1m%s\033[0m\n", substr($$0, 5); next} \
		/^[a-zA-Z0-9_-]+:.*?## / {printf "  \033[36m%-26s\033[0m %s\n", $$1, $$2}' \
		$(MAKEFILE_LIST)

# ============================================================================
# COMMON · VERSION & GIT
# ============================================================================
##@ Common · Version & Git
version:  ## Display the current project version
	@echo ">> [TODO G8] version not yet implemented"

checkCleanGit:  ## Guard: fail if the git working tree is dirty
	@echo ">> [TODO G8] checkCleanGit not yet implemented"

bumpPatch:  ## Bump patch version (0.0.x)
	@echo ">> [TODO G8] bumpPatch not yet implemented"

bumpMinor:  ## Bump minor version (0.x.0)
	@echo ">> [TODO G8] bumpMinor not yet implemented"

bumpMajor:  ## Bump major version (x.0.0)
	@echo ">> [TODO G8] bumpMajor not yet implemented"

tag: checkCleanGit version  ## Create and push a git tag
	@echo ">> [TODO G8] tag not yet implemented"

open-github:  ## Open the GitHub repository in the default browser (OS-aware)
	@echo ">> [TODO G8] open-github not yet implemented"

# ============================================================================
# COMMON · CLEAN  (base for pip install / test-in-env)
# ============================================================================
##@ Common · Clean
clean: cleanBuild cleanArtifacts cleanTest  ## Remove build, bytecode, and test artifacts

cleanBuild:  ## Delete build artifacts (build/ dist/ .eggs/ *.egg-info)
	@echo ">> [TODO G6] cleanBuild not yet implemented"

cleanArtifacts:  ## Remove Python bytecode and __pycache__
	@echo ">> [TODO G6] cleanArtifacts not yet implemented"

cleanTest:  ## Remove test/coverage/lint caches
	@echo ">> [TODO G6] cleanTest not yet implemented"

# ============================================================================
# UV · TOOLING
# ============================================================================
##@ UV · Tooling
check-uv:  ## Check if uv is installed (guard for all uv- targets)
	@command -v uv >/dev/null 2>&1 || { \
	  echo "ERROR: uv not found."; \
	  echo "  Install it with: make install-uv"; \
	  echo "  Or see: https://docs.astral.sh/uv/getting-started/installation/"; \
	  exit 1; }

install-uv:  ## Install uv (brew on macOS, installer script on Linux)
ifeq ($(UNAME_S),Darwin)
	@echo "Detected macOS - installing via Homebrew..."
	@command -v brew >/dev/null 2>&1 || { echo "ERROR: Homebrew not found. Install from https://brew.sh"; exit 1; }
	brew install uv
else ifeq ($(UNAME_S),Linux)
	@echo "Detected Linux - installing via official installer..."
	curl -LsSf https://astral.sh/uv/install.sh | sh
	@echo ""
	@echo "NOTE: You may need to add ~/.local/bin to your PATH:"
	@echo '  export PATH="$$HOME/.local/bin:$$PATH"'
else
	@echo "Unsupported OS: $(UNAME_S)"
	@echo "Install manually: https://docs.astral.sh/uv/getting-started/installation/"
	@exit 1
endif
	@echo ""
	@echo "uv installed successfully:"
	@uv --version

list-uv: check-uv  ## List uv envs, installed Pythons, packages, and cache info
	@echo "$(HR)"; echo "UV VERSION"; echo "$(HR)"
	@uv --version
	@echo ""; echo "$(HR)"; echo "INSTALLED PYTHON VERSIONS"; echo "$(HR)"
	@uv python list --only-installed
	@echo ""; echo "$(HR)"; echo "PROJECT VIRTUAL ENVIRONMENTS"; echo "$(HR)"
	@ls -d .venv 2>/dev/null || echo "No .venv found"
	@ls -d .venvs/*/ 2>/dev/null || echo "No .venvs/ matrix environments found"
	@echo ""; echo "$(HR)"; echo "INSTALLED PACKAGES (.venv)"; echo "$(HR)"
	@uv pip list 2>/dev/null || echo "No packages or .venv not found"
	@echo ""; echo "$(HR)"; echo "UV CACHE INFO"; echo "$(HR)"
	@uv cache dir
	@du -sh $$(uv cache dir) 2>/dev/null || echo "Cache empty or not accessible"

# ============================================================================
# UV · BOOTSTRAP & SYNC
# ============================================================================
##@ UV · Bootstrap & Sync
uv-bootstrap-pythons: check-uv  ## Install all configured Python versions via uv
	uv python install $(PYTHONS)

uv-bootstrap: check-uv uv-bootstrap-pythons  ## Full bootstrap: pythons + venv + deps
	uv venv --python $(DEFAULT_PYTHON)
	uv pip install -r requirements.txt
	uv pip install -e ".[dev]"
	@echo ""
	@echo "Bootstrap complete. Run 'make uv-test-all' to validate."

uv-sync: check-uv  ## Sync deps incl. dev (default uv dev workflow)
	@[ -d ".venv" ] || uv venv --python $(DEFAULT_PYTHON)
	uv pip install -r requirements.txt
	uv pip install -e ".[dev]"

uv-sync-headless: check-uv  ## Sync deps WITHOUT dev extras (deploy)
	@[ -d ".venv" ] || uv venv --python $(DEFAULT_PYTHON)
	uv pip install -r requirements.txt
	uv pip install .

uv-editable: check-uv  ## Install this package editable via uv (uv pip install -e .)
	uv pip install -e .

uv-refresh: check-uv  ## Clean cache + upgrade all deps to latest
	@echo ">> [TODO G7] uv-refresh not yet implemented"

# ============================================================================
# UV · QUALITY
# ============================================================================
##@ UV · Quality
uv-lint: check-uv  ## Run ruff linter
	@echo ">> [TODO G5] uv-lint not yet implemented"

uv-lintFix: check-uv  ## Run ruff linter with auto-fix
	@echo ">> [TODO G5] uv-lintFix not yet implemented"

uv-format: check-uv  ## Format code with ruff
	@echo ">> [TODO G5] uv-format not yet implemented"

uv-typecheck: check-uv  ## Strict type check with mypy
	@echo ">> [TODO G5] uv-typecheck not yet implemented"

uv-typecheck-ty: check-uv  ## Strict type check with ty (preview)
	@echo ">> [TODO G5] uv-typecheck-ty not yet implemented"

uv-fullCheck: uv-sync uv-lint uv-typecheck uv-test  ## lint + typecheck + tests
	@echo ">> [TODO G5] uv-fullCheck orchestrator (prereqs above)"

# ============================================================================
# UV · TEST
# ============================================================================
##@ UV · Test
uv-test: check-uv  ## Run tests on DEFAULT_PYTHON
	@echo ">> [TODO G4] uv-test not yet implemented"

uv-test-all: check-uv  ## Run tests across all configured Pythons (.venvs/<ver>)
	@echo ">> [TODO G4] uv-test-all not yet implemented"

uv-test-matrix: uv-bootstrap-pythons uv-test-all  ## Ensure pythons, then test-all
	@echo ">> [TODO G4] uv-test-matrix orchestrator (prereqs above)"

# ============================================================================
# UV · BUILD
# ============================================================================
##@ UV · Build
uv-build: check-uv  ## Build sdist+wheel via uv
	@echo ">> [TODO build] uv-build not yet implemented"

uv-validateBuild: uv-build  ## Build + validate with twine
	@echo ">> [TODO build] uv-validateBuild not yet implemented"

# ============================================================================
# UV · FLUSH / NUKE
# ============================================================================
##@ UV · Flush / Nuke
uv-clean:  ## Remove build artifacts, caches, lock file
	@echo ">> [TODO G6] uv-clean not yet implemented"

uv-flush-cache: check-uv  ## Clean uv cache
	@echo ">> [TODO G6] uv-flush-cache not yet implemented"

uv-flush-envs:  ## Remove all virtual environments (.venv + .venvs/<ver>)
	@echo ">> [TODO G6] uv-flush-envs not yet implemented"

uv-flush-pythons:  ## Remove uv-managed Python installs (NUCLEAR)
	@echo ">> [TODO G6] uv-flush-pythons not yet implemented"

uv-flush-everything: uv-clean uv-flush-envs uv-flush-cache  ## Full cleanup (keeps pythons)
	@echo ">> [TODO G6] uv-flush-everything orchestrator (prereqs above)"

uv-nuke: uv-flush-everything  ## NUCLEAR: everything, then prompt for python removal
	@echo ">> [TODO G6] uv-nuke not yet implemented"

uv-lifecycle-test: uv-flush-everything uv-bootstrap uv-test-all  ## flush -> bootstrap -> test-all
	@echo ">> [TODO G6] uv-lifecycle-test orchestrator (prereqs above)"

# ============================================================================
# PIP · INSTALL
# ============================================================================
##@ PIP · Install
installDev: clean  ## Install dev dependencies with pip
	-$(PIP) list --editable --format=freeze | cut -d= -f1 | xargs -r $(PIP) uninstall --break-system-packages -y 2>/dev/null || true
	$(PIP) install --break-system-packages --force-reinstall -r requirements.txt
	$(PIP) install --break-system-packages -e ".[dev]"

editable:  ## Install this package in editable mode (pip install -e .)
	$(PIP) install -e .

refresh:  ## Refresh all pip packages from requirements + editable dev
	$(PIP) install -r requirements.txt
	$(PIP) install --force-reinstall -e ".[dev]"

# ============================================================================
# PIP · TEST
# ============================================================================
##@ PIP · Test
test:  ## Run tests using the current Python environment
	@echo ">> [TODO G4] test not yet implemented"

testInEnvCleanup:  ## Delete the temporary venv ($(VENV))
	@echo ">> [TODO G4] testInEnvCleanup not yet implemented"

testInEnvInstallFromSetup: testInEnvCleanup  ## Create temp venv + install dev deps
	@echo ">> [TODO G4] testInEnvInstallFromSetup not yet implemented"

testInEnvRunPytest:  ## Run pytest inside the temporary venv
	@echo ">> [TODO G4] testInEnvRunPytest not yet implemented"

testInEnv: clean testInEnvInstallFromSetup testInEnvRunPytest testInEnvCleanup  ## Full clean-room test
	@echo ">> [TODO G4] testInEnv orchestrator (prereqs above)"

# ============================================================================
# PIP · BUILD & RELEASE
# ============================================================================
##@ PIP · Build & Release
build:  ## Build sdist+wheel ($(PYTHON) -m build)
	@echo ">> [TODO build] build not yet implemented"

validateBuild: build  ## Build + validate with twine
	@echo ">> [TODO build] validateBuild not yet implemented"

release-test: validateBuild  ## Upload to TestPyPI (user-editable index)
	@echo ">> [TODO release] release-test not yet implemented"

release: validateBuild  ## Upload to PyPI (user-editable index)
	@echo ">> [TODO release] release not yet implemented"

# ============================================================================
# PIP · FLUSH / LIST
# ============================================================================
##@ PIP · Flush / List
nuke:  ## Uninstall ALL pip packages incl. broken editables (skips system)
	@echo ">> [TODO G6] nuke not yet implemented"

list:  ## List pip packages in the current environment
	@echo ">> [TODO G6] list not yet implemented"
