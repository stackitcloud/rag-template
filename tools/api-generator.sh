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
        docker run --user $(id -u):$(id -g) --rm -v $PWD:/local openapitools/openapi-generator-cli@sha256:b35aee2d0f6ffadadcdad9d8fc3c46e8d48360c20b5731a5f47c809d51f67a04 generate -i /local/libs/admin-api-lib/openapi.yaml -g python-fastapi -o /local/libs/admin-api-lib --additional-properties=packageName=admin_api_lib,generateSourceCodeOnly=True
        rm -r libs/admin-api-lib/src/openapi_server
        cd ./libs/admin-api-lib
        black .
        cd ../..
        ;;
    "rag-backend")
        docker run --user $(id -u):$(id -g) --rm -v $PWD:/local openapitools/openapi-generator-cli@sha256:b35aee2d0f6ffadadcdad9d8fc3c46e8d48360c20b5731a5f47c809d51f67a04 generate -i /local/libs/rag-core-api/openapi.yaml -g python-fastapi -o /local/libs/rag-core-api --additional-properties=packageName=rag_core_api,generateSourceCodeOnly=True
        rm -r libs/rag-core-api/src/openapi_server
        cd ./libs/rag-core-api
        black .
        cd ../..
        docker run --user $(id -u):$(id -g) --rm -v $PWD:/local openapitools/openapi-generator-cli@sha256:b35aee2d0f6ffadadcdad9d8fc3c46e8d48360c20b5731a5f47c809d51f67a04 generate -i /local/libs/rag-core-api/openapi.yaml -g python -o /local/libs/admin-api-lib/src --additional-properties=generateSourceCodeOnly=True,packageName=admin_api_lib.rag_backend_client.openapi_client
        cd ./libs/admin-api-lib
        black .
        cd ../..
        ;;
    "extractor-api-lib")
        docker run --user $(id -u):$(id -g) --rm -v $PWD:/local openapitools/openapi-generator-cli@sha256:b35aee2d0f6ffadadcdad9d8fc3c46e8d48360c20b5731a5f47c809d51f67a04 generate -i /local/libs/extractor-api-lib/openapi.yaml -g python-fastapi -o /local/libs/extractor-api-lib --additional-properties=packageName=extractor_api_lib,generateSourceCodeOnly=True
        rm -r libs/extractor-api-lib/src/openapi_server
        cd ./libs/extractor-api-lib
        black .
        cd ../..
        docker run --user $(id -u):$(id -g) --rm -v $PWD:/local openapitools/openapi-generator-cli@sha256:b35aee2d0f6ffadadcdad9d8fc3c46e8d48360c20b5731a5f47c809d51f67a04 generate -i /local/libs/extractor-api-lib/openapi.yaml -g python -o /local/libs/admin-api-lib/src   --additional-properties=packageName=admin_api_lib.extractor_api_client.openapi_client,generateSourceCodeOnly=True,testOutput=false
        rm -r libs/admin-api-lib/src/openapi_server
        find ./libs/admin-api-lib/src/admin_api_lib/extractor_api_client -type f -name '*.md' -delete
        cd ./libs/admin-api-lib
        black .
        cd ../..
        ;;
    *)
        echo "Invalid api name"
        ;;
esac
