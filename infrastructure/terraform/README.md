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

## Cleanup

To destroy all resources:

```
terraform destroy
```
