#!/bin/bash
echo "Chose which api and its corresponding client to recreate. Possible values are: 0, 1, 2"
echo 0: admin-backend
echo 1: rag-backend
echo 2: document-extractor

read api_idx

declare -A api_names=( ["0"]="admin-backend" ["1"]="rag-backend" ["2"]="document-extractor" )
api_name=${api_names[$api_idx]}

echo $api_name

case $api_name in
    "admin-backend")
        docker run --user $(id -u):$(id -g) --rm -v $PWD:/local openapitools/openapi-generator-cli generate -i /local/admin-backend/openapi.yaml -g python-fastapi -o /local/admin-backend --additional-properties=packageName=admin_backend
        rm -r admin-backend/src/openapi_server
        black ./admin-backend
        ;;
    "rag-backend")
        docker run --user $(id -u):$(id -g) --rm -v $PWD:/local openapitools/openapi-generator-cli generate -i /local/rag-core-library/rag-core-api/openapi.yaml -g python-fastapi -o /local/rag-core-library/rag-core-api --additional-properties packageName=rag_core_api
        rm -r rag-core-library/rag-core-api/src/openapi_server
        black ./rag-core-library/rag-core-api 
        docker run --user $(id -u):$(id -g) --rm -v $PWD:/local openapitools/openapi-generator-cli generate -i /local/rag-core-library/rag-core-api/openapi.yaml -g python -o /local/admin-backend/src --additional-properties=generateSourceCodeOnly=True,packageName=admin_backend.rag_backend_client.openapi_client
        black ./admin-backend
        ;;
    "document-extractor")
        docker run --user $(id -u):$(id -g) --rm -v $PWD:/local openapitools/openapi-generator-cli generate -i /local/document-extractor/openapi.yaml -g python-fastapi -o /local/document-extractor --additional-properties=packageName=openapi_server
        black ./document-extractor
        docker run --user $(id -u):$(id -g) --rm -v $PWD:/local openapitools/openapi-generator-cli generate -i /local/document-extractor/openapi.yaml -g python -o /local/admin-backend/src --additional-properties=generateSourceCodeOnly=True,packageName=admin_backend.document_extractor_client.openapi_client
        rm -r admin-backend/src/openapi_server
        black ./admin-backend
        ;;
    *)
        echo "Invalid api name"
        ;;
esac
