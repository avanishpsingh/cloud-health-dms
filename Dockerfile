# Multi-stage Dockerfile — same image runs locally, on EC2, on ECS, or on App Runner.
FROM python:3.11-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install system deps for psycopg2 only when DB is Postgres (still <30 MB).
RUN apt-get update \
 && apt-get install -y --no-install-recommends gcc libpq-dev curl \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install -r requirements.txt \
 && pip install boto3 psycopg2-binary

COPY app ./app
COPY scripts ./scripts

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD curl -fsS http://localhost:8000/ || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
