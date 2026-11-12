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
