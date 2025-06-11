# RAG Core library

This repository contains the core of the STACKIT RAG template.
It provides comprehensive document extraction capabilities including support for files (PDF, DOCX, XML), web sources via sitemaps, and Confluence pages.
It consists of the following python packages:

- [`1. Rag Core API`](#1-rag-core-api)
  - [1.1 Requirements](#11-requirements)
  - [1.2 Endpoints](#12-endpoints)
  - [1.3 Replaceable parts](#13-replaceable-parts)
- [`2. Admin API lib`](#2-admin-api-lib)
  - [2.1 Requirements](#21-requirements)
  - [2.2 Endpoints](#22-endpoints)
  - [2.3 Replaceable parts](#23-replaceable-parts)
- [`3. Extractor API lib`](#3-extractor-api-lib)
  - [3.1 Requirements](#31-requirements)
  - [3.2 Endpoints](#32-endpoints)
  - [3.3 Replaceable parts](#33-replaceable-parts)
- [`4. RAG Core lib`](#4-rag-core-lib)
  - [4.1 Requirements](#41-requirements)

With the exception of the `RAG Core lib` all of these packages contain an API definition and are easy to adjust for your specific use case.
Each of the packages defines the replaceable parts([1.3 Replaceable Parts](#13-replaceable-parts), [2.3 Replaceable Parts](#23-replaceable-parts), [3.3 Replaceable Parts](#33-replaceable-parts)), expected types and offer a brief description.

> ⓘ INFO: If you replace parts it is important to keep the name of the component, otherwise the replacing-logic will not work.

This repository also contains a `Dockerfile` that is used to ensure proper linting and testing of the packages.

For an example on how to use the packages, please consult the [use case example repository](https://github.com/stackitcloud/rag-template)

## 1. RAG Core API

The rag-core-api contains a default implementation of a RAG.
For a default use case, no adjustments should be required.

The following endpoints are provided by the *backend*:

- `/chat/{session_id}`: The endpoint for chatting.
- `/evaluate`: Will start the evaluation of the RAG using the provided question-answer pairs.
- `/information_pieces/remove`: Endpoint to remove documents from the vector database.
- `/information_pieces/upload`: Endpoint to upload documents into the vector database. These documents need to have been parsed. For simplicity, a *LangChain* Documents like format is used.

### 1.1 Requirements

All required python libraries can be found in the [pyproject.toml](./rag-core-api/pyproject.toml) file.
In addition to python libraries, the following system packages are required:

```shell
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
By default `OpenAI` is used by the evaluation. If you want to use the same LLM-class for the evaluation as is used for the chat you have to set the environment variable `RAGA_USE_OPENAI` to `false` and adjust the `RAGAS_MODEL` environment variable to the model-name of your choice.

> 📝 NOTE: Due to quality problems with open-source LLMs, it is recommended to use OpenAI for the evaluation.

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
| embedder | [`rag_core_api.embeddings.embedder.Embedder`](./rag-core-api/src/rag_core_api/embeddings/embedder.py) | Depends on your settings. Can be [`rag_core_api.impl.embeddings.langchain_community_embedder.LangchainCommunityEmbedder`](./rag-core-api/src/rag_core_api/impl/embeddings/langchain_community_embedder.py) or [`rag_core_api.impl.embeddings.stackit_embedder.StackitEmbedder`](./rag-core-api/src/rag_core_api/impl/embeddings/stackit_embedder.py) | Selected by EmbedderClassTypeSettings.embedder_type. |
| vector_database | [`rag_core_api.vector_databases.vector_database.VectorDatabase`](./rag-core-api/src/rag_core_api/vector_databases/vector_database.py) | [`rag_core_api.impl.vector_databases.qdrant_database.QdrantDatabase`](./rag-core-api/src/rag_core_api/impl/vector_databases/qdrant_database.py) | |
| reranker | [`rag_core_api.reranking.reranker.Reranker`](./rag-core-api/src/rag_core_api/reranking/reranker.py)  | [`rag_core_api.impl.reranking.flashrank_reranker.FlashrankReranker`](./rag-core-api/src/rag_core_api/impl/reranking/flashrank_reranker.py) | Used in the *composed_retriever* |
| composed_retriever | [`rag_core_api.retriever.retriever.Retriever`](./rag-core-api/src/rag_core_api/retriever/retriever.py) | [`rag_core_api.impl.retriever.composite_retriever.CompositeRetriever`](./rag-core-api/src/rag_core_api/impl/retriever/composite_retriever.py) | Handles retrieval, re-ranking, etc. |
| large_language_model | `langchain_core.language_models.llms.BaseLLM` | `langchain_community.llms.vllm.VLLMOpenAI`, `langchain_community.llms.Ollama` or `langchain_community.llms.FakeListLLM` | The LLm that is used for all LLM tasks. The default depends on the value of `rag_core_lib.impl.settings.rag_class_types_settings.RAGClassTypeSettings.llm_type`. The FakeListLLM is used for testing |
| prompt | `str` | [`rag_core_api.prompt_templates.answer_generation_prompt.ANSWER_GENERATION_PROMPT`](./rag-core-api/src/rag_core_api/prompt_templates/answer_generation_prompt.py) | The prompt used for answering the question. |
| rephrasing_prompt | `str` |  [`rag_core_api.prompt_templates.question_rephrasing_prompt.ANSWER_REPHRASING_PROMPT`](./rag-core-api/src/rag_core_api/prompt_templates/question_rephrasing_prompt.py) | The prompt used for rephrasing the question. The rephrased question (and the *original* question are both used for retrival of the documents)|
| langfuse_manager | [`rag_core_lib.impl.langfuse_manager.langfuse_manager.LangfuseManager`](./rag-core-lib/src/rag_core_lib/impl/langfuse_manager/langfuse_manager.py) | [`rag_core_lib.impl.langfuse_manager.langfuse_manager.LangfuseManager`](./rag-core-lib/src/rag_core_lib/impl/langfuse_manager/langfuse_manager.py) | Retrieves additional settings, as well as the prompt from langfuse if available. |
| answer_generation_chain | [`rag_core_lib.chains.async_chain.AsyncChain[rag_core_api.impl.graph.graph_state.graph_state.AnswerGraphState, str]`](./rag-core-lib/src/rag_core_lib/chains/async_chain.py) | [`rag_core_api.impl.answer_generation_chains.answer_generation_chain.AnswerGenerationChain`](./rag-core-api/src/rag_core_api/impl/answer_generation_chains/answer_generation_chain.py) | LangChain chain used for answering the question. Is part of the *chat_graph*, |
| rephrasing_chain | [`rag_core_lib.chains.async_chain.AsyncChain[rag_core_api.impl.graph.graph_state.graph_state.AnswerGraphState, str]`](./rag-core-lib/src/rag_core_lib/chains/async_chain.py) | [`rag_core_api.impl.answer_generation_chains.rephrasing_chain.RephrasingChain`](./rag-core-api/src/rag_core_api/impl/answer_generation_chains/rephrasing_chain.py) | LangChain chain used for rephrasing the question. Is part of the *chat_graph*. |
| chat_graph | [`rag_core_api.graph.graph_base.GraphBase`](./rag-core-api/src/rag_core_api/graph/graph_base.py) | [`rag_core_api.impl.graph.chat_graph.DefaultChatGraph`](./rag-core-api/src/rag_core_api/impl/graph/chat_graph.py) | Langgraph graph that contains the entire logic for question answering. |
| traced_chat_graph | [`rag_core_lib.chains.async_chain.AsyncChain[Any, Any]`](./rag-core-lib/src/rag_core_lib/chains/async_chain.py)| [`rag_core_lib.impl.tracers.langfuse_traced_chain.LangfuseTracedGraph`](./rag-core-lib/src/rag_core_lib/impl/tracers/langfuse_traced_chain.py) | Wraps around the *chat_graph* and add langfuse tracing. |
| evaluator | [`rag_core_api.impl.evaluator.langfuse_ragas_evaluator.LangfuseRagasEvaluator`](./rag-core-api/src/rag_core_api/impl/evaluator/langfuse_ragas_evaluator.py) | [`rag_core_api.impl.evaluator.langfuse_ragas_evaluator.LangfuseRagasEvaluator`](./rag-core-api/src/rag_core_api/impl/evaluator/langfuse_ragas_evaluator.py) | The evaulator used in the evaluate endpoint. |
| chat_endpoint | [ `rag_core_api.api_endpoints.chat.Chat`](./rag-core-api/src/rag_core_api/api_endpoints/chat.py) | [`rag_core_api.impl.api_endpoints.default_chat.DefaultChat`](./rag-core-api/src/rag_core_api/impl/api_endpoints/default_chat.py) | Implementation of the chat endpoint. Default implementation just calls the *traced_chat_graph* |
| ragas_llm | `langchain_core.language_models.chat_models.BaseChatModel` | `langchain_openai.ChatOpenAI` or `langchain_ollama.ChatOllama` | The LLM used for the ragas evaluation. |

## 2. Admin API Lib

The Admin API Library contains all required components for file management capabilities for RAG systems, handling all document lifecycle operations. It also includes a default `dependency_container`, that is pre-configured and should fit most use-cases.


The following endpoints are provided by the *admin-api-lib*:

- `/delete_document/{identification}`: Deletes the file from storage (if applicable) and vector database. The `identification` can be retrieved from the `/all_documents_status` endpoint.
- `/document_reference/{identification}`: Returns the document.
- `/all_documents_status`: Return the `identification` and status of all available sources.
- `/upload_file`: Endpoint to upload files.
- `/upload_source`: Endpoint to upload non-file sources.

### 2.1 Requirements

All required python libraries can be found in the [pyproject.toml](./admin-api-lib/pyproject.toml) file.
In addition to python libraries, the following system packages are required:

```
build-essential
make
```

### 2.2 Endpoints

#### `/delete_document/{identification}`

Will delete the document from the connected storage system and will send a request to the `backend` to delete all related Documents from the vector database.

#### `/document_reference/{identification}`

Will return the source document stored in the connected storage system.

> ⓘ INFO: Confluence pages are not stored in the connected storage system. They are only stored in the vector database and can't be retrieved using this endpoint.

#### `/all_documents_status`

Will return a list of all sources for the chat and their current status.


#### `/upload_file`

Files can be uploaded here. This endpoint will process the document in a background and will extract information using the [document-extractor](#3-extractor-api-lib).
The extracted information will be summarized using a LLM. The summary, as well as the unrefined extracted document, will be uploaded to the [rag-core-api](#1-rag-core-api).

#### `/upload_source`

Loads all the content from an arbitrary non-file source using the [document-extractor](#3-extractor-api-lib).
The `type` of the source needs to correspond to an extractor in the [document-extractor](#3-extractor-api-lib). Supported types include `confluence` for Confluence pages and `sitemap` for web content via XML sitemaps.
The extracted information will be summarized using LLM. The summary, as well as the unrefined extracted document, will be uploaded to the [rag-core-api](#1-rag-core-api). An is configured. Defaults to 3600 seconds (1 hour). Can be adjusted by values in the helm chart.

### 2.3 Replaceable parts

| Name | Type | Default | Notes |
|----------|---------|--------------|--------------|
| file_service | [`admin_api_lib.file_services.file_service.FileService`](./admin-api-lib/src/admin_api_lib/file_services/file_service.py) | [`admin_api_lib.impl.file_services.s3_service.S3Service`](./admin_api_lib/src/admin_api_lib/impl/file_services/s3_service.py) | Handles operations on the connected storage. |
| large_language_model | `langchain_core.language_models.llms.BaseLLM` | `langchain_community.llms.vllm.VLLMOpenAI` or `langchain_community.llms.Ollama` | The LLm that is used for all LLM tasks. The default depends on the value of `rag_core_lib.impl.settings.rag_class_types_settings.RAGClassTypeSettings.llm_type` |
| key_value_store | [`admin_api_lib.impl.key_db.file_status_key_value_store.FileStatusKeyValueStore`](./admin-api-lib/src/admin_api_lib/impl/key_db/file_status_key_value_store.py) | [`admin_api_lib.impl.key_db.file_status_key_value_store.FileStatusKeyValueStore`](./admin-api-lib/src/admin_api_lib/impl/key_db/file_status_key_value_store.py) | Is used for storing the available sources and their current state. |
| chunker |  [`admin_api_lib.impl.chunker.chunker.Chunker`](./admin-api-lib/src/admin_api_lib/impl/chunker/chunker.py) | [`admin_api_lib.impl.chunker.text_chunker.TextChunker`](./admin-api-lib/src/admin_api_lib/impl/chunker/text_chunker.py) | Used for splitting the documents in managable chunks. |
| document_extractor | [`admin_api_lib.extractor_api_client.openapi_client.api.extractor_api.ExtractorApi`](./admin-api-lib/src/admin_api_lib/extractor_api_client/openapi_client/api/extractor_api.py) | [`admin_api_lib.extractor_api_client.openapi_client.api.extractor_api.ExtractorApi`](./admin-api-lib/src/admin_api_lib.extractor_api_client/openapi_client/api/extractor_api.py) | Needs to be replaced if adjustments to the `extractor-api` is made. |
| rag_api | [`admin_api_lib.rag_backend_client.openapi_client.api.rag_api.RagApi`](./admin-api-lib/src/admin_api_lib/rag_backend_client/openapi_client/api/rag_api.py) | [`admin_api_lib.rag_backend_client.openapi_client.api.rag_api.RagApi`](./admin-api-lib/src/admin_api_lib/rag_backend_client/openapi_client/api/rag_api.py) | Needs to be replaced if changes to the `/information_pieces/remove` or `/information_pieces/upload` of the [`rag-core-api`](#rag-core-api) are made. |
| summarizer_prompt | `str` | [`admin_api_lib.prompt_templates.summarize_prompt.SUMMARIZE_PROMPT`](./admin-api-lib/src/admin_api_lib/prompt_templates/summarize_prompt.py) | The prompt used of the summarization. |
| langfuse_manager | [`rag_core_lib.impl.langfuse_manager.langfuse_manager.LangfuseManager`](./rag-core-lib/src/rag_core_lib/impl/langfuse_manager/langfuse_manager.py) | [`rag_core_lib.impl.langfuse_manager.langfuse_manager.LangfuseManager`](./rag-core-lib/src/rag_core_lib/impl/langfuse_manager/langfuse_manager.py) | Retrieves additional settings, as well as the prompt from langfuse if available. |
| summarizer |  [`admin_api_lib.summarizer.summarizer.Summarizer`](./admin-api-lib/src/admin_api_lib/summarizer/summarizer.py) | [`admin_api_lib.impl.summarizer.langchain_summarizer.LangchainSummarizer`](./admin-api-lib/src/admin_api_lib/impl/summarizer/langchain_summarizer.py) | Creates the summaries. |
| untraced_information_enhancer |[`admin_api_lib.information_enhancer.information_enhancer.InformationEnhancer`](./admin-api-lib/src/admin_api_lib/information_enhancer/information_enhancer.py) | [`admin_api_lib.impl.information_enhancer.general_enhancer.GeneralEnhancer`](./admin-api-lib/src/admin_api_lib/impl/information_enhancer/general_enhancer.py) |  Uses the *summarizer* to enhance the extracted documents. |
| information_enhancer |  [`rag_core_lib.chains.async_chain.AsyncChain[Any, Any]`](./rag-core-lib/src/rag_core_lib/chains/async_chain.py)| [`rag_core_lib.impl.tracers.langfuse_traced_chain.LangfuseTracedGraph`](./rag-core-lib/src/rag_core_lib/impl/tracers/langfuse_traced_chain.py) |Wraps around the *untraced_information_enhancer* and adds langfuse tracing. |
| document_deleter |[`admin_api_lib.api_endpoints.document_deleter.DocumentDeleter`](./admin-api-lib/src/admin_api_lib/api_endpoints/document_deleter.py) | [`admin_api_lib.impl.api_endpoints.default_document_deleter.DefaultDocumentDeleter`](./admin-api-lib/src/admin_api_lib/impl/api_endpoints/default_document_deleter.py) |  Handles deletion of sources. |
| documents_status_retriever |  [`admin_api_lib.api_endpoints.documents_status_retriever.DocumentsStatusRetriever`](./admin-api-lib/src/admin_api_lib/api_endpoints/documents_status_retriever.py) | [`admin_api_lib.impl.api_endpoints.default_documents_status_retriever.DefaultDocumentsStatusRetriever`](./admin-api-lib/src/admin_api_lib/impl/api_endpoints/default_documents_status_retriever.py) |Handles return of source status. |
| source_uploader | [`admin_api_lib.api_endpoints.source_uploader.SourceUploader`](./admin-api-lib/src/admin_api_lib/api_endpoints/source_uploader.py) | [`admin_api_lib.impl.api_endpoints.default_source_uploader.DefaultSourceUploader`](./admin-api-lib/src/admin_api_lib/impl/api_endpoints/default_source_uploader.py)| Handles data loading and extraction from various non-file sources. |
| document_reference_retriever | [`admin_api_lib.api_endpoints.document_reference_retriever.DocumentReferenceRetriever`](./admin-api-lib/src/admin_api_lib/api_endpoints/document_reference_retriever.py) | [`admin_api_lib.impl.api_endpoints.default_document_reference_retriever.DefaultDocumentReferenceRetriever`](./admin-api-lib/src/admin_api_lib/impl/api_endpoints/default_document_reference_retriever.py) | Handles return of files from connected storage. |
| file_uploader | [`admin_api_lib.api_endpoints.file_uploader.FileUploader`](./admin-api-lib/src/admin_api_lib/api_endpoints/file_uploader.py) | [`admin_api_lib.impl.api_endpoints.default_file_uploader.DefaultFileUploader`](./admin-api-lib/src/admin_api_lib/impl/api_endpoints/default_file_uploader.py) | Handles upload and extraction of files. |

## 3. Extractor API Lib

The Extractor Library contains components that provide document parsing capabilities for various file formats and web sources. It supports extracting content from PDF, DOCX, XML files, as well as web pages via sitemaps and Confluence pages. It also includes a default `dependency_container`, that is pre-configured and is a good starting point for most use-cases. This API should not be exposed by ingress and only used for internally.


The following endpoints are provided by the *extractor-api-lib*:

- `/extract_from_file`: This endpoint extracts the information from files.
- `/extract_from_source`: This endpoint extracts the information from a non-file source.

### 3.1 Requirements

All required python libraries can be found in the [pyproject.toml](./extractor-api-lib/pyproject.toml) file.
In addition to python libraries, the following system packages are required:

```shell
build-essential
make
ffmpeg
poppler-utils
tesseract-ocr
tesseract-ocr-deu
tesseract-ocr-eng
```

### 3.2 Endpoints

#### `/extract_from_file`
This endpoint will extract the information from PDF,PTTX,WORD,XML files.
It will load the files from the connected storage.
The following types of information will be extracted:

- `TEXT`: plain text
- `TABLE`: data in tabular form found in the document

#### `/extract_from_source`

This endpoint will extract data for non-file source.
The type of information that is extracted will vary depending on the source. Supported sources include `confluence` for Confluence pages and `sitemap` for web pages via XML sitemaps.
The following types of information can be extracted:

- `TEXT`: plain text
- `TABLE`: data in tabular form found in the document
- `IMAGE`: image found in the document

For sitemap sources, additional parameters can be provided, e.g.:
- `web_path`: The URL of the XML sitemap to crawl
- `filter_urls`: JSON array of URL patterns to filter pages (optional)
- `header_template`: JSON object for custom HTTP headers (optional)

Technically, all parameters of the `SitemapLoader` from LangChain can be provided.


### 3.3 Replaceable parts

| Name | Type | Default | Notes |
|----------|---------|--------------|--------------|
| file_service | [`extractor_api_lib.file_services.file_service.FileService`](./extractor-api-lib/src/extractor_api_lib/file_services/file_service.py) | [`extractor_api_lib.file_services.s3_service.S3Service`](./extractor-api-lib/src/extractor_api_lib/file_services/s3_service.py) | Handles operations on the connected storage. |
| database_converter | [`extractor_api_lib.document_parser.table_converters.dataframe_converter.DataframeConverter`](./extractor-api-lib/src/extractor_api_lib/document_parser/table_converters/dataframe_converter.py) | [`extractor_api_lib.document_parser.table_converters.dataframe2markdown.DataFrame2Markdown`](./extractor-api-lib/src/extractor_api_lib/document_parser/table_converters/dataframe2markdown.py) | Converts the extracted table from *pandas.DataFrame* to markdown. If you want the table to have another format, this would need to be adjusted. |
| pdf_extractor | [`extractor_api_lib.document_parser.information_extractor.InformationExtractor`](./extractor-api-lib/src/extractor_api_lib/document_parser/information_extractor.py) |[`extractor_api_lib.document_parser.pdf_extractor.PDFExtractor`](./extractor-api-lib/src/extractor_api_lib/document_parser/pdf_extractor.py) | Extractor used for extracting information from PDF documents. |
| ms_docs_extractor |  [`extractor_api_lib.document_parser.information_extractor.InformationExtractor`](./extractor-api-lib/src/extractor_api_lib/document_parser/information_extractor.py) |[`extractor_api_lib.document_parser.ms_docs_extractor.MSDocsExtractor`](./extractor-api-lib/src/extractor_api_lib/document_parser/ms_docs_extractor.py) | Extractor used for extracting information from Microsoft Documents like *.docx, etc. |
| xml_extractor |  [`extractor_api_lib.document_parser.information_extractor.InformationExtractor`](./extractor-api-lib/src/extractor_api_lib/document_parser/information_extractor.py) | [`extractor_api_lib.document_parser.xml_extractor.XMLExtractor`](./extractor-api-lib/src/extractor_api_lib/document_parser/xml_extractor.py) | Extractor used for extracting content from XML documents. |
| all_extractors | `dependency_injector.providers.List[extractor_api_lib.document_parser.information_extractor.InformationExtractor]` | `dependency_injector.providers.List(pdf_extractor, ms_docs_extractor, xml_extractor)` | List of all available extractors. If you add a new type of extractor you would have to add it to this list. |
| general_extractor | [`extractor_api_lib.document_parser.information_extractor.InformationExtractor`](./extractor-api-lib/src/extractor_api_lib/document_parser/information_extractor.py) |[`extractor_api_lib.document_parser.general_extractor.GeneralExtractor`](./extractor-api-lib/src/extractor_api_lib/document_parser/general_extractor.py) | Combines multiple extractors and decides which one to use for the given file format. |
| file_extractor | [`extractor_api_lib.api_endpoints.file_extractor.FileExtractor`](./extractor-api-lib/src/extractor_api_lib/api_endpoints/file_extractor.py) | [`extractor_api_lib.impl.api_endpoints.default_file_extractor.DefaultFileExtractor`](./extractor-api-lib/src/extractor_api_lib/impl/api_endpoints/default_file_extractor.py) | Implementation of the `/extract_from_file` endpoint. Uses *general_extractor*. |
| general_source_extractor | [`extractor_api_lib.api_endpoints.source_extractor.SourceExtractor`](./extractor-api-lib/src/extractor_api_lib/api_endpoints/source_extractor.py) | [`extractor_api_lib.impl.api_endpoints.general_source_extractor.GeneralSourceExtractor`](./extractor-api-lib/src/extractor_api_lib/impl/api_endpoints/general_source_extractor.py) | Implementation of the `/extract_from_source` endpoint.  Will decide the correct extractor for the source. |
| confluence_extractor | [`extractor_api_lib.extractors.information_extractor.InformationExtractor`](./extractor-api-lib/src/extractor_api_lib/extractors/information_extractor.py) | [`extractor_api_lib.impl.extractors.confluence_extractor.ConfluenceExtractor`](./extractor-api-lib/src/extractor_api_lib/extractors/confluence_extractor.py) | Implementation of an esxtractor for the source `confluence`. |
| sitemap_extractor | [`extractor_api_lib.extractors.information_extractor.InformationExtractor`](./extractor-api-lib/src/extractor_api_lib/extractors/information_extractor.py) | [`extractor_api_lib.impl.extractors.sitemap_extractor.SitemapExtractor`](./extractor-api-lib/src/extractor_api_lib/impl/extractors/sitemap_extractor.py) | Implementation of an extractor for the source `sitemap`. Supports XML sitemap crawling with configurable parameters including URL filtering, custom headers, and crawling depth. Uses LangChain's SitemapLoader with support for custom parsing and meta functions via dependency injection. |
| sitemap_parsing_function | `dependency_injector.providers.Factory[Callable]` | [`extractor_api_lib.impl.utils.sitemap_extractor_utils.custom_sitemap_parser_function`](./extractor-api-lib/src/extractor_api_lib/impl/utils/sitemap_extractor_utils.py) | Custom parsing function for sitemap content extraction. Used by the sitemap extractor to parse HTML content from web pages. Can be replaced to customize how web page content is processed and extracted. |
| sitemap_meta_function | `dependency_injector.providers.Factory[Callable]` | [`extractor_api_lib.impl.utils.sitemap_extractor_utils.custom_sitemap_meta_function`](./extractor-api-lib/src/extractor_api_lib/impl/utils/sitemap_extractor_utils.py) | Custom meta function for sitemap content processing. Used by the sitemap extractor to extract metadata from web pages. Can be replaced to customize how metadata is extracted and structured from web content. |

## 4. RAG Core Lib

The rag-core-lib contains components of the `rag-core-api` that are also useful for other services and therefore are packaged in a way that makes it easy to use.
Examples of included components:

- tracing for `LangChain` chains using `Langfuse`
- settings for multiple LLMs and Langfuse
- factory for LLMs
- `ContentType` enum of the Documents.
- ...

### 4.1 Requirements
All required python libraries can be found in the [pyproject.toml](./extractor-api-lib/pyproject.toml) file.
In addition to python libraries the following system packages are required:

```shell
build-essential
make
```
