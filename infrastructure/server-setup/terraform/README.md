
# Terraform

## Source

Infrastructure as Code (IaC) solution from Hashicorp to provision our Azure infrastructure

## Getting started

```BASH
cd terraform

terraform init

terraform plan

terraform apply
```


## CLI

```BASH
terraform version
terraform fmt
terraform plan
terraform apply --auto-approve
terraform state list
terraform state show RESOURCE
terraform show
terraform plan -destroy
terraform validate
terraform apply -replace RESOURCENAME   # Ersetzen und neu aufsetzen
terraform apply -refresh-only
terraform output
terraform console
terraform destroy -target RESOURCENAME

```



