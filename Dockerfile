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

RUN apt-get update && \
    apt-get install -y --no-install-recommends openjdk-21-jre-headless git && \
    rm -rf /var/lib/apt/lists/*

RUN useradd -m smart-tests && chown -R smart-tests:smart-tests /src
USER smart-tests

ENTRYPOINT ["smart-tests"]
