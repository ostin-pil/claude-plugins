#!/usr/bin/env bash
# Deploy the meshctl control-plane config and restart its launch agent.
set -euo pipefail

CONFIG="${1:-config/meshctl.yaml}"
[ -f "$CONFIG" ] || { echo "config not found: $CONFIG" >&2; exit 1; }

echo "deploying meshctl with $CONFIG"
install -m 0644 "$CONFIG" "$HOME/Library/Application Support/meshctl/meshctl.yaml"
launchctl kickstart -k "gui/$(id -u)/com.meshctl.agent"
echo "done"
