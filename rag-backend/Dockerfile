# syntax = edrevo/dockerfile-plus

INCLUDE+ rag-core-library/Dockerfile.base

WORKDIR /app

ARG dev=0

COPY rag-core-library rag-core-library

ENV POETRY_CACHE_DIR "${HOME}/poetry_cache"

RUN DEBIAN_FRONTEND=noninteractive apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y build-essential --no-install-recommends make

COPY pyproject.toml pyproject.toml
# COPY poetry.lock poetry.lock

# Install Python dependencies
RUN if [ "$dev" = "1" ]; then \
        poetry install --no-interaction --no-ansi --no-root --with dev; \
    else \
        poetry install --no-interaction --no-ansi --no-root; \
    fi

COPY . .


