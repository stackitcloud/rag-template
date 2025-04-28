load("ext://dotenv", "dotenv")

# admin has been scrubbed, so all names including admin were very hard to read. To avoid that, scrubbing is disabled
secret_settings(disable_scrub=True)

if os.path.exists(".env"):
    dotenv(fn=".env")

config.define_bool("debug")
cfg = config.parse()
backend_debug = cfg.get("debug", False)

core_library_context = "./rag-core-library"


def create_linter_command(folder_name, name):
    return (
        "docker build -t "
        + name
        + " --build-arg dev=1 -f "
        + folder_name
        + "/Dockerfile .;docker run --rm --entrypoint make "
        + name
        + " lint"
    )


def create_test_command(folder_name, name):
    return (
        "docker build -t "
        + name
        + " --build-arg dev=1 -f "
        + folder_name
        + "/Dockerfile .;docker run --rm --entrypoint make "
        + name
        + " test"
    )


########################################################################################################################
########################################## build helm charts ###########################################################
########################################################################################################################
local_resource(
    "core helm chart",
    cmd="cd ./rag-infrastructure/rag && helm dependency update",
    ignore=[
        "rag-infrastructure/rag/charts/keydb-0.48.0.tgz",
        "rag-infrastructure/rag/charts/minio-14.6.7.tgz",
        "rag-infrastructure/rag/charts/langfuse-0.29.1.tgz",
        "rag-infrastructure/rag/charts/qdrant-0.9.1.tgz",
        "rag-infrastructure/rag/charts/ollama-0.29.1.tgz",
    ],
    labels=["helm"],
)
########################################################################################################################
############################## create k8s namespaces, if they don't exist ##############################################
########################################################################################################################

namespace = "rag"


def create_namespace_if_notexist(namespace):
    check_namespace_cmd = "kubectl get namespace %s --ignore-not-found" % namespace
    create_namespace_cmd = "kubectl create namespace %s" % namespace
    existing_namespace = local(check_namespace_cmd, quiet=True)
    print("existing_namespace: %s" % existing_namespace)
    if not existing_namespace:
        print("Creating namespace: %s" % namespace)
        local(create_namespace_cmd)


create_namespace_if_notexist(namespace)

########################################################################################################################
################################## core testing & linting ##############################################################
########################################################################################################################

# Add linting trigger
local_resource(
    "RAG core library linting",
    """set -e
    docker build -t rag_core --build-arg TEST=0 -f rag-core-library/Dockerfile rag-core-library;
    docker run --rm rag_core make lint""",
    labels=["linting"],
    auto_init=False,
    trigger_mode=TRIGGER_MODE_AUTO,
    allow_parallel=True,
)

# Add testing trigger
local_resource(
    "RAG core lib testing",
    """set -e
    docker build -t rag_core_lib --build-arg DIRECTORY=rag-core-lib -f rag-core-library/Dockerfile rag-core-library;
    docker run --rm rag_core_lib make test""",
    labels=["test"],
    auto_init=False,
    trigger_mode=TRIGGER_MODE_AUTO,
    allow_parallel=True,
)

local_resource(
    "RAG core API testing",
    """set -e
    docker build -t rag_core_api --build-arg DIRECTORY=rag-core-api -f rag-core-library/Dockerfile rag-core-library;
    docker run --rm rag_core_api make test""",
    labels=["test"],
    auto_init=False,
    trigger_mode=TRIGGER_MODE_AUTO,
    allow_parallel=True,
)

local_resource(
    "Admin API lib testing",
    """set -e
    docker build -t admin_api_lib --build-arg DIRECTORY=admin-api-lib -f rag-core-library/Dockerfile rag-core-library;
    docker run --rm admin_api_lib make test""",
    labels=["test"],
    auto_init=False,
    trigger_mode=TRIGGER_MODE_AUTO,
    allow_parallel=True,
)

local_resource(
    "Extractor API lib testing",
    """set -e
    docker build -t extractor_api_lib --build-arg DIRECTORY=extractor-api-lib -f rag-core-library/Dockerfile rag-core-library;
    docker run --rm extractor_api_lib make test""",
    labels=["test"],
    auto_init=False,
    trigger_mode=TRIGGER_MODE_AUTO,
    allow_parallel=True,
)


########################################################################################################################
################################## build backend_rag image and do live update ##########################################
########################################################################################################################

# NOTE: full image names should match the one in the helm chart values.yaml!
registry = "ghcr.io/stackitcloud/rag-template"
rag_api_image_name = "rag-backend"

backend_context = "./rag-backend"
rag_api_full_image_name = "%s/%s" % (registry, rag_api_image_name)
docker_build(
    rag_api_full_image_name,
    ".",
    build_args={
        "dev": "1" if backend_debug else "0",
    },
    live_update=[
        sync(backend_context, "/app/rag-backend"),
        sync(core_library_context+"/rag-core-api", "/app/rag-core-library/rag-core-api"),
        sync(core_library_context+"/rag-core-lib", "/app/rag-core-library/rag-core-lib"),
    ],
    dockerfile=backend_context + "/Dockerfile",
)

# Add linter trigger
local_resource(
    "RAG backend linting",
    create_linter_command(backend_context, "back"),
    labels=["linting"],
    auto_init=False,
    trigger_mode=TRIGGER_MODE_AUTO,
    allow_parallel=True,
)

# Add test trigger
local_resource(
    "RAG backend testing",
    create_test_command(backend_context, "back"),
    labels=["test"],
    auto_init=False,
    trigger_mode=TRIGGER_MODE_AUTO,
    allow_parallel=True,
)

########################################################################################################################
################################## build admin backend image and do live update ##############################################
########################################################################################################################

# NOTE: full image names should match the one in the helm chart values.yaml!
registry = "ghcr.io/stackitcloud/rag-template"
admin_api_image_name = "admin-backend"

admin_backend_context = "./admin-backend"
admin_api_full_image_name = "%s/%s" % (registry, admin_api_image_name)
docker_build(
    admin_api_full_image_name,
    ".",
    build_args={
        "dev": "1" if backend_debug else "0",
    },
    live_update=[
        sync(admin_backend_context, "/app/admin-backend"),
        sync(core_library_context + "/rag-core-lib", "/app/rag-core-library/rag-core-lib"),
        sync(core_library_context + "/admin-api-lib", "/app/rag-core-library/admin-api-lib"),
    ],
    dockerfile=admin_backend_context + "/Dockerfile",
)

# Add linter trigger
local_resource(
    "Admin backend linting",
    create_linter_command(admin_backend_context, "adminback"),
    labels=["linting"],
    auto_init=False,
    trigger_mode=TRIGGER_MODE_MANUAL,
    allow_parallel=True,
)

# Add test trigger
local_resource(
    "Admin backend testing",
    create_test_command(admin_backend_context, "adminback"),
    labels=["test"],
    auto_init=False,
    trigger_mode=TRIGGER_MODE_MANUAL,
    allow_parallel=True,
)

########################################################################################################################
################################## build document extractor image and do live update ##############################################
########################################################################################################################

# NOTE: full image names should match the one in the helm chart values.yaml!
registry = "ghcr.io/stackitcloud/rag-template"
document_extractor_image_name = "document-extractor"

extractor_context = "./document-extractor"
document_extractor_full_image_name = "%s/%s" % (registry, document_extractor_image_name)
docker_build(
    document_extractor_full_image_name,
    ".",
    build_args={
        "dev": "1" if backend_debug else "0",
    },
    live_update=[
        sync(extractor_context, "/app/document-extractor"),
        sync(core_library_context+"/rag-core-lib", "/app/rag-core-library/rag-core-lib"),
        sync(core_library_context +"/extractor-api-lib", "/app/rag-core-library/extractor-api-lib"),
        ],
    dockerfile=extractor_context + "/Dockerfile",
)

# Add linter trigger
local_resource(
    "Extractor linting",
    create_linter_command(extractor_context, "extractor"),
    labels=["linting"],
    auto_init=False,
    trigger_mode=TRIGGER_MODE_MANUAL,
    allow_parallel=True,
)

# Add test trigger
local_resource(
    "Extractor testing",
    create_test_command(extractor_context, "extractor"),
    labels=["test"],
    auto_init=False,
    trigger_mode=TRIGGER_MODE_MANUAL,
    allow_parallel=True,
)


########################################################################################################################
################################## build frontend image and do live update #############################################
########################################################################################################################

frontend_context = "./frontend"
frontend_image_name = "%s/frontend" % (registry)

docker_build(
    frontend_image_name,
    ".",
    dockerfile="./frontend/apps/chat-app/Dockerfile",
    live_update=[sync("./frontend/apps/chat-app", "/app")],
)

########################################################################################################################
################################## build admin frontend image and do live update ########################################
########################################################################################################################

adminfrontend_context = "./frontend"
adminfrontend_image_name = "%s/admin-frontend" % (registry)
docker_build(
    adminfrontend_image_name,
    ".",
    dockerfile="frontend/apps/admin-app/Dockerfile",
    live_update=[sync("./frontend/apps/admin-app", "/app")],
)


########################################################################################################################
############################ deploy local rag chart (back-/frontend) and forward port #############################
########################################################################################################################
value_override = [
    # secrets env
    "shared.secrets.s3.accessKey=%s" % os.environ["S3_ACCESS_KEY_ID"],
    "shared.secrets.s3.secretKey=%s" % os.environ["S3_SECRET_ACCESS_KEY"],
    "backend.secrets.basicAuth=%s" % os.environ["BASIC_AUTH"],
    "backend.secrets.langfuse.publicKey=%s" % os.environ["LANGFUSE_PUBLIC_KEY"],
    "backend.secrets.langfuse.secretKey=%s" % os.environ["LANGFUSE_SECRET_KEY"],
    "backend.secrets.ragas.openaiApikey=%s" % os.environ["RAGAS_OPENAI_API_KEY"],
    "frontend.secrets.viteAuth.VITE_AUTH_USERNAME=%s" % os.environ["VITE_AUTH_USERNAME"],
    "frontend.secrets.viteAuth.VITE_AUTH_PASSWORD=%s" % os.environ["VITE_AUTH_PASSWORD"],
    # variables
    "shared.debug.backend.enabled=%s" % backend_debug,
    "features.frontend.enabled=true",
    "shared.config.tls.enabled=false",
    "shared.ssl=false",
    # ingress host names
    "backend.ingress.host.name=rag.localhost",
    # langfuse
    "langfuse.langfuse.additionalEnv[0].name=LANGFUSE_INIT_ORG_ID",
    "langfuse.langfuse.additionalEnv[0].value=\"%s\"" % os.environ["LANGFUSE_INIT_ORG_ID"],
    "langfuse.langfuse.additionalEnv[1].name=LANGFUSE_INIT_PROJECT_ID",
    "langfuse.langfuse.additionalEnv[1].value=\"%s\"" % os.environ["LANGFUSE_INIT_PROJECT_ID"],
    "langfuse.langfuse.additionalEnv[2].name=LANGFUSE_INIT_PROJECT_PUBLIC_KEY",
    "langfuse.langfuse.additionalEnv[2].value=%s" % os.environ["LANGFUSE_INIT_PROJECT_PUBLIC_KEY"],
    "langfuse.langfuse.additionalEnv[3].name=LANGFUSE_INIT_PROJECT_SECRET_KEY",
    "langfuse.langfuse.additionalEnv[3].value=%s" % os.environ["LANGFUSE_INIT_PROJECT_SECRET_KEY"],
    "langfuse.langfuse.additionalEnv[4].name=LANGFUSE_INIT_USER_EMAIL",
    "langfuse.langfuse.additionalEnv[4].value=%s" % os.environ["LANGFUSE_INIT_USER_EMAIL"],
    "langfuse.langfuse.additionalEnv[5].name=LANGFUSE_INIT_USER_PASSWORD",
    "langfuse.langfuse.additionalEnv[5].value=%s" % os.environ["LANGFUSE_INIT_USER_PASSWORD"],
    "langfuse.langfuse.additionalEnv[6].name=LANGFUSE_INIT_USER_NAME",
    "langfuse.langfuse.additionalEnv[6].value=%s" % os.environ["LANGFUSE_INIT_USER_NAME"],
]

def has_confluence_config():
    required_keys = ["CONFLUENCE_TOKEN", "CONFLUENCE_URL", "CONFLUENCE_SPACE_KEY"]
    for key in required_keys:
        if key not in os.environ:
            return False
    return True

if has_confluence_config():
    token = os.environ["CONFLUENCE_TOKEN"].replace(",", "\\,")
    url = os.environ["CONFLUENCE_URL"].replace(",", "\\,")
    space_key = os.environ["CONFLUENCE_SPACE_KEY"].replace(",", "\\,")

    confluence_settings = [
        "adminBackend.secrets.confluenceLoader.token=%s" % token,
        "adminBackend.envs.confluenceLoader.CONFLUENCE_URL=%s" % url,
        "adminBackend.envs.confluenceLoader.CONFLUENCE_SPACE_KEY=%s" % space_key,
    ]

    if os.environ.get("CONFLUENCE_VERIFY_SSL"):
        verify_ssl = os.environ["CONFLUENCE_VERIFY_SSL"].replace(",", "\\,")
        confluence_settings.append("adminBackend.envs.confluenceLoader.CONFLUENCE_VERIFY_SSL=%s" % verify_ssl)
    if os.environ.get("CONFLUENCE_DOCUMENT_NAME"):
        document_names = os.environ["CONFLUENCE_DOCUMENT_NAME"].replace(",", "\\,")
        confluence_settings.append("adminBackend.envs.confluenceLoader.CONFLUENCE_DOCUMENT_NAME=%s" % document_names)
    value_override.extend(confluence_settings)

if os.environ.get("STACKIT_VLLM_API_KEY", False):
    stackit_vllm_settings = [
        "backend.secrets.stackitVllm.apiKey=%s" % os.environ["STACKIT_VLLM_API_KEY"],
    ]
    value_override.extend(stackit_vllm_settings)

if os.environ.get("STACKIT_EMBEDDER_API_KEY", False):
    stackit_embedder_settings = [
        "backend.secrets.stackitEmbedder.apiKey=%s" % os.environ["STACKIT_EMBEDDER_API_KEY"],
    ]
    value_override.extend(stackit_embedder_settings)


yaml = helm(
    "./rag-infrastructure/rag",
    name="rag",
    namespace="rag",
    values=[
        "./rag-infrastructure/rag/values.yaml",
    ],
    set=value_override,
)

k8s_yaml(yaml)

k8s_resource(
    "backend",
    links=[
        link("http://localhost:8888/docs", "Swagger UI"),
    ],
    port_forwards=[
        port_forward(
            8888,
            container_port=8080,
            name="Backend-Service-Portforward",
        ),
        port_forward(
            31415,
            container_port=31415,
            name="Backend-Debugger",
        )
    ],
    labels=["backend"],
)

k8s_resource(
    "extractor",
    links=[
        link("http://localhost:8081/docs", "Swagger UI"),
    ],
    port_forwards=[
        port_forward(
            8081,
            container_port=8080,
            name="Extractor-Service-Portforward",
        ),
        port_forward(
            31416,
            container_port=31415,
            name="Backend-Debugger",
        ),
    ],
    labels=["backend"],
)

k8s_resource(
    "admin-backend",
    links=[
        link("http://admin.rag.localhost/api/docs", "Swagger UI"),
    ],
    port_forwards=[
        port_forward(
            31417,
            container_port=31415,
            name="Backend-Debugger",
        ),
    ],
    labels=["backend"],
)


k8s_resource(
    "frontend",
    links=[
        link("http://rag.localhost", "Chat App"),
    ],
    labels=["frontend"],
)

k8s_resource(
    "admin-frontend",
    links=[
        link("http://admin.rag.localhost/", "Chat Admin App"),
    ],
    labels=["frontend"],
)


########################################################################################################################
############################################### port forwarding qdrant #################################################
########################################################################################################################

k8s_resource(
    "rag-qdrant",
    port_forwards=[
        port_forward(
            6333,
            container_port=6333,
            name="Qdrant dashboard",
            link_path="/dashboard",
        ),
    ],
    labels=["infrastructure"],
)

########################################################################################################################
###################################### port forwarding langfuse  #######################################################
########################################################################################################################

k8s_resource(
    "rag-langfuse-web",
    port_forwards=[
        port_forward(
            3000,
            container_port=3000,
            name="Langfuse Web",
        ),
    ],
    labels=["infrastructure"],
)

########################################################################################################################
###################################### port forwarding minio  #######################################################
########################################################################################################################

k8s_resource(
    "rag-minio",
    port_forwards=[
        port_forward(
            9001,
            container_port=9001,
            name="minio ui",
        ),
    ],
    labels=["infrastructure"],
)
