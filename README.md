# RAG Template

Welcome to the STACKIT RAG Template! This is a basic example of how to use the RAG-API libraries, designed to help you get started with building AI-powered chatbots and document management systems 📖 (see [main.py](./services/rag-backend/main.py), [container.py](./services/rag-backend/container.py) and [chat_endpoint.py](./services/rag-backend/chat_endpoint.py)).

<!-- The RAG (Retrieve, Augment, Generate) template is here to simplify your journey into developing and deploying AI-driven applications in a kubernetes cluster. It provides a comprehensive guide, including local setup as well as production deployment instructions. Whether you're a developer, data scientist, or researcher, this template offers everything you need to build and deploy your own RAG solution.  -->


## Features 🚀

**Document Management**: Supports PDFs, DOCX, PPTX, XML, EPUB documents and websource via confluence as well as sitemaps.

**AI Integration**: Multiple LLM and embedder providers for flexibility.

**Tracing & Evaluation**: Tools for monitoring and assessing system performance.

**Frontends**: User-friendly interfaces for easy interaction.

**Security**: Basic authentication for secure access.

**Deployment**: Options for both local and production
environments.

The template supports multiple LLM (Large Language Model) providers, such as STACKIT and Ollama, giving you flexibility in choosing the best fit for your project. It also integrates with Langfuse for enhanced monitoring and analytics, and uses S3 object storage for document management. 📁

## Table of Contents

- [1. Getting Started](#1-getting-started)
    - [1.1 Components](#11-components)
    - [1.2 Requirements](#12-requirements)
    - [1.3 Usage](#13-usage)
    - [1.4 Local setup instructions](#14-local-setup-instructions)
- [2. Deployment to server](#2-deployment-to-server)
    - [2.1 Server provisioning](#21-server-provisioning)
    - [2.2 Langfuse](#22-langfuse)
- [3. Build and Test](#3-build-and-test)
- [4. Contribution Guidelines](#4-contribution-guidelines)



## 1. Getting Started
A [`Tiltfile`](./Tiltfile) is provided to get you started :rocket:. If Tilt is new for you, and you want to learn more about it, please take a look at the [Tilt guides](https://docs.tilt.dev/tiltfile_authoring.html).

### 1.1 Components

This repository contains the following components:

- [*services/rag-backend*](#111-rag-backend): The main component of the RAG.
- [*services/admin-backend*](#112-admin-backend): Manages user documents and confluence spaces, interacts with document-extractor and rag-backend.
- [*services/document-extractor*](#113-document-extractor): Extracts content from documents and Confluence spaces.
- [*services/mcp-server*](#114-mcp-server): Model Context Protocol server that provides MCP-compatible access to the RAG system.
- [*services/frontend*](#115-frontend): Frontend for both, chat and admin APIs.
- [*infrastructure*](#116-infrastructure): Contains the helm-chart and other files related to infrastructure and deployment.
- [*libs*](#117-libs): Contains the API-libraries that are used to construct the backend-services in this repository.

#### 1.1.1 Rag backend
The backend is the main component of the RAG. It handles all connections to the vector database, as well as chatting.

All components are provided by the *rag-core-api*. For further information on endpoints and requirements, please consult [the libs README](./libs/README.md#1-rag-core-api).

#### 1.1.2 Admin backend

The Admin backend is a component that is used to manage user provided documents and confluence spaces. It communicates with the document-extractor to extract the content from the documents and confluence spaces. Besides, it communicates with the rag-backend to store the document chunks into the vector database. For storing the documents, it uses the S3 object storage. It also acts as interface to provide the current status of the documents and confluence spaces in the RAG.

All components are provided by the *admin-api-lib*. For further information on endpoints and requirements, please consult [the libs README](./libs/README.md#2-admin-api-lib).

#### 1.1.3 Document extractor

The Document extractor is a component that is used to extract the content from the documents and confluence spaces.

All components are provided by the *extractor-api-lib*. For further information on endpoints and requirements, please consult [the libs README](./libs/README.md#3-extractor-api-lib).

#### 1.1.4 MCP Server

The MCP Server is a Model Context Protocol (MCP) server that provides a bridge between MCP-compatible clients and the RAG backend. It enables AI assistants and other tools to interact with the RAG system through standardized MCP tools.

The MCP server runs as a sidecar container alongside the main RAG backend and exposes two main tools:

- `chat_simple`: Basic question-answering without conversation history
- `chat_with_history`: Advanced chat interface with conversation history and returns structured responses with `answer`, `finish_reason`, and `citations`.

##### Configuring Tool Documentation

The MCP server supports customizable documentation for its tools through environment variables. This allows you to customize the descriptions, parameter explanations, and examples shown to MCP clients. All documentation configuration uses the `MCP_` prefix and can be configured with the [values.yaml](infrastructure/rag/values.yaml). The following configuration options exist:

**For `chat_simple` tool:**

- `MCP_CHAT_SIMPLE_DESCRIPTION`: Main description of the tool
- `MCP_CHAT_SIMPLE_PARAMETER_DESCRIPTIONS`: JSON object mapping parameter names to descriptions
- `MCP_CHAT_SIMPLE_RETURNS`: Description of the return value
- `MCP_CHAT_SIMPLE_NOTES`: Additional notes about the tool
- `MCP_CHAT_SIMPLE_EXAMPLES`: Usage examples

**For `chat_with_history` tool:**

- `MCP_CHAT_WITH_HISTORY_DESCRIPTION`: Main description of the tool
- `MCP_CHAT_WITH_HISTORY_PARAMETER_DESCRIPTIONS`: JSON object mapping parameter names to descriptions
- `MCP_CHAT_WITH_HISTORY_RETURNS`: Description of the return value
- `MCP_CHAT_WITH_HISTORY_NOTES`: Additional notes about the tool
- `MCP_CHAT_WITH_HISTORY_EXAMPLES`: Usage examples


For further information on configuration and usage, please consult the [MCP Server README](./services/mcp-server/README.md).

#### 1.1.5 Frontend

The frontend provides user-friendly interfaces for both chat and document management. It consists of two main applications:

- **Chat App**: Interface for interacting with the RAG system
- **Admin App**: Interface for managing documents and system configuration

For further information, please consult the [Frontend README](./services/frontend/README.md).

#### 1.1.6 Infrastructure

Contains the Helm chart and other files related to infrastructure and deployment, including Kubernetes manifests, Terraform scripts, and cluster setup tools.

For further information, please consult the [Infrastructure README](./infrastructure/README.md).

#### 1.1.7 Libs

Contains the API libraries that are used to construct the backend services in this repository. This includes core RAG functionality, admin APIs, and document extraction APIs.

For further information, please consult the [Libs README](./libs/README.md).

### 1.2 Requirements

> 📝  *Windows users*: make sure you use wsl for infrastructure setup & orchestration.

Every package contains a `pyproject.toml` with the required Python packages.
[Poetry](https://python-poetry.org/)  is used for requirement management.
To ensure the requirements are consistent, you have to update the `poetry.lock` in addition to the `pyproject.toml` when updating/changing requirements. Additional requirements like *black* and *flake8* are provided for development. You can install them with `poetry install --with dev` inside the package-directory.

> 📝 Do not update the requirements in the `pyproject.toml` manually. Doing so will invalidate the `poetry.lock`. Use the *poetry* application for this.

#### Adding new requirements
Run
```bash
poetry add --lock <package>
```
insisde of the package directory in order to add new packages. This will automatically update the `pyproject.toml` and the `poetry.lock`.

System requirements have to manually be added to the `Dockerfile`.

### 1.3 Usage
This example of the rag-template includes a WebUI for document-management, as well as for the chat.

After following the setup instruction for either the [local installation](#-local-setup-instructions) or the [installation on a server](#-Deployment-to-server) the WebUI is accessible via the configured ingress.
After uploading a file in the document-management WebUI you can start asking question about your document in the chat WebUI.

For a complete documentation of the available REST-APIs, please consult [the libs README](./libs/README.md).

If you want to replace some dependencies with you own dependencies, see the services/rag-backend folder, especially the [main.py](./services/rag-backend/main.py), [container.py](./services/rag-backend/container.py) and [chat_endpoint.py](./services/rag-backend/chat_endpoint.py).

### 1.4 Local setup instructions

The following is a list of the dependencies. If you miss one of the dependencies, click on the name and follow the install instructions.

- [*k3d*](https://k3d.io/v5.6.0/#installation)
- [*helm*](https://helm.sh/docs/intro/install/)
- [*tilt*](https://docs.tilt.dev/install.html)

For local deployment, a few env variables need to be provided by an `.env` file (here: .)

The `.env` needs to contain the following values:

```dotenv
BASIC_AUTH=Zm9vOiRhcHIxJGh1VDVpL0ZKJG10elZQUm1IM29JQlBVMlZ4YkpUQy8K

S3_ACCESS_KEY_ID=...
S3_SECRET_ACCESS_KEY=...

VITE_AUTH_USERNAME=...
VITE_AUTH_PASSWORD=...

RAGAS_OPENAI_API_KEY=...

STACKIT_VLLM_API_KEY=...
STACKIT_EMBEDDER_API_KEY=...

# ONLY necessary, if no init values are set. if init values are set,
# the following two values should match the init values or be commented out
# or be created via the langfuse UI.
LANGFUSE_PUBLIC_KEY=pk-lf-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
LANGFUSE_SECRET_KEY=sk-lf-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

```

This results in a basic auth with username=`foo` and password=`bar`.

> 📝 NOTE: All values containing `...` are placeholders and have to be replaced with real values.
> This deployment comes with multiple options. You change the `global.config.envs.rag_class_types.RAG_CLASS_TYPE_LLM_TYPE` in the helm-deployment to on of the following values:
>
> - `stackit`: Uses an OpenAI compatible LLM, like the STACKIT model serving service.
> - `ollama`: Uses ollama as an LLM provider.
>

#### 1.4.1 Environment Variables Setup

Before running the application, you need to configure environment variables. Copy the provided example file and fill in your values:

```shell
cp .env.template .env
```

Edit the `.env` file with your actual configuration values. The [`.env.template`](./.env.template) file contains all required and optional environment variables with descriptions.

> 📝 **Important**: The `.env` file is required for the application to work.

In the following, the *k3d* cluster setup and the setup inside the *k3d* will be explained.

#### 1.4.2 *k3d* cluster setup

For a detailed explanation of the *k3d* setup, please consult the [infrastructure README](./infrastructure/README.md).

#### 1.4.3 Tilt deployment

If this is the first time you are starting the `Tiltfile` you have to build the helm-chart first.
This can be done with the following command from the root of the git-repository:

```shell
cd infrastructure/rag;helm dependency update; cd ../..
```

> 📝 NOTE: The configuration of the `Tiltfile` requires `features.frontend.enabled=true`, `features.keydb.enabled=true`, `features.langfuse.enabled=true` and `features.qdrant.enabled=true`.

After the initial build of the helm chart *Tilt* is able to update the files.

The following will tear up the microservices in *k3d*.
For the following steps, it is assumed your current working directory is the root of the git-repository.

```shell
tilt up
```

Environment variables are loaded from `.env` file in the root of this git-repository.

The *Tilt* UI is available at [http://localhost:10350/](http://localhost:10350/)

If you want to access *Qdrant* etc. just click the resource in the UI. In the upper corner will be the link, to access the resource.

To enable debugging, start tilt with the following command:

```shell
tilt up -- --debug=true
```

The backend will wait until your debugger is connected before it will fully start.
The debugger used is `debugpy` which is compatible with VS Code.
To connect the debugger, you can use the following `launch.json`:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "rag_backend",
            "type": "python",
            "request": "attach",
            "host": "localhost",
            "port": 31415,
            "justMyCode": false,
            "env": {
                "PYDEVD_WARN_EVALUATION_TIMEOUT": "600",
                "PYDEVD_THREAD_DUMP_ON_WARN_EVALUATION_TIMEOUT": "600"
            },
            "pathMappings": [
                {
                    "localRoot": "${workspaceFolder}/services/rag-backend",
                    "remoteRoot": "/app/services/rag-backend"
                },
                {
                    "localRoot": "${workspaceFolder}/libs/rag-core-lib",
                    "remoteRoot": "/app/libs/rag-core-lib"
                },
                {
                    "localRoot": "${workspaceFolder}/libs/rag-core-api",
                    "remoteRoot": "/app/libs/rag-core-api"
                },
                // avoid tilt warning of missing path mapping
                {
                    "localRoot": "${workspaceFolder}/libs/admin-api-lib",
                    "remoteRoot": "/app/libs/admin-api-lib"
                },
            ]
        },
        {
            "name": "document_extractor",
            "type": "python",
            "request": "attach",
            "host": "localhost",
            "port": 31416,
            "justMyCode": false,
            "env": {
                "PYDEVD_WARN_EVALUATION_TIMEOUT": "600",
                "PYDEVD_THREAD_DUMP_ON_WARN_EVALUATION_TIMEOUT": "600"
            },
            "pathMappings": [
                {
                    "localRoot": "${workspaceFolder}/services/document-extractor",
                    "remoteRoot": "/app/services/document-extractor"
                },
                {
                    "localRoot": "${workspaceFolder}/libs/extractor-api-lib",
                    "remoteRoot": "/app/libs/extractor-api-lib"
                },
                // avoid tilt warning of missing path mapping
                {
                    "localRoot": "${workspaceFolder}/libs/rag-core-api",
                    "remoteRoot": "/app/libs/rag-core-api"
                },
                {
                    "localRoot": "${workspaceFolder}/libs/admin-api-lib",
                    "remoteRoot": "/app/libs/admin-api-lib"
                },
            ]
        },
        {
            "name": "rag_admin_backend",
            "type": "python",
            "request": "attach",
            "host": "localhost",
            "port": 31417,
            "justMyCode": false,
            "env": {
                "PYDEVD_WARN_EVALUATION_TIMEOUT": "600",
                "PYDEVD_THREAD_DUMP_ON_WARN_EVALUATION_TIMEOUT": "600"
            },
            "pathMappings": [
                {
                    "localRoot": "${workspaceFolder}/services/admin-backend",
                    "remoteRoot": "/app/services/admin-backend"
                },
                {
                    "localRoot": "${workspaceFolder}/libs/rag-core-lib",
                    "remoteRoot": "/app/libs/rag-core-lib"
                },
                {
                    "localRoot": "${workspaceFolder}/libs/admin-api-lib",
                    "remoteRoot": "/app/libs/admin-api-lib"
                },
                // avoid tilt warning of missing path mapping
                {
                    "localRoot": "${workspaceFolder}/libs/rag-core-api",
                    "remoteRoot": "/app/libs/rag-core-api"
                }
            ]
        }


    ]
}
```

The following will delete everything deployed with `tilt up` command

```shell
tilt down
```

#### 1.4.4 Access via ingress

A detailed explanation of, how to access a service via ingress, can be found in the [infrastructure README](./infrastructure/README.md).



## 2. Deployment to server

### 2.1 Server provisioning

The RAG template requires *at least*:
 - A Kubernetes Cluster
 - S3 ObjectStorage

Provided is an example Terraform script, using the [STACKIT Terrraform Provider](https://registry.terraform.io/providers/stackitcloud/stackit/latest/docs):
```terraform
resource "stackit_ske_project" "rag-ske" {
  project_id = var.stackit_project_id
}

resource "stackit_ske_cluster" "rag-ske" {
  project_id         = stackit_ske_project.rag-ske.id
  name               = "rag"
  kubernetes_version = "1.27"
  node_pools = [
    {
    name         = "rag-node1"
    machine_type = "g1.4"
    max_surge    = 1
    minimum            = "1"
    maximum            = "1"
    availability_zones = ["eu01-1"]
    os_version = "3815.2.5"
    volume_size = 320
    volume_type = "storage_premium_perf1"
    }
  ]
  maintenance = {
    enable_kubernetes_version_updates    = true
    enable_machine_image_version_updates = true
    start                                = "01:00:00Z"
    end                                  = "02:00:00Z"
  }
}

resource "stackit_objectstorage_credentials_group" "credentials-group" {
  project_id = stackit_ske_project.rag-ske.id
  name       = "credentials-group"
  depends_on = [stackit_ske_project.rag-ske, stackit_objectstorage_bucket.docs]
}

resource "stackit_objectstorage_credential" "misc-creds" {
  depends_on = [stackit_objectstorage_credentials_group.credentials-group]
  project_id           = stackit_objectstorage_credentials_group.credentials-group.project_id
  credentials_group_id = stackit_objectstorage_credentials_group.credentials-group.credentials_group_id
  expiration_timestamp = "2027-01-02T03:04:05Z"
}

resource "stackit_objectstorage_bucket" "docs" {
  project_id = stackit_ske_project.rag-ske.id
  name       = "docs"
}
```

For further information please consult the [STACKIT Terrraform Provider documentation](https://registry.terraform.io/providers/stackitcloud/stackit/latest/docs).

Further requirements for the server can be found in the [infrastructure README](./infrastructure/README.md).

### 2.2 Langfuse

A detailed description regarding the configuration of Langfuse can be found in the [infrastructure README](./infrastructure/README.md).


## 3. Build and Test
The example `Tiltfile` provides a triggered linting and testing.
The linting-settings can be changed in the `services/rag-backend/pyproject.toml` file under section `tool.flake8`.

## 4. Contribution Guidelines

In order to contribute please consult the [CONTRIBUTING.md](./CONTRIBUTING.md).

