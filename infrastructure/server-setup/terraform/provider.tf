terraform {
  required_providers {
    stackit = {
      source = "stackitcloud/stackit"
      version = "0.9.1"
    }
    openstack = {
      source  = "terraform-provider-openstack/openstack"
      version = "~> 1.51.1"
    }
  }
}

provider "stackit" {
  region = "eu01"
  service_account_token = var.service_account_token
}

# l40s
provider "openstack" {
  tenant_id         = "527ac64079e948ef82141fa94272458b"
  tenant_name       = "ai_playground_k8MmrBAP"
  user_domain_name  = "portal_mvp"
  user_name         = "portal-uat-os-fn94LSKd"
  password          = var.os_password
  auth_url          = "https://keystone.api.iaas.eu01.stackit.cloud/v3"
  region            = "RegionOne"
  project_domain_id = "default"
  use_octavia       = true
}
