#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
root_dir="$(cd "${script_dir}/.." && pwd)"

backend_config_file="${BACKEND_CONFIG_FILE:-${root_dir}/.backend.hcl}"
auto_approve="${BOOTSTRAP_AUTO_APPROVE:-0}"

cd "${root_dir}"

if ! command -v terraform >/dev/null 2>&1; then
  echo "terraform is not installed or not in PATH." >&2
  exit 1
fi

if [ -f "${backend_config_file}" ]; then
  terraform init -backend-config="${backend_config_file}"
  exit 0
fi

echo "Bootstrapping object storage for Terraform state (local backend)."
terraform init -backend=false

if ! bucket="$(terraform output -raw object_storage_bucket 2>/dev/null)"; then
  apply_args=(
    "-target=stackit_objectstorage_bucket.tfstate"
    "-target=stackit_objectstorage_credentials_group.rag_creds_group"
    "-target=stackit_objectstorage_credential.rag_creds"
    "-target=time_rotating.key_rotation"       # <--- Add this (needed for creds)
    "-target=output.object_storage_bucket"     # <--- Add this
    "-target=output.object_storage_access_key" # <--- Add this
    "-target=output.object_storage_secret_key" # <--- Add this
  )
  if [ "${auto_approve}" = "1" ]; then
    terraform apply -auto-approve "${apply_args[@]}"
  else
    terraform apply "${apply_args[@]}"
  fi
  bucket="$(terraform output -raw object_storage_bucket)"
fi

access_key="$(terraform output -raw object_storage_access_key)"
secret_key="$(terraform output -raw object_storage_secret_key)"

cat > "${backend_config_file}" <<EOF
bucket = "${bucket}"
key    = "terraform.tfstate"
region = "eu01"

access_key = "${access_key}"
secret_key = "${secret_key}"

endpoints = {
  s3 = "https://object.storage.eu01.onstackit.cloud"
}

skip_credentials_validation = true
skip_region_validation      = true
skip_s3_checksum            = true
skip_requesting_account_id  = true
EOF

chmod 600 "${backend_config_file}"

terraform init -backend-config="${backend_config_file}" -force-copy
