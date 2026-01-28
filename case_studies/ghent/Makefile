.PHONY: help build up down restart logs ps clean rebuild health test stats dev

# Default target
help:
	@echo "Ghent Water System - Docker Management"
	@echo ""
	@echo "Available targets:"
	@echo "  build      - Build all containers"
	@echo "  up         - Start all services"
	@echo "  down       - Stop all services"
	@echo "  restart    - Restart all services"
	@echo "  logs       - View logs (use SERVICE=name for specific service)"
	@echo "  ps         - Show running containers"
	@echo "  clean      - Remove all containers, volumes, and images"
	@echo "  rebuild    - Clean build and start"
	@echo "  health     - Check health status of all services"
	@echo "  test       - Run integration tests"
	@echo "  stats      - View resource usage"
	@echo "  dev        - Start with development profile"
	@echo "  monitoring - Start with monitoring stack"
	@echo ""
	@echo "Service-specific commands:"
	@echo "  make logs SERVICE=orchestrator"
	@echo "  make restart SERVICE=frontend-react"
	@echo "  make rebuild SERVICE=dwp1"

nuke:
	docker stop "$(docker ps -a -q)"
# Build all containers
build:
	docker compose build --parallel

# Build specific service
build-service:
	@if [ -z "$(SERVICE)" ]; then \
		echo "Error: SERVICE variable required. Example: make build-service SERVICE=orchestrator"; \
		exit 1; \
	fi
	docker compose build $(SERVICE)

# Start all services
up:
	docker compose --profile full up -d
	@echo "Services started. Run 'make health' to check status."

# Start with monitoring stack
monitoring:
	docker compose --profile full up -d
	@echo ""
	@echo "=== Services Started ==="
	@echo "Frontend:     http://localhost:3000"
	@echo "Orchestrator: http://localhost:8080"
	@echo "Grafana:      http://localhost:3001 (admin/admin)"
	@echo "Prometheus:   http://localhost:9090"
	@echo "Loki:         http://localhost:3100"

# Start in development mode (backend only)
dev:
	docker compose --profile backend up -d

# Stop all services
down:
	docker compose down

# Restart all services or specific service
restart:
	@if [ -n "$(SERVICE)" ]; then \
		docker compose restart $(SERVICE); \
	else \
		docker compose restart; \
	fi

# View logs (all or specific service)
logs:
	@if [ -n "$(SERVICE)" ]; then \
		docker compose logs -f $(SERVICE); \
	else \
		docker compose logs -f; \
	fi

# Show running containers
ps:
	docker compose ps

# Clean everything
clean:
	docker compose down -v --rmi all --remove-orphans
	docker system prune -f

# Rebuild from scratch
rebuild: clean build up
	@echo "Rebuild complete. Waiting for services to be healthy..."
	@sleep 5
	@make health

# Check health status
health:
	@echo "Checking service health..."
	@docker compose ps --format json 2>/dev/null | jq -r '.[] | "\(.Service): \(.State) - \(.Health // "N/A")"' || docker compose ps

# Run integration tests
test:
	docker compose exec orchestrator pytest tests/integration -v

# View resource usage
stats:
	docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"

# Quick status check
status:
	@echo "=== Service Status ==="
	@docker compose ps
	@echo ""
	@echo "=== Access URLs ==="
	@echo "Frontend:     http://localhost:3000"
	@echo "Orchestrator: http://localhost:8080"
	@echo "Grafana:      http://localhost:3001"
	@echo "Prometheus:   http://localhost:9090"
