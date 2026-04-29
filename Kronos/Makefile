.PHONY: help build up down logs restart clean test lint format

help: ## Mostrar esta ayuda
	@echo "Comandos disponibles:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

build: ## Construir la imagen Docker
	docker-compose build

up: ## Levantar el servicio
	docker-compose up -d

down: ## Detener el servicio
	docker-compose down

logs: ## Ver logs del servicio
	docker-compose logs -f kronos-api

restart: ## Reiniciar el servicio
	docker-compose restart

clean: ## Limpiar contenedores, volúmenes e imágenes
	docker-compose down -v
	docker system prune -f

dev: ## Levantar en modo desarrollo (con hot-reload)
	docker-compose -f docker-compose.dev.yml up

dev-down: ## Detener modo desarrollo
	docker-compose -f docker-compose.dev.yml down

test: ## Ejecutar tests
	docker-compose exec kronos-api pytest || pytest

lint: ## Ejecutar linters
	docker-compose exec kronos-api ruff check . || ruff check .
	docker-compose exec kronos-api black --check . || black --check .
	docker-compose exec kronos-api mypy src/ || mypy src/

format: ## Formatear código
	docker-compose exec kronos-api black . || black .
	docker-compose exec kronos-api ruff check --fix . || ruff check --fix .

shell: ## Abrir shell en el contenedor
	docker-compose exec kronos-api bash

verify: ## Verificar importaciones y código
	python scripts/verify_imports.py

test-api: ## Probar endpoints de la API
	python scripts/test_api.py
