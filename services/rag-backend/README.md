# RAG backend

The RAG backend provides the chat and retrieval API for the template. It uses
the shared RAG libraries to connect uploaded content, embeddings, vector
storage, and language model calls.

# Requirements

All required Python libraries can be found in the [pyproject.toml](pyproject.toml)
file. The backend ships its own `Dockerfile` and `Dockerfile.dev` and depends on
the [rag-core-api](../../libs/rag-core-api/) and
[rag-core-lib](../../libs/rag-core-lib/) packages.

# Deployment

A detailed explanation of the deployment can be found in the
[project README](../../README.md). The Helm chart used for deployment is in the
[infrastructure directory](../../infrastructure/).
