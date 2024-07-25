# syntax = edrevo/dockerfile-plus

INCLUDE+ rag-core-library/Dockerfile.base

WORKDIR /app/rag-backend
COPY rag-backend/pyproject.toml pyproject.toml
COPY rag-backend/poetry.lock poetry.lock

RUN if [ "$dev" = "1" ]; then \
        poetry install --no-interaction --no-ansi --no-root --with dev; \
    else \
        poetry install --no-interaction --no-ansi --no-root; \
    fi

COPY rag-backend .
