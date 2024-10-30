ARG TAG=nonroot

FROM --platform=linux/amd64 python:3.11.7-bookworm AS build

ARG dev=0

ENV POETRY_VIRTUALENVS_PATH=/app/rag-backend/.venv
ENV POETRY_VERSION=1.8.3

WORKDIR /app

RUN DEBIAN_FRONTEND=noninteractive apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y build-essential --no-install-recommends make && \
    python3 -m venv "${POETRY_VIRTUALENVS_PATH}" \
    && $POETRY_VIRTUALENVS_PATH/bin/pip install "poetry==${POETRY_VERSION}"
ENV PATH="${POETRY_VIRTUALENVS_PATH}/bin:$PATH"

COPY rag-core-library rag-core-library

WORKDIR /app/rag-backend
COPY rag-backend/pyproject.toml rag-backend/poetry.lock ./

RUN mkdir log && chmod 700 log
RUN touch /app/rag-backend/log/logfile.log && chmod 600 /app/rag-backend/log/logfile.log

RUN if [ "$dev" = "1" ]; then \
    poetry install --no-interaction --no-ansi --no-root --with dev; \
    else \
    poetry install --no-interaction --no-ansi --no-root; \
    fi

FROM --platform=linux/amd64 gcr.io/distroless/python3-debian12:${TAG}

ENV POETRY_VIRTUALENVS_PATH=/app/rag-backend/.venv
COPY --from=build ${POETRY_VIRTUALENVS_PATH} ${POETRY_VIRTUALENVS_PATH}
COPY --from=build /usr/local/bin/ /usr/local/bin/
COPY --from=build /usr/bin/make /usr/bin/make
COPY --from=build /usr/local/lib/ /usr/local/lib/

COPY rag-core-library /app/rag-core-library

WORKDIR /app/rag-backend
COPY rag-backend .
COPY --from=build --chown=nonroot:nonroot  /app/rag-backend/log /app/rag-backend/log



ENV PATH="${POETRY_VIRTUALENVS_PATH}/bin:${PATH}"
