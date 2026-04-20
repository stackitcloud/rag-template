# Seed Secrets Manager data with Terraform

This folder writes the `rag-secrets` KV secret used by External Secrets.

Why this is a separate step:
- The Secrets Manager instance ID and user credentials are created by the main Terraform stack.
- Provider blocks cannot depend on resources, so we pass them in via variables and run a second apply.

## Steps

1. Apply the main stack to create the Secrets Manager instance and user.
2. Copy `terraform.tfvars.example` to `terraform.tfvars` and fill `rag_secrets` with app/API values referenced by your ExternalSecret resources.
   Include `STACKIT_CERT_MANAGER_SA_JSON` (service account key JSON for STACKIT DNS webhook auth) via `rag_secrets` or `rag_secrets_overrides`.
3. Run (standalone mode):
   ```bash
   terraform init
   terraform plan
   terraform apply
   ```
4. In standalone mode, also provide the Vault connection variables (`vault_mount_path`, `vault_username`, `vault_password`) from main-stack outputs, either in `terraform.tfvars` or an extra `-var-file`.

When using `infrastructure/scripts/deploy-rag-prod.sh`, the script auto-injects:
- `vault_mount_path`
- `vault_username`
- `vault_password`

And it passes `rag_secrets_overrides` automatically for:
- `POSTGRES_PASSWORD`
- `REDIS_USERNAME`
- `REDIS_PASSWORD`
- `S3_ACCESS_KEY_ID`
- `S3_SECRET_ACCESS_KEY`
- `STACKIT_EMBEDDER_API_KEY` (from Terraform output `model_serving_bearer_token`)
- `STACKIT_VLLM_API_KEY` (from Terraform output `model_serving_bearer_token`)
- `RAGAS_OPENAI_API_KEY` (from Terraform output `model_serving_bearer_token`)

`STACKIT_CERT_MANAGER_SA_JSON` is not auto-generated and must be provided in your tfvars.

Additionally, `deploy-rag-prod.sh` auto-generates these values with `openssl` when they are missing or still placeholders in `rag_secrets`:
- `LANGFUSE_INIT_USER_PASSWORD`
- `LANGFUSE_PUBLIC_KEY`
- `LANGFUSE_SECRET_KEY`
- `LANGFUSE_SALT`
- `LANGFUSE_NEXTAUTH`
- `BASIC_AUTH_PASSWORD` (and `BASIC_AUTH` if `BASIC_AUTH_USER` is set)
- `CLICKHOUSE_PASSWORD`

## Security note

All values written by `vault_kv_secret_v2` are stored in Terraform state. Use a secure backend and restrict access.

## Troubleshooting

If you see a 404 from `auth/token/create`, the backend does not allow child token creation.
This module sets `skip_child_token = true` so Vault uses the login token directly.
