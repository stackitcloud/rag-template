FROM --platform=linux/amd64 python:3.11.7-bookworm AS build

ARG dev=0
ENV POETRY_VIRTUALENVS_PATH=/app/services/mcp-server/.venv
ENV POETRY_VERSION=1.8.3

WORKDIR /app

RUN DEBIAN_FRONTEND=noninteractive apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y build-essential --no-install-recommends make && \
    python3 -m venv "${POETRY_VIRTUALENVS_PATH}" \
    && $POETRY_VIRTUALENVS_PATH/bin/pip install "poetry==${POETRY_VERSION}"
ENV PATH="${POETRY_VIRTUALENVS_PATH}/bin:$PATH"


WORKDIR /app/services/mcp-server
COPY services/mcp-server/pyproject.toml services/mcp-server/poetry.lock ./

RUN mkdir log && chmod 700 log
RUN touch /app/services/mcp-server/log/logfile.log && chmod 600 /app/services/mcp-server/log/logfile.log

RUN poetry config virtualenvs.create false &&\
    if [ "$dev" = "1" ]; then \
    poetry install --no-interaction --no-ansi --no-root --with dev; \
    else \
    poetry install --no-interaction --no-ansi --no-root; \
    fi

FROM --platform=linux/amd64 python:3.11.7-bookworm
ARG dev=0

RUN adduser --disabled-password --gecos "" --uid 65532 nonroot

ENV POETRY_VIRTUALENVS_PATH=/app/services/mcp-server/.venv
COPY --from=build --chown=nonroot:nonroot ${POETRY_VIRTUALENVS_PATH} ${POETRY_VIRTUALENVS_PATH}
COPY --from=build /usr/local/bin/ /usr/local/bin/
COPY --from=build /usr/bin/make /usr/bin/make
COPY --from=build /usr/local/lib/ /usr/local/lib/

WORKDIR /app/services/mcp-server
COPY --chown=nonroot:nonroot services/mcp-server/src ./src
COPY --chown=nonroot:nonroot services/mcp-server/pyproject.toml services/mcp-server/poetry.lock ./
# cleanup
RUN apt-get clean autoclean
RUN apt-get autoremove --yes

RUN if [ "$dev" = "0" ]; then \
        while read -r shell; do rm -f "$shell"; done < /etc/shells; \
        rm -rf /var/lib/{apt,dpkg,cache,log}/ \
    else \
        echo "POETRY_VIRTUALENVS_PATH=/app/services/mcp-server/.venv" >> /etc/environment;\
        export POETRY_VIRTUALENVS_PATH=/app/services/mcp-server/.venv;\
        export PATH="${POETRY_VIRTUALENVS_PATH}/bin:$PATH";\
    fi


USER nonroot
COPY --from=build --chown=nonroot:nonroot  /app/services/mcp-server/log /app/services/mcp-server/log

ENV PATH="${POETRY_VIRTUALENVS_PATH}/bin:${PATH}"

CMD [ "poetry", "run", "python", "src/main.py" ]
