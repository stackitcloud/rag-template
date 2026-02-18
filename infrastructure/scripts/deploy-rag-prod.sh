#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INFRA_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
TF_DIR="${INFRA_DIR}/terraform"
SEED_DIR="${TF_DIR}/seed-secrets"
BACKEND_CONFIG_FILE="${TF_DIR}/.backend.hcl"
BASE_CHART_DIR="${INFRA_DIR}/server-setup/base-setup"
RAG_CHART_DIR="${INFRA_DIR}/server-setup/rag-setup"

AUTO_APPROVE=0
SKIP_BACKEND_BOOTSTRAP=0
HELM_TIMEOUT="20m"
BASE_NAMESPACE="cert-manager"
RAG_NAMESPACE="rag"
VAULT_USERPASS_NAMESPACE="cert-manager"
VALUES_OUTPUT_FILE="${RAG_CHART_DIR}/values.prod.auto.yaml"
SEED_TFVARS_FILE="${SEED_DIR}/terraform.tfvars"
ISSUER_EMAIL=""

usage() {
  cat <<'EOF'
Deploy full RAG production setup in one run:
- Terraform infra apply
- Seed Secrets Manager (rag-secrets)
- Generate rag-setup prod Helm values from Terraform outputs
- Deploy base-setup and rag-setup charts

Usage:
  ./infrastructure/scripts/deploy-rag-prod.sh --issuer-email <email> [options]

Options:
  --issuer-email <email>         Required ACME email for cert-manager ClusterIssuer.
  --auto-approve                 Pass -auto-approve to Terraform apply commands.
  --skip-backend-bootstrap       Skip terraform backend bootstrap helper.
  --seed-tfvars-file <path>      Seed secrets tfvars file (default: infrastructure/terraform/seed-secrets/terraform.tfvars).
  --values-output-file <path>    Generated rag values file path (default: infrastructure/server-setup/rag-setup/values.prod.auto.yaml).
  --base-namespace <name>        Namespace for base-setup release (default: cert-manager).
  --rag-namespace <name>         Namespace for rag-setup release (default: rag).
  --vault-userpass-namespace <name>
                                 Namespace for stackit-vault-userpass secret (default: cert-manager).
  --helm-timeout <duration>      Helm wait timeout (default: 20m).
  -h, --help                     Show this help.

Required precondition:
  - seed-secrets tfvars exists and includes user-provided app/API values in rag_secrets.
    This script auto-injects vault_mount_path, vault_username, vault_password and
    overrides Terraform-derived keys (POSTGRES_PASSWORD, REDIS_USERNAME, REDIS_PASSWORD,
    S3_ACCESS_KEY_ID, S3_SECRET_ACCESS_KEY, STACKIT_EMBEDDER_API_KEY,
    STACKIT_VLLM_API_KEY, RAGAS_OPENAI_API_KEY).
    STACKIT_CERT_MANAGER_SA_JSON must be provided in tfvars (rag_secrets or rag_secrets_overrides).
    It also auto-generates selected secrets with openssl when missing/placeholder:
    LANGFUSE_INIT_USER_PASSWORD, LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY,
    LANGFUSE_SALT, LANGFUSE_NEXTAUTH, BASIC_AUTH_PASSWORD, CLICKHOUSE_PASSWORD.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --issuer-email)
      ISSUER_EMAIL="${2:-}"
      shift 2
      ;;
    --auto-approve)
      AUTO_APPROVE=1
      shift
      ;;
    --skip-backend-bootstrap)
      SKIP_BACKEND_BOOTSTRAP=1
      shift
      ;;
    --seed-tfvars-file)
      SEED_TFVARS_FILE="${2:-}"
      shift 2
      ;;
    --values-output-file)
      VALUES_OUTPUT_FILE="${2:-}"
      shift 2
      ;;
    --base-namespace)
      BASE_NAMESPACE="${2:-}"
      shift 2
      ;;
    --rag-namespace)
      RAG_NAMESPACE="${2:-}"
      shift 2
      ;;
    --vault-userpass-namespace)
      VAULT_USERPASS_NAMESPACE="${2:-}"
      shift 2
      ;;
    --helm-timeout)
      HELM_TIMEOUT="${2:-}"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

if [[ -z "${ISSUER_EMAIL}" ]]; then
  echo "--issuer-email is required." >&2
  usage >&2
  exit 1
fi

if [[ ! -f "${SEED_TFVARS_FILE}" ]]; then
  echo "Seed tfvars file not found: ${SEED_TFVARS_FILE}" >&2
  echo "Copy ${SEED_DIR}/terraform.tfvars.example and fill app/API values in rag_secrets first." >&2
  echo "The deploy script injects vault_* and Terraform-derived DB/Redis/S3/model-serving values automatically." >&2
  exit 1
fi

for cmd in terraform helm kubectl jq grep awk openssl; do
  if ! command -v "${cmd}" >/dev/null 2>&1; then
    echo "Missing required command: ${cmd}" >&2
    exit 1
  fi
done

rag_dependency_repo="$(
  awk '
    BEGIN { in_rag = 0 }
    /^[[:space:]]*-[[:space:]]*name:[[:space:]]*rag[[:space:]]*$/ { in_rag = 1; next }
    in_rag && /^[[:space:]]*repository:[[:space:]]*/ {
      line = $0
      sub(/^[[:space:]]*repository:[[:space:]]*/, "", line)
      gsub(/["'\''[:space:]]/, "", line)
      print line
      exit
    }
  ' "${RAG_CHART_DIR}/Chart.yaml"
)"

if [[ "${rag_dependency_repo}" == file://* ]]; then
  echo "Production deploy requires rag-setup to use a published rag chart repository, not ${rag_dependency_repo}." >&2
  echo "Update ${RAG_CHART_DIR}/Chart.yaml dependency 'rag.repository' to the published GitHub chart repo first." >&2
  exit 1
fi

if grep -Eq '<<[^>]+>>' "${SEED_TFVARS_FILE}"; then
  echo "Warning: ${SEED_TFVARS_FILE} still contains placeholder markers (<<...>>)." >&2
  echo "Deployment will continue, but placeholder values may be written for unreplaced keys." >&2
fi

if ! grep -Eq '^[[:space:]]*STACKIT_CERT_MANAGER_SA_JSON[[:space:]]*=' "${SEED_TFVARS_FILE}"; then
  echo "Seed tfvars must define STACKIT_CERT_MANAGER_SA_JSON (in rag_secrets or rag_secrets_overrides)." >&2
  exit 1
fi

approve_args=()
if [[ "${AUTO_APPROVE}" -eq 1 ]]; then
  approve_args+=("-auto-approve")
fi

log() {
  echo "[deploy-rag-prod] $*"
}

extract_rag_secret_value() {
  local key="$1"
  local raw_value

  raw_value="$(awk -v wanted="${key}" '
    BEGIN { in_map = 0 }
    /^[[:space:]]*rag_secrets[[:space:]]*=[[:space:]]*{/ { in_map = 1; next }
    in_map && /^[[:space:]]*}/ { in_map = 0; next }
    in_map {
      line = $0
      sub(/#.*/, "", line)
      if (match(line, "^[[:space:]]*" wanted "[[:space:]]*=")) {
        sub("^[[:space:]]*" wanted "[[:space:]]*=[[:space:]]*", "", line)
        gsub(/^[[:space:]]+|[[:space:]]+$/, "", line)
        print line
        exit
      }
    }
  ' "${SEED_TFVARS_FILE}")"

  raw_value="${raw_value#"${raw_value%%[![:space:]]*}"}"
  raw_value="${raw_value%"${raw_value##*[![:space:]]}"}"

  if [[ "${raw_value}" == \"*\" && "${raw_value}" == *\" ]]; then
    raw_value="${raw_value:1:${#raw_value}-2}"
  elif [[ "${raw_value}" == \'*\' && "${raw_value}" == *\' ]]; then
    raw_value="${raw_value:1:${#raw_value}-2}"
  fi

  printf '%s' "${raw_value}"
}

is_missing_or_placeholder() {
  local value="$1"
  [[ -z "${value}" || "${value}" == *"<<"*">>"* ]]
}

if [[ "${SKIP_BACKEND_BOOTSTRAP}" -eq 0 ]]; then
  log "Bootstrapping Terraform backend if needed"
  BOOTSTRAP_AUTO_APPROVE="${AUTO_APPROVE}" "${TF_DIR}/scripts/init-backend.sh"
else
  log "Skipping backend bootstrap by request"
fi

log "Applying main Terraform stack"
if [[ -f "${BACKEND_CONFIG_FILE}" ]]; then
  terraform -chdir="${TF_DIR}" init -reconfigure -backend-config="${BACKEND_CONFIG_FILE}"
else
  terraform -chdir="${TF_DIR}" init -reconfigure
fi
terraform -chdir="${TF_DIR}" apply "${approve_args[@]}"

log "Reading Terraform outputs"
secretsmanager_instance_id="$(terraform -chdir="${TF_DIR}" output -raw secretsmanager_instance_id)"
secretsmanager_username="$(terraform -chdir="${TF_DIR}" output -raw secretsmanager_username)"
secretsmanager_password="$(terraform -chdir="${TF_DIR}" output -raw secretsmanager_password)"
postgres_password="$(terraform -chdir="${TF_DIR}" output -raw postgres_password)"
redis_username="$(terraform -chdir="${TF_DIR}" output -raw redis_username)"
redis_password="$(terraform -chdir="${TF_DIR}" output -raw redis_password)"
s3_access_key_id="$(terraform -chdir="${TF_DIR}" output -raw object_storage_access_key)"
s3_secret_access_key="$(terraform -chdir="${TF_DIR}" output -raw object_storage_secret_key)"
model_serving_bearer_token="$(terraform -chdir="${TF_DIR}" output -raw model_serving_bearer_token 2>/dev/null || true)"
dns_name="$(terraform -chdir="${TF_DIR}" output -raw dns_name | sed 's/\.$//')"

if [[ -n "${model_serving_bearer_token}" ]]; then
  log "Found model serving bearer token output for STACKIT_* and RAGAS_OPENAI_API_KEY overrides"
else
  log "No model_serving_bearer_token output found; STACKIT_EMBEDDER_API_KEY/STACKIT_VLLM_API_KEY/RAGAS_OPENAI_API_KEY will not be auto-overridden"
fi

generated_langfuse_init_user_password=""
generated_langfuse_public_key=""
generated_langfuse_secret_key=""
generated_langfuse_salt=""
generated_langfuse_nextauth=""
generated_basic_auth_password=""
generated_clickhouse_password=""
generated_basic_auth=""

if is_missing_or_placeholder "$(extract_rag_secret_value "LANGFUSE_INIT_USER_PASSWORD")"; then
  generated_langfuse_init_user_password="$(openssl rand -hex 24)"
  log "Generated LANGFUSE_INIT_USER_PASSWORD override"
fi

if is_missing_or_placeholder "$(extract_rag_secret_value "LANGFUSE_PUBLIC_KEY")"; then
  generated_langfuse_public_key="pk-lf-$(openssl rand -hex 16)"
  log "Generated LANGFUSE_PUBLIC_KEY override"
fi

if is_missing_or_placeholder "$(extract_rag_secret_value "LANGFUSE_SECRET_KEY")"; then
  generated_langfuse_secret_key="sk-lf-$(openssl rand -hex 32)"
  log "Generated LANGFUSE_SECRET_KEY override"
fi

if is_missing_or_placeholder "$(extract_rag_secret_value "LANGFUSE_SALT")"; then
  generated_langfuse_salt="$(openssl rand -hex 32)"
  log "Generated LANGFUSE_SALT override"
fi

if is_missing_or_placeholder "$(extract_rag_secret_value "LANGFUSE_NEXTAUTH")"; then
  generated_langfuse_nextauth="$(openssl rand -hex 32)"
  log "Generated LANGFUSE_NEXTAUTH override"
fi

if is_missing_or_placeholder "$(extract_rag_secret_value "BASIC_AUTH_PASSWORD")"; then
  generated_basic_auth_password="$(openssl rand -hex 24)"
  log "Generated BASIC_AUTH_PASSWORD override"
fi

if is_missing_or_placeholder "$(extract_rag_secret_value "CLICKHOUSE_PASSWORD")"; then
  generated_clickhouse_password="$(openssl rand -hex 24)"
  log "Generated CLICKHOUSE_PASSWORD override"
fi

if [[ -n "${generated_basic_auth_password}" ]]; then
  basic_auth_user="$(extract_rag_secret_value "BASIC_AUTH_USER")"
  if ! is_missing_or_placeholder "${basic_auth_user}"; then
    generated_basic_auth_hash="$(openssl passwd -apr1 "${generated_basic_auth_password}")"
    generated_basic_auth="${basic_auth_user}:${generated_basic_auth_hash}"
    log "Generated BASIC_AUTH override from BASIC_AUTH_USER + generated BASIC_AUTH_PASSWORD"
  else
    log "BASIC_AUTH_USER missing/placeholder; BASIC_AUTH override was not generated"
  fi
fi

seed_override_file="$(mktemp)"
cleanup() {
  rm -f "${seed_override_file}"
}
trap cleanup EXIT

jq -n \
  --arg vault_mount_path "${secretsmanager_instance_id}" \
  --arg vault_username "${secretsmanager_username}" \
  --arg vault_password "${secretsmanager_password}" \
  --arg postgres_password "${postgres_password}" \
  --arg redis_username "${redis_username}" \
  --arg redis_password "${redis_password}" \
  --arg s3_access_key_id "${s3_access_key_id}" \
  --arg s3_secret_access_key "${s3_secret_access_key}" \
  --arg model_serving_bearer_token "${model_serving_bearer_token}" \
  --arg generated_langfuse_init_user_password "${generated_langfuse_init_user_password}" \
  --arg generated_langfuse_public_key "${generated_langfuse_public_key}" \
  --arg generated_langfuse_secret_key "${generated_langfuse_secret_key}" \
  --arg generated_langfuse_salt "${generated_langfuse_salt}" \
  --arg generated_langfuse_nextauth "${generated_langfuse_nextauth}" \
  --arg generated_basic_auth_password "${generated_basic_auth_password}" \
  --arg generated_clickhouse_password "${generated_clickhouse_password}" \
  --arg generated_basic_auth "${generated_basic_auth}" \
  '{
    vault_mount_path: $vault_mount_path,
    vault_username: $vault_username,
    vault_password: $vault_password,
    rag_secrets_overrides: (
      {
        POSTGRES_PASSWORD: $postgres_password,
        REDIS_USERNAME: $redis_username,
        REDIS_PASSWORD: $redis_password,
        S3_ACCESS_KEY_ID: $s3_access_key_id,
        S3_SECRET_ACCESS_KEY: $s3_secret_access_key
      } + (
        if $model_serving_bearer_token != "" then
          (
            {
              STACKIT_EMBEDDER_API_KEY: $model_serving_bearer_token,
              STACKIT_VLLM_API_KEY: $model_serving_bearer_token,
              RAGAS_OPENAI_API_KEY: $model_serving_bearer_token
            }
          )
        else
          {}
        end
      ) + (
        if $generated_langfuse_init_user_password != "" then
          { LANGFUSE_INIT_USER_PASSWORD: $generated_langfuse_init_user_password }
        else
          {}
        end
      ) + (
        if $generated_langfuse_public_key != "" then
          { LANGFUSE_PUBLIC_KEY: $generated_langfuse_public_key }
        else
          {}
        end
      ) + (
        if $generated_langfuse_secret_key != "" then
          { LANGFUSE_SECRET_KEY: $generated_langfuse_secret_key }
        else
          {}
        end
      ) + (
        if $generated_langfuse_salt != "" then
          { LANGFUSE_SALT: $generated_langfuse_salt }
        else
          {}
        end
      ) + (
        if $generated_langfuse_nextauth != "" then
          { LANGFUSE_NEXTAUTH: $generated_langfuse_nextauth }
        else
          {}
        end
      ) + (
        if $generated_basic_auth_password != "" then
          { BASIC_AUTH_PASSWORD: $generated_basic_auth_password }
        else
          {}
        end
      ) + (
        if $generated_clickhouse_password != "" then
          { CLICKHOUSE_PASSWORD: $generated_clickhouse_password }
        else
          {}
        end
      ) + (
        if $generated_basic_auth != "" then
          { BASIC_AUTH: $generated_basic_auth }
        else
          {}
        end
      )
    )
  }' > "${seed_override_file}"

log "Applying seed-secrets stack"
terraform -chdir="${SEED_DIR}" init
terraform -chdir="${SEED_DIR}" apply \
  "${approve_args[@]}" \
  -var-file="${SEED_TFVARS_FILE}" \
  -var-file="${seed_override_file}"

log "Generating rag-setup production values"
"${TF_DIR}/scripts/generate-rag-setup-prod-values.sh" \
  --terraform-dir "${TF_DIR}" \
  --output "${VALUES_OUTPUT_FILE}"

log "Ensuring namespaces exist"
kubectl get namespace "${BASE_NAMESPACE}" >/dev/null 2>&1 || kubectl create namespace "${BASE_NAMESPACE}"
kubectl get namespace "${RAG_NAMESPACE}" >/dev/null 2>&1 || kubectl create namespace "${RAG_NAMESPACE}"
kubectl get namespace "${VAULT_USERPASS_NAMESPACE}" >/dev/null 2>&1 || kubectl create namespace "${VAULT_USERPASS_NAMESPACE}"

log "Syncing stackit-vault-userpass secret in namespace ${VAULT_USERPASS_NAMESPACE}"
kubectl -n "${VAULT_USERPASS_NAMESPACE}" create secret generic stackit-vault-userpass \
  --from-literal=password="${secretsmanager_password}" \
  --dry-run=client -o yaml | kubectl apply -f -

log "Updating Helm dependencies"
helm dependency update "${BASE_CHART_DIR}"
helm dependency update "${RAG_CHART_DIR}"

log "Deploying base-setup chart"
helm upgrade --install base-setup "${BASE_CHART_DIR}" \
  -n "${BASE_NAMESPACE}" \
  --create-namespace \
  --set certIssuer.email="${ISSUER_EMAIL}" \
  --wait \
  --timeout "${HELM_TIMEOUT}"

log "Deploying rag-setup chart"
helm upgrade --install rag-setup "${RAG_CHART_DIR}" \
  -n "${RAG_NAMESPACE}" \
  --create-namespace \
  -f "${RAG_CHART_DIR}/values.yaml" \
  -f "${VALUES_OUTPUT_FILE}" \
  --wait \
  --timeout "${HELM_TIMEOUT}"

log "Done"
echo "RAG URL: https://rag.${dns_name}"
echo "Admin URL: https://admin.${dns_name}"
