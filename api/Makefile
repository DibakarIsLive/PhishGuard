.DEFAULT_GOAL := help

.PHONY: help install setup-env dev runserver check test test-features test-api shell status clean clean-cache freeze outdated security-check format compile urls ping train-info

PYTHON ?= python3
VENV ?= .venv
VENV_BIN := $(VENV)/bin
PY := $(VENV_BIN)/python
PIP := $(VENV_BIN)/pip
MANAGE := $(PY) manage.py
PORT ?= 8000
HOST ?= 127.0.0.1
FORCE ?= 0

# `FORCE=1` adds the same explicit override accepted by manage.py.
RUNSERVER_FORCE := $(if $(filter 1 true yes on,$(FORCE)),--force,)

# ─────────────────────────────────────────────────────────────────────────────
# Terminal palette
# ─────────────────────────────────────────────────────────────────────────────
RESET  := \033[0m
BOLD   := \033[1m
DIM    := \033[2m
CYAN   := \033[36m
BLUE   := \033[34m
GREEN  := \033[32m
YELLOW := \033[33m
RED    := \033[31m
MAGENTA:= \033[35m
WHITE  := \033[97m
TITLE  := $(BOLD)$(BLUE)API$(RESET)

help:
	@printf '\n$(BLUE)╭────────────────────────────────────────────────────────────╮$(RESET)\n'
	@printf '$(BLUE)│  🐍  $(TITLE)  ·  Django + MongoEngine control room             │$(RESET)\n'
	@printf '$(BLUE)╰────────────────────────────────────────────────────────────╯$(RESET)\n'
	@printf '\n$(BOLD)Quick start$(RESET)\n'
	@printf '  $(GREEN)make install$(RESET)       Create .venv and install dependencies\n'
	@printf '  $(GREEN)make dev$(RESET)           Start the Django API\n'
	@printf '  $(GREEN)make doctor$(RESET)        Inspect API readiness\n'
	@printf '\n$(BOLD)Develop$(RESET)\n'
	@printf '  $(CYAN)dev$(RESET) / $(CYAN)runserver$(RESET)  Start Django\n'
	@printf '  $(CYAN)shell$(RESET)             Open a Django shell\n'
	@printf '  $(CYAN)urls$(RESET)              Print registered URLs\n'
	@printf '  $(CYAN)ping$(RESET)              Call the local health endpoint\n'
	@printf '\n$(BOLD)Quality$(RESET)\n'
	@printf '  $(CYAN)check$(RESET)             Run Django system checks\n'
	@printf '  $(CYAN)test$(RESET)              Run the complete pytest suite\n'
	@printf '  $(CYAN)test-features$(RESET)    Test URL features\n'
	@printf '  $(CYAN)test-api$(RESET)          Test scan service and API behavior\n'
	@printf '  $(CYAN)compile$(RESET)           Compile-check Python files\n'
	@printf '\n$(BOLD)Maintain$(RESET)\n'
	@printf '  $(CYAN)format$(RESET)            Show formatting hook guidance\n'
	@printf '  $(CYAN)freeze$(RESET)            Export installed packages\n'
	@printf '  $(CYAN)outdated$(RESET)          List outdated packages\n'
	@printf '  $(CYAN)security-check$(RESET)   Validate installed dependencies\n'
	@printf '  $(CYAN)clean$(RESET)             Remove caches and .venv\n\n'

$(PY):
	@printf '$(MAGENTA)✦ Creating API virtual environment...$(RESET)\n'
	@command -v $(PYTHON) >/dev/null 2>&1 || { printf '$(RED)✘ Python not found: $(PYTHON)$(RESET)\n'; exit 1; }
	$(PYTHON) -m venv $(VENV)
	@$(PIP) install --upgrade pip --disable-pip-version-check >/dev/null
	@printf '$(GREEN)✔ Virtual environment ready.$(RESET)\n'

install: $(PY) setup-env
	@printf '$(MAGENTA)✦ Installing API dependencies...$(RESET)\n'
	@$(PIP) install -r requirements.txt --disable-pip-version-check
	@printf '$(GREEN)✔ API dependencies installed.$(RESET)\n'

setup-env:
	@if [ ! -f .env ] && [ -f .env.example ]; then cp .env.example .env; printf '$(GREEN)✔ Created .env from .env.example$(RESET)\n'; else printf '$(DIM)· Environment file already configured.$(RESET)\n'; fi

runserver: dev

dev: $(PY)
	@printf '\n$(BOLD)$(BLUE)🚀 Django API$(RESET)  →  http://$(HOST):$(PORT)/api/\n'
	@printf '$(DIM)MongoDB is required. Use FORCE=1 only for an explicit startup bypass.$(RESET)\n'
	@printf '$(DIM)Press Ctrl-C to stop the server.$(RESET)\n\n'
	@$(MANAGE) runserver $(HOST):$(PORT) $(RUNSERVER_FORCE)

check: $(PY)
	@printf '$(MAGENTA)✦ Running Django checks...$(RESET)\n'
	@$(MANAGE) check
	@printf '$(GREEN)✔ Django checks passed.$(RESET)\n'

test: $(PY)
	@printf '$(MAGENTA)✦ Running API tests...$(RESET)\n'
	@$(PY) -m pytest -q
	@printf '$(GREEN)✔ API tests passed.$(RESET)\n'

test-features: $(PY)
	@$(PY) -m pytest -q tests/test_feature_extractor.py

test-api: $(PY)
	@$(PY) -m pytest -q tests/test_scan_service.py

shell: $(PY)
	@$(MANAGE) shell

urls: $(PY)
	@$(MANAGE) show_urls 2>/dev/null || $(MANAGE) check

ping:
	@printf '$(CYAN)♥ Pinging Django health endpoint...$(RESET)\n'
	@curl --fail --silent --show-error http://$(HOST):$(PORT)/api/health/ | python3 -m json.tool

compile:
	@printf '$(MAGENTA)✦ Compile-checking Python files...$(RESET)\n'
	@$(PYTHON) -m compileall -q .
	@printf '$(GREEN)✔ Python compilation passed.$(RESET)\n'

format:
	@printf '$(YELLOW)Formatting is intentionally non-mutating here.$(RESET)\n'
	@printf '  Install Ruff when desired, then use: ruff format . && ruff check .\n'

doctor:
	@printf '\n$(BOLD)$(BLUE)🩺 API doctor$(RESET)\n'
	@printf '  Python:  '; command -v $(PYTHON) >/dev/null 2>&1 && printf '$(GREEN)✔ %s$(RESET)\n' "$$($(PYTHON) --version 2>&1)" || printf '$(RED)✘ missing$(RESET)\n'
	@printf '  Venv:    '; test -x $(PY) && printf '$(GREEN)✔ ready$(RESET)\n' || printf '$(YELLOW)○ missing — run make install$(RESET)\n'
	@printf '  Django:  '; test -x $(PY) && $(PY) -c 'import django' 2>/dev/null && printf '$(GREEN)✔ installed$(RESET)\n' || printf '$(YELLOW)○ unavailable$(RESET)\n'
	@printf '  MongoDB: '; lsof -ti:27017 >/dev/null 2>&1 && printf '$(GREEN)✔ detected$(RESET)\n' || printf '$(RED)✘ required / not detected$(RESET)\n'

	@printf '  Model:   '; test -f ml-models/phishguard_model.joblib && printf '$(GREEN)✔ present$(RESET)\n' || printf '$(DIM)○ optional / heuristic fallback$(RESET)\n'

status:
	@printf '\n$(BOLD)$(BLUE)📡 API status$(RESET)\n'
	@printf '  Virtual environment: '; test -x $(PY) && printf '$(GREEN)ready$(RESET)\n' || printf '$(YELLOW)missing$(RESET)\n'
	@printf '  Django port $(PORT):   '; lsof -ti:$(PORT) >/dev/null 2>&1 && printf '$(GREEN)running$(RESET)\n' || printf '$(DIM)stopped$(RESET)\n'
	@printf '  MongoDB port 27017:   '; lsof -ti:27017 >/dev/null 2>&1 && printf '$(GREEN)running$(RESET)\n' || printf '$(RED)required / stopped$(RESET)\n'

	@printf '  Model file:           '; test -f ml-models/phishguard_model.joblib && printf '$(GREEN)present$(RESET)\n' || printf '$(DIM)not present$(RESET)\n'

clean-cache:
	@find . -type d -name __pycache__ -prune -exec rm -rf {} +
	@find . -type f -name '*.pyc' -delete
	@rm -rf .pytest_cache .coverage htmlcov
	@printf '$(GREEN)✔ API caches removed.$(RESET)\n'

clean: clean-cache
	@rm -rf $(VENV)
	@printf '$(GREEN)✔ API virtual environment removed.$(RESET)\n'

freeze: $(PY)
	@$(PIP) freeze > requirements-freeze.txt
	@printf '$(GREEN)✔ Wrote requirements-freeze.txt$(RESET)\n'

outdated: $(PY)
	@$(PIP) list --outdated

security-check: $(PY)
	@$(PIP) check
	@printf '$(GREEN)✔ Python dependency check passed.$(RESET)\n'
