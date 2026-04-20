resource "stackit_redis_instance" "rag_redis" {
  project_id = var.project_id
  name       = "${var.name_prefix}-redis"
  version    = var.redis_version
  plan_name  = var.redis_plan_name

  parameters = {
    sgw_acl                 = join(",", stackit_ske_cluster.rag_cluster.egress_address_ranges)
    enable_monitoring       = false
    down_after_milliseconds = 30000
  }
}


resource "stackit_redis_credential" "rag_redis_cred" {
  project_id  = var.project_id
  instance_id = stackit_redis_instance.rag_redis.instance_id
}

output "redis_host" {
  value = stackit_redis_credential.rag_redis_cred.host
}

output "redis_load_balanced_host" {
  value = stackit_redis_credential.rag_redis_cred.load_balanced_host
}

output "redis_port" {
  value = stackit_redis_credential.rag_redis_cred.port
}

output "redis_username" {
  value = stackit_redis_credential.rag_redis_cred.username
}

output "redis_password" {
  value     = stackit_redis_credential.rag_redis_cred.password
  sensitive = true
}

output "redis_uri" {
  value     = stackit_redis_credential.rag_redis_cred.uri
  sensitive = true
}
