# rag-core-api

High-level API layer for the STACKIT [`RAG-Template`](https://github.com/stackitcloud/rag-template). It transforms its own primitives and those from [`rag-core-lib`](../rag-core-lib/) into a production-ready FastAPI surface, exposing chat, evaluation, and document-management endpoints used by [`services/rag-backend`](https://github.com/stackitcloud/rag-template/tree/main/services/rag-backend) and the MCP server of the `RAG-Template`.

## Responsibilities

- **Dependency Injection** – Compose the dependency-injector container to assemble LLMs, embeddings, vector stores, rerankers, and retrievers from [`rag-core-lib`](../rag-core-lib/).
- **API Exposure** – Expose production-ready FastAPI routers for chat, evaluation, and information piece management.
- **Chat Orchestration** – Provide default LangGraph chat orchestration and evaluation pipelines that downstream services can reuse or override.
- **Knowledge base integration** – Manages all interaction with the knowledge base (vector database).

## Feature highlights

- **Chat graph built on LangGraph** – Default `DefaultChatGraph` stitches together language detection, question rephrasing, retrieval (with reranking), answer generation, and Langfuse tracing.
- **Evaluation endpoint** – Ships a Langfuse + RAGAS evaluator so you can score QA datasets against your RAG stack without custom plumbing.
- **Pluggable components** – Replace embedder, vector database, reranker, prompts, or chains via dependency-injector overrides. The defaults target Qdrant + FlashRank but every interface is typed.
- **Consistent models** – Pydantic schemas in `rag_core_api.models` cover request/response payloads for chat, evaluation, and document ingestion.
- **Shared configuration** – Reuses [`rag-core-lib`](../rag-core-lib/) settings so LLMS, embeddings, retries, and Langfuse behave the same way across services.

## Installation

```bash
pip install rag-core-api
```

Requires Python 3.13 and `rag-core-lib`.

## Where it fits in the RAG solution

| Layer | Responsibilities | Package |
| --- | --- | --- |
| RAG primitives | LLMs, embeddings, retry, tracing (shared in multiple libs) | [`rag-core-lib`](../rag-core-lib/) |
| API assembly (this package) | Routers, dependency container, evaluators, graph wiring | `rag-core-api` |
| Service runtime | FastAPI application to customize the API offered by `rag-core-api` | [`services/rag-backend`](https://github.com/stackitcloud/rag-template/tree/main/services/rag-backend) |

Other services (admin backend and MCP server) call the endpoints provided by this package to ingest, delete, and chat with information pieces.

## Module tour

- `dependency_container.py` – Configures dependency-injector providers. Override registrations here to swap providers or inject fakes for tests.
- `api_endpoints/` & `impl/api_endpoints/` – Thin endpoints + abstractions (`Chat`, `InformationPiecesUploader`, etc.) that map HTTP verbs to underlying logic.
- `api/` – Core API definitions, mostly created by API-specs and openapi generator.
- `embeddings/` & `impl/embeddings/` – Embedding classes + abstractions + embedder type definitions.
- `evaluator/` & `impl/evaluator/` – Langfuse + RAGAS evaluator used by `/evaluate` endpoint.
- `graph/` & `impl/graph/` – LangGraph graph + state definitions for chat flows, including language detection, rephrasing, retrieval etc.
- `reranking/` & `impl/reranking/` – Reranking logic for selecting most relevant documents.
- `retriever/` & `impl/retriever/` – Document retrieval logic.
- `impl/settings/` – Configuration settings for dependency injection container components.
- `mapper/` – Information piece 2 langchain documents mapper.
- `prompt_templates/` – Default LLM prompts for answering, rephrasing, and language detection. Override them via Langfuse or dependency injection.
- `embeddings/` – Thin wrappers that adapt embedder instances from `rag-core-lib` for retriever usage. They will be removed in v4.
- `utils/` – Shared utility functions and classes.
- `vector_databases/` & `impl/vector_databases/` – Interfaces plus default implementations (Qdrant, FlashRank).

## Endpoints provided

- `POST /chat/{session_id}` – Conversational RAG (streaming and non-streaming depending on transport). Handles language detection, retrieval, and answer generation.
- `POST /evaluate` – Runs RAGAS evaluation on supplied question/answer datasets; outputs Langfuse traces and aggregate metrics.
- `POST /information_pieces/upload` – Accepts pre-extracted (e.g., from `extractor-api-lib`) and processed (e.g., from `admin-api-lib`) documents for ingestion into the vector store.
- `POST /information_pieces/remove` – Removes stored information pieces by document identifier from the vector store.

Refer to [`libs/README.md`](../README.md#1-rag-core-api) for in-depth API documentation.

## Configuration overview

`rag-core-api` consumes the same environment variables as `rag-core-lib` for provider selection (`RAG_CLASS_TYPE_LLM_TYPE`, `EMBEDDER_CLASS_TYPE_EMBEDDER_TYPE`, Langfuse keys, retry settings). Additional knobs include:

- `QDRANT_URL`, `QDRANT_API_KEY`, `QDRANT_COLLECTION_NAME` – passed into the default `QdrantDatabase`.
- `FLASHRANK_MODEL_NAME` – tuner for FlashRank reranker.
- `RAGAS_DATASET_FILENAME`, `RAGAS_MODEL` – control evaluation dataset and LLM.

The Helm chart supplies these values through `backend.envs.*`. Local development can rely on `.env` configuration (see repository root documentation).

## Typical usage

```python
from rag_core_api.main import app as perfect_rag_app
```

Delivers a full functional API. See [`services/rag-backend/main.py`](https://github.com/stackitcloud/rag-template/blob/main/services/rag-backend/main.py) and [`services/rag-backend/container.py`](https://github.com/stackitcloud/rag-template/blob/main/services/rag-backend/container.py), which compose the API with additional middleware, auth, and deployment-specific wiring.

## Extending the library

1. Subclass the relevant interface (e.g., `VectorDatabase`, `Retriever`, `Chat` endpoint).
2. Register your implementation in the dependency container.
3. Add pytest-based tests under `libs/rag-core-api/tests` that exercise the new component via the container.

Because components depend on interfaces defined here, downstream services can swap behavior without modifying the public API surface.

## Contributing

Ensure new endpoints or adapters remain thin and defer to [`rag-core-lib`](../rag-core-lib/) for shared logic. Run `poetry run pytest` and the configured linters before opening a PR. For further instructions see the [Contributing Guide](https://github.com/stackitcloud/rag-template/blob/main/CONTRIBUTING.md).

## License

Licensed under the project license. See the root [`LICENSE`](https://github.com/stackitcloud/rag-template/blob/main/LICENSE) file.
