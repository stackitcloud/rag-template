load("ext://dotenv", "dotenv")

# admin has been scrubbed, so all names including admin were very hard to read. To avoid that, scrubbing is disabled
secret_settings(disable_scrub=True)

if os.path.exists(".env"):
    dotenv(fn=".env")

config.define_bool("debug")
config.define_bool("dev")
cfg = config.parse()
backend_debug = cfg.get("debug", False)
dev_mode = cfg.get("dev", False)

# Print mode information
if dev_mode:
    print("🚀 Running in DEVELOPMENT mode (using Dockerfile.dev)")
    print("   - Live code updates enabled")
    print("   - Fast iteration optimized builds")
else:
    print("🏭 Running in PRODUCTION mode (using Dockerfile)")
    print("   - Production-optimized builds")
    print("   - No live updates")

core_library_context = "./libs"


def libs_ignore_except(include_libs):
    """Return a list of paths to ignore for docker builds under the project root.

    include_libs: list of folder names under ./libs that should NOT be ignored.
    All other folders under ./libs will be ignored to avoid triggering rebuilds when
    unrelated libraries change.
    """
    all_libs = [
        "admin-api-lib",
        "extractor-api-lib",
        "rag-core-api",
        "rag-core-lib",
    ]
    ignore = []
    for lib in all_libs:
        if lib not in include_libs:
            ignore.append("libs/%s/" % lib)
    return ignore


def create_linter_command(folder_name, name):
    # Build with appropriate Dockerfile based on context
    if folder_name == "./libs":
        dockerfile = folder_name + "/Dockerfile"
        build_args = " --build-arg TEST=0"
    else:
        # For services, always use .dev for testing/linting (dev tools needed)
        dockerfile = folder_name + "/Dockerfile.dev"
        build_args = ""
    return (
        "docker build -t "
        + name
        + build_args
        + " -f "
        + dockerfile
        + " .;docker run --rm --entrypoint make "
        + name
        + " lint"
    )


def create_test_command(folder_name, name):
    # Build with appropriate Dockerfile based on context
    if folder_name == "./libs":
        dockerfile = folder_name + "/Dockerfile"
        build_args = " --build-arg TEST=1"
    else:
        # For services, always use .dev for testing/linting (dev tools needed)
        dockerfile = folder_name + "/Dockerfile.dev"
        build_args = ""
    return (
        "docker build -t "
        + name
        + build_args
        + " -f "
        + dockerfile
        + " .;docker run --rm --entrypoint make "
        + name
        + " test"
    )


########################################################################################################################
########################################## build helm charts ###########################################################
########################################################################################################################
local_resource(
    "core helm chart",
    cmd="cd ./infrastructure/rag && helm dependency update",
    ignore=[
        "infrastructure/rag/charts/keydb-0.48.0.tgz",
        "infrastructure/rag/charts/minio-14.6.7.tgz",
        "infrastructure/rag/charts/langfuse-0.29.1.tgz",
        "infrastructure/rag/charts/qdrant-0.9.1.tgz",
        "infrastructure/rag/charts/ollama-0.29.1.tgz",
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
    docker build -t rag_core --build-arg TEST=0 -f libs/Dockerfile libs;
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
    docker build -t rag_core_lib --build-arg DIRECTORY=rag-core-lib --build-arg TEST=1 -f libs/Dockerfile libs;
    docker run --rm rag_core_lib make test""",
    labels=["test"],
    auto_init=False,
    trigger_mode=TRIGGER_MODE_AUTO,
    allow_parallel=True,
)

local_resource(
    "RAG core API testing",
    """set -e
    docker build -t rag_core_api --build-arg DIRECTORY=rag-core-api --build-arg TEST=1 -f libs/Dockerfile libs;
    docker run --rm rag_core_api make test""",
    labels=["test"],
    auto_init=False,
    trigger_mode=TRIGGER_MODE_AUTO,
    allow_parallel=True,
)

local_resource(
    "Admin API lib testing",
    """set -e
    docker build -t admin_api_lib --build-arg DIRECTORY=admin-api-lib --build-arg TEST=1 -f libs/Dockerfile libs;
    docker run --rm admin_api_lib make test""",
    labels=["test"],
    auto_init=False,
    trigger_mode=TRIGGER_MODE_AUTO,
    allow_parallel=True,
)

local_resource(
    "Extractor API lib testing",
    """set -e
    docker build -t extractor_api_lib --build-arg DIRECTORY=extractor-api-lib --build-arg TEST=1 -f libs/Dockerfile libs;
    docker run --rm extractor_api_lib make test""",
    labels=["test"],
    auto_init=False,
    trigger_mode=TRIGGER_MODE_AUTO,
    allow_parallel=True,
)


########################################################################################################################
################################## build backend_rag image and do live update ##########################################
########################################################################################################################

# Base ignore patterns applied to docker_builds that reference IGNORE_BASE.
# These are files and directories that should not trigger rebuilds: build artifacts,
# Python caches, test caches, virtualenvs, node_modules, and other OS/tooling files.
IGNORE_BASE = [
    # project directories we don't want to include in build context
    "infrastructure/",
    "services/frontend/",
    # Python caches and bytecode
    "**/__pycache__/",
    "**/*.pyc",
    "**/*.pyo",
    "**/*.py[co]",
    ".pytest_cache/",
    "**/.pytest_cache/",
    ".mypy_cache/",
    # virtualenvs / local python envs
    ".venv/",
    "venv/",
    "env/",
    # build artifacts
    "build/",
    "dist/",
    "*.egg-info/",
    # tooling caches
    "node_modules/",
    "**/node_modules/",
    "services/frontend/node_modules/",
    # OS / editor files
    "**/.DS_Store",
    "*.swp",
    "*.swo",
    # pytest / test caches inside libs
    "**/.pytest_cache/",
    # nix / package manager locks and temp files (optional)
    "**/.cache/",
]

# NOTE: full image names should match the one in the helm chart values.yaml!
registry = "ghcr.io/stackitcloud/rag-template"
rag_api_image_name = "rag-backend"

backend_context = "./services/rag-backend"
rag_api_full_image_name = "%s/%s" % (registry, rag_api_image_name)

# Choose dockerfile based on dev mode
backend_dockerfile = backend_context + ("/Dockerfile.dev" if dev_mode else "/Dockerfile")

docker_build_config = {
    "ref": rag_api_full_image_name,
    "context": ".",
    "dockerfile": backend_dockerfile,
    "ignore": IGNORE_BASE + libs_ignore_except(["rag-core-api", "rag-core-lib"]),
}

# Add build args and live_update based on dev mode
if dev_mode:
    docker_build_config["live_update"] = [
        sync(backend_context, "/app/services/rag-backend"),
        sync(core_library_context+"/rag-core-api", "/app/libs/rag-core-api"),
        sync(core_library_context+"/rag-core-lib", "/app/libs/rag-core-lib"),
    ]
else:
    # Use prod-local for Tilt with production Dockerfile
    docker_build_config["build_args"] = {
        "DEPENDENCY_GROUP": "prod-local"
    }

docker_build(**docker_build_config)

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

################################## build mcp image and do live update ##################################################
# NOTE: full image names should match the one in the helm chart values.yaml!
registry = "ghcr.io/stackitcloud/rag-template"
mcp_image_name = "mcp-server"

mcp_context = "./services/mcp-server"
mcp_full_image_name = "%s/%s" % (registry, mcp_image_name)

# Choose dockerfile based on dev mode
mcp_dockerfile = mcp_context + ("/Dockerfile.dev" if dev_mode else "/Dockerfile")

mcp_docker_build_config = {
    "ref": mcp_full_image_name,
    "context": ".",
    "dockerfile": mcp_dockerfile,
    "ignore": IGNORE_BASE + libs_ignore_except([]),
}

# Add live_update only in dev mode
if dev_mode:
    mcp_docker_build_config["live_update"] = [
        sync(mcp_context, "/app/services/mcp-server"),
    ]

docker_build(**mcp_docker_build_config)

# Add linter trigger
local_resource(
    "MCP server linting",
    create_linter_command(mcp_context, "back"),
    labels=["linting"],
    auto_init=False,
    trigger_mode=TRIGGER_MODE_AUTO,
    allow_parallel=True,
)

########################################################################################################################
################################## build admin backend image and do live update ########################################
########################################################################################################################

# NOTE: full image names should match the one in the helm chart values.yaml!
registry = "ghcr.io/stackitcloud/rag-template"
admin_api_image_name = "admin-backend"

admin_backend_context = "./services/admin-backend"
admin_api_full_image_name = "%s/%s" % (registry, admin_api_image_name)

# Choose dockerfile based on dev mode
admin_dockerfile = admin_backend_context + ("/Dockerfile.dev" if dev_mode else "/Dockerfile")

admin_docker_build_config = {
    "ref": admin_api_full_image_name,
    "context": ".",
    "dockerfile": admin_dockerfile,
    "ignore": IGNORE_BASE + libs_ignore_except(["rag-core-lib", "admin-api-lib"]),
}

# Add build args and live_update based on dev mode
if dev_mode:
    admin_docker_build_config["live_update"] = [
        sync(admin_backend_context, "/app/services/admin-backend"),
        sync(core_library_context + "/rag-core-lib", "/app/libs/rag-core-lib"),
        sync(core_library_context + "/admin-api-lib", "/app/libs/admin-api-lib"),
    ]
else:
    # Use prod-local for Tilt with production Dockerfile
    admin_docker_build_config["build_args"] = {
        "DEPENDENCY_GROUP": "prod-local"
    }

docker_build(**admin_docker_build_config)

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

extractor_context = "./services/document-extractor"
document_extractor_full_image_name = "%s/%s" % (registry, document_extractor_image_name)

# Choose dockerfile based on dev mode
extractor_dockerfile = extractor_context + ("/Dockerfile.dev" if dev_mode else "/Dockerfile")

extractor_docker_build_config = {
    "ref": document_extractor_full_image_name,
    "context": ".",
    "dockerfile": extractor_dockerfile,
    "ignore": IGNORE_BASE + libs_ignore_except(["extractor-api-lib"]),
}

# Add build args and live_update based on dev mode
if dev_mode:
    extractor_docker_build_config["live_update"] = [
        sync(extractor_context, "/app/services/document-extractor"),
        sync(core_library_context +"/extractor-api-lib", "/app/libs/extractor-api-lib"),
    ]
else:
    # Use prod-local for Tilt with production Dockerfile
    extractor_docker_build_config["build_args"] = {
        "DEPENDENCY_GROUP": "prod-local"
    }

docker_build(**extractor_docker_build_config)

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

frontend_context = "./services/frontend"
frontend_image_name = "%s/frontend" % (registry)

docker_build(
    frontend_image_name,
    ".",
    dockerfile="./services/frontend/apps/chat-app/Dockerfile",
    # Sync only built assets into the writable Nginx html volume.
    # Avoid syncing sources/.nx into read-only paths in the runtime image.
    live_update=[
        sync("./services/frontend/dist/apps/chat-app", "/usr/share/nginx/html"),
        sync("./services/frontend/dist/libs", "/usr/share/nginx/html/libs"),
    ],
    ignore=[
        # exclude non-frontend areas
        "libs/",
        "services/admin-backend/",
        "services/rag-backend/",
        "services/document-extractor/",
        "services/mcp-server/",
        "infrastructure/",
        "tools/",
        "docs/",
        ".github/",
        ".vscode/",
        # caches/artifacts
        "**/__pycache__/",
        "**/.pytest_cache/",
        ".mypy_cache/",
        ".venv/",
        "venv/",
        "env/",
        "build/",
        "dist/",
        "*.egg-info/",
        # frontend-specific caches
        "services/frontend/.nx/",
        "services/frontend/tmp/",
        "services/frontend/node_modules/",
        # OS/editor files
        ".DS_Store",
        "*.swp",
        "*.swo",
    ],
)

########################################################################################################################
################################## build admin frontend image and do live update ########################################
########################################################################################################################

adminfrontend_context = "./services/frontend"
adminfrontend_image_name = "%s/admin-frontend" % (registry)
docker_build(
    adminfrontend_image_name,
    ".",
    dockerfile="services/frontend/apps/admin-app/Dockerfile",
    # Sync only built assets into the writable Nginx html volume.
    live_update=[
        sync("./services/frontend/dist/apps/admin-app", "/usr/share/nginx/html"),
        sync("./services/frontend/dist/libs", "/usr/share/nginx/html/libs"),
    ],
    ignore=[
        # exclude non-frontend areas
        "libs/",
        "services/admin-backend/",
        "services/rag-backend/",
        "services/document-extractor/",
        "services/mcp-server/",
        "infrastructure/",
        "tools/",
        "docs/",
        ".github/",
        ".vscode/",
        # caches/artifacts
        "**/__pycache__/",
        "**/.pytest_cache/",
        ".mypy_cache/",
        ".venv/",
        "venv/",
        "env/",
        "build/",
        "dist/",
        "*.egg-info/",
        # frontend-specific caches
        "services/frontend/.nx/",
        "services/frontend/tmp/",
        "services/frontend/node_modules/",
        # OS/editor files
        ".DS_Store",
        "*.swp",
        "*.swo",
    ],
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
    "features.minio.enabled=true",
    "shared.config.tls.enabled=false",
    "shared.ssl=false",
    "shared.config.basicAuth.enabled=true",
    "features.mcp.enabled=true",
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
    "./infrastructure/rag",
    name="rag",
    namespace="rag",
    values=[
        "./infrastructure/rag/values.yaml",
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
        ),
        port_forward(
            9090,
            container_port=8000,
            name="MCP-Server",
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

# Frontend test and lint resources (matching GitHub Actions)
local_resource(
    'Frontend testing',
    cmd='cd services/frontend && npm install && npm run test',
    deps=['services/frontend/apps', 'services/frontend/libs', 'services/frontend/package.json', 'services/frontend/package-lock.json'],
    labels=['test'],
    auto_init=False,
    trigger_mode=TRIGGER_MODE_MANUAL,
    allow_parallel=True,
)

local_resource(
    'Frontend linting',
    cmd='cd services/frontend && npm install && npm run eslint',
    deps=['services/frontend/apps', 'services/frontend/libs', 'services/frontend/package.json', 'services/frontend/package-lock.json'],
    labels=['linting'],
    auto_init=False,
    trigger_mode=TRIGGER_MODE_MANUAL,
    allow_parallel=True,
)

# Infrastructure validation resources (matching GitHub Actions)
local_resource(
    'Terraform format check',
    cmd='cd infrastructure/terraform && terraform fmt -check -recursive',
    deps=['infrastructure/terraform'],
    labels=['linting'],
    auto_init=False,
    trigger_mode=TRIGGER_MODE_MANUAL,
    allow_parallel=True,
)

local_resource(
    'Terraform validate',
    cmd='cd infrastructure/terraform && terraform init -backend=false && terraform validate',
    deps=['infrastructure/terraform'],
    labels=['linting'],
    auto_init=False,
    trigger_mode=TRIGGER_MODE_MANUAL,
    allow_parallel=True,
)

local_resource(
    'Helm chart validation',
    cmd='helm lint infrastructure/rag/',
    deps=['infrastructure/rag'],
    labels=['linting'],
    auto_init=False,
    trigger_mode=TRIGGER_MODE_MANUAL,
    allow_parallel=True,
)
