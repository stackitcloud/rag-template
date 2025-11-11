resource "stackit_objectstorage_bucket" "documents" {
  name       = "${var.name_prefix}-documents-${var.deployment_timestamp}"
  project_id = var.project_id
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
  expiration_timestamp = timeadd(timestamp(), "8760h") # Expires after 1 year
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
  value = stackit_objectstorage_bucket.documents.name
}
