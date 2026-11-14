# Changelog

Breadcrumbs. One line per step, in the order it happened.

## 2026-11-10

- Home lab audit: bare-metal Ubuntu, Docker stack verified live
  (Home Assistant, MQTT, Frigate + Coral, Ollama, Open WebUI).

## 2026-11-11

- ComfyUI working on CPU (v0.44.2), verified over the local network.
- GPU vs CPU benchmark: 7B chat model generates at ~12.2 tok/s on
  both the GTX 1060 and the CPU — the old card buys nothing for
  that model.
- Pulled a 32B local model for security triage.
- Head-to-head, 4 scenarios: 32B 4/4 correct, 7B undercalled every
  real threat and false-positived on a routine update. 32B is the
  triage brain; 7B stays as the chat model.
- Security poller v1 installed, log-only: polls ntopng every 60s,
  7-day rolling retention, triage via the 32B, max 1 flag per run.
- pfSense hardware verified: old Dell OptiPlex, i5-6500, 8 GB RAM,
  pfSense 2.9.0, Suricata + pfBlockerNG + ntopng on the edge.
- Switch identified: 24-port Gb PoE smart switch, fw 2019.
  Config database overflow fixed by shortening interface
  descriptions. Firmware upgrade queued.
- Network documented: VLAN00 WiFi, VLAN20 office/servers,
  VLAN30 cameras (airgapped, no cameras mounted yet — one bench
  test only). Server RAM confirmed 4x32GB, 4 slots free.

## 2026-11-13

- Home Assistant chat fixed: the Ollama agent asked the 7B chat
  model to think, and it doesn't support thinking (400). Thinking
  off, chat works.
- Image model picked: Pony Diffusion V6 XL. Models moved to the
  storage disks (13 GB), Pony downloaded, SHA256-verified.
- GPU back: after the system upgrade, the driver existed only for
  the old kernel, so Ollama couldn't see the card at all. Driver
  reinstalled for the current kernel; chat model now fully on GPU
  (prompt eval ~68 to ~393 tok/s). 32B still mostly CPU-bound.
- ComfyUI mount-path bug found and fixed: compose pointed the
  models at /root/comfy/ComfyUI, but ComfyUI lives at /root/ComfyUI.
  The model list was empty since day one. Paths corrected, all three
  checkpoints selectable.
- Pretty URLs live: Nginx Proxy Manager + local DNS overrides, six
  names (chat, images, home, cameras, net, firewall). Fixed DHCP
  handing out public DNS instead of the firewall, and a self-signed
  wildcard cert so the Secure-cookie logins stick. All six hosts
  HTTPS.
