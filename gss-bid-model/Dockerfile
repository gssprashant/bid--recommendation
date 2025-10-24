### Multi-stage build: install dependencies and create small runtime image
FROM python:3.11-slim AS builder
WORKDIR /install

# Install build deps
RUN apt-get update && apt-get install -y --no-install-recommends gcc build-essential ca-certificates && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --upgrade pip && pip wheel --no-deps --wheel-dir /install/wheels -r requirements.txt

FROM python:3.11-slim
WORKDIR /app

# Create a non-root user
RUN useradd --create-home appuser && mkdir -p /app
COPY --from=builder /install/wheels /wheels
RUN pip install --no-cache /wheels/* || pip install --no-cache -r requirements.txt

# Copy app
COPY . /app
RUN chown -R appuser:appuser /app
USER appuser

ENV MODEL_DIR=/app/models
EXPOSE 8000

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
