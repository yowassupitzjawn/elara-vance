# Hardware

What this runs on. Specs only — applications are a later story.

## Server

- Dell Precision 5820 Tower
- Xeon W-2145, 8 cores / 16 threads
- 128 GB DDR4 RAM (4x32GB, 4 of 8 slots free)
- GTX 1060 6GB (Pascal, driver 580 — the last branch that supports it)
- Coral Edge TPU (M.2 PCIe, passed to Frigate)
- Bare-metal Ubuntu 26.04 LTS, Docker + Docker Compose
- Storage: 238 GB root disk, three separate 1.8 TB disks
  (no RAID — each mounted on its own)

## Firewall

- Old Dell OptiPlex, Intel i5-6500 @ 3.20GHz (4 cores), 8 GB RAM
- pfSense 2.9.0-RELEASE, 10GbE on every interface
- Suricata on WAN (IDS mode, watching, not blocking), pfBlockerNG
  (DNSBL + GeoIP + PRI1 feeds), ntopng 6.6 for flow monitoring

## Switch

- 24-port Gb PoE smart switch, fw 2019 — upgrade queued,
  incremental, backup first
- Config database overflow fixed Nov 11 by shortening interface
  descriptions (startup config had hit its size limit)

## Network

- VLANs for servers and cameras — see `docs/network.md`
- Cameras on a VLAN with no gateway — they cannot reach the
  internet, even though the server forwards traffic

## Stack

- Home Assistant, Mosquitto MQTT, Frigate + Coral, Ollama,
  Open WebUI, ComfyUI — all local, all in Docker, all up
