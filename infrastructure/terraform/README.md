# RAG Infrastructure - Terraform Setup

This guide explains how to deploy RAG (Retrieval Augmented Generation) infrastructure on STACKIT using Terraform.

## Overview

This Terraform configuration deploys:
- A single-node SKE (STACKIT Kubernetes Engine) cluster
- PostgreSQL Flex database for Langfuse
- Object storage bucket for documents
- DNS zone configuration

## Prerequisites

- [Terraform](https://www.terraform.io/downloads.html) (v1.0.0+)
- STACKIT account with service account credentials
- Service account JSON key file

## Setup Instructions

1. **Prepare credentials**
   ```
   # Save your STACKIT service account key to sa_key.json
   cp /path/to/your/credentials.json ./sa_key.json
   ```

:::info
### Using STACKIT CLI

```bash
# Login to STACKIT CLI
stackit auth login

# List your projects
stackit project list

# Select your project
stackit config set --project-id YOUR_PROJECT_ID

# Create a service account for Terraform
stackit service-account create --name terraform-rag

# Create a key for the service account
stackit service-account key create --email terraform-rag-XXXX@sa.stackit.cloud > sa_key.json

# Assign necessary permissions
stackit project member add terraform-rag-XXXX@sa.stackit.cloud --role editor
```

Important: The sa_key.json file contains sensitive credentials. Never commit it to version control. Consider using a secure method to store and access this file, especially in team environments.
:::

2. **Review and customize variables**
   ```
   # Edit terraform.tfvars with your project ID and other preferences
   vim terraform.tfvars
   ```

3. **Initialize Terraform**
   ```
   terraform init
   ```

4. **Plan the deployment**
   ```
   terraform plan -out=rag.tfplan
   ```

5. **Apply the configuration**
   ```
   terraform apply rag.tfplan
   ```

## Single-Node SKE Configuration

The SKE cluster is configured with a single node setup which is suitable for development and testing:

- Uses a g1.4 machine type (4 vCPUs)
- 50GB premium storage volume
- No auto-scaling (fixed at 1 node)
- Deployed in a single availability zone

To connect to your cluster after deployment:
```
terraform output -json | jq -r .cluster_name.value
# Use this name to get the kubeconfig from STACKIT console or CLI
```

## Important Notes

- **Production Readiness**: The single-node setup is NOT recommended for production use as it lacks high availability and fault tolerance
- **Security**: The sa_key.json file contains sensitive credentials and should never be committed to version control
- **State Management**: Consider using remote state storage for team environments

## Using the bucket as a Terraform S3 backend (optional)

If you want Terraform state to be stored in the object storage bucket, add a backend block to your root module.
Note: backend blocks cannot reference resources, so you must hardcode or pass the values via variables/partials.

### Bootstrap script (recommended)

Note: `backend "s3" {}` is already defined in `main.tf`. The bootstrap step still works because it runs `terraform init -backend=false`, which ignores the backend block.

Use the helper script to bootstrap the backend in two phases:
1) Run a local-only apply to create the bucket + credentials.
2) Generate `.backend.hcl` and migrate state to S3.

```bash
./scripts/init-backend.sh
```

This writes `infrastructure/terraform/.backend.hcl` (contains credentials) and runs `terraform init -force-copy`.
You can re-run the script at any time; it reuses the existing backend config if present.
If you want remote state from the start, run this script before your first full `terraform apply`.

If you want non-interactive bootstrap:

```bash
BOOTSTRAP_AUTO_APPROVE=1 ./scripts/init-backend.sh
```

Manual phase 1 (if you want to see the exact commands the script runs):

```bash
terraform init -backend=false
terraform apply \
  -target=stackit_objectstorage_bucket.tfstate \
  -target=stackit_objectstorage_credentials_group.rag_creds_group \
  -target=stackit_objectstorage_credential.rag_creds
```

### Manual backend block

```hcl
terraform {
  backend "s3" {
    bucket = "<BUCKET_NAME>"
    key    = "terraform.tfstate"
    region = "eu01"

    # Use the same credentials as above
    access_key = "<ACCESS_KEY>"
    secret_key = "<SECRET_KEY>"

    endpoints = {
      s3 = "https://object.storage.eu01.onstackit.cloud"
    }

    # AWS-specific checks must be disabled for STACKIT
    skip_credentials_validation = true
    skip_region_validation      = true
    skip_s3_checksum            = true
    skip_requesting_account_id  = true
  }
}
```

## Cleanup

To destroy all resources:

```
terraform destroy
```
