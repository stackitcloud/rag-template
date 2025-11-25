FROM --platform=linux/amd64 python:3.13.7-bookworm AS build

ENV POETRY_VIRTUALENVS_PATH=/opt/.venv \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_VIRTUALENVS_IN_PROJECT=false \
    VIRTUAL_ENV=/opt/.venv \
    PATH=/opt/.venv/bin:$PATH \
    POETRY_VERSION=2.1.3

WORKDIR /app

RUN DEBIAN_FRONTEND=noninteractive apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y build-essential --no-install-recommends make \
    && python3 -m venv "${POETRY_VIRTUALENVS_PATH}" \
    && ${POETRY_VIRTUALENVS_PATH}/bin/pip install "poetry==${POETRY_VERSION}"
ENV PATH="${POETRY_VIRTUALENVS_PATH}/bin:$PATH"

WORKDIR /app/services/mcp-server
COPY services/mcp-server/pyproject.toml services/mcp-server/poetry.lock ./

RUN mkdir -p log && chmod 700 log \
    && touch /app/services/mcp-server/log/logfile.log && chmod 600 /app/services/mcp-server/log/logfile.log

RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

FROM --platform=linux/amd64 python:3.13.7-bookworm

WORKDIR /app/services/mcp-server

RUN adduser --disabled-password --gecos "" --uid 10001 nonroot

ENV POETRY_VIRTUALENVS_PATH=/opt/.venv
ENV POETRY_VIRTUALENVS_IN_PROJECT=false \
    VIRTUAL_ENV=/opt/.venv \
    PATH=/opt/.venv/bin:$PATH

COPY --from=build --chown=nonroot:nonroot ${POETRY_VIRTUALENVS_PATH} ${POETRY_VIRTUALENVS_PATH}
COPY --from=build /usr/local/bin/ /usr/local/bin/
COPY --from=build /usr/bin/make /usr/bin/make
COPY --from=build /usr/local/lib/ /usr/local/lib/

COPY --from=build --chown=nonroot:nonroot  /app/services/mcp-server/log /app/services/mcp-server/log
COPY --chown=nonroot:nonroot services/mcp-server/src ./src
COPY --chown=nonroot:nonroot services/mcp-server/tests ./tests
COPY --chown=nonroot:nonroot services/mcp-server/pyproject.toml services/mcp-server/poetry.lock ./
COPY --chown=nonroot:nonroot services/mcp-server/Makefile ./

# cleanup
RUN apt-get clean autoclean && apt-get autoremove --yes \
    && while read -r shell; do rm -f "$shell"; done < /etc/shells || true \
    && rm -rf /var/lib/{apt,dpkg,cache,log}/ || true

USER nonroot

CMD [ "poetry", "run", "python", "src/main.py" ]
