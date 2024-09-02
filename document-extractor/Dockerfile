FROM python:3.11.7-bookworm

ARG dev=0

ENV POETRY_CACHE_DIR "${HOME}/poetry_cache"

RUN DEBIAN_FRONTEND=noninteractive apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y build-essential --no-install-recommends make

RUN DEBIAN_FRONTEND=noninteractive apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    ffmpeg \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-deu \
    tesseract-ocr-eng

RUN pip install poetry==1.7.1

WORKDIR /app/document-extractor

# Install dependencies
COPY document-extractor/pyproject.toml pyproject.toml
COPY document-extractor/poetry.lock poetry.lock

# Install Python dependencies
RUN if [ "$dev" = "1" ]; then \
        poetry install --no-interaction --no-ansi --no-root --with dev; \
    else \
        poetry install --no-interaction --no-ansi --no-root; \
    fi

COPY document-extractor .
