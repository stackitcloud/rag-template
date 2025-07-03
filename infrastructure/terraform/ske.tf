resource "stackit_ske_cluster" "rag_cluster" {
  project_id             = var.project_id
  name                   = var.rag_cluster_name
  kubernetes_version_min = "1.31" # Update to the latest available version

  node_pools = [
    {
      name               = "${var.name_prefix}-node"
      machine_type       = "g1.4"
      os_name            = "flatcar"
      minimum            = "1"
      maximum            = "1"
      max_surge          = "1"
      availability_zones = ["${var.region}-1"] # Single availability zone
      volume_size        = 50
      volume_type        = "storage_premium_perf1"
    }
  ]

  maintenance = {
    enable_kubernetes_version_updates    = true
    enable_machine_image_version_updates = true
    start                                = "01:00:00Z"
    end                                  = "02:00:00Z"
  }
}

output "cluster_name" {
  value = stackit_ske_cluster.rag_cluster.name
}
