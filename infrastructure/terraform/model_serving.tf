resource "stackit_modelserving_token" "rag_modelserving" {
  project_id = var.project_id
  name       = "${var.name_prefix}-modelserving-token"

  # No ttl_duration set -> token does not expire.
}

output "model_serving_bearer_token" {
  description = "Bearer token for AI Model Serving API"
  value       = stackit_modelserving_token.rag_modelserving.token
  sensitive   = true
}
