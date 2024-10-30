ARG TAG=nonroot

FROM --platform=linux/amd64 python:3.11.7-bookworm AS build

ARG dev=0

ENV POETRY_VIRTUALENVS_PATH=/app/document-extractor/.venv
ENV POETRY_VERSION=1.7.1

RUN DEBIAN_FRONTEND=noninteractive apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y build-essential --no-install-recommends make \
    ffmpeg \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-deu \
    tesseract-ocr-eng && \
    python3 -m venv "${POETRY_VIRTUALENVS_PATH}" \
      && $POETRY_VIRTUALENVS_PATH/bin/pip install "poetry==${POETRY_VERSION}"
ENV PATH="${POETRY_VIRTUALENVS_PATH}/bin:$PATH"

WORKDIR /app/document-extractor

COPY document-extractor/pyproject.toml document-extractor/poetry.lock ./

RUN mkdir log && chmod 700 log
RUN touch /app/document-extractor/log/logfile.log && chmod 600 /app/document-extractor/log/logfile.log

RUN if [ "$dev" = "1" ]; then \
        poetry install --no-interaction --no-ansi --no-root --with dev; \
    else \
        poetry install --no-interaction --no-ansi --no-root; \
    fi

FROM --platform=linux/amd64 gcr.io/distroless/python3-debian12:${TAG}

ENV POETRY_VIRTUALENVS_PATH=/app/document-extractor/.venv
COPY --from=build ${POETRY_VIRTUALENVS_PATH} ${POETRY_VIRTUALENVS_PATH}
COPY --from=build /usr/local/bin/ /usr/local/bin/
COPY --from=build /usr/bin/ /usr/bin/
COPY --from=build /usr/local/lib/ /usr/local/lib/
COPY --from=build /usr/lib/x86_64-linux-gnu/ /usr/lib/x86_64-linux-gnu/
COPY --from=build /usr/share/tesseract-ocr/5/tessdata /usr/share/tesseract-ocr/5/tessdata

WORKDIR /app/document-extractor
COPY document-extractor .
COPY --from=build --chown=nonroot:nonroot  /app/document-extractor/log /app/document-extractor/log

ENV PATH="${POETRY_VIRTUALENVS_PATH}/bin:${PATH}"
