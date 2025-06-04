FROM --platform=linux/amd64 python:3.13-bookworm AS build

ARG dev=0
ENV POETRY_VIRTUALENVS_PATH=/app/admin-backend/.venv
ENV POETRY_VERSION=1.8.3

RUN DEBIAN_FRONTEND=noninteractive apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y build-essential --no-install-recommends make && \
    python3 -m venv "${POETRY_VIRTUALENVS_PATH}" \
      && $POETRY_VIRTUALENVS_PATH/bin/pip install "poetry==${POETRY_VERSION}"
ENV PATH="${POETRY_VIRTUALENVS_PATH}/bin:$PATH"

COPY rag-core-library/admin-api-lib /app/rag-core-library/admin-api-lib
COPY rag-core-library/rag-core-lib /app/rag-core-library/rag-core-lib

WORKDIR /app/admin-backend
COPY admin-backend/pyproject.toml admin-backend/poetry.lock ./

RUN mkdir log && chmod 700 log
RUN touch /app/admin-backend/log/logfile.log && chmod 600 /app/admin-backend/log/logfile.log

RUN poetry config virtualenvs.create false && \
    if [ "$dev" = "1" ]; then \
        poetry install --no-interaction --no-ansi --no-root --with dev; \
    else \
        poetry install --no-interaction --no-ansi --no-root; \
    fi

FROM --platform=linux/amd64 python:3.13-bookworm
ARG dev=0

RUN adduser --disabled-password --gecos "" --uid 65532 nonroot

ENV POETRY_VIRTUALENVS_PATH=/app/admin-backend/.venv
COPY --from=build --chown=nonroot:nonroot ${POETRY_VIRTUALENVS_PATH} ${POETRY_VIRTUALENVS_PATH}
COPY --from=build /usr/local/bin/ /usr/local/bin/
COPY --from=build /usr/bin/make /usr/bin/make
COPY --from=build /usr/local/lib/ /usr/local/lib/

COPY --chown=nonroot:nonroot rag-core-library/admin-api-lib /app/rag-core-library/admin-api-lib
COPY --chown=nonroot:nonroot rag-core-library/rag-core-lib /app/rag-core-library/rag-core-lib

WORKDIR /app/admin-backend

COPY --chown=nonroot:nonroot admin-backend .

# cleanup
RUN apt-get clean autoclean
RUN apt-get autoremove --yes

RUN if [ "$dev" = "0" ]; then \
        while read -r shell; do rm -f "$shell"; done < /etc/shells; \
        rm -rf /var/lib/{apt,dpkg,cache,log}/ \
    else \
        echo "POETRY_VIRTUALENVS_PATH=/app/admin-backend/.venv" >> /etc/environment;\
        export POETRY_VIRTUALENVS_PATH=/app/admin-backend/.venv;\
        export PATH="${POETRY_VIRTUALENVS_PATH}/bin:$PATH";\
    fi


USER nonroot
COPY --from=build --chown=nonroot:nonroot  /app/admin-backend/log /app/admin-backend/log

ENV PATH="${POETRY_VIRTUALENVS_PATH}/bin:${PATH}"
