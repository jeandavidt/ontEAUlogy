FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml ./
COPY src/ ./src/

# Install dependencies
RUN pip install --no-cache-dir -e .[dev]

# Command to run (will be overridden in docker-compose)
CMD ["python", "-m", "household_water.runners.model_runner", "--model", "mbr", "--port", "8101"]
