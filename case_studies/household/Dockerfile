FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml .
RUN pip install --no-cache-dir -e .

COPY src/ src/

CMD ["python", "-m", "household_water.runners.model_runner", "--model", "mbr"]
