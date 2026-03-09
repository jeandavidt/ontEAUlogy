# ontEAUlogy Core

Core orchestrator for ontEAUlogy case studies.

## Features

- Generic FastAPI orchestrator for water system ontologies
- Configuration-driven model discovery via YAML
- SPARQL query endpoint
- LLM-powered natural language queries
- WebSocket support for real-time sensor data
- Model proxy and simulation management

## Configuration

Create an `orchestrator.yaml` file:

```yaml
app:
  name: "My Case Study"
  version: "0.1.0"

models:
  discovery:
    - id: "model1"
      endpoint: "http://model1:8000"
      entity: "case:Model1"

ontology:
  base_path: "/shared-ontology"
  case_study_path: "/app/data"
```

## Usage

```bash
# Run with default config
onteaulogy-orchestrator

# Run with custom config
onteaulogy-orchestrator /path/to/config.yaml
```

## Docker

```bash
docker build -t onteaulogy-core:latest .
docker run -p 8080:8080 -v $(pwd)/config.yaml:/app/config.yaml onteaulogy-core:latest
```
