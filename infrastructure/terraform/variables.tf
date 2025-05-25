variable "project_id" {
  description = "STACKIT Project ID"
  type        = string
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
