FROM --platform=linux/amd64 python:3.13-bookworm

ARG DIRECTORY=""
ARG TEST=1

WORKDIR /app

RUN DEBIAN_FRONTEND=noninteractive apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y build-essential --no-install-recommends make; \
    if [ "${DIRECTORY}" = "extractor-api-lib" ]; then DEBIAN_FRONTEND=noninteractive apt-get install -y ffmpeg \
        poppler-utils \
        tesseract-ocr \
        tesseract-ocr-deu \
        tesseract-ocr-eng; \
    fi

# Copy the entire libs directory
COPY . .

RUN pip install poetry==1.8.3

# Set working directory to the specific library
WORKDIR /app/${DIRECTORY}

# Configure poetry
RUN poetry config virtualenvs.create false

# Install dependencies (no need to remove parent files since we're in a library-specific directory)
RUN if [ "$TEST" = "1" ]; then \
        poetry install --with dev; \
    else \
        poetry install; \
    fi

# Default command
CMD ["make", "lint"]
