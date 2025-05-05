#!/bin/bash

        
docker run --user $(id -u):$(id -g) --rm -v $PWD:/local openapitools/openapi-generator-cli@sha256:b35aee2d0f6ffadadcdad9d8fc3c46e8d48360c20b5731a5f47c809d51f67a04 generate -i /local/rag-core-library/rag-core-api/openapi.yaml -g python -o /local/mcp-server/src --additional-properties=generateSourceCodeOnly=True,packageName=rag_backend_client.openapi_client
cd ./mcp-server
black .
cd ..
