resource "stackit_ske_project" "rag-ske" {
  project_id = var.stackit_project_id
}

resource "stackit_ske_cluster" "rag-ske" {
  project_id         = stackit_ske_project.rag-ske.id
  name               = "rag"
  kubernetes_version = "1.27"
  node_pools = [
    {
    name         = "rag-node1"
    machine_type = "g1.4"
    max_surge    = 1
    minimum            = "1"
    maximum            = "1"
    availability_zones = ["eu01-1"]
    os_version = "3815.2.5"
    volume_size = 320
    volume_type = "storage_premium_perf0"
    }
  ]
  maintenance = {
    enable_kubernetes_version_updates    = true
    enable_machine_image_version_updates = true
    start                                = "01:00:00Z"
    end                                  = "02:00:00Z"
  }
}

resource "stackit_objectstorage_credentials_group" "credentials-group" {  
  project_id = stackit_ske_project.rag-ske.id
  name       = "credentials-group"
  depends_on = [stackit_ske_project.rag-ske, stackit_objectstorage_bucket.docs]
}

resource "stackit_objectstorage_credential" "misc-creds" {
  depends_on = [stackit_objectstorage_credentials_group.credentials-group]
  project_id           = stackit_objectstorage_credentials_group.credentials-group.project_id
  credentials_group_id = stackit_objectstorage_credentials_group.credentials-group.credentials_group_id
  expiration_timestamp = "2027-01-02T03:04:05Z"
}

resource "stackit_objectstorage_bucket" "docs" {
  project_id = stackit_ske_project.rag-ske.id
  name       = "docs"
}