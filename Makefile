.DEFAULT_GOAL := help

.PHONY: help install setup-env dev dev-tabs dev-single api-only web-only api ui build check test test-features test-api doctor health status clean-cache clean stop ci

API_PORT ?= 8000
WEB_PORT ?= 5173
FORCE ?= 0

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

PROJECT := $(BOLD)$(CYAN)PHISHGUARD$(RESET)

# Small, dependency-free terminal helpers.
SHELL := /bin/sh

help:
	@printf '\n$(CYAN)╭────────────────────────────────────────────────────────────╮$(RESET)\n'
	@printf '$(CYAN)│  🛡️  $(PROJECT)  ·  full-stack command center               │$(RESET)\n'
	@printf '$(CYAN)╰────────────────────────────────────────────────────────────╯$(RESET)\n'
	@printf '\n$(BOLD)Quick start$(RESET)\n'
	@printf '  $(GREEN)make install$(RESET)       Prepare API and web\n'
	@printf '  $(GREEN)make dev$(RESET)           Launch API + web in Terminal tabs\n'
	@printf '  $(GREEN)make doctor$(RESET)        Inspect the local development setup\n'
	@printf '\n$(BOLD)Run$(RESET)\n'
	@printf '  $(CYAN)dev$(RESET)               Start API + web in tabs\n'
	@printf '  $(CYAN)dev-single$(RESET)        Start both services in one terminal\n'
	@printf '  $(CYAN)api-only$(RESET)         Start only the Django API\n'
	@printf '  $(CYAN)web-only$(RESET)         Start only the React web app\n'
	@printf '  $(CYAN)api$(RESET)               Shortcut for api-only\n'
	@printf '  $(CYAN)ui$(RESET)                Shortcut for web-only\n'
	@printf '\n$(BOLD)Quality$(RESET)\n'
	@printf '  $(CYAN)build$(RESET)             Build the web\n'
	@printf '  $(CYAN)check$(RESET)             Run API/Django checks\n'
	@printf '  $(CYAN)test$(RESET)              Run all API tests\n'
	@printf '  $(CYAN)test-features$(RESET)    Test URL feature extraction\n'
	@printf '  $(CYAN)test-api$(RESET)          Test API/service behavior\n'
	@printf '  $(CYAN)ci$(RESET)                Run checks, tests, and web build\n'
	@printf '\n$(BOLD)Inspect & clean$(RESET)\n'
	@printf '  $(CYAN)health$(RESET)            Check API availability\n'
	@printf '  $(CYAN)status$(RESET)            Show API/web status\n'
	@printf '  $(CYAN)clean-cache$(RESET)      Remove generated caches\n'
	@printf '  $(CYAN)clean$(RESET)             Remove local dependencies and caches\n'
	@printf '  $(CYAN)stop$(RESET)              Stop local development servers\n\n'

install:
	@printf '\n$(MAGENTA)✦$(RESET) $(BOLD)Bootstrapping PhishGuard$(RESET)\n'
	@$(MAKE) -C api install
	@$(MAKE) -C web install
	@printf '$(GREEN)✔ All dependencies are ready. Happy building! 🚀$(RESET)\n\n'

setup-env:
	@$(MAKE) -C api setup-env

dev: dev-tabs

dev-tabs:
	@if [ "$$(uname)" = "Darwin" ]; then \
		printf '$(CYAN)✦ Opening API and web in separate Terminal windows...$(RESET)\n'; \
		osascript -e 'tell application "Terminal" to do script "cd \"$(CURDIR)/api\" && make dev FORCE=$(FORCE)"' >/dev/null; \
		osascript -e 'tell application "Terminal" to do script "cd \"$(CURDIR)/web\" && make dev PORT=$(WEB_PORT)"' >/dev/null; \
		printf '$(GREEN)✔ Development cockpit launched.$(RESET)\n'; \
	else \
		printf '$(YELLOW)Tabs are macOS-specific; switching to one-terminal mode.$(RESET)\n'; \
		$(MAKE) dev-single; \
	fi

dev-single:
	@printf '$(MAGENTA)✦ Starting API + web — press Ctrl-C to stop$(RESET)\n'
	@trap 'kill 0' INT TERM; (cd api && $(MAKE) dev FORCE=$(FORCE) PORT=$(API_PORT)) & (cd web && $(MAKE) dev PORT=$(WEB_PORT)) & wait

api-only api:
	@$(MAKE) -C api dev FORCE=$(FORCE) PORT=$(API_PORT)

web-only ui:
	@$(MAKE) -C web dev PORT=$(WEB_PORT)

build:
	@$(MAKE) -C web build

check:
	@$(MAKE) -C api check

test:
	@$(MAKE) -C api test

test-features:
	@$(MAKE) -C api test-features

test-api:
	@$(MAKE) -C api test-api

ci:
	@printf '\n$(MAGENTA)╭─ CI runway ────────────────────────────────────────────────╮$(RESET)\n'
	@$(MAKE) check
	@$(MAKE) test
	@$(MAKE) build
	@printf '$(GREEN)╰─ ✔ CI runway clear ────────────────────────────────────────╯$(RESET)\n\n'

doctor:
	@printf '\n$(BOLD)$(CYAN)🩺 PhishGuard environment doctor$(RESET)\n'
	@printf '  Python:    '; command -v python3 >/dev/null 2>&1 && printf '$(GREEN)✔ available$(RESET)\n' || printf '$(RED)✘ missing$(RESET)\n'
	@printf '  Node:      '; command -v node >/dev/null 2>&1 && printf '$(GREEN)✔ %s$(RESET)\n' "$$(node --version)" || printf '$(RED)✘ missing$(RESET)\n'
	@printf '  npm:       '; command -v npm >/dev/null 2>&1 && printf '$(GREEN)✔ %s$(RESET)\n' "$$(npm --version)" || printf '$(RED)✘ missing$(RESET)\n'
	@printf '  MongoDB:   '; lsof -ti:27017 >/dev/null 2>&1 && printf '$(GREEN)✔ detected$(RESET)\n' || printf '$(RED)✘ required / not detected$(RESET)\n'
	@printf '  .env:      '; test -f api/.env && printf '$(GREEN)✔ present$(RESET)\n' || printf '$(YELLOW)○ missing — run make setup-env$(RESET)\n'

health:
	@$(MAKE) -C web health

status:
	@printf '\n$(BOLD)$(CYAN)📡 Service status$(RESET)\n'
	@$(MAKE) -C api status
	@$(MAKE) -C web status

clean-cache:
	@$(MAKE) -C api clean-cache
	@$(MAKE) -C web clean-cache

clean:
	@printf '$(YELLOW)⚠ Removes api/.venv, web/node_modules, and package-lock.json.$(RESET)\n'
	@$(MAKE) -C api clean
	@$(MAKE) -C web clean

stop:
	@pkill -f "manage.py runserver" 2>/dev/null || true
	@pkill -f "vite" 2>/dev/null || true
	@lsof -ti:$(API_PORT) | xargs kill 2>/dev/null || true
	@lsof -ti:$(WEB_PORT) | xargs kill 2>/dev/null || true
	@printf '$(GREEN)✔ Development servers stopped. Terminal is calm again.$(RESET)\n'
