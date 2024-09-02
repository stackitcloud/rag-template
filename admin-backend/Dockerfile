FROM python:3.11.7-bookworm

ARG dev=0

WORKDIR /app

RUN DEBIAN_FRONTEND=noninteractive apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y build-essential --no-install-recommends make

RUN pip install poetry==1.8.3

COPY rag-core-library rag-core-library

WORKDIR /app/admin-backend
COPY admin-backend/pyproject.toml pyproject.toml
COPY admin-backend/poetry.lock poetry.lock

RUN if [ "$dev" = "1" ]; then \
        poetry install --no-interaction --no-ansi --no-root --with dev; \
    else \
        poetry install --no-interaction --no-ansi --no-root; \
    fi

COPY admin-backend .


