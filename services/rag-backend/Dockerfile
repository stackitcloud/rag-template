FROM --platform=linux/amd64 python:3.13-bookworm AS build

ARG dev=0
ENV POETRY_VIRTUALENVS_PATH=/app/services/rag-backend/.venv
ENV POETRY_VERSION=2.1.3

WORKDIR /app

RUN DEBIAN_FRONTEND=noninteractive apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y build-essential --no-install-recommends make && \
    python3 -m venv "${POETRY_VIRTUALENVS_PATH}" \
    && $POETRY_VIRTUALENVS_PATH/bin/pip install "poetry==${POETRY_VERSION}"
ENV PATH="${POETRY_VIRTUALENVS_PATH}/bin:$PATH"

COPY libs/rag-core-lib /app/libs/rag-core-lib
COPY libs/rag-core-api /app/libs/rag-core-api

WORKDIR /app/services/rag-backend
COPY services/rag-backend/pyproject.toml services/rag-backend/poetry.lock ./

RUN mkdir log && chmod 700 log
RUN touch /app/services/rag-backend/log/logfile.log && chmod 600 /app/services/rag-backend/log/logfile.log

RUN poetry config virtualenvs.create false &&\
    if [ "$dev" = "1" ]; then \
    poetry install --no-interaction --no-ansi --no-root --with dev; \
    else \
    poetry install --no-interaction --no-ansi --no-root; \
    fi

FROM --platform=linux/amd64 python:3.13-bookworm
ARG dev=0

RUN adduser --disabled-password --gecos "" --uid 10001 nonroot

ENV POETRY_VIRTUALENVS_PATH=/app/services/rag-backend/.venv
COPY --from=build --chown=nonroot:nonroot ${POETRY_VIRTUALENVS_PATH} ${POETRY_VIRTUALENVS_PATH}
COPY --from=build /usr/local/bin/ /usr/local/bin/
COPY --from=build /usr/bin/make /usr/bin/make
COPY --from=build /usr/local/lib/ /usr/local/lib/


COPY --chown=nonroot:nonroot libs/rag-core-lib /app/libs/rag-core-lib
COPY --chown=nonroot:nonroot libs/rag-core-api /app/libs/rag-core-api

WORKDIR /app/services/rag-backend
COPY --chown=nonroot:nonroot services/rag-backend .


# cleanup
RUN apt-get clean autoclean
RUN apt-get autoremove --yes

RUN if [ "$dev" = "0" ]; then \
        while read -r shell; do rm -f "$shell"; done < /etc/shells; \
        rm -rf /var/lib/{apt,dpkg,cache,log}/ \
    else \
        echo "POETRY_VIRTUALENVS_PATH=/app/services/rag-backend/.venv" >> /etc/environment;\
        export POETRY_VIRTUALENVS_PATH=/app/services/rag-backend/.venv;\
        export PATH="${POETRY_VIRTUALENVS_PATH}/bin:$PATH";\
    fi


USER nonroot
COPY --from=build --chown=nonroot:nonroot  /app/services/rag-backend/log /app/services/rag-backend/log

ENV PATH="${POETRY_VIRTUALENVS_PATH}/bin:${PATH}"
