variable "project_id" {
  description = "STACKIT Project ID"
  type        = string
}

variable "dns_name" {
  description = "DNS name for the service. Desired free sub‑domain (e.g. ends with .runs.onstackit.cloud)."
  type        = string
  validation {
    condition     = can(regex("^([a-z0-9.-]+)$", var.dns_name))
    error_message = "The DNS name must only contain lowercase letters, numbers, hyphens, and dots."
  }
}

variable "rag_cluster_name" {
  description = "Name of the RAG cluster. Max length: 11 characters."
  type        = string
  validation {
    condition     = can(regex("^([a-z0-9-]+)$", var.rag_cluster_name)) && length(var.rag_cluster_name) <= 11
    error_message = "The RAG cluster name must only contain lowercase letters, numbers, and hyphens, and be max 11 characters long."
  }
}

variable "name_prefix" {
  description = "rag"
  type        = string
  default     = "rag"
}

variable "region" {
  description = "STACKIT region"
  type        = string
  default     = "eu01"
}

variable "deployment_timestamp" {
  description = "Static timestamp for resource naming to avoid recreation on each apply"
  type        = string
  default     = "20260113" # Set this once and don't change unless you want to recreate resources
}

variable "redis_version" {
  description = "Redis service version"
  type        = string
  default     = "7"
}

variable "redis_plan_name" {
  description = "Redis plan name"
  type        = string
  default     = "stackit-redis-1.2.10-replica"
}

variable "secretsmanager_user_description" {
  description = "Description for the Secrets Manager user"
  type        = string
  default     = "RAG secrets manager user"
}

variable "secretsmanager_user_write_enabled" {
  description = "Allow the Secrets Manager user to write secrets"
  type        = bool
  default     = true
}
