# This resource stays stable for 365 days, then changes
resource "time_rotating" "key_rotation" {
  rotation_days = 365
}

resource "stackit_objectstorage_bucket" "documents" {
  name       = "${var.name_prefix}-documents-${var.deployment_timestamp}"
  project_id = var.project_id
}

resource "stackit_objectstorage_bucket" "tfstate" {
  name       = "${var.name_prefix}-tfstate-${var.deployment_timestamp}"
  project_id = var.project_id
  depends_on = [stackit_objectstorage_credentials_group.rag_creds_group]
}

resource "stackit_objectstorage_bucket" "langfuse" {
  name       = "${var.name_prefix}-langfuse-${var.deployment_timestamp}"
  project_id = var.project_id
}

resource "stackit_objectstorage_credentials_group" "rag_creds_group" {
  project_id = var.project_id
  name       = "${var.name_prefix}-credentials"
}

resource "stackit_objectstorage_credential" "rag_creds" {
  project_id           = var.project_id
  credentials_group_id = stackit_objectstorage_credentials_group.rag_creds_group.credentials_group_id
  expiration_timestamp = timeadd(time_rotating.key_rotation.rfc3339, "8760h")
}

output "object_storage_access_key" {
  value     = stackit_objectstorage_credential.rag_creds.access_key
  sensitive = true
}

output "object_storage_secret_key" {
  value     = stackit_objectstorage_credential.rag_creds.secret_access_key
  sensitive = true
}

output "object_storage_bucket" {
  value = stackit_objectstorage_bucket.tfstate.name
}
