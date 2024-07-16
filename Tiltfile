load("ext://dotenv", "dotenv")

if os.path.exists(".env"):
    dotenv(fn=".env")

config.define_bool("debug")
cfg = config.parse()
backend_debug = cfg.get("debug", False)
def create_linter_command(folder_name, name):
    return "docker build -t " +name+" --build-arg dev=1 -f "+folder_name+"/Dockerfile " + folder_name + ";docker run --rm "+name+" make lint"

def create_test_command(folder_name, name):
    return "docker build -t " +name+" --build-arg dev=1 -f "+folder_name+"/Dockerfile " + folder_name + ";docker run --rm "+name+" make test"

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
registry = "ghcr.io/mmmake-gmbh/rag"
rag_api_image_name = "rag_api"

backend_context = "./rag-backend"
rag_api_full_image_name = "%s/%s" % (registry, rag_api_image_name)
docker_build(
    rag_api_full_image_name,
    backend_context,
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
    trigger_mode=TRIGGER_MODE_AUTO,
    allow_parallel=True,
)

# Add test trigger
local_resource(
    "RAG Backend testing",
    create_test_command(backend_context, "back"),
    labels=["test"],
    trigger_mode=TRIGGER_MODE_AUTO,
    allow_parallel=True,
)
########################################################################################################################
############################ deploy local doctopus chart (back-/frontend) and forward port #############################
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
    # variables
    "global.debug.backend.enabled=%s" % backend_debug,
    "global.config.tls.enabled=false",
    "global.ssl=false",
    #ingress host names
    "backend.ingress.host.name=rag.localhost",
]

yaml = helm(
    "./rag-infrastructure/rag",
    name="rag",
    namespace="rag",
    values=["./rag-infrastructure/rag/values.yaml"],
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
