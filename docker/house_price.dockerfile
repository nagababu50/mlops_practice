FROM python:3.11-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1
ENV UV_NO_CACHE=1
ENV UV_NO_ENV_FILE=1
ENV UV_PROJECT_ENVIRONMENT="/usr/local/"
ENV UV_SYSTEM_PYTHON=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    gcc \
    vim \
    python3-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory to /app
WORKDIR /app

# Copy dependency files and source
COPY pyproject.toml /app/
COPY uv.lock /app/
COPY .python-version /app/
COPY README.md /app/

# Copy the application into the container.
COPY gcp_demo /app/gcp_demo/

# RUN uv sync --locked --no-dev
# RUN uv sync --locked --groups pipeline
RUN uv sync --locked --all-groups --no-dev

