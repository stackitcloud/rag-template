# syntax = edrevo/dockerfile-plus

INCLUDE+ rag-core-library/Dockerfile.base

COPY rag-core-library rag-core-library

ENV POETRY_VIRTUALENVS_CREATE=false
ENV POETRY_VIRTUALENVS_PATH="/app"

COPY poetry.lock pyproject.toml ./

RUN poetry install --no-root

# TODO: investigate if multi context build might be a better solution, to avoid copying the rag-core-library twice
COPY . . 
