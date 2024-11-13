# RAG Core API

The rag-core-api contains a default implementation of a RAG.
For a default use case no adjustments should be required, but adjustments can easily be made.

A minimal example use case which replaces the `chat_chain` can be found [here](https://dev.azure.com/schwarzit-wiking/schwarzit.rag-template-sit-stackit/_git/use-case-example)


The following endpoints are provided by the *backend*:
- `/chat/{session_id}`: The endpoint for chatting.
- `/information_pieces/remove`: Endpoint to remove documents from the vector database.
- `/search`: Endpoint to search documents. This is the same search that is internally used when using the chat-endpoint.
- `/information_pieces`: Endpoint to upload documents into the vector database. These documents need to have been parsed. For simplicity a Langchain Documents like format is used.

# Requirements
All required python libraries can be found in the [pyproject.toml](pyproject.toml) file.
In addition to python libnraries the following system packages are required:
```
build-essential
make
```

# Endpoints

## `/chat/{session_id}`
This endpoint is used for chatting.

## `/information_pieces/remove`
Endpoint to remove documents from the vector database.

## `/information_pieces`
Endpoint to upload documents into the vector database. These documents need to have been parsed. For simplicity a Langchain Documents like format is used.
Uploaded documents are required to contain the following metadata:
- `document_url` that points to a download link to the source document.
- All documents of the type `IMAGE` require the content of the image encoded in base64 in the `base64_image` key.
