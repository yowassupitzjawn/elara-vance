# Hardware

What this runs on. Specs only — applications are a later story.

## Server

- Dell Precision 5820 Tower
- Xeon W-2145, 8 cores / 16 threads
- 123 GB DDR4 RAM
- GTX 1060 6GB (Pascal, driver 580 — the last branch that supports it)
- Coral Edge TPU (M.2 PCIe, passed to Frigate)
- Bare-metal Ubuntu 26.04 LTS, Docker + Docker Compose
- Storage: 238 GB root disk, three separate 1.8 TB disks
  (no RAID — each mounted on its own)

## Network

- pfSense firewall, VLANs for servers and cameras
- Cameras on a VLAN with no gateway — they cannot reach the
  internet, even though the server forwards traffic
- ntopng 6.6 on pfSense for flow monitoring

## Stack

- Home Assistant, Mosquitto MQTT, Frigate + Coral, Ollama,
  Open WebUI, ComfyUI — all local, all in Docker, all up
