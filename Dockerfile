# syntax = edrevo/dockerfile-plus

INCLUDE+ rag-core-library/Dockerfile.base

COPY rag-core-library rag-core-library
COPY poetry.lock pyproject.toml ./

RUN poetry install --no-root
# TODO: investigate if multi context build might be a better solution, to avoid copying the rag-core-library twice

ENV PATH="/home/.cache/pypoetry/virtualenvs/rag-usecase-example-9TtSrW0h-py3.11/bin/"

COPY . . 
