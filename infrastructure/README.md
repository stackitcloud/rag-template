# RAG Infrastructure

This repository contains the infrastructure setup for the STACKIT RAG template.

The documentation is structured as follows:

- [1. Components and Configuration Values to Adjust](#1-components-and-configuration-values-to-adjust)
  - [1.1 Langfuse](#11-langfuse)
  - [1.2 Qdrant](#12-qdrant)
  - [1.3 KeyDB](#13-keydb)
  - [1.4 Frontend](#14-frontend)
  - [1.5 Backend](#15-backend)
  - [1.6 MCP Server](#16-mcp-server)
  - [1.7 Use Case Environment Variables](#17-use-case-environment-variables)
- [2. Requirements and Setup Instructions](#2-requirements-and-setup-instructions)
  - [2.1 Local setup instructions](#21-local-setup-instructions)
  - [2.2 Production setup instructions](#22-production-setup-instructions)
- [3. Contributing](#3-contributing)

## 1. Components and Configuration Values to Adjust

This Repository contains the helm chart for the following RAG components:

- [Langfuse](https://langfuse.com/) (dependency)
- [Qdrant](https://qdrant.tech/) (dependency)
- [KeyDB](https://docs.keydb.dev/) (dependency)
- Frontend
- Backend
- MCP Server

> 📝 NOTE: Only the settings you are most likely to adjust are listed here. For all available settings please take a look at the [values.yaml](rag/values.yaml).

Except all `backend` services all components can be disabled and exchanged with components of your choice.
This can be done by overwriting the following values in your `values.yaml`

```yaml
features:
  ollama:
    enabled: false
  minio:
    enabled: false
  langfuse:
    enabled: true
  qdrant:
    enabled: true
  frontend:
    enabled: true
  keydb:
    enabled: true
  mcp:
    enabled: true
```

It is optional to provide an `imagePullSecret`. If you need one for pulling the images belonging to the rag-template you can either provide your own already existing secret by using the example below:

```yaml
shared:
  imagePullSecret:
    create: false
    name: cr-credentials
```

Or you can create a secret with your own values like this:

```yaml
shared:
  imagePullSecret:
    create: true
    name: cr-credentials
    auths:
      username: ...
      pat: ...
      email: ...
```

For local development, the `imagePullSecret` is not necessary.

### 1.1 Langfuse

You can deploy Langfuse with initial values for the public and secret API keys. The respective values are shown below:

```yaml
# For production deployment with external PostgreSQL
langfuse:
  postgresql:
    deploy: true # If you want to use an external PostgreSQL, set this to false
  langfuse:
    additionalEnv:
    - name: DATABASE_URL
      value: "postgresql://username:password@postgres-host:5432/langfuse" # Your PostgreSQL connection string
    - name: LANGFUSE_INIT_ORG_ID
      value: ... # Optional: Pre-create organization
    - name: LANGFUSE_INIT_PROJECT_ID
      value: ... # Optional: Pre-create project
    - name: LANGFUSE_INIT_PROJECT_PUBLIC_KEY
      value: ... # Optional: Set initial public key
    - name: LANGFUSE_INIT_PROJECT_SECRET_KEY
      value: ... # Optional: Set initial secret key
    - name: LANGFUSE_INIT_USER_EMAIL
      value: ... # Optional: Create initial user
    - name: LANGFUSE_INIT_USER_NAME
      value: ... # Optional: Initial user name
    - name: LANGFUSE_INIT_USER_PASSWORD
      value: ... # Optional: Initial user password
```

Besides, you can deploy Langfuse in a two-step approach. First, you deploy Langfuse without the API keys, and then you can create the API keys via the Web UI. Therefore, after deployment, you have to sign up in the Web UI and create a project in the local Langfuse instance, create API keys via the settings; see below.

![langfuse-api-key](./figures/langfuse-api-access.png)

Default values for the deployment are provided in the `rag/values.yaml` file under the `langfuse` key.

> 📝 NOTE: Langfuse utilizes a PostgreSQL database under the hood.
>In production, it is recommended to use the [STACKIT Postgresflex](https://www.stackit.de/en/product/stackit-postgresql-flex/) instead of the Postgres deployment bundled with Langfuse.
>You have to change the following values to use [STACKIT Postgresflex](https://www.stackit.de/en/product/stackit-postgresql-flex/):
>
>```yaml
>langfuse:
>  deploy: false
>  host: ...
>  auth:
>    username: ...
>    password: ...
>    database: ...
>```
>
>All values containing `...` are placeholders and have to be replaced with real values.

### 1.2 Qdrant

The deployment of the Qdrant can be disabled by setting the following value in the helm-chart:

```yaml
features:
  qdrant:
    enabled: false
```

For more information on the values for the Qdrant helm chart please consult the [README of the Qdrant helm chart](https://github.com/qdrant/qdrant-helm/blob/qdrant-1.12.3/charts/qdrant/README.md).

> ⓘ INFO: Qdrant is a subchart of this helm chart with the name `qdrant`. Therefore, all configuration values for Qdrant are required to be under the key `qdrant`, e.g. for changing the `replicaCount` you have to add the following value:

```yaml
qdrant:
  replicaCount: 3
```

### 1.3 KeyDB

The usage of the KeyDB is **only recommended for development** purposes. KeyDB is used as alternative to Redis to store the state of each uploaded document. The Admin Backend uses the key-value-pairs of the KeyDB to keep track of the current state of the RAG sources. Note, sources include documents as well as non-document sources like confluence.

In **production**, the usage of a fully-managed Redis instance (e.g. provided by STACKIT) is recommended. The following parameters need to be adjusted in the `values.yaml` file:

```yaml
# For production: Use external Redis instead of KeyDB
adminBackend:
  envs:
    keyValueStore:
      USECASE_KEYVALUE_HOST: ... # Your Redis host (e.g., redis.yourdomain.com)
      USECASE_KEYVALUE_PORT: 6379

features:
  keydb:
    enabled: false # Disable KeyDB for production

langfuse:
  valkey:
    deploy: false # Use Redis instead of KeyDB
  langfuse:
    additionalEnv:
    - name: REDIS_CONNECTION_STRING
      value: "redis:"
```

### 1.4 Frontend

The following values should be adjusted for the deployment:

```yaml
frontend:
  envs:
    vite:
      # Required: Update these URLs for your deployment
      VITE_API_URL: "https://rag.yourdomain.com/api" # Your backend API URL
      VITE_CHAT_URL: "https://rag.yourdomain.com" # Your chat frontend URL
      VITE_ADMIN_URL: "https://admin.rag.yourdomain.com" # Your admin frontend URL
      VITE_ADMIN_API_URL: "https://admin.rag.yourdomain.com/api" # Your admin API URL

  ingress:
    host:
      name: ... # Your domain name (e.g., rag.yourdomain.com)

  secrets:
    viteAuth:
      # Required: Credentials for backend authentication
      VITE_AUTH_USERNAME: ... # Username for basic auth
      VITE_AUTH_PASSWORD: ... # Password for basic auth
```

### 1.5 Backend

The following values should be adjusted for the deployment:

```yaml
backend:
  secrets:
    # Required: Basic authentication for the backend API
    basicAuth: ... # Set your basic auth credentials

    # Required: Langfuse API keys for observability
    langfuse:
      publicKey: ... # Your Langfuse public key
      secretKey: ... # Your Langfuse secret key

    # Required: API keys for your chosen LLM provider
    # STACKIT LLM provider
    stackitEmbedder:
      apiKey: ... # Your STACKIT embedder API key
    stackitVllm:
      apiKey: ... # Your STACKIT vLLM API key

    # Optional: Only needed if using RAGAS evaluation with OpenAI
    ragas:
      openaiApikey: ... # Your OpenAI API key for RAGAS evaluation

  envs:
    # Required: Choose your LLM and embedder providers
    ragClassTypes:
      RAG_CLASS_TYPE_LLM_TYPE: "stackit" # Options: "stackit", "ollama"
    embedderClassTypes:
      EMBEDDER_CLASS_TYPE_EMBEDDER_TYPE: "stackit" # Options: "stackit", "ollama"

    # Optional: Adjust retriever settings for your use-case
    # These control how many documents are retrieved from the vector database
    retriever:
      RETRIEVER_THRESHOLD: 0.3
      RETRIEVER_K_DOCUMENTS: 10
      RETRIEVER_TOTAL_K: 7
      RETRIEVER_SUMMARY_THRESHOLD: 0.3
      RETRIEVER_SUMMARY_K_DOCUMENTS: 10
      RETRIEVER_TABLE_THRESHOLD: 0.3
      RETRIEVER_TABLE_K_DOCUMENTS: 10
      RETRIEVER_IMAGE_THRESHOLD: 0.7
      RETRIEVER_IMAGE_K_DOCUMENTS: 10
    # Optional: Adjust Reranker settings for your use-case
    reranker:
      RERANKER_K_DOCUMENTS: 5
      RERANKER_MIN_RELEVANCE_SCORE: 0.001
    # Error messages that get returned in case of special events.
    errorMessages:
      ERROR_MESSAGES_NO_DOCUMENTS_MESSAGE: "I'm sorry, my responses are limited. You must ask the right questions."
      ERROR_MESSAGES_NO_OR_EMPTY_COLLECTION: "No documents were provided for searching."
      ERROR_MESSAGES_HARMFUL_QUESTION: "I'm sorry, but harmful requests cannot be processed."
      ERROR_MESSAGES_NO_ANSWER_FOUND: "I'm sorry, I couldn't find an answer with the context provided."
    # Settings for the evaluation. You can specify the datasetname, as well as the path (in the container) where the dataset is located.
    langfuse:
      LANGFUSE_DATASET_NAME: "test_ds"
      LANGFUSE_DATASET_FILENAME: "/app/test_data.json"

    ragas:
      RAGAS_IS_DEBUG: false
      RAGAS_MODEL: "gpt-4o-mini"
      RAGAS_USE_OPENAI: true
      RAGAS_MAX_CONCURRENCY: "5"

  ingress:
    host:
      name: ... # Your domain name (e.g., rag.yourdomain.com)

# Required for production deployments
shared:
  config:
    dns:
    - ... # Your primary domain (e.g., rag.yourdomain.com)
    - ... # Your admin domain (e.g., admin.rag.yourdomain.com)

    tls:
      enabled: true
      host: ... # Your primary domain for TLS certificate
      secretName: tls-certificate
      issuerName: letsencrypt-cluster-issuer # Adjust if using different cert issuer

```

> 📝 NOTE: Values marked with `...` are placeholders that **must** be replaced with your actual values for deployment.

> ⓘ INFO: This deployment comes with multiple options. You can change the `backend.envs.ragClassTypes.RAG_CLASS_TYPE_LLM_TYPE` in `./rag/values.yaml` to one of the following values:
>
> - `stackit`: Uses the STACKIT LLM as an LLM provider.
> - `ollama`: Uses Ollama as an LLM provider.
>
> The same options are also available for the `backend.envs.embedderClassTypes.EMBEDDER_CLASS_TYPE_EMBEDDER_TYPE`.

### 1.6 MCP Server

The MCP (Model Context Protocol) Server runs as a sidecar container alongside the main RAG backend and provides MCP-compatible access to the RAG system. It can be enabled or disabled using the following configuration:

```yaml
features:
  mcp:
    enabled: true # Set to false to disable MCP server
```

When enabled, the MCP server can be configured with the following values:

```yaml
backend:
  mcp:
    name: "mcp" # Name of the MCP server container
    port: "8000" # Port on which the MCP server listens (default: 8000)
    host: "0.0.0.0" # Host address for the MCP server
    image:
      repository: ghcr.io/stackitcloud/rag-template
      name: rag-mcp
      pullPolicy: Always
      tag: "v1.0.0"
```

The MCP server exposes the following endpoints:

- **Development**: Accessible via `/mcp` path through port-forward on port 9090 in Tilt setup
- **Production**: Accessible via `/mcp` path through the main ingress

> 📝 NOTE: The MCP server provides two main tools:
>
> - `chat_simple`: Basic question-answering without conversation history
> - `chat_with_history`: Advanced chat interface with conversation history and returns structured responses with `answer`, `finish_reason`, and `citations`.
>
> For detailed information about MCP server configuration and usage, see the [MCP Server README](../mcp-server/README.md).

### 1.7 Use Case Environment Variables

To add use case specific environment variables, the `usecase` secret and configmap can be used. Adding new environment variables to the `usecase` secret and configmap can be done by adding the following values to the `values.yaml` file:

```yaml
shared:
  envs:
    usecase:
      USECASE_CONFIG_MAP_ENV_VAR: ...
  secrets:
    usecase:
      USECASE_SECRET_ENV_VAR: ...
```

## 2. Requirements and Setup Instructions

The following section describes the requirements for the infrastructure setup and provides instructions for the local and production setup.

> 📝 NOTE: *Windows users*: make sure you use WSL for infrastructure setup & orchestration.

### 2.1 Local setup instructions

The following is a list of the dependencies. If you miss one of the dependencies, click on the name and follow the installation instructions.

- [*k3d*](https://k3d.io/v5.6.0/#installation)
- [*helm*](https://helm.sh/docs/intro/install/)

For local deployment it is recommended to use [*tilt*](https://docs.tilt.dev/install.html).

In the following, the *k3d* cluster setup and the setup inside the *k3d* will be explained.

#### 2.1.1 k3d Cluster Setup

Assumption: You are in the root directory of this repository. A local registry is created at `registry.localhost:5000`.

```shell
cd local-cluster-setup && bash setup-k3d-cluster.sh
```

Note: only tested under Linux (Ubuntu 22.04 LTS)

In case of an error, you have to manually set up the *k3d* cluster and the nginx ingress controller (if necessary).

##### (Optional) Setup-check

Images can be pushed, pulled, removed etc. to/from the local repo, see:

```shell
docker pull busybox:latest
docker tag busybox:latest registry.localhost:5000/busybox:latest
docker push registry.localhost:5000/busybox:latest
docker run --rm registry.localhost:5000/busybox:latest /bin/sh -c "echo '<<< stackiteers say \"hello\" to you ]:-> >>>'"
docker image rm registry.localhost:5000/busybox:latest
```

It is time to check if the cluster works with the local repo :sunglasses: :

```shell
kubectl run test-pod-name --image registry.localhost:5000/busybox:latest -- /bin/sh -c "while true; do echo '<<< stackiteers say \"hello\" to you ]:-> >>>'; sleep 1; done"
kubectl wait --for=condition=ready pod test-pod-name
kubectl logs test-pod-name
kubectl delete po test-pod-name
```

Under linux, `*.localhost` should be resolved :fire:, otherwise you have to adjust the hosts file. In windows and macOS append the hosts file with the following line:

```shell
127.0.0.1 registry.localhost
```

More information about adjusting the hosts file can be found in the section 'Access via ingress'.

#### 2.1.2 Tilt Deployment

The following will spin up the microservices in *k3d*

```shell
tilt up
```

Environment variables are loaded from the `.env` file in the same directory the `Tiltfile` is located. The [use case README](../README.md#installation--usage) should contain a list of the required variables.

The Tilt UI is available at [http://localhost:10350/](http://localhost:10350/)

If you want to access MinIO/Qdrant etc. just click the resource in the UI. In the upper corner will be the link, to access the resource.

To enable debugging, follow instructions in [README](../README.md).

The following will delete everything deployed with `tilt up` command

```shell
tilt down
```

#### 2.1.3 Access via Ingress

To access the ingress by its hostname, the hosts file need to be adjusted. On *linux/macOS*, you have to adjust `/etc/hosts` as follows.

```shell
echo "127.0.0.1 rag.localhost" | sudo tee -a /etc/hosts > /dev/null
```

Afterwards, the services are accessible from [http://rag.localhost](http://rag.localhost)

Note: The command above has only been tested on *Ubuntu 22.04 LTS*.

On *Windows* you can adjust the hosts file as described [here](https://docs.digitalocean.com/products/paperspace/machines/how-to/edit-windows-hosts-file/).

### 2.2 Production Setup Instructions

The *helm* chart provided in this repository requires a *NGINX Ingress Controller*, (e.g. [Bitnami package for NGINX Ingress Controller](https://artifacthub.io/packages/helm/bitnami/nginx-ingress-controller)).
If you want to use SSL-Encryption, a Cert-Manager is also required. An installation tutorial for the *STACKIT Cert-Manager Webhook* can be found in the [Github Repository](https://github.com/stackitcloud/stackit-cert-manager-webhook).
For deployment of the *NGINX Ingress Controller* and a cert-manager, the following helm chart can be used:

[base-setup](server-setup/base-setup/Chart.yaml)

The email [here](server-setup/base-setup/templates/cert-issuer.yaml) should be changed from `<replace@me.com>` to a real email address.

## 3. Contributing

Please see the [CONTRIBUTING.md](CONTRIBUTING.md) file for more information on how to contribute to the RAG Infrastructure.
