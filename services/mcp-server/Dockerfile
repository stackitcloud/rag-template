FROM --platform=linux/amd64 python:3.13.7-bookworm AS build

ARG dev=0
ENV POETRY_VIRTUALENVS_PATH=/opt/.venv \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_VIRTUALENVS_IN_PROJECT=false \
    VIRTUAL_ENV=/opt/.venv \
    PATH=/opt/.venv/bin:$PATH \
    POETRY_VERSION=2.1.3

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

# Cache bust with dev arg so dev dependencies install when dev=1
RUN echo "CACHE_BUST_DEV=$dev" && poetry config virtualenvs.create false &&\
    if [ "$dev" = "1" ]; then \
    poetry install --no-interaction --no-ansi --no-root --with dev; \
    else \
    poetry install --no-interaction --no-ansi --no-root; \
    fi

FROM --platform=linux/amd64 python:3.13.7-bookworm
ARG dev=0

RUN adduser --disabled-password --gecos "" --uid 10001 nonroot

ENV POETRY_VIRTUALENVS_PATH=/opt/.venv

COPY --from=build --chown=nonroot:nonroot ${POETRY_VIRTUALENVS_PATH} ${POETRY_VIRTUALENVS_PATH}
COPY --from=build /usr/local/bin/ /usr/local/bin/
COPY --from=build /usr/bin/make /usr/bin/make
COPY --from=build /usr/local/lib/ /usr/local/lib/

WORKDIR /app/services/mcp-server
COPY --chown=nonroot:nonroot services/mcp-server/src ./src
COPY --chown=nonroot:nonroot services/mcp-server/tests ./tests
COPY --chown=nonroot:nonroot services/mcp-server/pyproject.toml services/mcp-server/poetry.lock ./
COPY --chown=nonroot:nonroot services/mcp-server/Makefile ./

# Ensure poetry reuses existing virtualenv when running as nonroot
ENV POETRY_VIRTUALENVS_CREATE=false \
    POETRY_VIRTUALENVS_IN_PROJECT=false \
    VIRTUAL_ENV=/opt/.venv \
    PATH=/opt/.venv/bin:$PATH

# cleanup
RUN apt-get clean autoclean
RUN apt-get autoremove --yes

RUN if [ "$dev" = "0" ]; then \
        while read -r shell; do rm -f "$shell"; done < /etc/shells; \
        rm -rf /var/lib/{apt,dpkg,cache,log}/ \
    else \
        echo "POETRY_VIRTUALENVS_PATH=/opt/.venv" >> /etc/environment;\
        export POETRY_VIRTUALENVS_PATH=/opt/.venv;\
        export PATH="${POETRY_VIRTUALENVS_PATH}/bin:$PATH";\
    fi


USER nonroot
COPY --from=build --chown=nonroot:nonroot  /app/services/mcp-server/log /app/services/mcp-server/log

CMD [ "poetry", "run", "python", "src/main.py" ]
