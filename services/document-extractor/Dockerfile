FROM --platform=linux/amd64 python:3.13-bookworm AS build

# Build argument to control which dependency group to install
ARG DEPENDENCY_GROUP=prod
ENV POETRY_VIRTUALENVS_PATH=/opt/.venv
ENV POETRY_VIRTUALENVS_CREATE=false \
    POETRY_VIRTUALENVS_IN_PROJECT=false \
    VIRTUAL_ENV=${POETRY_VIRTUALENVS_PATH}} \
    PATH=${POETRY_VIRTUALENVS_PATH}/bin:$PATH \
    POETRY_VERSION=2.1.3

RUN DEBIAN_FRONTEND=noninteractive apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y build-essential --no-install-recommends make \
    ffmpeg \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-deu \
    tesseract-ocr-eng \
    libleptonica-dev \
    pkg-config && \
    python3 -m venv "${POETRY_VIRTUALENVS_PATH}" \
      && $POETRY_VIRTUALENVS_PATH/bin/pip install "poetry==${POETRY_VERSION}"

WORKDIR /app/services/document-extractor
COPY services/document-extractor/pyproject.toml services/document-extractor/poetry.lock ./

# Copy the extractor-api-lib dependency (needed for both prod and prod-local)
COPY libs/extractor-api-lib/pyproject.toml libs/extractor-api-lib/poetry.lock /app/libs/extractor-api-lib/
COPY libs/extractor-api-lib/src /app/libs/extractor-api-lib/src

RUN mkdir -p log && chmod 700 log \
    && touch /app/services/document-extractor/log/logfile.log && chmod 600 /app/services/document-extractor/log/logfile.log

RUN poetry config virtualenvs.create false \
    && cd /app/services/document-extractor \
    && poetry install --no-interaction --no-ansi --no-root --with ${DEPENDENCY_GROUP}

FROM --platform=linux/amd64 python:3.13-bookworm

RUN adduser --disabled-password --gecos "" --uid 10001 nonroot

ENV POETRY_VIRTUALENVS_PATH=/opt/.venv
# Ensure poetry reuses existing virtualenv when running as nonroot
ENV POETRY_VIRTUALENVS_IN_PROJECT=false \
    VIRTUAL_ENV=${POETRY_VIRTUALENVS_PATH} \
    PATH=${POETRY_VIRTUALENVS_PATH}/bin:$PATH
COPY --from=build  --chown=nonroot:nonroot ${POETRY_VIRTUALENVS_PATH} ${POETRY_VIRTUALENVS_PATH}
COPY --from=build /usr/local/bin/ /usr/local/bin/
COPY --from=build /usr/bin/ /usr/bin/
COPY --from=build /usr/local/lib/ /usr/local/lib/
COPY --from=build /usr/lib/x86_64-linux-gnu/ /usr/lib/x86_64-linux-gnu/
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata
COPY --from=build /usr/share/tesseract-ocr/5/tessdata ${TESSDATA_PREFIX}

# Copy the library source code to the final stage only for local path dependencies
ARG DEPENDENCY_GROUP=prod
COPY --from=build --chown=nonroot:nonroot \
    /app/libs/extractor-api-lib \
    /tmp/conditional-libs/extractor-api-lib

# Move libraries to final location only if using prod-local
RUN if [ "$DEPENDENCY_GROUP" = "prod-local" ]; then \
        mkdir -p /app/libs && \
        mv /tmp/conditional-libs/* /app/libs/ && \
        chown -R nonroot:nonroot /app/libs; \
    fi && \
    rm -rf /tmp/conditional-libs

WORKDIR /app/services/document-extractor

COPY --chown=nonroot:nonroot services/document-extractor .
COPY --from=build --chown=nonroot:nonroot  /app/services/document-extractor/log /app/services/document-extractor/log

# cleanup
RUN apt-get clean autoclean && apt-get autoremove --yes \
    && while read -r shell; do rm -f "$shell"; done < /etc/shells || true \
    && rm -rf /var/lib/{apt,dpkg,cache,log}/ || true

USER nonroot
