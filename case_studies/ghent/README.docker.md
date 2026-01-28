# Dockerized Ghent Water System

This document provides instructions on how to run the Ghent Water System using Docker.

## Prerequisites

- Docker installed on your machine
- Docker Compose installed (usually included with Docker Desktop)

## Running the System

### Step 1: Build and Start the Containers

From the project root directory, run:

```bash
cd /Users/jeandavidt/Developer/jeandavidt/ontEAUlogy/case_studies/ghent
docker-compose up -d
```

This command will:
1. Build the necessary Docker images (if they don't exist)
2. Start all containers in the background
3. Create a Docker network for communication between containers

### Step 2: Verify the System is Running

Check the status of all containers:

```bash
docker-compose ps
```

All containers should show `Up` status. You should see:
- 1 orchestrator container (ghent-orchestrator)
- 12 model containers (ghent-dwp1, ghent-dwp2, ..., ghent-muide)

### Step 3: Access the API Documentation

Open your web browser and go to:

```
http://localhost:8080/docs
```

This will display the Swagger UI for the API, where you can explore and test all endpoints.

### Step 4: Test the Health Endpoint

```bash
curl -X GET http://localhost:8080/health
```

You should receive a response like:
```json
{"status":"healthy","version":"0.1.0","components":{"ontology":"healthy","sparql_engine":"ready"}}
```

### Step 5: Check Registered Models

```bash
curl -X GET http://localhost:8080/api/v1/models/
```

This will return a list of all registered models.

## Stopping the System

To stop all containers:

```bash
docker-compose down
```

To stop and remove all containers, networks, and volumes:

```bash
docker-compose down -v
```

## Troubleshooting

### Container Health Check Failures

If a container's health check fails, you can check the logs for that container:

```bash
docker-compose logs <container_name>
```

For example, to check the orchestrator logs:
```bash
docker-compose logs ghent-orchestrator
```

### Rebuilding Containers

If you make changes to the codebase, you may need to rebuild the containers:

```bash
docker-compose build
docker-compose up -d
```

### Accessing Container Shell

To access the shell inside a container:

```bash
docker exec -it <container_name> /bin/bash
```

For example, to access the orchestrator container:
```bash
docker exec -it ghent-orchestrator /bin/bash
```

## Network Configuration

- All containers are connected to the `ghent-water-network` Docker network
- Containers communicate using their service names (e.g., `http://ghent-dwp1:8001`)
- Ports are mapped to the host machine as follows:
  - Orchestrator API: 8080
  - Model Services: 8001-8012
  - Frontend: 8501

## Project Structure

```
case_studies/ghent/
├── docker-compose.yml          # Docker Compose configuration
├── Dockerfile.orchestrator    # Orchestrator Dockerfile
├── Dockerfile.model           # Model services Dockerfile
├── Dockerfile.frontend        # Frontend Dockerfile
├── .dockerignore              # Docker ignore file
└── README.docker.md           # This file
```

## Notes

- The system uses a single base image (`ghent-water-base`) for all containers to optimize resource usage
- The orchestrator container loads the ontology from the `data/` directory
- All model containers are identical and use the model identifier from the command line
- The frontend is currently not implemented as a separate service
