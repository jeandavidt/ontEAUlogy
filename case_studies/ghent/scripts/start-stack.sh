#!/bin/bash
set -e

echo "=== Ghent Water System - Starting Stack ==="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}Warning: .env file not found. Creating from .env.example...${NC}"
    cp .env.example .env
    echo -e "${GREEN}Created .env file. Please review and update if needed.${NC}"
fi

# Parse command line arguments
PROFILE="${1:-full}"
BUILD_FLAG="${2:-}"

echo "Starting with profile: $PROFILE"

# Build if requested
if [ "$BUILD_FLAG" == "--build" ]; then
    echo -e "${YELLOW}Building containers...${NC}"
    docker compose build --parallel
fi

# Start services
echo -e "${YELLOW}Starting services...${NC}"
docker compose --profile $PROFILE up -d

# Wait for services to be healthy
echo -e "${YELLOW}Waiting for services to be healthy...${NC}"
sleep 10

# Check health
echo -e "\n${GREEN}Service Status:${NC}"
docker compose ps

# Show access URLs
echo -e "\n${GREEN}=== Access URLs ===${NC}"
echo "Frontend:     http://localhost:3000"
echo "Orchestrator: http://localhost:8080"
echo "Grafana:      http://localhost:3001 (admin/admin)"
echo "Prometheus:   http://localhost:9090"
echo "Loki:         http://localhost:3100"

echo -e "\n${GREEN}=== Model Services ===${NC}"
for port in {8001..8012}; do
    service_name=$(docker ps --filter "publish=$port" --format "{{.Names}}" 2>/dev/null || echo "")
    if [ -n "$service_name" ]; then
        echo "  http://localhost:$port - $service_name"
    fi
done

echo -e "\n${GREEN}Stack started successfully!${NC}"
echo -e "View logs: ${YELLOW}docker compose logs -f${NC}"
echo -e "View specific service: ${YELLOW}docker compose logs -f orchestrator${NC}"
echo -e "Or use: ${YELLOW}make logs${NC} or ${YELLOW}make logs SERVICE=orchestrator${NC}"
