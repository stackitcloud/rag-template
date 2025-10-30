# rag-core-lib

Foundation library for the STACKIT RAG template. It packages all reusable Retrieval-Augmented Generation (RAG) primitives—LLM factories, embedding providers, retry/backoff helpers, Langfuse instrumentation, and configuration models—so higher-level services and libs can stay thin and declarative.

`rag-core-lib` sits at the bottom of the dependency pyramid:

- `rag-core-api` builds the public FastAPI surface on top of it.
- `admin-api-lib` and `extractor-api-lib` reuse the same factories, tracing, and configuration system.
- Service deployments (see `services/*`) can replace components through dependency-injector in the dependency containers of the libs. These dependency containers that can be overridden live in the respective API libs ([`rag-core-api`](https://pypi.org/project/rag-core-api/), [`admin-api-lib`](https://pypi.org/project/admin-api-lib/), [`extractor-api-lib`](https://pypi.org/project/extractor-api-lib/)); [`rag-core-lib`](https://pypi.org/project/rag-core-lib/) itself is a pure building-block library with no injectable services to swap.

## What you get

- **Provider-agnostic LLM & embedding adapters** – OpenAI-compatible, STACKIT model serving, Ollama, plus fake implementations for tests. Selection happens through `RAGClassTypeSettings` / `EmbedderClassTypeSettings`.
- **Shared configuration models** – `pydantic-settings` based schemas for Langfuse, retry/backoff knobs, and feature flags. All values can be set via environment variables or Helm values.
- **LangChain/LangGraph utilities** – Reusable `AsyncRunnable` abstraction, default chat graph wiring, and structured tracing wrappers (`LangfuseTracedRunnable`).
- **Observability tooling** – Langfuse manager, structured logging hooks, and rate-limit aware retry decorator.
- **Safety & testing utilities** – Fake providers, deterministic defaults, and pytest helpers reused across the monorepo.

## Installation

```bash
pip install rag-core-lib
```

Python 3.13 is required.

## Package map at a glance

| Module | Purpose |
| --- | --- |
| `rag_core_lib.impl.settings.*` | Pydantic settings for LLM/embedding providers, Langfuse, retry decorator, and feature toggles. |
| `rag_core_lib.impl.llms.llm_factory` | Produces chat/completion models based on the selected provider (`stackit`, `ollama`, `fake`). |
| `rag_core_lib.impl.embeddings.*` | Embedding adapters with retry wrapping and provider-specific configuration. |
| `rag_core_lib.impl.tracers.*` | Langfuse-backed wrappers to trace LangChain/LangGraph runnables. |
| `rag_core_lib.impl.utils.retry_decorator` | Exponential backoff decorator shared by summarizers, embedders, and other outbound calls. |
| `rag_core_lib.runnables.*` | Asynchronous runnable abstractions used by chat graphs and admin workflows. |
| `rag_core_lib.tracers.*` | Abstractions for tracing runnables. |

## Configuration & environment variables

All settings derive from `pydantic-settings` models, so you can either build them in code or supply environment variables:

- **LLM selection** – `RAG_CLASS_TYPE_LLM_TYPE` (`stackit`, `ollama`, `fake`). Provider-specific keys such as `STACKIT_VLLM_API_KEY` or `OLLAMA_BASE_URL` fill the matching settings models (`StackitVLLMSettings`, `OllamaLLMSettings`).
- **Embedding selection** – `EMBEDDER_CLASS_TYPE_EMBEDDER_TYPE` plus provider-specific variables (for example `STACKIT_EMBEDDER_MODEL`, `OLLAMA_EMBEDDER_MODEL`).
- **Langfuse** – `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, and optional host/project settings configure tracing.
- **Retry defaults** – `RETRY_DECORATOR_MAX_RETRIES`, `RETRY_DECORATOR_BACKOFF_FACTOR`, and related keys feed `RetryDecoratorSettings`. Components can override them through their own settings models (e.g., `StackitEmbedderSettings`).

When deploying through the provided Helm chart, the same keys are exposed under `shared.envs.*`, `backend.envs.*`, and `adminBackend.envs.*`.

## Typical usage

```python
# Assumptions:
# - STACKIT exposes an OpenAI-compatible endpoint, so the default provider works out of the box.
# - You have a STACKIT_VLLM_API_KEY available via environment variables or provide it explicitly below.

from rag_core_lib.impl.llms.llm_factory import chat_model_provider
from rag_core_lib.impl.settings.stackit_vllm_settings import StackitVllmSettings

# Build settings from env or manually override defaults
settings = StackitVllmSettings(
    model="cortecs/Llama-3.3-70B-Instruct-FP8-Dynamic",
    temperature=0.1,
)

# Resolve the LangChain chat model (async or sync)
chat_llm = chat_model_provider(settings)

response = chat_llm.invoke("Tell me about RAG pipelines")
print(response.content)
```

## Related packages

- [`rag-core-api`](../rag-core-api/) – HTTP API layer that exposes chat, evaluation, and information piece endpoints.
- [`admin-api-lib`](../admin-api-lib/) – Document lifecycle orchestration built on top of this foundation.
- [`extractor-api-lib`](../extractor-api-lib/) – Content extraction service using shared retry, settings, and tracing primitives.

## Contributing

Follow the repository conventions (Black, isort, Flake8, pytest). When adding new providers or utilities, include typed settings, update Helm values if required, and add unit tests under `libs/rag-core-lib/tests`. For further instructions see the [Contributing Guide](https://github.com/stackitcloud/rag-template/blob/main/CONTRIBUTING.md).

## License

Licensed under Apache 2.0, see the project license at the root [`LICENSE`](https://github.com/stackitcloud/rag-template/blob/66570f95d8decb431a2ff7626e911d43231914a6/LICENSE) file of this repository.
