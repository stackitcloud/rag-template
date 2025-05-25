resource "stackit_dns_zone" "rag_zone" {
  project_id = var.project_id
  name       = "${var.name_prefix}-zone"
  dns_name   = "university-rag.stackit.gg" # Replace with your desired domain
}

output "dns_nameservers" {
  value = stackit_dns_zone.rag_zone.id
}

output "dns_name" {
  value = stackit_dns_zone.rag_zone.dns_name
}
