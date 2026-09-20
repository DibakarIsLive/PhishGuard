.DEFAULT_GOAL := help

.PHONY: help install dev build preview test-api health status clean clean-build clean-cache deps-check deps-update audit doctor lint format bundle-size open mi md mb mp mt mhealth mstatus mdoctor mopen mcache mclean-build mc mdeps-check mdeps-update maudit mlint mformat mbundle

NPM ?= npm
PORT ?= 5173
API_URL ?= http://127.0.0.1:8000

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
TITLE  := $(BOLD)$(MAGENTA)UI$(RESET)

help:
	@printf '\n$(MAGENTA)╭────────────────────────────────────────────────────────────╮$(RESET)\n'
	@printf '$(MAGENTA)│  ⚛️  $(TITLE)  ·  React + Vite launch pad                         │$(RESET)\n'
	@printf '$(MAGENTA)╰────────────────────────────────────────────────────────────╯$(RESET)\n'
	@printf '\n$(BOLD)Quick start$(RESET)\n'
	@printf '  $(GREEN)make install$(RESET)       Install npm dependencies\n'
	@printf '  $(GREEN)make dev$(RESET)           Start Vite\n'
	@printf '  $(GREEN)make doctor$(RESET)        Inspect UI readiness\n'
	@printf '\n$(BOLD)Develop$(RESET)\n'
	@printf '  $(CYAN)dev$(RESET)                Start the Vite development server\n'
	@printf '  $(CYAN)build$(RESET)              Create a production build\n'
	@printf '  $(CYAN)preview$(RESET)            Preview the production build\n'
	@printf '  $(CYAN)open$(RESET)               Open the UI in the default browser\n'
	@printf '\n$(BOLD)Quality & inspect$(RESET)\n'
	@printf '  $(CYAN)test-api$(RESET)          Check the API health endpoint\n'
	@printf '  $(CYAN)health$(RESET)             Show app/API availability\n'
	@printf '  $(CYAN)bundle-size$(RESET)        Show generated bundle sizes\n'
	@printf '  $(CYAN)lint$(RESET)               Run npm lint when configured\n'
	@printf '  $(CYAN)format$(RESET)             Show formatting hook guidance\n'
	@printf '\n$(BOLD)Maintain$(RESET)\n'
	@printf '  $(CYAN)deps-check$(RESET)         List outdated packages\n'
	@printf '  $(CYAN)deps-update$(RESET)        Update compatible packages\n'
	@printf '  $(CYAN)audit$(RESET)             Run npm security audit\n'
	@printf '  $(CYAN)clean$(RESET)              Remove dependencies and generated files\n\n'
	@printf '$(BOLD)Shortcuts$(RESET)\n'
	@printf '  $(CYAN)mi$(RESET)                = make install\n'
	@printf '  $(CYAN)md$(RESET)                = make dev\n'
	@printf '  $(CYAN)mb$(RESET)                = make build\n'
	@printf '  $(CYAN)mp$(RESET)                = make preview\n'
	@printf '  $(CYAN)mt$(RESET)                = make test-api\n'
	@printf '  $(CYAN)mhealth$(RESET)           = make health\n'
	@printf '  $(CYAN)mstatus$(RESET)           = make status\n'
	@printf '  $(CYAN)mdoctor$(RESET)           = make doctor\n'
	@printf '  $(CYAN)mopen$(RESET)             = make open\n'
	@printf '  $(CYAN)mcache$(RESET)            = make clean-cache\n'
	@printf '  $(CYAN)mclean-build$(RESET)       = make clean-build\n'
	@printf '  $(CYAN)mc$(RESET)                = make clean\n'
	@printf '  $(CYAN)mdeps-check$(RESET)        = make deps-check\n'
	@printf '  $(CYAN)mdeps-update$(RESET)       = make deps-update\n'
	@printf '  $(CYAN)maudit$(RESET)             = make audit\n'
	@printf '  $(CYAN)mlint$(RESET)              = make lint\n'
	@printf '  $(CYAN)mformat$(RESET)            = make format\n'
	@printf '  $(CYAN)mbundle$(RESET)            = make bundle-size\n\n'

install:
	@printf '$(MAGENTA)✦ Installing UI dependencies...$(RESET)\n'
	@$(NPM) install --no-audit --no-fund
	@printf '$(GREEN)✔ UI dependencies installed.$(RESET)\n'

dev:
	@if [ ! -d node_modules ]; then printf '$(RED)✘ node_modules is missing; run make install first.$(RESET)\n'; exit 1; fi
	@printf '\n$(BOLD)$(MAGENTA)⚛ Vite development server$(RESET)  →  http://localhost:$(PORT)/\n'
	@printf '$(DIM)API expected at $(API_URL)/api/$(RESET)\n\n'
	@$(NPM) run dev -- --host 127.0.0.1 --port $(PORT) --open http://localhost:$(PORT)/

build:
	@printf '$(MAGENTA)✦ Building the React UI...$(RESET)\n'
	@$(NPM) run build
	@test -d dist
	@printf '$(GREEN)✔ UI build completed in dist/.$(RESET)\n'

preview:
	@if [ ! -d dist ]; then printf '$(RED)✘ dist/ is missing; run make build first.$(RESET)\n'; exit 1; fi
	@printf '$(CYAN)▸ Preview: http://localhost:$(PORT)/$(RESET)\n'
	@$(NPM) run preview -- --host 127.0.0.1 --port $(PORT)

test-api:
	@command -v curl >/dev/null 2>&1 || { printf '$(RED)✘ curl is required.$(RESET)\n'; exit 1; }
	@printf '$(CYAN)♥ Pinging API health endpoint...$(RESET)\n'
	@curl --fail --silent --show-error $(API_URL)/api/health/ | python3 -m json.tool

health:
	@printf '\n$(BOLD)$(MAGENTA)💓 UI health$(RESET)\n'
	@printf '  Dependencies: '; test -d node_modules && printf '$(GREEN)ready$(RESET)\n' || printf '$(YELLOW)missing$(RESET)\n'
	@printf '  Build:        '; test -d dist && printf '$(GREEN)present$(RESET)\n' || printf '$(DIM)not created$(RESET)\n'
	@printf '  API:  '; curl --silent --fail $(API_URL)/api/health/ >/dev/null 2>&1 && printf '$(GREEN)reachable$(RESET)\n' || printf '$(YELLOW)unavailable$(RESET)\n'

status: health

doctor:
	@printf '\n$(BOLD)$(MAGENTA)🩺 UI doctor$(RESET)\n'
	@printf '  Node:       '; command -v node >/dev/null 2>&1 && printf '$(GREEN)✔ %s$(RESET)\n' "$$(node --version)" || printf '$(RED)✘ missing$(RESET)\n'
	@printf '  npm:        '; command -v npm >/dev/null 2>&1 && printf '$(GREEN)✔ %s$(RESET)\n' "$$(npm --version)" || printf '$(RED)✘ missing$(RESET)\n'
	@printf '  node_modules:'; test -d node_modules && printf ' $(GREEN)✔ ready$(RESET)\n' || printf ' $(YELLOW)○ run make install$(RESET)\n'
	@printf '  package lock:'; test -f package-lock.json && printf ' $(GREEN)✔ present$(RESET)\n' || printf ' $(YELLOW)○ missing$(RESET)\n'
	@printf '  API:        '; curl --silent --fail $(API_URL)/api/health/ >/dev/null 2>&1 && printf '$(GREEN)✔ reachable$(RESET)\n' || printf '$(DIM)○ start the API first$(RESET)\n'

bundle-size:
	@if [ ! -d dist ]; then printf '$(YELLOW)○ dist/ missing; run make build first.$(RESET)\n'; exit 1; fi
	@du -sh dist dist/assets 2>/dev/null || true
	@find dist/assets -type f -maxdepth 1 -print 2>/dev/null | sort

open:
	@if [ "$$(uname)" = "Darwin" ]; then open "http://localhost:$(PORT)"; else printf '$(CYAN)Open http://localhost:$(PORT) in your browser.$(RESET)\n'; fi

lint:
	@if $(NPM) run | grep -qE '^  lint'; then $(NPM) run lint; else printf '$(YELLOW)○ No lint script is configured yet.$(RESET)\n'; fi

format:
	@printf '$(YELLOW)Formatting is intentionally non-mutating here.$(RESET)\n'
	@printf '  Add Prettier later, then use: npx prettier --write src\n'

clean-build:
	@rm -rf dist .vite
	@printf '$(GREEN)✔ UI build files removed.$(RESET)\n'

clean-cache:
	@rm -rf .vite node_modules/.vite
	@printf '$(GREEN)✔ UI Vite caches removed.$(RESET)\n'

clean: clean-build clean-cache
	@rm -rf node_modules package-lock.json
		@printf '$(GREEN)✔ UI dependencies and lockfile removed.$(RESET)\n'

# Short aliases keep common UI commands fast without duplicating recipes.
mi: install
md: dev
mb: build
mp: preview
mt: test-api
mhealth: health
mstatus: status
mdoctor: doctor
mopen: open
mcache: clean-cache
mclean-build: clean-build
mc: clean
mdeps-check: deps-check
mdeps-update: deps-update
maudit: audit
mlint: lint
mformat: format
mbundle: bundle-size

deps-check:
	@$(NPM) outdated || test $$? -eq 1

deps-update:
	@$(NPM) update

audit:
	@$(NPM) audit
