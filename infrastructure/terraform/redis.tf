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
