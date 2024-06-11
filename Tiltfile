load("ext://dotenv", "dotenv")

if os.path.exists(".env"):
    dotenv(fn=".env")

config.define_bool("debug")
cfg = config.parse()
backend_debug = cfg.get("debug", False)


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

backend_context = "."
rag_api_full_image_name = "%s/%s" % (registry, rag_api_image_name)
docker_build(
    rag_api_full_image_name,
    backend_context,
    live_update=[sync(".", "/app")],
    dockerfile=backend_context+("DebugDockerfile" if backend_debug else "Dockerfile")
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

helm_remote(
    "rag",
    repo_name="rag",
    values="<<some_values.yaml>>",
    namespace="rag",
    version="0.0.1",
    repo_url="<<REPO_URL>>",
    set=value_override,
)

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
)

########################################################################################################################
############################################### port forwarding qdrant #################################################
########################################################################################################################

k8s_resource(
    "qdrant",
    port_forwards=[
        port_forward(
            6333,
            container_port=6333,
            name="Qdrant dashboard",
            link_path="/dashboard",
        ),
    ],
)

########################################################################################################################
###################################### port forwarding langfuse  #######################################################
########################################################################################################################

k8s_resource(
    "langfuse",
    port_forwards=[
        port_forward(
            3000,
            container_port=3000,
            name="Langfuse Web",
        ),
    ],
)
