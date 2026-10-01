#!/usr/bin/env bash
set -euo pipefail

environment="$1"
image="$2"

: "${VM_HOST:?Set VM_HOST in the GitHub Environment Variables}"
: "${VM_USER:?Set VM_USER in the GitHub Environment Variables}"
: "${VM_DEPLOY_PATH:?Set VM_DEPLOY_PATH in the GitHub Environment Variables}"
: "${VM_SSH_PRIVATE_KEY:-}"
: "${VM_SSH_PASSWORD:-}"
if [[ -z "$VM_SSH_PRIVATE_KEY" && -z "$VM_SSH_PASSWORD" ]]; then
  echo "Set either VM_SSH_PRIVATE_KEY or VM_SSH_PASSWORD in the GitHub Environment Secrets" >&2
  exit 1
fi

ssh_options=(-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null)
if [[ -n "$VM_SSH_PRIVATE_KEY" ]]; then
  key_file="$(mktemp)"
  trap 'rm -f "$key_file"' EXIT
  printf '%s\n' "$VM_SSH_PRIVATE_KEY" > "$key_file"
  chmod 600 "$key_file"
  ssh_options+=(-i "$key_file" -o IdentitiesOnly=yes)
  ssh_command=(ssh "${ssh_options[@]}")
  scp_command=(scp "${ssh_options[@]}")
else
  if ! command -v sshpass >/dev/null 2>&1; then
    sudo apt-get update
    sudo apt-get install --yes sshpass
  fi
  ssh_command=(sshpass -e ssh "${ssh_options[@]}" -o PreferredAuthentications=password -o PubkeyAuthentication=no)
  scp_command=(sshpass -e scp "${ssh_options[@]}" -o PreferredAuthentications=password -o PubkeyAuthentication=no)
fi

# 1. 確保遠端目標目錄存在
"${ssh_command[@]}" "${VM_USER}@${VM_HOST}" "mkdir -p '$VM_DEPLOY_PATH'"

# 2. 將專案中的 docker-compose.yml 同步到遠端 VM
"${scp_command[@]}" docker-compose.yml "${VM_USER}@${VM_HOST}:${VM_DEPLOY_PATH}/docker-compose.yml"

# 3. 執行 Docker Compose 更新服務
"${ssh_command[@]}" "${VM_USER}@${VM_HOST}" \
  "cd '$VM_DEPLOY_PATH' && export IMAGE='$image' && docker compose pull && docker compose up -d --remove-orphans"

echo "VM deployment completed for ${environment}: ${image}"
