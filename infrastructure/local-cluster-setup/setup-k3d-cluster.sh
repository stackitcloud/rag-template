#!/bin/bash

# Fail fast on errors, unset vars, and propagate pipe failures
set -euo pipefail

CLUSTER_NAME="rag"
K3D_CONFIG_FILE="k3d-cluster-config.yaml"

echo "Creating k3d cluster '${CLUSTER_NAME}' (if it does not already exist)..."
cluster_exists=false
if command -v jq >/dev/null 2>&1; then
    if k3d cluster list -o json 2>/dev/null | jq -e --arg name "$CLUSTER_NAME" 'map(select(.name==$name)) | length > 0' >/dev/null; then
        cluster_exists=true
    fi
else
    # Fallback without jq (less robust)
    if k3d cluster list --no-headers 2>/dev/null | awk '{print $1}' | grep -qx "${CLUSTER_NAME}"; then
        cluster_exists=true
    fi
fi

if [ "${cluster_exists}" = true ]; then
    echo "Cluster '${CLUSTER_NAME}' already exists. Skipping create."
else
    k3d cluster create "${CLUSTER_NAME}" --config "${K3D_CONFIG_FILE}" --k3s-arg "--disable=traefik@server:*"
fi

echo "Waiting for all nodes to become Ready..."
kubectl wait --for=condition=ready node --all --timeout=120s || {
  echo "WARNING: Some nodes did not reach Ready state within timeout." >&2
}

INGRESS_REPO_NAME="ingress-nginx"
INGRESS_REPO_URL="https://kubernetes.github.io/ingress-nginx"
INGRESS_NAMESPACE="ingress-nginx"
INGRESS_RELEASE="ingress-nginx"
INGRESS_CHART="ingress-nginx/ingress-nginx"
INGRESS_CHART_VERSION="${INGRESS_CHART_VERSION:-4.13.3}"
if ! helm repo list | awk '{print $1}' | grep -qx "$INGRESS_REPO_NAME"; then
  echo "Adding Helm repository $INGRESS_REPO_NAME ($INGRESS_REPO_URL)..."
  helm repo add "$INGRESS_REPO_NAME" "$INGRESS_REPO_URL"
else
  echo "Helm repository $INGRESS_REPO_NAME already exists."
fi
echo "Updating Helm repository $INGRESS_REPO_NAME..."
helm repo update "$INGRESS_REPO_NAME"

echo "Installing / upgrading '$INGRESS_RELEASE' chart version ${INGRESS_CHART_VERSION}"
helm upgrade --install "$INGRESS_RELEASE" "$INGRESS_CHART" \
  --namespace "$INGRESS_NAMESPACE" \
  --create-namespace \
  --version "$INGRESS_CHART_VERSION"
echo "Waiting for ingress controller deployment rollout..."
if kubectl rollout status deployment/${INGRESS_RELEASE}-controller -n "$INGRESS_NAMESPACE" --timeout=180s; then
  echo "Ingress controller successfully rolled out."
else
  echo "Rollout not complete. Recent events:" >&2
  kubectl -n "$INGRESS_NAMESPACE" get events --sort-by=.lastTimestamp | tail -n 30 || true
fi

echo "Current ingress-nginx pods:"
kubectl get pods -n "$INGRESS_NAMESPACE" -l app.kubernetes.io/name=ingress-nginx || true



