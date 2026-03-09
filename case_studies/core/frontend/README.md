# ontEAUlogy Core Frontend

Shared React components and utilities for ontEAUlogy case studies.

## Overview

This package provides:
- Shared TypeScript types
- API client utilities
- React hooks for data fetching
- State management stores (Zustand)
- Component prop type definitions

## Installation

```bash
npm install @onteaulogy/core-frontend
```

## Usage

### Types

```typescript
import type { Entity, ModelInfo, SPARQLResult } from '@onteaulogy/core-frontend/types';
```

### API Client

```typescript
import { APIClient, checkHealth } from '@onteaulogy/core-frontend/api';

const client = new APIClient({ baseUrl: 'http://localhost:8080' });
const health = await checkHealth('http://localhost:8080');
```

### Hooks

```typescript
import { useEntities, useSensors, useWebSocket } from '@onteaulogy/core-frontend/hooks';

function MyComponent() {
  const { entities, loading } = useEntities('http://localhost:8080');
  const { readings, connected } = useSensors('http://localhost:8080');
  // ...
}
```

### Stores

```typescript
import { useSelectionStore, useConfigStore } from '@onteaulogy/core-frontend/stores';

function MyComponent() {
  const { selectedEntity, setSelectedEntity } = useSelectionStore();
  const { orchestratorUrl } = useConfigStore();
  // ...
}
```

## Structure

```
core/frontend/
├── src/
│   ├── api/          # API client and utilities
│   ├── components/   # Component type definitions
│   ├── hooks/        # React hooks
│   ├── stores/       # Zustand state stores
│   ├── types/        # TypeScript types
│   └── utils/        # Utility functions
├── package.json
└── tsconfig.json
```

## Note on Components

This package provides **type definitions and interfaces** for components.
Actual UI implementations should be created in each case study's frontend,
as they require specific styling and layout decisions.

Case studies should implement their own:
- Visual components (using Mantine, etc.)
- Page layouts
- Map visualizations
- Charts and graphs
