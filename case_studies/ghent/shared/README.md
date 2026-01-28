# Shared Type Generation Pipeline

This directory contains the automated type generation pipeline for the ontEAUlogy project.

## Overview

The type generation pipeline automatically creates TypeScript type definitions from the FastAPI OpenAPI specification, ensuring frontend-backend type consistency.

## Files

- `generate-types.sh` - Main type generation script
- `openapi.json` - Generated OpenAPI specification (auto-generated)
- `../frontend-react/src/api/generated-types.ts` - Generated TypeScript types (auto-generated)

## Usage

### Generate Types
```bash
# Generate types from running server
./shared/generate-types.sh generate

# Or with custom server URL
SERVER_URL=http://localhost:9000 ./shared/generate-types.sh generate
```

### Individual Commands
```bash
# Wait for server to be ready
./shared/generate-types.sh wait

# Clean up generated files
./shared/generate-types.sh cleanup

# Show help
./shared/generate-types.sh help
```

### NPM Scripts (from frontend directory)
```bash
# Generate types
npm run generate-types

# Generate types and run type check
npm run verify-types

# Just type check existing types
npm run type-check
```

## Process Flow

1. **Server Health Check** - Waits for server at `http://localhost:8080`
2. **OpenAPI Export** - Fetches OpenAPI spec from `/openapi.json`
3. **Type Generation** - Uses `openapi-typescript` to generate TypeScript types
4. **Validation** - Runs `npm run type-check` to verify generated types
5. **Statistics** - Reports generation metrics

## Configuration

### Environment Variables
- `SERVER_URL` - Backend server URL (default: `http://localhost:8080`)
- `TIMEOUT` - Request timeout in seconds (default: 10)

### Generated Files Structure

The generated TypeScript types include:
- API request/response types
- Entity and model schemas
- Parameter and payload interfaces
- Error response types

## Integration with CI/CD

### Before Commits
```bash
npm run verify-types
```

### In CI Pipeline
```yaml
- name: Generate and verify types
  run: |
    npm run generate-types
    npm run type-check
```

## Troubleshooting

### Common Issues

1. **Server not reachable**
   - Start the backend: `cd src/ghent_water/orchestrator && python main.py`
   - Check server URL with `SERVER_URL=http://localhost:9000 ./generate-types.sh`

2. **Type generation fails**
   - Ensure `openapi-typescript` is installed: `npm install -D openapi-typescript`
   - Check OpenAPI spec accessibility: `curl http://localhost:8080/openapi.json`

3. **Type check fails**
   - Check generated types in `frontend-react/src/api/generated-types.ts`
   - Verify backend API models match expected interfaces

### Manual Type Generation

If automatic generation fails, you can manually generate types:

```bash
# Export OpenAPI spec
curl http://localhost:8080/openapi.json > shared/openapi.json

# Generate types
cd frontend-react
npx openapi-typescript ../shared/openapi.json -o src/api/generated-types.ts
```

## Benefits

- **Type Safety** - Ensures frontend matches backend API contracts
- **Developer Experience** - Autocomplete and compile-time checking
- **Documentation** - Generated types serve as API documentation
- **Consistency** - Single source of truth for type definitions
- **Automation** - Reduces manual type maintenance overhead