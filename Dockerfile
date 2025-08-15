FROM python:3.13-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git \
        openjdk-21-jre-headless \
        curl && \
    rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /src
COPY . .

# Install dependencies and build the package using uv
# This works with normal Git repositories (non-worktree)
RUN uv sync --frozen --no-dev

# Add virtual environment to PATH
ENV PATH="/src/.venv/bin:$PATH"

RUN useradd -m smart-tests
USER smart-tests

ENTRYPOINT ["smart-tests"]
