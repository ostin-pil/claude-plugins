#!/usr/bin/env bash
# Probe the local meshctl agent's health endpoint.
set -euo pipefail

endpoint="${MESHCTL_ENDPOINT:-http://127.0.0.1:8080/health}"
if curl -fsS "$endpoint" >/dev/null; then
  echo "ok"
else
  echo "unhealthy" >&2
  exit 1
fi
