#!/bin/bash

docker run --user $(id -u):$(id -g) --rm -v $PWD:/local openapitools/openapi-generator-cli generate -i /local/rag-backend/rag-core-library/openapi.yaml -g python -o /local/admin-backend/src --additional-properties=generateSourceCodeOnly=True,packageName=admin_backend.rag_backend_client.openapi_client
docker run --user $(id -u):$(id -g) --rm -v $PWD:/local openapitools/openapi-generator-cli generate -i /local/admin-backend/openapi.yaml -g python-fastapi -o /local/admin-backend --additional-properties=packageName=admin_backend
black ./admin-backend

# docker run --user $(id -u):$(id -g) --rm -v $PWD:/local openapitools/openapi-generator-cli generate -i /local/document-extractor/openapi.yaml -g python-fastapi -o /local/document-extractor
# black ./document-extractor
