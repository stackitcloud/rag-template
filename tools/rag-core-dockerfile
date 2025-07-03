FROM --platform=linux/amd64 python:3.13-bookworm

ARG DIRECTORY=""
ARG TEST=1

WORKDIR /app

RUN DEBIAN_FRONTEND=noninteractive apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y build-essential --no-install-recommends make; \
    if [ ${DIRECTORY}="extractor-api-lib" ]; then DEBIAN_FRONTEND=noninteractive apt-get install -y ffmpeg \
        poppler-utils \
        tesseract-ocr \
        tesseract-ocr-deu \
        tesseract-ocr-eng; \
    fi

COPY . .

RUN pip install poetry==1.8.3

WORKDIR /app/${DIRECTORY}
RUN poetry config virtualenvs.create false
RUN if [ "$TEST" = "1" ]; then rm ../poetry.lock; rm ../pyproject.toml; poetry install --with dev; else poetry install; fi
