# Seed Secrets Manager data with Terraform

This folder writes the `rag-secrets` KV secret used by External Secrets.

Why this is a separate step:
- The Secrets Manager instance ID and user credentials are created by the main Terraform stack.
- Provider blocks cannot depend on resources, so we pass them in via variables and run a second apply.

## Steps

1. Apply the main stack to create the Secrets Manager instance and user.
2. Copy `terraform.tfvars.example` to `terraform.tfvars` and fill in the values:
   - `vault_mount_path` is the Secrets Manager instance ID.
   - `vault_username`/`vault_password` are from the `secretsmanager_*` outputs.
   - `rag_secrets` should include all keys referenced by your ExternalSecret resources.
     For the cert-manager webhook, store the service account key JSON under `STACKIT_CERT_MANAGER_SA_JSON` (use a heredoc to avoid escaping).
3. Run:
   ```bash
   terraform init
   terraform plan
   terraform apply
   ```

## Security note

All values written by `vault_kv_secret_v2` are stored in Terraform state. Use a secure backend and restrict access.

## Troubleshooting

If you see a 404 from `auth/token/create`, the backend does not allow child token creation.
This module sets `skip_child_token = true` so Vault uses the login token directly.
