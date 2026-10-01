#!/usr/bin/env bash
set -euo pipefail
environment="$1"
image="$2"
: "${AZURE_RESOURCE_GROUP:?Set AZURE_RESOURCE_GROUP in the GitHub Environment}"
: "${AKS_CLUSTER_NAME:?Set AKS_CLUSTER_NAME in the GitHub Environment}"
: "${AKS_NAMESPACE:?Set AKS_NAMESPACE in the GitHub Environment}"

az aks get-credentials --resource-group "$AZURE_RESOURCE_GROUP" --name "$AKS_CLUSTER_NAME" --overwrite-existing
kubectl create namespace "$AKS_NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -
sed "s|IMAGE_PLACEHOLDER|${image}|g" k8s/deployment.yml | kubectl apply -n "$AKS_NAMESPACE" -f -
kubectl rollout status deployment/dt-api -n "$AKS_NAMESPACE" --timeout=180s
echo "AKS deployment completed for ${environment}: ${image}"
