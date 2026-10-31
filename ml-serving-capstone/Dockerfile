FROM python:3.12-slim

# Create an unprivileged user for security (UID 1000)
RUN groupadd -g 1000 appgroup && \
    useradd -u 1000 -g appgroup -s /bin/bash -m appuser

WORKDIR /app

# Copy the fast uv binary directly from official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency specifications first for Docker layer caching
COPY pyproject.toml uv.lock README.md ./

# Ensure appuser owns the workdir
RUN chown -R appuser:appgroup /app
USER appuser

# Step 1: Install external dependencies without installing the project code
RUN uv sync --frozen --no-dev --no-install-project

# Step 2: Copy application source
COPY --chown=appuser:appgroup src/ ./src/

# Step 3: Install the project itself (fast, reuses cached venv)
RUN uv sync --frozen --no-dev

# Place the virtual environment's bin on PATH
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "ml_serving_capstone.main:app", "--host", "0.0.0.0", "--port", "8000"]
