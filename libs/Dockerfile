FROM python:3.11.7-bookworm

ARG dev=0

WORKDIR /app

RUN DEBIAN_FRONTEND=noninteractive apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y build-essential --no-install-recommends make

RUN pip install poetry==1.8.3

WORKDIR /app

COPY . .

RUN poetry config virtualenvs.create false
RUN cd rag-core-api; poetry install --with dev
