#!/usr/bin/env bash
set -euo pipefail

echo "Choose which API and its corresponding client to recreate. Possible values are: 0, 1, 2"
echo "0: admin-api-lib"
echo "1: rag-backend"
echo "2: extractor-api-lib"

api_idx="${1:-}"
if [[ -z "${api_idx}" ]]; then
    read -r api_idx
fi

api_name=""
case "${api_idx}" in
    0) api_name="admin-api-lib" ;;
    1) api_name="rag-backend" ;;
    2) api_name="extractor-api-lib" ;;
    *) echo "Invalid api index: ${api_idx}" ; exit 1 ;;
esac

echo "${api_name}"

format_with_black() {
    local dir="$1"
    if command -v black >/dev/null 2>&1; then
        (cd "${dir}" && black .)
        return 0
    fi
    if command -v poetry >/dev/null 2>&1; then
        # Poetry environments are not guaranteed to be installed locally; don't hard-fail on formatting.
        (cd "${dir}" && poetry run black .) || true
        return 0
    fi
    echo "Warning: black not found; skipping formatting for ${dir}" >&2
}

case "${api_name}" in
    "admin-api-lib")
        docker run --user $(id -u):$(id -g) --rm -v $PWD:/local openapitools/openapi-generator-cli@sha256:b35aee2d0f6ffadadcdad9d8fc3c46e8d48360c20b5731a5f47c809d51f67a04 generate -i /local/libs/admin-api-lib/openapi.yaml -g python-fastapi -o /local/libs/admin-api-lib --additional-properties=packageName=admin_api_lib,generateSourceCodeOnly=True
        rm -rf libs/admin-api-lib/src/openapi_server
        format_with_black "./libs/admin-api-lib"
        ;;
    "rag-backend")
        docker run --user $(id -u):$(id -g) --rm -v $PWD:/local openapitools/openapi-generator-cli@sha256:b35aee2d0f6ffadadcdad9d8fc3c46e8d48360c20b5731a5f47c809d51f67a04 generate -i /local/libs/rag-core-api/openapi.yaml -g python-fastapi -o /local/libs/rag-core-api --additional-properties=packageName=rag_core_api,generateSourceCodeOnly=True
        rm -rf libs/rag-core-api/src/openapi_server
        format_with_black "./libs/rag-core-api"
        docker run --user $(id -u):$(id -g) --rm -v $PWD:/local openapitools/openapi-generator-cli@sha256:b35aee2d0f6ffadadcdad9d8fc3c46e8d48360c20b5731a5f47c809d51f67a04 generate -i /local/libs/rag-core-api/openapi.yaml -g python -o /local/libs/admin-api-lib/src --additional-properties=generateSourceCodeOnly=True,packageName=admin_api_lib.rag_backend_client.openapi_client
        format_with_black "./libs/admin-api-lib"
        ;;
    "extractor-api-lib")
        docker run --user $(id -u):$(id -g) --rm -v $PWD:/local openapitools/openapi-generator-cli@sha256:b35aee2d0f6ffadadcdad9d8fc3c46e8d48360c20b5731a5f47c809d51f67a04 generate -i /local/libs/extractor-api-lib/openapi.yaml -g python-fastapi -o /local/libs/extractor-api-lib --additional-properties=packageName=extractor_api_lib,generateSourceCodeOnly=True
        rm -rf libs/extractor-api-lib/src/openapi_server
        format_with_black "./libs/extractor-api-lib"
        docker run --user $(id -u):$(id -g) --rm -v $PWD:/local openapitools/openapi-generator-cli@sha256:b35aee2d0f6ffadadcdad9d8fc3c46e8d48360c20b5731a5f47c809d51f67a04 generate -i /local/libs/extractor-api-lib/openapi.yaml -g python -o /local/libs/admin-api-lib/src   --additional-properties=packageName=admin_api_lib.extractor_api_client.openapi_client,generateSourceCodeOnly=True,testOutput=false
        rm -rf libs/admin-api-lib/src/openapi_server
        find ./libs/admin-api-lib/src/admin_api_lib/extractor_api_client -type f -name '*.md' -delete
        format_with_black "./libs/admin-api-lib"
        ;;
    *)
        echo "Invalid api name"
        ;;
esac
