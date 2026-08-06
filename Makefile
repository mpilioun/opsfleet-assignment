CURRENT_DIR:=$(shell pwd)

.DEFAULT_GOAL := help

.PHONY: help
help:
	@echo "Development targets:"
	@echo "  make format                   isort + ruff format"
	@echo "  make compile                   format + ruff check --fix"
	@echo "  make run                       Run src/app/main.py"
	@echo ""
	@echo "Docker image:"
	@echo "  make docker-build              Build opsfleet-assignment image"
	@echo "  make docker-run                Run image in foreground"
	@echo "  make docker-run-detached       Run image detached"
	@echo "  make docker-stop               Stop + remove container"
	@echo "  make docker-clean              docker-stop + remove image"
	@echo ""
	@echo "Local services (pg, pgadmin, litellm):"
	@echo "  make db-up                     docker compose up -d"
	@echo "  make db-down                   docker compose down"
	@echo "  make db-clean                  docker compose down -v (wipes volumes)"
	@echo ""
	@echo "Probes (manual smoke tests against live services):"
	@echo "  make probe-llm                 Send a test chat request through the LiteLLM proxy"

POSTGRES_USER ?= postgres
POSTGRES_PASSWORD ?= postgres
POSTGRES_DB ?= postgres
PGADMIN_DEFAULT_EMAIL ?= admin@admin.com
PGADMIN_DEFAULT_PASSWORD ?= admin
LITELLM_MASTER_KEY ?= sk-litellm-master
LITELLM_SALT_KEY ?= sk-litellm-salt
AZURE_OPENAI_API_KEY ?=
AZURE_OPENAI_ENDPOINT ?=
AZURE_OPENAI_API_VERSION ?= 2025-04-01-preview
AZURE_OPENAI_EMBEDDING_API_VERSION ?= 2024-12-01-preview

.PHONY: format
format:
	uvx isort src
	uvx ruff format src

.PHONY: compile
compile: format
	uvx ruff check src --fix

.PHONY: run
run:
	uv run src/app/main.py

.PHONY: docker-build
docker-build:
	docker build -t opsfleet-assignment:latest .

.PHONY: docker-run
docker-run:
	docker run --rm -p 8000:8000 opsfleet-assignment:latest

.PHONY: docker-run-detached
docker-run-detached:
	docker run -d --name opsfleet-assignment -p 8000:8000 opsfleet-assignment:latest

.PHONY: docker-stop
docker-stop:
	docker stop opsfleet-assignment 2>/dev/null || true
	docker rm opsfleet-assignment 2>/dev/null || true

.PHONY: docker-clean
docker-clean: docker-stop
	docker rmi opsfleet-assignment:latest 2>/dev/null || true

.PHONY: db-up
db-up:
	POSTGRES_USER=$(POSTGRES_USER) POSTGRES_PASSWORD=$(POSTGRES_PASSWORD) POSTGRES_DB=$(POSTGRES_DB) \
	PGADMIN_DEFAULT_EMAIL=$(PGADMIN_DEFAULT_EMAIL) PGADMIN_DEFAULT_PASSWORD=$(PGADMIN_DEFAULT_PASSWORD) \
	LITELLM_MASTER_KEY=$(LITELLM_MASTER_KEY) LITELLM_SALT_KEY=$(LITELLM_SALT_KEY) \
	AZURE_OPENAI_API_KEY=$(AZURE_OPENAI_API_KEY) AZURE_OPENAI_ENDPOINT=$(AZURE_OPENAI_ENDPOINT) \
	AZURE_OPENAI_API_VERSION=$(AZURE_OPENAI_API_VERSION) AZURE_OPENAI_EMBEDDING_API_VERSION=$(AZURE_OPENAI_EMBEDDING_API_VERSION) \
	docker compose up -d

.PHONY: db-down
db-down:
	docker compose down

.PHONY: db-clean
db-clean:
	docker compose down -v

# --- Probes (manual smoke tests against live services) ---

.PHONY: probe-llm
probe-llm:
	uv run python scripts/probe_llm.py
