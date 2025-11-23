.PHONY: help dev build up down logs seed test clean migrate

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

dev: ## Start development environment
	docker-compose up --build

build: ## Build all containers
	docker-compose build

up: ## Start all services
	docker-compose up -d

down: ## Stop all services
	docker-compose down

logs: ## View logs
	docker-compose logs -f

seed: ## Seed database with initial data
	docker-compose exec backend python scripts/seed_db.py

migrate: ## Run database migrations (optional)
	@echo "Running database migrations..."
	docker-compose exec backend python -c "from app.core.database import init_db; init_db()"

test: ## Run tests
	docker-compose exec backend pytest tests/
	cd frontend && npm test

clean: ## Clean up containers and volumes
	docker-compose down -v
	rm -rf backend/__pycache__ backend/**/__pycache__
	rm -rf frontend/node_modules frontend/dist

install-backend: ## Install backend dependencies locally
	cd backend && pip install -r requirements.txt

install-frontend: ## Install frontend dependencies locally
	cd frontend && npm install

generate: ## Generate new resource (usage: make generate name=ResourceName)
	docker-compose exec backend python scripts/generate_resource.py $(name)
