resource "stackit_dns_zone" "rag_zone" {
  project_id = var.project_id
  name       = "${var.name_prefix}-zone"
  dns_name   =  var.dns_name
}

output "dns_nameservers" {
  value = stackit_dns_zone.rag_zone.id
}

output "dns_name" {
  value = stackit_dns_zone.rag_zone.dns_name
}
