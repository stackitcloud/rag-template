# Introduction
This is a very basic example of how to use the RAG-API libraries.
It also gives an example of how to replace modules. TODO: add replacement example


# Getting Started
An example tiltfile is provided to get you started.

## Components

This repository contains the following components:
- *admin-backend*: TODO
- *document-extractor*: TODO
- [*rag-backend*](#rag-backend): The main component of the RAG.
- *frontend*: Frontend for both, chat and admin APIs.
- *rag-infrastructure*: Contains the helm-chart and other files related to infrastructure and deployment. Please consult [this README](./rag-infrastructure/README.md) for further information.
- *rag-core-library*: Contains the API-libraries that are used to construct the backend-services in this repository. For further information, please consult [this README](./rag-core-library/README.md#1-rag-core-api).

### Rag backend
The backend is the main component of the RAG. It handles all connections to the vector database, as well as chatting.

All components are provided by the *rag-core-api*. For further information on endpoints and requirements, please consult [this README](./rag-core-library/README.md#1-rag-core-api).

## Requirements

> 📝  *Windows users*: make sure you use wsl for infrastructure setup & orchestration.

Every package contains a `pyproject.toml` with the required Python packages.
[Poetry](https://python-poetry.org/)  is used for requirement management.
To ensure the requirements are consistent, you have to update the `poetry.lock` in addition to the `pyproject.toml` when updating/changing requirements. Additional requirements like *black* and *flake8* are provided for development. You can install them with `poetry install --with dev` inside the package-directory.

> 📝 Do not update the requirements in the `pyproject.toml` manually. Doing so will invalidate the `poetry.lock`. Use the *poetry* application for this.

### Adding new requirements
Run
```bash
poetry add --lock <package>
```
insisde of the package directory in order to add new packages. This will automatically update the `pyproject.toml` and the `poetry.lock`.

System requirements have to manually be added to the `Dockerfile`.

## Usage
This example of the rag-template includes a WebUI for document-management, as well as for the chat.

After following the setup instruction for either the [local installation](#-local-setup-instructions) or the [installation on a server](#-Deployment-to-server) the WebUI is accessible via the configured ingress.
After uploading a file in the document-management WebUI you can start asking question about your document in the chat WebUI.

For a complete documentation of the available REST-APIs, please consult [the README of the rag-core-library](./rag-core-library/README.md).


## Local setup instructions

The following is a list of the dependencies. If you miss one of the dependencies, click on the name and follow the install instructions.

- [*k3d*](https://k3d.io/v5.6.0/#installation)
- [*helm*](https://helm.sh/docs/intro/install/)
- [*tilt*](https://docs.tilt.dev/install.html)

For local deployment, a few env variables need to be provided by an `.env` file (here: .)

The `.env` needs to contain the following values:

```
BASIC_AUTH=Zm9vOiRhcHIxJGh1VDVpL0ZKJG10elZQUm1IM29JQlBVMlZ4YkpUQy8K

S3_ACCESS_KEY_ID=...
S3_SECRET_ACCESS_KEY=...

VITE_AUTH_USERNAME=...
VITE_AUTH_PASSWORD=...

ALEPH_ALPHA_ALEPH_ALPHA_API_KEY=...

OPENAI_API_KEY=...

STACKIT_AUTH_CLIENT_ID=...
STACKIT_AUTH_CLIENT_SECRET=...

STACKIT_VLLM_API_KEY=...
STACKIT_EMBEDDER_API_KEY=...

OPENAI_API_KEY=...

# ONLY necessary, if no init values are set. if init values are set,
# the following two values should match the init values or be commented out
# or be created via the langfuse UI
LANGFUSE_PUBLIC_KEY=pk-lf-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
LANGFUSE_SECRET_KEY=sk-lf-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

# OPTIONAL: instead of generating the org, project, user, public key
# and secret key through the UI, you can set INIT values for them.
LANGFUSE_INIT_ORG_ID=...
LANGFUSE_INIT_PROJECT_ID=...
LANGFUSE_INIT_PROJECT_PUBLIC_KEY=pk-lf-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
LANGFUSE_INIT_PROJECT_SECRET_KEY=sk-lf-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

LANGFUSE_INIT_USER_EMAIL=...
LANGFUSE_INIT_USER_NAME=...
LANGFUSE_INIT_USER_PASSWORD=...

```

This results in a basic auth with username=`foo` and password=`bar`.

> 📝 NOTE: All values containg `...` are placeholders and have to be replaced with real values.
> This deployment comes with multiple options. You change the `global.config.envs.rag_class_types.RAG_CLASS_TYPE_LLM_TYPE` in the helm-deployment to on of the following values:
> - `stackit`: Uses an OpenAI compatible LLM, like the STACKIT model serving service.
> - `alephalpha`: Uses the public AlephAlpha instance.
> - `ollama`: Uses ollama as an LLM provider.
>

In the following, the *k3d* cluster setup and the setup inside the *k3d* will be explained.

### *k3d* cluster setup

TODO: link to rag-infrastructure readme section once the readme is done


### *tilt* deployment

If this is the first time you are starting the *tiltfile* you have to build the helm-chart first.
This can be done with the following command from the root of the git-repository:
```shell
cd rag-infrastructure/rag;helm dependency update; cd ../..
```

> 📝 NOTE: The configuration of the *tiltfile* requires `features.frontend.enabled=true`, `features.langfuse.enabled=true` and `features.qdrant.enabled=true`.

After the initial build of the helm chart `tilt` is able to update the files.


The following will tear up the microservices in *k3d*.
For the following steps, it is assumed your current working directory is the root of the git-repository.

```shell
tilt up
```

Environment variables are loaded from `.env` file in the root of this git-repository.

The tilt ui is available at [http://localhost:10350/](http://localhost:10350/)

If you want to access *Qdrant* etc. just click the resource in the UI. In the upper corner will be the link, to access the resource.

To enable debugging, start tilt with the following command:
'''shell
tilt up -- --debug=true
'''

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
                    "localRoot": "${workspaceFolder}/rag-backend",
                    "remoteRoot": "/app/rag-backend"
                },
                {
                    "localRoot": "${workspaceFolder}/rag-core-library/rag-core-lib",
                    "remoteRoot": "/app/rag-core-library/rag-core-lib"
                },
                {
                    "localRoot": "${workspaceFolder}/rag-core-library/rag-core-api",
                    "remoteRoot": "/app/rag-core-library/rag-core-api"
                }
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
                    "localRoot": "${workspaceFolder}/document-extractor",
                    "remoteRoot": "/app/document-extractor"
                }
            ]
        },
        {
            "name": "rag_admin_api_lib",
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
                    "localRoot": "${workspaceFolder}/admin-backend",
                    "remoteRoot": "/app/admin-backend"
                },
                {
                    "localRoot": "${workspaceFolder}/rag-core-library/rag-core-lib",
                    "remoteRoot": "/app/rag-core-library/rag-core-lib"
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

### Access via ingress

To access the ingress by its hostname, the hosts file need to be adjusted. On *linux/macOS*, you have to adjust `/etc/hosts` as follows.

```shell
echo "127.0.0.1 rag.localhost" | sudo tee -a /etc/hosts > /dev/null
```

Afterwards, the services should be accessible from [http://rag.localhost](http://rag.localhost)

Note: The command above has only been tested on *Ubuntu 22.04 LTS*.

On *Windows*, you can adjust the hosts file as described [here](https://docs.digitalocean.com/products/paperspace/machines/how-to/edit-windows-hosts-file/).


# Deployment to server

A tutorial on how to deploy on a server can be found [here](TODO: write tutorial in rag-infrastructure readme and link it here).

# Langfuse

TODO: link to instructions in infra once infra readme is done

LangFuse utilizes a PostgreSQL database under the hood. After both services are available, browse to the specified url.
After signing up and creating a project in the local LangFuse instance, create API keys via the settings; see below.

![langfuse-api-key](./figures/langfuse-api-access.png)


# Build and Test
The example Tiltfile provides a triggered linting and testing.
The linting-settings can be changed in the `rag-backend/pyproject.toml` file under section `tool.flake8`.

# Contribute
This use case example contains 2 git submodules, the `rag-infrastructure` and the `rag-core-library`.
In order to contribute you can simply create a new branch, make changes and create a PR.

 > 📝 Before creating a pull request please run `black .`, as well as `flake8 .` in every package and ensure there are no complaints by these tools.

## TODO: add contribution guideline
