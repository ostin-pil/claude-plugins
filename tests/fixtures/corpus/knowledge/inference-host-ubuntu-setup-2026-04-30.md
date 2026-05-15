# Inference Host on Ubuntu: Dual-Boot Setup Guide

**Date**: 2026-04-30 **Target hardware**: laptop with NVIDIA RTX 5090 Laptop GPU (Blackwell, 24 GB GDDR7), 64 GB system RAM **Goal**: dedicated Linux model host for Untype's Ollama polish stage and RemoteWhisper STT, reachable from the Mac dev box via Tailscale + SSH tunnel

This guide assumes Windows is the existing OS on the laptop and you want to keep it (gaming / Windows-only software). Ubuntu lives alongside in a dual-boot configuration.

---

## Why Ubuntu (not WSL2 / Docker Desktop on Windows)

- CUDA / cuDNN / NVIDIA drivers are first-class on Linux.
- Native container runtime, Podman is the project's preference per the user's `feedback_podman_over_docker.md` memory. No Docker Desktop license/abstraction layer.
- Headless inference host: systemd services, no Windows Update reboots interrupting a long-running serve.
- Tooling we deploy (Ollama, faster-whisper-server, vLLM, llama.cpp) ships Linux-first.

Cost: 1–3 hours of one-off setup vs. ~30 min on Windows + Docker. Worth it if this laptop's primary role is "model server" rather than "daily Windows driver that happens to have a GPU".

---

## Phase 1: Windows-side prep (do before flashing the USB)

1. **Back up** anything irreplaceable. Repartitioning is reversible in theory, hairy in practice.
2. **Suspend BitLocker** on `C:` (Control Panel to BitLocker Drive Encryption to Suspend protection). Otherwise shrinking the volume fails or the recovery key prompt ambushes you on first Windows boot post-install.
3. **Disable Fast Startup**: Control Panel to Power Options to "Choose what the power buttons do" to uncheck "Turn on fast startup". Otherwise Windows leaves NTFS half-mounted between boots and Linux refuses to mount it cleanly.
4. **Shrink C:** in `diskmgmt.msc` (right-click C: to Shrink). Free **300–500 GB unallocated** for Ubuntu, the three Ollama models alone are ~100 GB; container images, OS, headroom add another 100–150 GB. See *Storage budget* at the bottom.
5. **Secure Boot can stay on.** Ubuntu's signed shim handles it. Only disable if MOK enrollment for the NVIDIA driver later gives you trouble (usually visible as the driver loading but `nvidia-smi` reporting no devices).

---

## Phase 2: Ubuntu installer USB

- **Use the latest 24.04 LTS point release.** Conservative pick for a server box. Pair with the HWE kernel + the `graphics-drivers` PPA for a current NVIDIA branch.
- 25.04 has a newer kernel out-of-box but only 9 months of support, not worth it for an inference host.
- **Flash with Rufus** (Windows) in **"DD image" mode**. Default ISO mode sometimes produces a USB that won't boot on Secure Boot systems.
- Boot via your laptop's boot menu (usually F12 or F2). In the installer, choose **"Install Ubuntu alongside Windows"** to auto-partition the unallocated space, or pick **manual partitioning** for finer control (`/` ext4 ≥150 GB, swap ≈ RAM size for hibernation or 8 GB for crash dumps only, share existing EFI partition with Windows).

---

## Phase 3: Post-install: NVIDIA driver for Blackwell

Two things will save you. Blackwell (RTX 50-series) requires:

- **The `-open` driver variant.** The legacy proprietary kernel modules don't support Blackwell. The Ubuntu installer's helper picks the right one, but verify by name.
- **Driver branch ≥ 570 + CUDA ≥ 12.8.** By 2026 the latest -open branch in `graphics-drivers/ppa` (575/580/585) is the right pick.

```bash
# Make sure HWE kernel is in use (24.04 ships it via linux-generic-hwe-24.04)
uname -r                    # should be 6.11+ on a recent point release
sudo apt update
sudo apt install -y software-properties-common
sudo add-apt-repository -y ppa:graphics-drivers/ppa
sudo apt update

# Let Ubuntu pick the recommended driver for your GPU
ubuntu-drivers devices
sudo ubuntu-drivers install --gpgpu

# Or pin a specific branch (replace 580 with whatever's current):
# sudo apt install -y nvidia-driver-580-open

sudo reboot
```

Verify:

```bash
nvidia-smi
# Must show: NVIDIA RTX 5090 Laptop GPU, driver version ≥570, CUDA ≥12.8
```

If `nvidia-smi` says "No devices were found" but the driver is installed: Secure Boot blocked the kernel module. Either reboot and enroll the MOK at next boot, or disable Secure Boot in BIOS as a last resort.

---

## Phase 4: Container runtime: Podman + NVIDIA CDI

Podman matches the project's existing container preference. NVIDIA's container toolkit supports Podman via the **CDI** (Container Device Interface) standard.

```bash
sudo apt install -y podman

# NVIDIA container toolkit
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | \
  sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
  sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
  sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt update
sudo apt install -y nvidia-container-toolkit

# Generate the CDI spec — describes the GPUs to Podman
sudo nvidia-ctk cdi generate --output=/etc/cdi/nvidia.yaml
```

Smoke test:

```bash
podman run --rm --device nvidia.com/gpu=all \
  docker.io/nvidia/cuda:12.8.0-base-ubuntu24.04 nvidia-smi
# Should print the same nvidia-smi output as the host
```

---

## Phase 5: Network: Tailscale + OpenSSH

```bash
# Tailscale — same tailnet as the Mac
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up

# SSH server
sudo apt install -y openssh-server
sudo systemctl enable --now ssh
# (Optional) generate keys on the Mac and ssh-copy-id user@<host>.tailXXXX.ts.net
```

From the Mac, verify reachability:

```bash
tailscale status                              # Ubuntu node visible
ssh <user>@<ubuntu-host>.tailXXXX.ts.net echo ok
```

---

## Phase 6: Ollama

```bash
curl -fsSL https://ollama.com/install.sh | sh

# Make Ollama listen on all interfaces (Tailscale IP, not just localhost).
# Done via a systemd drop-in so the override survives upgrades.
sudo mkdir -p /etc/systemd/system/ollama.service.d
sudo tee /etc/systemd/system/ollama.service.d/override.conf <<'EOF'
[Service]
Environment="OLLAMA_HOST=0.0.0.0:11434"
EOF
sudo systemctl daemon-reload
sudo systemctl restart ollama

# Pull the three models the registry seeds
ollama pull gemma3:27b
ollama pull llama3.3:70b
ollama pull qwen2.5:72b
ollama list
```

Smoke test from the Mac:

```bash
curl -s http://<ubuntu-host>:11434/v1/models | jq '.data[].id'
```

> **Untype gotcha**: `CloudProviderConfig.ollama()` hardcodes
> `http://localhost:11434/v1`. From the Mac you still need an SSH
> tunnel `ssh -N -L 11434:localhost:11434 <ubuntu-host>` so Untype
> sees the server on its expected localhost. (RemoteWhisper, by
> contrast, has a configurable URL, no tunnel needed.)
>
> Follow-up worth filing: lift the localhost hardcode into an
> `@AppStorage` baseURL like `RemoteWhisperSTTDescriptor`. Removes the
> tunnel requirement entirely.

### Sizing reality on a 24 GB GPU

| Model | Q4_K_M size | Fits VRAM? | Speed |
|---|---|---|---|
| `gemma3:27b` | ~17 GB | yes | fast (25–40 tok/s) |
| `llama3.3:70b` | ~42 GB | no, partial CPU offload to 64 GB RAM | slow (5–10 tok/s) |
| `qwen2.5:72b` | ~43 GB | no, partial CPU offload | slow (5–10 tok/s) |

For interactive polish the 27b model is the right default. Keep the 70b/72b around for batch / quality comparison; treat their slow speed as expected, not as a regression.

---

## Phase 7, faster-whisper-server (Podman quadlet)

Podman quadlets are systemd-native unit files for containers. Cleaner than a `podman run` command in `crontab` or a hand-rolled service file.

```bash
sudo mkdir -p /etc/containers/systemd
sudo tee /etc/containers/systemd/fws.container <<'EOF'
[Unit]
Description=faster-whisper-server (CUDA)
After=network-online.target
Wants=network-online.target

[Container]
Image=docker.io/fedirz/faster-whisper-server:latest-cuda
ContainerName=fws
PublishPort=8080:8000
AddDevice=nvidia.com/gpu=all
Environment=WHISPER__MODEL=large-v3

[Service]
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl start fws
sudo systemctl enable fws
journalctl -u fws -f       # confirm "Uvicorn running on http://0.0.0.0:8000"
```

Smoke test:

```bash
# From Ubuntu host
curl http://localhost:8080/v1/models | jq '.data[].id'

# From the Mac (Untype setting will use this URL directly)
curl http://<ubuntu-host>.tailXXXX.ts.net:8080/v1/models | jq '.data[].id'
```

---

## Phase 8: Mac side wiring

Set the Untype RemoteWhisper URL to point at the Tailscale name directly (Settings to Transcription Engine to Remote Whisper):

- **Server URL**: `http://<ubuntu-host>.tailXXXX.ts.net:8080`
- **Model**: `large-v3`

For Ollama, open the SSH tunnel:

```bash
# In a long-running terminal (or wrap in launchd / autossh later)
ssh -N -L 11434:localhost:11434 <user>@<ubuntu-host>.tailXXXX.ts.net
```

Sanity:

```bash
curl -s localhost:11434/v1/models | jq '.data[].id'   # three models
```

Verification of the end-to-end Untype paths against this host: see `knowledge/branches-sor-verification-runbook-2026-04-30.md`.

---

## Storage budget (300–500 GB recommended for Ubuntu)

| Component | Approximate size |
|---|---|
| Ubuntu base + apps | 30 GB |
| `gemma3:27b` | 17 GB |
| `llama3.3:70b` | 42 GB |
| `qwen2.5:72b` | 43 GB |
| Whisper `large-v3` (faster-whisper) | 5 GB |
| Container images + layers | 15 GB |
| User home + buffer | 50–100 GB |
| **Total comfortable** | **300 GB** |
| **With headroom for more models** | **500 GB** |

---

## Known gotchas

- **Wayland vs X11.** Recent NVIDIA drivers handle Wayland fine for desktop sessions, but if you hit weirdness (cursor lag, screen recording issues), log out and pick "Ubuntu on Xorg" at the login screen. Doesn't affect headless inference.
- **Suspend/resume on laptop dGPUs.** Some laptops drop the dGPU on suspend; CUDA contexts die and Ollama needs a restart. Either set the laptop to never sleep when on AC, or run `systemctl restart ollama fws` from a wake hook. Lower priority, verify whether your specific laptop is affected.
- **Hybrid graphics (iGPU + dGPU).** PRIME render offload is the default. CUDA workloads always target the dGPU; no manual selection needed.
- **`ollama serve` race during boot.** If `fws` and `ollama` both start before the NVIDIA module is fully up, one may fail. The `After=network-online.target` in the quadlet is usually enough; if not, add `ExecStartPre=/bin/sleep 5`.
- **MOK enrollment with Secure Boot.** First boot after installing the NVIDIA driver pauses for MOK enrollment. Easy to miss; if you miss it, run `sudo mokutil --import /var/lib/shim-signed/mok/MOK.der` and reboot.
