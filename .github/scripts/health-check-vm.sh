#!/usr/bin/env bash
set -euo pipefail

environment="$1"

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
else
  if ! command -v sshpass >/dev/null 2>&1; then
    sudo apt-get update
    sudo apt-get install --yes sshpass
  fi
  ssh_command=(sshpass -e ssh "${ssh_options[@]}" -o PreferredAuthentications=password -o PubkeyAuthentication=no)
fi

if [[ -n "${VM_HEALTHCHECK_URL:-}" ]]; then
  "${ssh_command[@]}" "${VM_USER}@${VM_HOST}" \
    "curl --fail --silent --show-error --max-time 30 '$VM_HEALTHCHECK_URL' >/dev/null"
else
  "${ssh_command[@]}" "${VM_USER}@${VM_HOST}" \
    "cd '$VM_DEPLOY_PATH' && test -n \"\$(docker compose ps --status running --services)\""
fi

echo "VM health check passed for ${environment}"
