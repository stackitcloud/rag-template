terraform {
  required_providers {
    vault = {
      source  = "hashicorp/vault"
      version = "~> 5.6"
    }
  }
}

provider "vault" {
  address          = var.vault_address
  skip_child_token = true

  auth_login {
    path = "auth/${var.vault_userpass_path}/login/${var.vault_username}"
    parameters = {
      password = var.vault_password
    }
  }
}

resource "vault_kv_secret_v2" "rag_docs" {
  mount     = var.vault_mount_path
  name      = var.vault_secret_name
  data_json = jsonencode(var.rag_secrets)
}
