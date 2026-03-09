# Multi-stage build for ontEAUlogy core orchestrator
FROM python:3.11-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy shared package first (dependency of orchestrator)
COPY case_studies/core/shared-python/ ./shared-python/

# Install shared package
RUN pip install --no-cache-dir ./shared-python

# Copy orchestrator package
COPY case_studies/core/orchestrator/ ./orchestrator/

# Install orchestrator package
RUN pip install --no-cache-dir ./orchestrator

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Create non-root user for security
RUN useradd -m -u 1000 orchestrator && \
    mkdir -p /app/data && \
    chown -R orchestrator:orchestrator /app

USER orchestrator

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import httpx; exit(0 if httpx.get('http://localhost:8080/health', timeout=5).status_code == 200 else 1)"

# Default command (config path can be overridden)
CMD ["onteaulogy-orchestrator"]
