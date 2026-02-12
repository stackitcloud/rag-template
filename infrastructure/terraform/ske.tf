resource "stackit_ske_cluster" "rag_cluster" {
  project_id             = var.project_id
  name                   = var.rag_cluster_name
  kubernetes_version_min = "1.34" # Update to the latest available version

  node_pools = [
    {
      name               = "${var.name_prefix}-node"
      machine_type       = "g2i.8"
      os_name            = "flatcar"
      minimum            = "1"
      maximum            = "1"
      max_surge          = "1"
      availability_zones = ["${var.region}-1"] # Single availability zone
      volume_size        = 64
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


# -------------------------------------------------
# Kubeconfig for the cluster
# -------------------------------------------------
resource "stackit_ske_kubeconfig" "kubeconfig" {
  project_id   = var.project_id
  cluster_name = stackit_ske_cluster.rag_cluster.name

  # 6‑month expiration (seconds)
  expiration = 15552000

  # Refresh only when the config is already expired
  refresh = true
}

output "kubeconfig" {
  description = "Base‑64 encoded kubeconfig"
  value       = stackit_ske_kubeconfig.kubeconfig.kube_config
  sensitive   = true
}

resource "local_file" "kubeconfig_file" {
  filename = "${path.module}/kubeconfig.yaml"
  content  = stackit_ske_kubeconfig.kubeconfig.kube_config
}
