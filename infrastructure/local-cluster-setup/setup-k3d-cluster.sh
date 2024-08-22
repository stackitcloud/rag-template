#!/bin/bash
k3d cluster create rag --config k3d-cluster-config.yaml --k3s-arg "--disable=traefik@server:*"

kubectl wait --for=condition=ready node --all --timeout=120s

REPO_NAME="bitnami"
# Add the Helm repository if it doesn't exist
if ! helm repo list | grep -q "$REPO_NAME"; then
  echo "Adding Helm repository $REPO_NAME..."
  helm repo add $REPO_NAME https://charts.bitnami.com/bitnami
  helm repo update
else
  echo "Helm repository $REPO_NAME already exists."
fi

helm install nginx-ingress-controller bitnami/nginx-ingress-controller --namespace nginx-ingress --version "10.3.0" --create-namespace

