# Components

This Repository contains the helmchart for the following RAG components:
- [langfuse](https://langfuse.com/)
- [qdrant](https://qdrant.tech/)
- frontend
- backend

The complete list of available settings can be found in the [rag/values.yaml](rag/values.yaml) file.
This README only explains the most important settings.

With the exception of the `backend` all components can be disabled and exchanged with components of your choice.
This can be done by overwriting the following values in your `values.yaml`
```yaml
langfuse:
  enabled: true
qdrant:
  enabled: true
frontend:
  enabled: true
```

It is required to use an `imagePullSecret` for pulling the images belonging to the rag-template.
You can either provide your own already existing secret by using the example below:
```yaml
global:
  ssl: true
  imagePullSecret:
    create: false
    name: cr-credentials
```
Or you can create a secret with your own values like this:
```yaml
registry:
  auths:
    crIo:
      username: github-username # replace with your github username
      pat: github-pat # replace with your github personal access token
      email: email-address@domain.de # replace with your email address
  name: "ghcr.io"

global:
  ssl: true
  imagePullSecret:
    create: true
    name: cr-credentials
```

## Langfuse

LangFuse utilizes a PostgreSQL database under the hood. After both services are available, browse to the spcified url.
After signing up and creating a project in the local LangFuse instance, create API keys via the settings; see below.

![langfuse-api-key](./figures/langfuse-api-access.png)

Default values for the deployment are provided in the `rag/langfuse_values.yaml` file.

## Qdrant

Default values for the deployment are provided in the `rag/qdrant_values.yaml` file.

## Frontend
TODO: Adjust once the frontend actually works.

## Backend

The following values should be adjusted for the deployment:
```yaml
backend:
  image:
      repository: schwarzit-xx-sit-rag-template-sit-stackit-docker-local.jfrog.io
      name: rag-backend
      tag: "402196"

  ingress:
      host:
      name: rag.localhost

global:
  ssl: true
  secrets:
    aleph_alpha:
      aleph_alpha_aleph_alpha_api_key: ...
    basic_auth: ...
    langfuse:
      public_key: ...
      secret_key: ...
    stackit_myapi_llm:
      auth_client_id: ...
      auth_client_secret: ...
  config:
    envs:
      rag_class_types:
        RAG_CLASS_TYPE_LLM_TYPE: "myapi"
        RAG_CLASS_TYPE_EMBEDDER_TYPE: "myapi"

```
> 📝 NOTE: All values containg `...` are placeholders and have to be replaced with real values.

> ⓘ INFO: The sit-internal instance of AlephAlpha has proven to be not the most reliable.
> This deployment comes with multiple options. You can change the `global.config.envs.rag_class_types.RAG_CLASS_TYPE_LLM_TYPE` in `./rag/values.yaml` to one of the following values:
> - `myapi`: Uses the sit-internal AlephAlpha instance.
> - `alephalpha`: Uses the public AlephAlpha instance.
> - `ollama`: Uses ollama as an LLM provider.
>
> The same options are also available for the `global.config.envs.rag_class_types.RAG_CLASS_TYPE_EMBEDDER_TYPE`.
> Both *AlephAlpha* options share the same settings. There is no instance of *Ollama* bundled with this package. If you require one you have to deploy your own instance.



# Requirements

> *Windows users*: make sure you use wsl for infrastructure setup & orchestration.


## Local setup instructions

The following is a list of the dependencies. If you miss one of the dependencies, click on the name and follow the install instructions.

- [*k3d*](https://k3d.io/v5.6.0/#installation)
- [*helm*](https://helm.sh/docs/intro/install/)

For local deployment it is recommended to use [*tilt*](https://docs.tilt.dev/install.html).

In the following, the *k3d* cluster setup and the setup inside the *k3d* will be explained.

### *k3d* cluster setup

Assumption: You are in the root directory of this repository. A local registry is created at `registry.localhost:5000`.

```shell
cd cluster-setup && bash setup-k3d-cluster.sh
```

Note: only tested under Linux (Ubuntu 22.04 LTS)

In case of error, you have to manually setup the *k3d* cluster and the nginx ingress controller (if necessary).

#### (Optional) Setup-check

Images can be pushed, pulled, removed etc. to/from the local repo, see:

```shell
docker pull busybox:latest
docker tag busybox:latest registry.localhost:5000/busybox:latest
docker push registry.localhost:5000/busybox:latest
docker run --rm registry.localhost:5000/busybox:latest /bin/sh -c "echo '<<< mmmakies say \"hello\" to you ]:-> >>>'"
docker image rm registry.localhost:5000/busybox:latest
```


It is time to check if the cluster works with the local repo :sunglasses: :

```shell
kubectl run test-pod-name --image registry.localhost:5000/busybox:latest -- /bin/sh -c "while true; do echo '<<< mmmakies say \"hello\" to you ]:-> >>>'; sleep 1; done"
kubectl wait --for=condition=ready pod test-pod-name
kubectl logs test-pod-name
kubectl delete po test-pod-name
```

Under linux, `*.localhost` should be resolved :fire:, otherwise you have to adjust the hosts file. In windows and macOS append the hosts file with the following line:

```shell
127.0.0.1 registry.localhost
```

More information about adjusting the hosts file can be found in the section 'Access via ingress'.


### *tilt* deployment

The following will spin up the microservices in *k3d*

```shell
tilt up
```

Environment variables are loaded from the `.env` file in the same directory the `Tiltfile` is located. The [use case README](../README.md#installation--usage) should contain a list of the required variables.

The tilt ui is available at [http://localhost:10350/](http://localhost:10350/)

If you want to access minio/qdrant etc. just click the resource in the ui. In the upper corner will be the link, to access the resource.

To enable debugging, follow instructions in [README](../README.md).

The following will delete everything deployed with `tilt up` command

```shell
tilt down
```

### Access via ingress

To access the ingress by its hostname, the hosts file need to be adjusted. On *linux/macOS*, you have to adjust `/etc/hosts` as follows.

```shell
echo "127.0.0.1 rag.localhost" | sudo tee -a /etc/hosts > /dev/null
```

Afterwards the services should be accessible from [http://rag.localhost](http://rag.localhost)

Note: The command above has only been tested on *Ubnutu 22.04 LTS*.

On *Windows* you can adjust the hosts file as described [here](https://docs.digitalocean.com/products/paperspace/machines/how-to/edit-windows-hosts-file/).

