# Admin backend

The main job of the admin-backend is file handling. Upload and deletion of files should be triggered here.

The following endpoints are provided by the *admin-backend*:
- `/delete_document/{id}`: Deletes the file from storage and vector database. The `id` can be retrieved from the `/all_documents` endpoint.
- `/document_reference/{id}`: Returns the document.
- `/all_documents`: Return the id and status of all available documents currently stored.
- `/upload_documents`: Endpoint to upload PDF files.

# Requirements

All required python libraries can be found in the [pyproject.toml](pyproject.toml) file.
The admin-backend uses the base Dockerfile of the [libs](../../libs/) and share the system requirements with this library.

# Endpoints

## `/delete_document/{id}`

Will delete the document from the connected storage system and will send a request to the `backend` to delete all related Documents from the vector database.

## `/document_reference/{id}`

Will return the source document stored in the connected storage system.

## `/all_documents`

Will return a list of all available documents in the connected storage.

> **Note**:
> Might list Documents which are still being processed and are not available yet for chatting.

## `/upload_documents`

PDF files can be uploaded here. This endpoint will process the document in a background and will extract information using the [document-extractor](../document-extractor/).
The extracted information will be summarized using LLM. The summary, as well as the unrefined extracted document, will be uploaded to the [rag-backend](../rag-backend/).

## Deployment

A detailed explanation of the deployment can be found in the [project README](../../README.md).
The *helm-chart* used for the deployment can be found in the [infrastructure directory](../../infrastructure/).

## Chunking modes

The admin backend supports multiple chunkers for splitting content before uploading to the vector database:

- Semantic (default via Helm chart): LangChain `SemanticChunker` with sentence-aware rebalancing
- Recursive (library default when `CHUNKER_MODE` is unset): LangChain `RecursiveCharacterTextSplitter`

Select via environment variable `CHUNKER_MODE` set to `semantic` or `recursive`.

Helm users: set `adminBackend.envs.chunker.CHUNKER_MODE` in `infrastructure/rag/values.yaml` to switch. The chart defaults to `semantic` and also exposes tuning keys like `CHUNKER_MAX_SIZE`, `CHUNKER_OVERLAP`, and semantic-specific knobs.

For detailed configuration (min/max size, overlap, semantic thresholds, buffer size, trimming, and embeddings), see the libraries guide: libs/README.md section "2.4 Chunker configuration (multiple chunkers)".
