.PHONY: help build run run-prod stop logs test clean lint security-scan deploy-staging deploy-production

build:
	@echo "🔨 Building Docker image..."
	docker build -t weather-service:latest .

run: build
	@echo "🚀 Starting development container..."
	docker run -d --name weather-service \
		-p 8000:8000 \
		-v $(PWD)/data:/app/data \
		weather-service:latest

test:
	@echo "Running tests with coverage..."
	python -m pytest --cov=. --cov-report=term-missing --cov-report=html --cov-report=xml

health-check:
	@echo "🏥 Checking service health..."
	@if curl -f http://localhost:8000/healthz >/dev/null 2>&1; then \
		echo "Service is healthy"; \
	else \
		echo "Service is not responding"; \
	fi

dev: setup-dev run
	@echo "🚀 Development environment started!"
	@echo "Service available at: http://localhost:8000"
	@echo "API docs at: http://localhost:8000/docs"
	@echo "Health check at: http://localhost:8000/healthz"
