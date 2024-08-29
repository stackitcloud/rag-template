load("ext://dotenv", "dotenv")

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
        + "/Dockerfile .;docker run --rm "
        + name
        + " make lint"
    )


def create_test_command(folder_name, name):
    return (
        "docker build -t "
        + name
        + " --build-arg dev=1 -f "
        + folder_name
        + "/Dockerfile .;docker run --rm "
        + name
        + " make test"
    )


########################################################################################################################
########################################## build helm charts ###########################################################
########################################################################################################################
local_resource(
    "core helm chart",
    cmd="cd ./rag-infrastructure/rag && helm dependency update",
    ignore=[
        "rag-infrastructure/rag/charts/backend-0.0.1.tgz",
        "rag-infrastructure/rag/charts/frontend-0.0.1.tgz",
        "rag-infrastructure/rag/charts/langfuse-0.2.1.tgz",
        "rag-infrastructure/rag/charts/qdrant-0.9.1.tgz",
    ],
    labels=["helm"],
)
local_resource(
    "use case helm chart",
    cmd="cd ./helm-chart && helm dependency update",
    ignore=[
        "helm-chart/charts/admin-backend-0.0.1.tgz",
        "helm-chart/charts/keydb-0.48.0.tgz",
        "helm-chart/charts/minio-14.6.7.tgz",
        "helm-chart/charts/rag-0.0.1.tgz",
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
################################## build backend_rag image and do live update ##############################################
########################################################################################################################

# NOTE: full image names should match the one in the helm chart values.yaml!
registry = "schwarzit-xx-sit-rag-template-sit-stackit-docker-local.jfrog.io"
rag_api_image_name = "rag-backend"

backend_context = "./rag-backend"
rag_api_full_image_name = "%s/%s" % (registry, rag_api_image_name)
docker_build(
    rag_api_full_image_name,
    ".",
    build_args={
        "dev": "1" if backend_debug else "0",
    },
    live_update=[sync(backend_context, "/app")],
    dockerfile=backend_context + "/Dockerfile",
)
# Add linter trigger
local_resource(
    "RAG Backend linting",
    create_linter_command(backend_context, "back"),
    labels=["linting"],
    auto_init=False,
    trigger_mode=TRIGGER_MODE_AUTO,
    allow_parallel=True,
)

# Add test trigger
local_resource(
    "RAG Backend testing",
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
registry = "schwarzit-xx-sit-rag-template-sit-stackit-docker-local.jfrog.io"
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
        sync(core_library_context, "/app/rag-core-library/Dockerfile.base"),
        sync(core_library_context, "/app/rag-core-library/rag-core-lib"),
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
registry = "schwarzit-xx-sit-rag-template-sit-stackit-docker-local.jfrog.io"
document_extractor_image_name = "document-extractor"

extractor_context = "./document-extractor"
document_extractor_full_image_name = "%s/%s" % (registry, document_extractor_image_name)
docker_build(
    document_extractor_full_image_name,
    ".",
    build_args={
        "dev": "1" if backend_debug else "0",
    },
    live_update=[sync(extractor_context, "/app/document-extractor")],
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
################################## build adminfrontend image and do live update ########################################
########################################################################################################################

adminfrontend_context = "./frontend"
adminfrontend_image_name = "%s/adminfrontend" % (registry)
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
    "global.secrets.aleph_alpha.aleph_alpha_aleph_alpha_api_key=%s" % os.environ["ALEPH_ALPHA_ALEPH_ALPHA_API_KEY"],
    "global.secrets.stackit_myapi_llm.auth_client_id=%s" % os.environ["STACKIT_AUTH_CLIENT_ID"],
    "global.secrets.stackit_myapi_llm.auth_client_secret=%s" % os.environ["STACKIT_AUTH_CLIENT_SECRET"],
    "global.secrets.openai.api_key=%s" % os.environ["OPENAI_API_KEY"],
    "global.secrets.s3.access_key=%s" % os.environ["S3_ACCESS_KEY_ID"],
    "global.secrets.s3.secret_key=%s" % os.environ["S3_SECRET_ACCESS_KEY"],
    "global.secrets.basic_auth=%s" % os.environ["BASIC_AUTH"],
    "global.secrets.langfuse.public_key=%s" % os.environ["LANGFUSE_PUBLIC_KEY"],
    "global.secrets.langfuse.secret_key=%s" % os.environ["LANGFUSE_SECRET_KEY"],
    "global.secrets.vite_auth.VITE_AUTH_USERNAME=%s" % os.environ["VITE_AUTH_USERNAME"],
    "global.secrets.stackit_vllm.api_key=%s" % os.environ["STACKIT_VLLM_API_KEY"],
    "global.secrets.vite_auth.VITE_AUTH_PASSWORD=%s" % os.environ["VITE_AUTH_PASSWORD"],
    # variables
    "global.debug.backend.enabled=%s" % backend_debug,
    "frontend.enabled=true",
    "global.config.tls.enabled=false",
    "global.ssl=false",
    # ingress host names
    "backend.ingress.host.name=rag.localhost",
]

yaml = helm(
    "./helm-chart",
    name="rag",
    namespace="rag",
    values=[
        "./helm-chart/values.yaml",
        "./helm-chart/rag-core-values.yaml",
        "./helm-chart/minio-values.yaml",
        "./helm-chart/langfuse-values.yaml",
        "./helm-chart/qdrant-values.yaml",
        "./helm-chart/ollama-values.yaml",
    ],
    set=value_override,
)

k8s_yaml(yaml)

k8s_resource(
    "backend",
    links=[
        link("http://rag.localhost/api/docs", "Swagger UI"),
    ],
    port_forwards=[
        port_forward(
            31415,
            container_port=31415,
            name="Backend-Debugger",
        ),
    ],
    labels=["backend"],
)

k8s_resource(
    "extractor",
    links=[
        link("http://localhost:8080/docs", "Swagger UI"),
    ],
    port_forwards=[
        port_forward(8080, container_port=8080, name="-"),
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
    "adminfrontend",
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
    "rag-langfuse",
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
            9000,
            container_port=9001,
            name="minio ui",
        ),
    ],
    labels=["infrastructure"],
)
