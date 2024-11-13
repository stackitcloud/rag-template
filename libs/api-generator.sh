#!/bin/bash
echo "Chose which api and its corresponding client to recreate. Possible values are: 0, 1, 2"
echo 0: admin-api-lib
echo 1: rag-backend
echo 2: extractor-api-lib

read api_idx

declare -A api_names=( ["0"]="admin-api-lib" ["1"]="rag-backend" ["2"]="extractor-api-lib" )
api_name=${api_names[$api_idx]}

echo $api_name

case $api_name in
    "admin-api-lib")
        docker run --user $(id -u):$(id -g) --rm -v $PWD:/local openapitools/openapi-generator-cli@sha256:b35aee2d0f6ffadadcdad9d8fc3c46e8d48360c20b5731a5f47c809d51f67a04 generate -i /local/admin-api-lib/openapi.yaml -g python-fastapi -o /local/admin-api-lib --additional-properties=packageName=admin_api_lib
        rm -r admin-api-lib/src/openapi_server
        black ./admin-api-lib
        ;;
    "rag-backend")
        docker run --user $(id -u):$(id -g) --rm -v $PWD:/local openapitools/openapi-generator-cli@sha256:b35aee2d0f6ffadadcdad9d8fc3c46e8d48360c20b5731a5f47c809d51f67a04 generate -i /local/rag-core-api/openapi.yaml -g python-fastapi -o /local/rag-core-api --additional-properties=packageName=rag_core_api
        rm -r rag-core-library/rag-core-api/src/openapi_server
        black ./rag-core-library/rag-core-api
        docker run --user $(id -u):$(id -g) --rm -v $PWD:/local openapitools/openapi-generator-cli@sha256:b35aee2d0f6ffadadcdad9d8fc3c46e8d48360c20b5731a5f47c809d51f67a04 generate -i /local/rag-core-api/openapi.yaml -g python -o /local/admin-api-lib/src --additional-properties=generateSourceCodeOnly=True,packageName=admin_api_lib.rag_backend_client.openapi_client
        black ./admin-api-lib
        ;;
    "extractor-api-lib")
        docker run --user $(id -u):$(id -g) --rm -v $PWD:/local openapitools/openapi-generator-cli@sha256:b35aee2d0f6ffadadcdad9d8fc3c46e8d48360c20b5731a5f47c809d51f67a04 generate -i /local/extractor-api-lib/openapi.yaml -g python-fastapi -o /local/extractor-api-lib --additional-properties=packageName=extractor_api_lib
        black ./extractor-api-lib
        docker run --user $(id -u):$(id -g) --rm -v $PWD:/local openapitools/openapi-generator-cli@sha256:b35aee2d0f6ffadadcdad9d8fc3c46e8d48360c20b5731a5f47c809d51f67a04 generate -i /local/extractor-api-lib/openapi.yaml -g python -o /local/admin-api-lib/src --additional-properties=generateSourceCodeOnly=True,packageName=admin_api_lib.extractor_api_client.openapi_client
        rm -r admin-api-lib/src/openapi_server
        black ./admin-api-lib
        ;;
    *)
        echo "Invalid api name"
        ;;
esac
