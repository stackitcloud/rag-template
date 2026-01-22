FROM --platform=linux/amd64 python:3.13-bookworm AS build

ENV POETRY_VIRTUALENVS_PATH=/opt/.venv \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_VIRTUALENVS_IN_PROJECT=false \
    VIRTUAL_ENV=/opt/.venv \
    PATH=/opt/.venv/bin:$PATH \
    POETRY_VERSION=2.1.3

# Build argument to control which dependency group to install
ARG DEPENDENCY_GROUP=prod

WORKDIR /app

RUN DEBIAN_FRONTEND=noninteractive apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y build-essential --no-install-recommends make \
    && python3 -m venv "${POETRY_VIRTUALENVS_PATH}" \
    && ${POETRY_VIRTUALENVS_PATH}/bin/pip install "poetry==${POETRY_VERSION}"

# Copy service manifest + lockfile and install runtime deps using the lock
WORKDIR /app/services/rag-backend
COPY services/rag-backend/pyproject.toml services/rag-backend/poetry.lock ./

# Copy the required lib dependencies
COPY libs/rag-core-api/pyproject.toml libs/rag-core-api/poetry.lock /app/libs/rag-core-api/
COPY libs/rag-core-api/README.md /app/libs/rag-core-api/README.md
COPY libs/rag-core-api/src /app/libs/rag-core-api/src
COPY libs/rag-core-lib/pyproject.toml libs/rag-core-lib/poetry.lock /app/libs/rag-core-lib/
COPY libs/rag-core-lib/README.md /app/libs/rag-core-lib/README.md
COPY libs/rag-core-lib/src /app/libs/rag-core-lib/src

RUN mkdir -p log && chmod 700 log \
    && touch /app/services/rag-backend/log/logfile.log && chmod 600 /app/services/rag-backend/log/logfile.log

RUN poetry config virtualenvs.create false \
    && cd /app/services/rag-backend \
    && poetry install --no-interaction --no-ansi --no-root --with ${DEPENDENCY_GROUP}

FROM --platform=linux/amd64 python:3.13-bookworm

WORKDIR /app/services/rag-backend

RUN adduser --disabled-password --gecos "" --uid 10001 nonroot

ENV POETRY_VIRTUALENVS_PATH=/opt/.venv
ENV POETRY_VIRTUALENVS_IN_PROJECT=false \
    VIRTUAL_ENV=${POETRY_VIRTUALENVS_PATH} \
    PATH=${POETRY_VIRTUALENVS_PATH}/bin:$PATH

COPY --from=build --chown=nonroot:nonroot ${POETRY_VIRTUALENVS_PATH} ${POETRY_VIRTUALENVS_PATH}
COPY --from=build /usr/local/bin/ /usr/local/bin/
COPY --from=build /usr/bin/make /usr/bin/make
COPY --from=build /usr/local/lib/ /usr/local/lib/

COPY --chown=nonroot:nonroot services/rag-backend .
# Preserve log directory from build stage
COPY --from=build --chown=nonroot:nonroot /app/services/rag-backend/log /app/services/rag-backend/log

# Copy the library source code to the final stage only for local path dependencies
ARG DEPENDENCY_GROUP=prod
COPY --from=build --chown=nonroot:nonroot \
    /app/libs/rag-core-api \
    /tmp/conditional-libs/rag-core-api
COPY --from=build --chown=nonroot:nonroot \
    /app/libs/rag-core-lib \
    /tmp/conditional-libs/rag-core-lib

# Move libraries to final location only if using prod-local
RUN if [ "$DEPENDENCY_GROUP" = "prod-local" ]; then \
        mkdir -p /app/libs && \
        mv /tmp/conditional-libs/* /app/libs/ && \
        chown -R nonroot:nonroot /app/libs; \
    fi && \
    rm -rf /tmp/conditional-libs

# cleanup
RUN apt-get clean autoclean && apt-get autoremove --yes \
    && while read -r shell; do rm -f "$shell"; done < /etc/shells || true \
    && rm -rf /var/lib/{apt,dpkg,cache,log}/ || true

USER nonroot
