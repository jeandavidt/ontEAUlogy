#!/bin/bash

echo "=== Ghent Water System - Health Check ==="

# Check each service
services=(
    "frontend-react:3000"
    "orchestrator:8080:/health"
    "dwp1:8001:/health"
    "dwp2:8002:/health"
    "wwtp1:8003:/health"
    "wwtp2:8004:/health"
    "texfin:8005:/health"
    "foodpro:8006:/health"
    "chiptech:8007:/health"
    "pharmagen:8008:/health"
    "brewco:8009:/health"
    "lieve_river:8010:/health"
    "dampoort:8011:/health"
    "muide:8012:/health"
)

all_healthy=true

for service_info in "${services[@]}"; do
    IFS=':' read -r name port path <<< "$service_info"

    # Default path if not specified
    if [ -z "$path" ]; then
        path="/"
    fi

    # Try to reach the health endpoint
    if curl -sf "http://localhost:$port$path" > /dev/null 2>&1; then
        echo "✓ $name - HEALTHY"
    else
        echo "✗ $name - UNHEALTHY"
        all_healthy=false
    fi
done

# Check monitoring services
echo ""
echo "=== Monitoring Services ==="
if curl -sf "http://localhost:9090/-/healthy" > /dev/null 2>&1; then
    echo "✓ Prometheus - HEALTHY"
else
    echo "✗ Prometheus - UNHEALTHY or not running"
fi

if curl -sf "http://localhost:3100/ready" > /dev/null 2>&1; then
    echo "✓ Loki - HEALTHY"
else
    echo "✗ Loki - UNHEALTHY or not running"
fi

if curl -sf "http://localhost:3001/api/health" > /dev/null 2>&1; then
    echo "✓ Grafana - HEALTHY"
else
    echo "✗ Grafana - UNHEALTHY or not running"
fi

echo ""
if [ "$all_healthy" = true ]; then
    echo "All core services are healthy!"
    exit 0
else
    echo "Some services are unhealthy. Check logs with: docker compose logs"
    exit 1
fi
