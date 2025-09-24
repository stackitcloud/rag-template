terraform {
  required_providers {
    stackit = {
      source  = "stackitcloud/stackit"
<<<<<<< HEAD
      version = "~> 0.58.0"
=======
      version = "~> 0.61.0"
>>>>>>> main
    }
  }
}

provider "stackit" {
  service_account_key_path = "sa_key.json"
}
