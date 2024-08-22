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
