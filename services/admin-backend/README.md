# Admin backend

The main job of the admin-backend is file and source handling. Upload and deletion of files and non-file sources (for example Confluence or sitemaps) should be triggered here.

The following endpoints are provided by the *admin-backend*:
- `/delete_document/{identification}`: Deletes the file/source from storage (if applicable) and the vector database. The `identification` can be retrieved from the `/all_documents_status` endpoint.
- `/document_reference/{identification}`: Returns the stored document (files only).
- `/all_documents_status`: Return the `identification` and status of all available sources.
- `/upload_file`: Endpoint to upload files (PDF, Office, etc.).
- `/upload_source`: Endpoint to upload non-file sources such as Confluence or sitemaps.

# Requirements

All required python libraries can be found in the [pyproject.toml](pyproject.toml) file.
The admin-backend ships its own `Dockerfile`/`Dockerfile.dev` and depends on the [admin-api-lib](../../libs/admin-api-lib/) and [rag-core-lib](../../libs/rag-core-lib/) packages. See the Dockerfiles for system package requirements.

# Endpoints

## `/delete_document/{identification}`

Will delete the document/source from the connected storage system (if applicable) and will send a request to the `backend` to delete all related documents from the vector database.

## `/document_reference/{identification}`

Will return the source document stored in the connected storage system. Non-file sources (for example Confluence or sitemaps) are not stored and therefore cannot be returned here.

## `/all_documents_status`

Will return a list of all available sources and their current status.

> **Note**:
> Might list Documents which are still being processed and are not available yet for chatting.

## `/upload_file`

Files can be uploaded here. This endpoint processes the document in the background and extracts information using the [document-extractor](../document-extractor/).
The extracted information is summarized using an LLM. The summary, as well as the extracted content, will be uploaded to the [rag-backend](../rag-backend/).

## `/upload_source`

Non-file sources can be uploaded here (for example Confluence spaces or sitemaps). The admin backend forwards the source parameters to the [document-extractor](../document-extractor/) and ingests the extracted content into the [rag-backend](../rag-backend/).

## Deployment

A detailed explanation of the deployment can be found in the [project README](../../README.md).
The *helm-chart* used for the deployment can be found in the [infrastructure directory](../../infrastructure/).

## Chunking modes

The admin backend supports multiple chunkers for splitting content before uploading to the vector database:

- Semantic: LangChain `SemanticChunker` with sentence-aware rebalancing
- Recursive (Default): LangChain `RecursiveCharacterTextSplitter`

Select via environment variable `CHUNKER_CLASS_TYPE_CHUNKER_TYPE` set to `semantic` or `recursive`.

Helm users: set `adminBackend.envs.chunker.CHUNKER_CLASS_TYPE_CHUNKER_TYPE` in `infrastructure/rag/values.yaml` to switch. The chart defaults to `recursive` and also exposes tuning keys like `CHUNKER_MAX_SIZE`, `CHUNKER_OVERLAP`, and semantic-specific knobs.

For detailed configuration (min/max size, overlap, semantic thresholds, buffer size, and embeddings), see the libraries guide: libs/README.md section "2.4 Chunker configuration (multiple chunkers)".
