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

## Requirement handling

The backend uses [poetry](https://python-poetry.org/) for requirement management.
To ensure the requirements are consistent you have to update the `poetry.lock` in addition to the `pyproject.toml` when updating/changing requirements.
Additional requirements like *black* and *flake8* are provided for development. You can install them with `poetry install --with dev` inside of the subproject directory.
> 📝 Before creating a pull request please run `black .`, as well as `flake8 .` and ensure there are no complaints by these tools.

> 📝 Do not update the requirements in the `pyproject.toml` manually. Doing so will invalidate the `poetry.lock`. Use the *poetry* application for this.

### Adding new requirements
Run
```bash
poetry add <package>
```
insisde of the container in order to add new packages. This will automatically update the `pyproject.toml` and the `poetry.lock`.
You can copy the content of these files using the following command
```bash
kubectl cp <namespace>/<backend container name>:/path/to/pyproject.toml ./pyproject.toml
kubectl cp <namespace>/<backend container name>:/path/to/poetry.lock ./poetry.lock
```

System requirements have to manually be added to the `Dockerfile`.

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
