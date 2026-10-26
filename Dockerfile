# Stage 1: Build virtual environment
FROM python:3.10-slim AS builder

WORKDIR /app

ENV UV_HTTP_TIMEOUT=120

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev --no-install-project

# Stage 2: Minimal runtime image
FROM python:3.10-slim AS runtime

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY src /app/src

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "src.food11.serve:app", "--host", "0.0.0.0", "--port", "8000"]
