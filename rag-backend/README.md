# RAG-Backend
The backend is the main component of doctopus. It handles all connections to the vector database, as well as chatting.

The following endpoints are provided by the *backend*:
- `/chat/{session_id}`: The endpoint for chatting.
- `/source_documents/remove`: Endpoint to remove documents from the vector database.
- `/search`: Endpoint to search documents. This is the same search that is internally used when using the chat-endpoint.
- `/source_documents`: Endpoint to upload documents into the vector database. These documents need to have been parsed. For simplicity a Langchain Documents like format is used.

The rag-backend uses the [rag-core-api](../rag-core-library/rag-core-api/).
In this example only the default behaviour is used and no components are changed. For a documentation of the default behaviour please consult [this](../rag-core-library/rag-core-api/README.md) Readme.

# Requirements
All required python libraries can be found in the [pyproject.toml](pyproject.toml) file.
The backend uses the base Dockerfile of the [rag-core-library](../rag-core-library/) and shares the system requirements with this library.

# Endpoints

## `/chat/{session_id}`
This endpoint is used for chatting.

## `/source_documents/remove`
Endpoint to remove documents from the vector database.

## `/search`
Endpoint to search documents. This is the same search that is internally used when using the chat-endpoint.

## `/source_documents`
Endpoint to upload documents into the vector database. These documents need to have been parsed. For simplicity a Langchain Documents like format is used.
Uploaded documents are required to contain the following metadata:
- `document_url` that points to a download link to the source document.
- `document` need to contain the name of the source document which contains the product name.
- All documents of the type `IMAGE` require the content of the image encoded in base64 in the `base64_image` key.

# Deployment
A detailed explanation of the deployment can be found in the [Readme](../README.md) of the project.
The *helm-chart* used for the deployment can be found [here](../helm-chart/charts/adminfrontend/).
