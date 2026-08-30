# Команды разработки «ШТАБа». Всё запускается в докере, локально ставить ничего не нужно.
COMPOSE = docker compose -f infra/docker-compose.yml --env-file .env

.DEFAULT_GOAL := help
.PHONY: help up down logs migrate revision seed test lint

help: ## показать список команд
	@grep -hE '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-10s %s\n", $$1, $$2}'

.env:
	@cp .env.example .env
	@echo "Создан .env из .env.example — поправьте его, если нужно."

up: .env ## поднять всё локально
	$(COMPOSE) up --build -d
	@echo "api  → http://localhost:8000/health"
	@echo "web  → http://localhost:5173"
	@echo "minio → http://localhost:9001"

down: ## остановить всё
	$(COMPOSE) down

logs: ## смотреть логи api и web
	$(COMPOSE) logs -f api web

migrate: .env ## накатить миграции
	$(COMPOSE) run --rm api alembic upgrade head

revision: .env ## создать миграцию: make revision M="описание"
	$(COMPOSE) run --rm api alembic revision --autogenerate -m "$(M)"

seed: .env ## залить тестовые данные
	$(COMPOSE) run --rm api python -m app.seed

test: .env ## прогнать тесты: pytest + vitest
	$(COMPOSE) run --rm api pytest
	$(COMPOSE) run --rm web npm run test

lint: .env ## проверить код: ruff + mypy + eslint + tsc
	$(COMPOSE) run --rm api ruff check .
	$(COMPOSE) run --rm api mypy app
	$(COMPOSE) run --rm web npm run lint
