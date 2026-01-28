# DevOps Quick Start Guide

## What's New

Your Ghent Water System now has enterprise-grade DevOps infrastructure!

### Key Improvements

✅ **Simplified Management** - Use `make` commands instead of long docker compose commands
✅ **Centralized Logging** - View logs from all 13 services in one place with Loki
✅ **Real-time Monitoring** - Grafana dashboards showing CPU, memory, network usage
✅ **Resource Limits** - Prevent runaway containers from consuming all resources
✅ **Health Checks** - Automated service health monitoring
✅ **Environment Profiles** - Easily start different combinations of services

## Quick Start (3 Minutes)

### 1. Start Everything

```bash
make up
```

This starts:
- All 11 model services (ports 8001-8012)
- Orchestrator (port 8080)
- Frontend (port 3000)
- Grafana (port 3001)
- Prometheus (port 9090)
- Loki (port 3100)

### 2. Check Health

```bash
make health
```

### 3. Access Dashboards

Open in your browser:
- **Application**: http://localhost:3000
- **Grafana Monitoring**: http://localhost:3001 (admin/admin)

## Common Commands

```bash
# View all logs (live)
make logs

# View logs from specific service
make logs SERVICE=orchestrator
make logs SERVICE=dwp1

# Check service status
make ps

# Stop everything
make down

# Restart everything
make restart

# View resource usage
make stats

# Get help
make help
```

## Development Workflow

### Backend Development (Without Frontend)

```bash
make dev
```

### View Logs While Developing

```bash
# Terminal 1: Start services
make dev

# Terminal 2: Watch logs
make logs SERVICE=orchestrator
```

### Rebuild After Code Changes

```bash
docker compose build orchestrator
docker compose restart orchestrator
```

## Monitoring & Debugging

### View All Logs in Grafana

1. Open http://localhost:3001
2. Login (admin/admin)
3. Go to **Explore** → Select **Loki**
4. Try these queries:

```logql
# All orchestrator logs
{container="ghent-orchestrator"}

# All error logs across all services
{job="docker"} |= "ERROR"

# Logs from all model services
{service="model"}

# Specific model logs
{model="dwp1"}
```

### View Metrics in Grafana

1. Go to **Dashboards** → **Ghent Water System Overview**
2. See:
   - Service health status
   - CPU usage per container
   - Memory usage per container
   - Error logs
   - Network I/O

## Troubleshooting

### Service won't start?

```bash
# Check what's wrong
make logs SERVICE=<service-name>

# Check health
make health

# Rebuild from scratch
make rebuild
```

### Out of disk space?

```bash
# Clean up
make clean

# Check disk usage
docker system df
```

### Services running slow?

```bash
# Check resource usage
make stats
```

## File Structure

```
case_studies/ghent/
├── Makefile                          # Simplified commands
├── docker-compose.yml                # Enhanced with monitoring
├── .env                              # Environment configuration
├── .env.example                      # Environment template
├── DEVOPS.md                         # Full documentation
├── DEVOPS_QUICKSTART.md             # This file
├── scripts/
│   ├── start-stack.sh               # Startup script
│   └── check-health.sh              # Health check script
└── monitoring/
    ├── loki-config.yaml             # Log aggregation config
    ├── promtail-config.yaml         # Log collection config
    ├── prometheus.yml               # Metrics config
    └── grafana/
        ├── datasources/             # Pre-configured datasources
        │   └── datasources.yml
        └── dashboards/              # Pre-built dashboards
            ├── dashboard-provider.yml
            └── ghent-water-overview.json
```

## What You Get

### Before
```bash
docker compose up -d
docker compose logs -f orchestrator
docker compose ps
docker compose down
```

### After
```bash
make up
make logs SERVICE=orchestrator
make ps
make down
```

Plus:
- 📊 Real-time dashboards
- 🔍 Centralized log search
- 🚨 Health monitoring
- 💾 Resource limits
- 🎯 Service profiles

## Next Steps

1. **Customize Grafana Dashboards** - Add widgets for your specific metrics
2. **Set up Alerts** - Configure Prometheus alerts for critical issues
3. **Adjust Resource Limits** - Fine-tune CPU/memory based on your workload
4. **Create Custom Profiles** - Define your own service combinations

## Learn More

- Full documentation: [DEVOPS.md](./DEVOPS.md)
- Make commands: `make help`
- Docker profiles: `docker compose --help`

## Support

Run into issues?
1. Check logs: `make logs SERVICE=<name>`
2. Check health: `make health`
3. View dashboards: http://localhost:3001
4. Read [DEVOPS.md](./DEVOPS.md)
