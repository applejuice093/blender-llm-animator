# Developer shortcuts. Run `make help` for the list.
# Uses backend/venv (same location as scripts/setup_env.sh / setup_env.ps1).

PYTHON ?= python3
VENV   := backend/venv
VPY    := $(VENV)/bin/python
PORT   ?= 8000

.DEFAULT_GOAL := help
.PHONY: help venv install install-backend install-dev install-finetune install-frontend \
        test run-api run-frontend build-frontend lint-frontend clean

help: ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

$(VPY):
	$(PYTHON) -m venv $(VENV)
	$(VPY) -m pip install --upgrade pip

venv: $(VPY) ## Create backend/venv if missing

install: install-dev install-frontend ## Install backend (with dev tools) and frontend

install-backend: $(VPY) ## Install core API requirements
	$(VPY) -m pip install -r backend/requirements.txt

install-dev: $(VPY) ## Install API + test requirements
	$(VPY) -m pip install -r backend/requirements-dev.txt

install-finetune: $(VPY) ## Install the Unsloth fine-tuning stack (CUDA GPU required)
	$(VPY) -m pip install -r backend/requirements-finetune.txt

install-frontend: ## npm ci in frontend/
	cd frontend && npm ci

test: ## Run the backend pytest suite
	cd backend && ../$(VPY) -m pytest

run-api: ## Start FastAPI with reload (PORT=8000 by default)
	cd backend && ../$(VPY) -m uvicorn main:app --reload --port $(PORT)

run-frontend: ## Start the Vite dev server (http://localhost:5173)
	cd frontend && npm run dev

build-frontend: ## Type-check and build the frontend
	cd frontend && npm run build

lint-frontend: ## Run oxlint on the frontend
	cd frontend && npm run lint

clean: ## Remove caches and build output (keeps venv, datasets and Chroma DB)
	find backend -name __pycache__ -type d -prune -exec rm -rf {} +
	rm -rf backend/.pytest_cache frontend/dist
