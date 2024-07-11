# syntax = edrevo/dockerfile-plus

INCLUDE+ Dockerfile.base

WORKDIR /app

COPY . .

RUN poetry install --with dev
