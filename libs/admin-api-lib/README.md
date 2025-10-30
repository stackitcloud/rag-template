# admin-api-lib

Document lifecycle orchestration for the STACKIT RAG template. This library exposes a FastAPI-compatible admin surface that receives raw user content, coordinates extraction, summarisation, chunking, and storage, and finally hands normalized information pieces to the core RAG API.

It powers the [`services/admin-backend`](https://github.com/stackitcloud/rag-template/tree/main/services/admin-backend) deployment and is the primary integration point for operators managing their document corpus.

## Responsibilities

1. **Ingestion** – Accept files or external sources from the admin UI or API clients.
2. **Extraction** – Call `extractor-api-lib` to obtain normalized information pieces.
3. **Enhancement** – Summarize and enrich content using LLMs and tracing hooks from `rag-core-lib`.
4. **Chunking** – Split content via recursive or semantic strategies before vectorization.
5. **Persistence** – Store raw assets in S3-compatible storage and push processed chunks to `rag-core-api`.
6. **Status tracking** – Keep track of upload progress and expose document status endpoints backed by KeyDB/Redis.

## Feature highlights

- Ready-to-wire dependency-injector container with sensible defaults for S3 storage, KeyDB status tracking, and background tasks.
- Pluggable chunkers (`recursive` vs `semantic`) and summariser implementations with shared retry/backoff controls.
- Rich Pydantic request/response models covering uploads, non-file sources, and document status queries.
- Thin endpoint implementations that can be swapped or extended while keeping the public API stable.
- Structured tracing (Langfuse) and logging that mirror the behaviour of the chat backend.

## Installation

```bash
pip install admin-api-lib
```

Requires Python 3.13 and `rag-core-lib`.

## Module tour

- `dependency_container.py` – Configures and wires dependency-injection providers. Override registrations here to customise behaviour.
- `api_endpoints/` & `impl/api_endpoints/` – Endpoints + abstractions for file uploads, source uploads, deletions, document status, and reference retrieval.
- `apis/` – Admin API abstractions and implementations.
- `chunker/` & `impl/chunker/` – Abstractions + default text/semantic chunkers and chunker type selection class.
- `extractor_api_client/` & `rag_backend_client/` – Generated OpenAPI clients to talk to the extractor and rag core API services.
- `file_services/` & `impl/file_services/` – Abstract and default S3 interface.
- `summarizer/` & `impl/summarizer/` – Interfaces and LangChain-based summariser that leverage shared retry logic.
- `information_enhancer/` & `impl/information_enhancer/` – Abstractions + page and summary enhancer. Enhancers are centralized with general enhancer.
- `impl/key_db/` – KeyDB/Redis client implementation for document status tracking.
- `impl/mapper/` – Mapper between extractor documents and langchain documents.
- `impl/settings/` – Configuration settings for dependency injection container components.
- `prompt_templates/` – Default summarisation prompt shipped with the template.
- `utils/` – Utility functions and classes.

## Endpoints provided

- `POST /upload_file` – Uploads user selected files
- `POST /upload_source` - Uploads user selected sources
- `DELETE /documents/{identification}` – Deletes a document from the system.
- `GET /document_reference/{identification}` – Retrieves a document reference.
- `GET /all_documents_status` – Retrieves the status of all documents.

Refer to [`libs/README.md`](../README.md#2-admin-api-lib) for in-depth API documentation.

## Configuration overview

All settings are powered by `pydantic-settings`, so you can use environment variables or instantiate classes manually:

- `S3_*` (`S3_ACCESS_KEY_ID`, `S3_SECRET_ACCESS_KEY`, `S3_ENDPOINT`, `S3_BUCKET`) – configure storage for raw uploads.
- `DOCUMENT_EXTRACTOR_HOST` – base URL of the extractor service.
- `RAG_API_HOST` – base URL of the rag-core API.
- `CHUNKER_CLASS_TYPE_CHUNKER_TYPE` – choose `recursive` (default) or `semantic` chunking.
- `CHUNKER_*` (`CHUNKER_MAX_SIZE`, `CHUNKER_OVERLAP`, `CHUNKER_BREAKPOINT_THRESHOLD_TYPE`, …) – fine-tune chunking behaviour.
- `SUMMARIZER_MAXIMUM_INPUT_SIZE`, `SUMMARIZER_MAXIMUM_CONCURRENCY`, `SUMMARIZER_MAX_RETRIES`, etc. – tune summariser limits and retry behaviour.
- `SOURCE_UPLOADER_TIMEOUT` – adjust how long non-file source ingestions wait before timing out.
- `USECASE_KEYVALUE_HOST` / `USECASE_KEYVALUE_PORT` – configure the KeyDB/Redis instance that persists document status.

The Helm chart forwards these values through `adminBackend.envs.*`, keeping deployments declarative. Local development can rely on `.env` as described in the repository root README.

## Typical usage

```python
from admin_api_lib.main import app as perfect_admin_app
```

The admin frontend (`services/frontend` → Admin app) and automation scripts talk to these endpoints to manage the corpus. Downstream, `rag-core-api` receives the processed information pieces and stores them in the vector database.

## Extending the library

1. Implement a new interface (e.g., `Chunker`, `Summarizer`, `FileService`).
2. Register it in `dependency_container.py` or override via dependency-injector in your service.
3. Update or add API endpoints if you expose new capabilities.
4. Cover the new behaviour with pytest-based unit tests under `libs/admin-api-lib/tests`.

Because components depend on interfaces defined here, downstream services can swap behavior without modifying the public API surface.

## Contributing

Ensure new endpoints or adapters remain thin and defer to [`rag-core-lib`](../rag-core-lib/) for shared logic. Run `poetry run pytest` and the configured linters before opening a PR. For further instructions see the [Contributing Guide](https://github.com/stackitcloud/rag-template/blob/main/CONTRIBUTING.md).

## License

Licensed under the project license. See the root [`LICENSE`](https://github.com/stackitcloud/rag-template/blob/main/LICENSE) file.
