# syntax = edrevo/dockerfile-plus

INCLUDE+ rag-core-library/Dockerfile.base

WORKDIR /app/admin-backend
COPY admin-backend/pyproject.toml pyproject.toml
COPY admin-backend/poetry.lock poetry.lock

RUN if [ "$dev" = "1" ]; then \
        poetry install --no-interaction --no-ansi --no-root --with dev; \
    else \
        poetry install --no-interaction --no-ansi --no-root; \
    fi

COPY admin-backend .


