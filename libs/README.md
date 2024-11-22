# RAG Core library

This repository contains the core of the STACKIT RAG template.
It consists of the following python packages:
- [`1. Rag Core API`](#1-rag-core-api): Core API for a rag solution.
    - [1.1 Requirements](#11-requirements)
    - [1.2 Endpoints](#12-endpoints)
    - [1.3 Replaceable parts](#13-replaceable-parts)
- `2. Admin API lib`: Admin API for a rag solution.
- `3. Extractor API lib`: Extraction API for a rag solution.
- `4. RAG Core lib`: Useful rag-related components that are used in multiple packages.

With the exception of the `RAG Core lib` all of these packages contain an API definition and are easy to adjust for your specific use case.
Each of the packages defines the replaceable parts([1.3 Replaceable Parts](#13-replaceable-parts)), expected types and offer a brief description.

> ⓘ INFO: If you replace parts it is important to keep the name of the component, otherwise the replacing-logic will not work.

This repository also contains a `Dockerfile` that is used to ensure proper linting and testing of the packages.

For an example on how to use the packages, please consult the [use case example repository](TODO: add github link)

## 1. Rag Core API

The rag-core-api contains a default implementation of a RAG.
For a default use case, no adjustments should be required.

The following endpoints are provided by the *backend*:
- `/chat/{session_id}`: The endpoint for chatting.
- `/evaluate`: Will start the evaluation of the RAG using the provided question-answer pairs.
- `/information_pieces/remove`: Endpoint to remove documents from the vector database.
- `/information_pieces/upload`: Endpoint to upload documents into the vector database. These documents need to have been parsed. For simplicity, a LangChain Documents like format is used.

### 1.1 Requirements
All required python libraries can be found in the [pyproject.toml](pyproject.toml) file.
In addition to python libraries, the following system packages are required:
```
build-essential
make
```

### 1.2 Endpoints

#### `/chat/{session_id}`
This endpoint is used for chatting.

### `/evaluate`
Will start the evaluation of the RAG using the provided question-answer pairs.
The file containing the dataset can be set by changing the `RAGAS_DATASET_FILENAME` environment variable, the default is `test_data.json`.
This path can be either an absolute path, or a path relative to the current working directory.

#### `/information_pieces/remove`
Endpoint to remove documents from the vector database.

#### `/information_pieces/upload`
Endpoint to upload documents into the vector database. These documents need to have been parsed. For simplicity, a LangChain Documents like format is used.
Uploaded documents are required to contain the following metadata:
- `document_url` that points to a download link to the source document.
- All documents of the type `IMAGE` require the content of the image encoded in base64 in the `base64_image` key.

### 1.3 Replaceable parts

| Name | Type | Default | Notes |
|----------|---------|--------------|--------------|
| embedder | `rag_core_api.embeddings.embedder.Embedder` | Depends on your settings. Can be `rag_core_api.impl.embeddings.alephalpha_embedder.AlephAlphaEmbedder`, `rag_core_api.impl.embeddings.langchain_community_embedder.LangchainCommunityEmbedder` or `rag_core_api.impl.embeddings.stackit_embedder.StackitEmbedder` | |
| vector_database | `rag_core_api.vector_databases.vector_database.VectorDatabase` | `rag_core_api.impl.vector_databases.qdrant_database.QdrantDatabase` | |
| reranker | `rag_core_api.reranking.reranker.Reranker`  | `rag_core_api.impl.reranking.flashrank_reranker.FlashrankReranker` | Used in the *composed_retriever* |
| composed_retriever | `rag_core_api.retriever.retriever.Retriever` | `from rag_core_api.impl.retriever.composite_retriever.CompositeRetriever` | Handles retrieval, re-ranking, etc. |
| llm_secret_provider | `rag_core_lib.secret_provider.secret_provider.SecretProvider` | Depends on your LLM settings. Can be one of the following: `rag_core_lib.impl.secret_provider.static_secret_provider_stackit.StaticSecretProviderStackit`,  `rag_core_lib.impl.secret_provider.static_secret_provider_alephalpha.StaticSecretProviderAlephAlpha`, `rag_core_lib.impl.secret_provider.no_secret_provider.NoSecretProvider` | The `DynamicSecretProvider` can dynamically change the secret it provides at runtime. |
| large_language_model | `langchain_core.language_models.llms.LLM` | `rag_core_lib.impl.llms.secured_llm.SecuredLLM` | The LLm that is used for all LLM tasks. The `SecuredLLM` takes a secret provider that will configure the LLM with the provided secret. |
| prompt | `str` | `rag_core_api.impl.prompt_templates.answer_generation_prompt.ANSWER_GENERATION_PROMPT` | The prompt used for answering the question. |
| rephrasing_prompt | `str` |  `rag_core_api.impl.prompt_templates.answer_rephrasing_prompt.ANSWER_REPHRASING_PROMPT` | The prompt used for rephrasing the question. The rephrased question (and the *original* question are bot hused for retrival of the documents)|
| langfuse_manager | `rag_core_lib.impl.langfuse_manager.langfuse_manager.LangfuseManager` | `rag_core_lib.impl.langfuse_manager.langfuse_manager.LangfuseManager` | Retrieves additional settings, as well as the prompt from langfuse if available. |
| answer_generation_chain | `rag_core_lib.chains.async_chain.AsyncChain[rag_core_api.impl.graph.graph_state.graph_state.AnswerGraphState, str]` | `rag_core_api.impl.answer_generation_chains.answer_generation_chain.AnswerGenerationChain` | LangChain chain used for answering the question. Is part of the *chat_graph*, |
| rephrasing_chain | `rag_core_lib.chains.async_chain.AsyncChain[rag_core_api.impl.graph.graph_state.graph_state.AnswerGraphState, str]` | `rag_core_api.impl.answer_generation_chains.rephrasing_chainRephrasingChain` | LangChain chain used for rephrasing the question. Is part of the *chat_graph*. |
| chat_graph | `rag_core_api.graph.graph_base.GraphBase` | `rag_core_api.impl.graph.chat_graph.DefaultChatGraph` | Langgraph graph that contains the entire logic for question answering. |
| traced_chat_graph | `rag_core_lib.chains.async_chain.AsyncChain[Any, Any]`| `rag_core_lib.impl.tracers.langfuse_traced_chain.LangfuseTracedGraph` | Wraps around the *chat_graph* and add langfuse tracing. |
| evaluator | `rag_core_api.impl.evaluator.langfuse_ragas_evaluator.LangfuseRagasEvaluator` | `rag_core_api.impl.evaluator.langfuse_ragas_evaluator.LangfuseRagasEvaluator` | The evaulator used in the evaluate endpoint. |
| chat_endpoint |  `rag_core_api.api_endpoints.chat.Chat` |`rag_core_api.impl.api_endpoints.default_chat.DefaultChat` | Implementation of the chat endpoint. Default implementation just calls the *traced_chat_graph* |
