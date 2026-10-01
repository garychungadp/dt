#!/usr/bin/env bash
# AKS 專用 Health Check；一般 VM 使用 health-check-vm.sh。
set -euo pipefail

# AKS Cluster 與 Namespace 由 GitHub Environment Variables 提供。
: "${AKS_CLUSTER_NAME:?請在 GitHub Environment Variables 設定 AKS_CLUSTER_NAME}"
: "${AKS_NAMESPACE:?請在 GitHub Environment Variables 設定 AKS_NAMESPACE}"

# 確認 AKS Deployment 已完成滾動更新。
kubectl rollout status deployment/dt-api -n "$AKS_NAMESPACE" --timeout=180s
# 顯示 Deployment 狀態，方便在 Actions Log 中追蹤。
kubectl get deployment dt-api -n "$AKS_NAMESPACE"

# 輸出檢查成功的環境與 AKS 資訊。
echo "AKS Health Check 通過：環境=$1，Cluster=${AKS_CLUSTER_NAME}，Namespace=${AKS_NAMESPACE}，Deployment=dt-api"
