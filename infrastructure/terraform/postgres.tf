resource "stackit_postgresflex_instance" "rag_db" {
  project_id = var.project_id
  name       = "${var.name_prefix}-db"

  # Allow access only from the SKE cluster
  acl = stackit_ske_cluster.rag_cluster.egress_address_ranges

  replicas        = 3
  version         = 17                   # PostgreSQL version
  flavor          = { cpu = 2, ram = 4 } # 2 vCPUs, 4GB RAM
  storage         = { class = "premium-perf6-stackit", size = 10 }
  backup_schedule = "00 00 * * *" # Daily backup at midnight
}

resource "stackit_postgresflex_user" "rag_db_user" {
  project_id  = var.project_id
  instance_id = stackit_postgresflex_instance.rag_db.instance_id
  username    = "raguser"
  roles       = ["login", "createdb"]
}

resource "stackit_postgresflex_database" "rag_langfuse_db" {
  project_id  = var.project_id
  instance_id = stackit_postgresflex_instance.rag_db.instance_id
  name        = "langfuse"
  owner       = stackit_postgresflex_user.rag_db_user.username
}

output "postgres_host" {
  value = stackit_postgresflex_user.rag_db_user.host
}

output "postgres_port" {
  value = stackit_postgresflex_user.rag_db_user.port
}

output "postgres_username" {
  value = stackit_postgresflex_user.rag_db_user.username
}

output "postgres_password" {
  value     = stackit_postgresflex_user.rag_db_user.password
  sensitive = true
}

output "postgres_database" {
  value = stackit_postgresflex_database.rag_langfuse_db.name
}
