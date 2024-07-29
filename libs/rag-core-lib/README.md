# RAG Core lib

The rag-core-lib contains components of the `rag-core-api` that are also useful for other services and therefore are packaged in a way that makes it easy to use.
Examples of included components:
- tracing for `langchain` chains using `langfuse`
- settings for multiple LLM and langfsue
- factory for LLMs
- `ContentType` enum of the Documents.
- ...

# Requirements
All required python libraries can be found in the [pyproject.toml](pyproject.toml) file.
In addition to python libnraries the following system packages are required:
```
build-essential
make
```
