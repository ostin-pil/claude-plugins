# meshctl

Operational tooling for a self-hosted mesh control plane. Plain shell scripts, a
YAML config, and a launchd agent; there is nothing to compile. Deploy and operate
with the scripts under `scripts/`.

## Layout

- `scripts/` deploy, health-check, and backup scripts (bash)
- `config/meshctl.yaml` the control-plane config
- `launchd/com.meshctl.agent.plist` the macOS launch agent

## Operate

```
scripts/deploy.sh config/meshctl.yaml
scripts/healthcheck.sh
```
