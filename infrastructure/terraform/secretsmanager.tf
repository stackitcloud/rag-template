resource "stackit_secretsmanager_instance" "rag_secrets" {
  project_id = var.project_id
  name       = "${var.name_prefix}-secrets"
}

resource "stackit_secretsmanager_user" "rag_secrets_user" {
  project_id    = var.project_id
  instance_id   = stackit_secretsmanager_instance.rag_secrets.instance_id
  description   = var.secretsmanager_user_description
  write_enabled = var.secretsmanager_user_write_enabled
}

output "secretsmanager_instance_id" {
  value = stackit_secretsmanager_instance.rag_secrets.instance_id
}

output "secretsmanager_username" {
  value = stackit_secretsmanager_user.rag_secrets_user.username
}

output "secretsmanager_password" {
  value     = stackit_secretsmanager_user.rag_secrets_user.password
  sensitive = true
}
