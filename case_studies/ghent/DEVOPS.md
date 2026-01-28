# DevOps Infrastructure Guide

This guide explains how to use the enhanced Docker infrastructure for the Ghent Water System.

## Quick Start

### Initial Setup

1. **Create your environment file:**
```bash
cp .env.example .env
```

2. **Start all services with monitoring:**
```bash
make up
# or
./scripts/start-stack.sh full --build
```

3. **Check service health:**
```bash
make health
# or
./scripts/check-health.sh
```

## Available Make Commands

The Makefile provides simplified container management:

```bash
make help        # Show all available commands
make build       # Build all containers
make up          # Start all services (full profile)
make dev         # Start backend services only
make monitoring  # Start all services including monitoring stack
make down        # Stop all services
make restart     # Restart all services
make logs        # View logs from all services
make ps          # Show running containers
make health      # Check health status
make stats       # View resource usage
make test        # Run integration tests
make clean       # Remove all containers and volumes
make rebuild     # Clean rebuild from scratch
```

### Service-Specific Operations

```bash
# View logs for a specific service
make logs SERVICE=orchestrator
make logs SERVICE=dwp1

# Restart a specific service
make restart SERVICE=frontend-react

# Build a specific service
make build-service SERVICE=orchestrator
```

## Docker Compose Profiles

The project uses profiles to manage different deployment scenarios:

### Full Stack (All Services + Monitoring)
```bash
docker compose --profile full up -d
# or
make up
```

Includes:
- Frontend (port 3000)
- Orchestrator (port 8080)
- All 11 model services (ports 8001-8012)
- Loki (log aggregation, port 3100)
- Promtail (log shipping)
- Prometheus (metrics, port 9090)
- Grafana (visualization, port 3001)
- cAdvisor (container metrics, port 8081)

### Backend Only (Development)
```bash
docker compose --profile backend up -d
# or
make dev
```

Includes:
- Orchestrator
- All model services
- No frontend
- No monitoring stack

### Frontend Only
```bash
docker compose --profile frontend up -d
```

### Monitoring Only
```bash
docker compose --profile monitoring up -d
```

### Models Only
```bash
docker compose --profile models up -d
```

## Monitoring & Observability

### Access Dashboards

After starting with `make up` or `make monitoring`:

- **Grafana**: http://localhost:3001
  - Username: `admin`
  - Password: `admin` (change in .env)
  - Pre-configured with Prometheus and Loki datasources

- **Prometheus**: http://localhost:9090
  - Metrics explorer and query interface

- **cAdvisor**: http://localhost:8081
  - Real-time container resource usage

### Centralized Logging with Loki

View logs from all services in Grafana:

1. Open Grafana at http://localhost:3001
2. Go to Explore → Select "Loki" datasource
3. Use LogQL queries:

```logql
# All logs from orchestrator
{container="ghent-orchestrator"}

# All error logs
{job="docker"} |= "ERROR"

# Logs from all model services
{service="model"}

# Logs from a specific model
{model="dwp1"}

# Filter by log level
{container="ghent-orchestrator"} | json | level="ERROR"
```

### Metrics with Prometheus

Query metrics in Prometheus or Grafana:

```promql
# Container CPU usage
rate(container_cpu_usage_seconds_total{name=~"ghent-.*"}[5m]) * 100

# Container memory usage (MB)
container_memory_usage_bytes{name=~"ghent-.*"} / 1024 / 1024

# Service uptime
up{job=~"orchestrator|models"}

# Request rate (if metrics exposed)
rate(http_requests_total[5m])
```

## Resource Limits

All services now have resource limits to prevent runaway containers:

### Model Services
- CPU Limit: 1.0 core
- Memory Limit: 512MB
- CPU Reservation: 0.25 core
- Memory Reservation: 128MB

### Orchestrator
- CPU Limit: 2.0 cores
- Memory Limit: 1GB

### Frontend
- CPU Limit: 0.5 core
- Memory Limit: 256MB

## Log Management

All services use JSON file logging with automatic rotation:
- Max size per file: 10MB
- Max files retained: 3
- Total max storage per service: ~30MB

View logs:
```bash
# All services
make logs

# Specific service
make logs SERVICE=orchestrator

# Last 100 lines
docker compose logs --tail=100 orchestrator

# Follow logs in real-time
docker compose logs -f dwp1
```

## Health Checks

All services have health checks configured:

### Manual Health Check
```bash
make health
# or
./scripts/check-health.sh
```

### Service Dependencies
Services now use health check dependencies:
- Frontend waits for orchestrator to be healthy before starting
- Grafana waits for Prometheus and Loki

### Health Check Endpoints

All services expose `/health` endpoints:
```bash
curl http://localhost:8080/health  # Orchestrator
curl http://localhost:8001/health  # DWP1
curl http://localhost:8002/health  # DWP2
# ... etc for all model services
```

## Environment Variables

Configure services via `.env` file:

```bash
# Environment
ENVIRONMENT=development

# Service Ports
FRONTEND_PORT=3000
ORCHESTRATOR_PORT=8080

# Logging
LOG_LEVEL=INFO

# Grafana Credentials
GRAFANA_USER=admin
GRAFANA_PASSWORD=changeme123

# Model Services
MODEL_SERVICES=dwp1,dwp2,wwtp1,wwtp2,texfin,foodpro,chiptech,pharmagen,brewco,lieve_river,dampoort,muide

# Version
VERSION=latest
```

## Troubleshooting

### Service Won't Start

1. Check logs:
```bash
make logs SERVICE=<service-name>
```

2. Check health:
```bash
make health
```

3. Check resource usage:
```bash
make stats
```

### Out of Memory

If containers are killed due to OOM:

1. Check current memory usage:
```bash
docker stats
```

2. Adjust resource limits in `docker-compose.yml`:
```yaml
deploy:
  resources:
    limits:
      memory: 1G  # Increase as needed
```

### Disk Space Issues

Clean up unused Docker resources:
```bash
# Remove stopped containers and dangling images
docker system prune

# Full cleanup (WARNING: removes all unused resources)
make clean
```

### View Disk Usage
```bash
docker system df
```

## Development Workflow

### Local Development

1. Start backend only:
```bash
make dev
```

2. Make code changes

3. Rebuild specific service:
```bash
docker compose build orchestrator
docker compose restart orchestrator
```

4. View logs:
```bash
make logs SERVICE=orchestrator
```

### Running Tests

```bash
# Integration tests
make test

# Unit tests (inside container)
docker compose exec orchestrator pytest tests/unit -v
```

## Production Deployment

For production environments:

1. Update `.env` with production values:
```bash
ENVIRONMENT=production
LOG_LEVEL=WARNING
GRAFANA_PASSWORD=<strong-password>
```

2. Build with production target:
```bash
FRONTEND_TARGET=production docker compose --profile full build
```

3. Start services:
```bash
docker compose --profile full up -d
```

4. Set up backups for volumes:
   - `prometheus-data`
   - `grafana-data`
   - `loki-data`

## Advanced Usage

### Scaling Model Services

Scale a specific model service to multiple instances:
```bash
docker compose up -d --scale dwp1=3
```

### Custom Profiles

Start specific combinations:
```bash
# Backend + monitoring (no frontend)
docker compose --profile backend --profile monitoring up -d
```

### Export Logs

Export logs for analysis:
```bash
docker compose logs --no-color > all-logs.txt
docker compose logs orchestrator --no-color > orchestrator-logs.txt
```

### Backup Grafana Dashboards

```bash
docker exec ghent-grafana grafana-cli admin export-dashboard > backup.json
```

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    Docker Network                       │
│  (ghent-water-network)                                 │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Frontend (React/Nginx)                                │
│  └─> Orchestrator                                      │
│       ├─> Model: DWP1                                  │
│       ├─> Model: DWP2                                  │
│       ├─> Model: WWTP1                                 │
│       ├─> Model: WWTP2                                 │
│       ├─> Model: TexFin                                │
│       ├─> Model: FoodPro                               │
│       ├─> Model: ChipTech                              │
│       ├─> Model: PharmaGen                             │
│       ├─> Model: BrewCo                                │
│       ├─> Model: Lieve River                           │
│       ├─> Model: Dampoort                              │
│       └─> Model: Muide                                 │
│                                                         │
│  ┌──────────────────────────────────────┐              │
│  │   Observability Stack                │              │
│  ├──────────────────────────────────────┤              │
│  │  Promtail (Log Collector)            │              │
│  │      └─> Loki (Log Storage)          │              │
│  │                                      │              │
│  │  cAdvisor (Container Metrics)        │              │
│  │      └─> Prometheus (Metrics)        │              │
│  │                                      │              │
│  │  Grafana (Visualization)             │              │
│  │      ├─> Loki                        │              │
│  │      └─> Prometheus                  │              │
│  └──────────────────────────────────────┘              │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Support

For issues or questions:
1. Check logs: `make logs SERVICE=<service-name>`
2. Check health: `make health`
3. Check resource usage: `make stats`
4. Review this documentation
5. Check Grafana dashboards for insights
