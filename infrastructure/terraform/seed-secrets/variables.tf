variable "vault_address" {
  description = "Vault address (STACKIT Secrets Manager URL)."
  type        = string
  default     = "https://prod.sm.eu01.stackit.cloud"
}

variable "vault_mount_path" {
  description = "Secrets Manager instance ID (KV mount path)."
  type        = string
}

variable "vault_userpass_path" {
  description = "Vault userpass auth path."
  type        = string
  default     = "userpass"
}

variable "vault_username" {
  description = "Secrets Manager user name."
  type        = string
}

variable "vault_password" {
  description = "Secrets Manager user password."
  type        = string
  sensitive   = true
}

variable "vault_secret_name" {
  description = "KV secret name used by External Secrets."
  type        = string
  default     = "rag-secrets"
}

variable "rag_secrets" {
  description = "Map of secret keys/values stored under the rag-secrets secret."
  type        = map(string)
  sensitive   = true
}
