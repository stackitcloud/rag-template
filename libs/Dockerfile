# syntax = edrevo/dockerfile-plus

INCLUDE+ Dockerfile.base

WORKDIR /app

COPY poetry.lock poetry.lock
COPY pyproject.toml pyproject.toml

RUN poetry install --with dev

COPY . .
