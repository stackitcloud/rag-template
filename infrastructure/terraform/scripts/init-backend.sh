#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
root_dir="$(cd "${script_dir}/.." && pwd)"

backend_config_file="${BACKEND_CONFIG_FILE:-${root_dir}/.backend.hcl}"
auto_approve="${BOOTSTRAP_AUTO_APPROVE:-0}"
main_tf="${root_dir}/main.tf"
main_tf_backup=""

cd "${root_dir}"

if ! command -v terraform >/dev/null 2>&1; then
  echo "terraform is not installed or not in PATH." >&2
  exit 1
fi

read_output_raw() {
  local output_name="$1"
  terraform output -raw "${output_name}" 2>/dev/null || true
}

is_valid_output_value() {
  local value="$1"
  [[ -n "${value}" ]] || return 1
  [[ "${value}" != *"No outputs found"* ]] || return 1
  [[ "${value}" != *$'\n'* ]] || return 1
  return 0
}

if [ -f "${backend_config_file}" ]; then
  # Recover from previously corrupted backend config files.
  if grep -q "No outputs found" "${backend_config_file}"; then
    echo "Detected invalid ${backend_config_file}; regenerating it."
    rm -f "${backend_config_file}"
  else
    terraform init -reconfigure -backend-config="${backend_config_file}"
    exit 0
  fi
fi

restore_main_tf() {
  if [ -n "${main_tf_backup}" ] && [ -f "${main_tf_backup}" ]; then
    cp "${main_tf_backup}" "${main_tf}"
    rm -f "${main_tf_backup}"
    main_tf_backup=""
  fi
}

prepare_local_bootstrap_config() {
  if [ ! -f "${main_tf}" ]; then
    echo "Expected Terraform file not found: ${main_tf}" >&2
    exit 1
  fi

  main_tf_backup="$(mktemp)"
  cp "${main_tf}" "${main_tf_backup}"

  awk '
    BEGIN {
      skip = 0
      depth = 0
    }
    {
      line = $0
      if (!skip && line ~ /^[[:space:]]*backend[[:space:]]+"s3"[[:space:]]*{/) {
        skip = 1
      }
      if (skip) {
        opens = gsub(/{/, "{", line)
        closes = gsub(/}/, "}", line)
        depth += opens - closes
        if (depth <= 0) {
          skip = 0
          depth = 0
        }
        next
      }
      print $0
    }
  ' "${main_tf_backup}" > "${main_tf}"
}

trap restore_main_tf EXIT

echo "Bootstrapping object storage for Terraform state (local backend)."
prepare_local_bootstrap_config
terraform init -reconfigure

bucket="$(read_output_raw object_storage_bucket)"
access_key="$(read_output_raw object_storage_access_key)"
secret_key="$(read_output_raw object_storage_secret_key)"

if ! is_valid_output_value "${bucket}" || ! is_valid_output_value "${access_key}" || ! is_valid_output_value "${secret_key}"; then
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
  bucket="$(read_output_raw object_storage_bucket)"
  access_key="$(read_output_raw object_storage_access_key)"
  secret_key="$(read_output_raw object_storage_secret_key)"
fi

if ! is_valid_output_value "${bucket}" || ! is_valid_output_value "${access_key}" || ! is_valid_output_value "${secret_key}"; then
  echo "Failed to read valid backend outputs after bootstrap apply." >&2
  echo "bucket='${bucket}'" >&2
  echo "access_key length=${#access_key}" >&2
  echo "secret_key length=${#secret_key}" >&2
  exit 1
fi

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

restore_main_tf
trap - EXIT

terraform init -reconfigure -backend-config="${backend_config_file}" -force-copy
