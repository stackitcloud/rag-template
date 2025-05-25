terraform {
  required_providers {
    stackit = {
      source  = "stackitcloud/stackit"
      version = "~> 0.50.0"
    }
  }
}

provider "stackit" {
  service_account_key_path = "sa_key.json"
}
