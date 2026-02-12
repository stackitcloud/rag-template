terraform {
  backend "s3" {}
  required_providers {
    stackit = {
      source  = "stackitcloud/stackit"
      version = "~> 0.79.0"
    }
  }
}

provider "stackit" {
  service_account_key_path = "sa_key.json"
  default_region           = "eu01"
}
