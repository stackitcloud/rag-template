#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INFRA_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
TF_DIR="${INFRA_DIR}/terraform"
SEED_DIR="${TF_DIR}/seed-secrets"
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
  - seed-secrets tfvars exists and includes app/API secrets in rag_secrets.
    Infra-derived keys (POSTGRES_PASSWORD, REDIS_USERNAME, REDIS_PASSWORD,
    S3_ACCESS_KEY_ID, S3_SECRET_ACCESS_KEY) are auto-overridden from Terraform outputs.
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
  echo "Copy ${SEED_DIR}/terraform.tfvars.example and fill app/API secrets first." >&2
  exit 1
fi

for cmd in terraform helm kubectl jq grep; do
  if ! command -v "${cmd}" >/dev/null 2>&1; then
    echo "Missing required command: ${cmd}" >&2
    exit 1
  fi
done

if grep -Eq '<<[^>]+>>' "${SEED_TFVARS_FILE}"; then
  echo "Warning: ${SEED_TFVARS_FILE} still contains placeholder markers (<<...>>)." >&2
  echo "Deployment will continue, but seed-secrets apply may fail or write placeholder values." >&2
fi

approve_args=()
if [[ "${AUTO_APPROVE}" -eq 1 ]]; then
  approve_args+=("-auto-approve")
fi

log() {
  echo "[deploy-rag-prod] $*"
}

if [[ "${SKIP_BACKEND_BOOTSTRAP}" -eq 0 ]]; then
  log "Bootstrapping Terraform backend if needed"
  BOOTSTRAP_AUTO_APPROVE="${AUTO_APPROVE}" "${TF_DIR}/scripts/init-backend.sh"
else
  log "Skipping backend bootstrap by request"
fi

log "Applying main Terraform stack"
terraform -chdir="${TF_DIR}" init
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
dns_name="$(terraform -chdir="${TF_DIR}" output -raw dns_name | sed 's/\.$//')"

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
  '{
    vault_mount_path: $vault_mount_path,
    vault_username: $vault_username,
    vault_password: $vault_password,
    rag_secrets_overrides: {
      POSTGRES_PASSWORD: $postgres_password,
      REDIS_USERNAME: $redis_username,
      REDIS_PASSWORD: $redis_password,
      S3_ACCESS_KEY_ID: $s3_access_key_id,
      S3_SECRET_ACCESS_KEY: $s3_secret_access_key
    }
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
