FROM python:3.13-bookworm AS build

ENV POETRY_VIRTUALENVS_PATH=/app/services/rag-backend/.venv
ENV VIRTUAL_ENV="${POETRY_VIRTUALENVS_PATH}"
ENV POETRY_VERSION=2.1.3

WORKDIR /app

RUN DEBIAN_FRONTEND=noninteractive apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y build-essential --no-install-recommends make \
    && python3 -m venv "${POETRY_VIRTUALENVS_PATH}" \
    && ${POETRY_VIRTUALENVS_PATH}/bin/pip install "poetry==${POETRY_VERSION}"
ENV PATH="${POETRY_VIRTUALENVS_PATH}/bin:$PATH"

# Copy only service lockfiles and install runtime deps (no local lib sources)
WORKDIR /app/services/rag-backend
COPY services/rag-backend/pyproject.toml services/rag-backend/poetry.lock ./

RUN mkdir -p log && chmod 700 log \
    && touch /app/services/rag-backend/log/logfile.log && chmod 600 /app/services/rag-backend/log/logfile.log

RUN poetry config virtualenvs.create false \
    && cd /app/services/rag-backend \
    && poetry install --no-interaction --no-ansi --no-root --with prod

FROM python:3.13-bookworm

WORKDIR /app/services/rag-backend

RUN adduser --disabled-password --gecos "" --uid 65532 nonroot

ENV POETRY_VIRTUALENVS_PATH=/app/services/rag-backend/.venv
COPY --from=build --chown=nonroot:nonroot ${POETRY_VIRTUALENVS_PATH} ${POETRY_VIRTUALENVS_PATH}
COPY --from=build /usr/local/bin/ /usr/local/bin/
COPY --from=build /usr/bin/make /usr/bin/make
COPY --from=build /usr/local/lib/ /usr/local/lib/

# cleanup
RUN apt-get clean autoclean && apt-get autoremove --yes \
    && while read -r shell; do rm -f "$shell"; done < /etc/shells || true \
    && rm -rf /var/lib/{apt,dpkg,cache,log}/ || true

ENV VIRTUAL_ENV="${POETRY_VIRTUALENVS_PATH}"
ENV PATH="${POETRY_VIRTUALENVS_PATH}/bin:${PATH}"

USER nonroot

COPY --chown=nonroot:nonroot services/rag-backend .
# Preserve log directory from build stage
COPY --from=build --chown=nonroot:nonroot /app/services/rag-backend/log /app/services/rag-backend/log
