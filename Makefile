CURRENT_DIR:=$(shell pwd)

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
