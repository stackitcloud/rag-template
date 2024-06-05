docker run --user $(id -u):$(id -g) --rm -v $PWD:/local openapitools/openapi-generator-cli generate -i /local/openapi.yaml -g python-fastapi -o /local
