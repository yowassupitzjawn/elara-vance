# Models

Two local models, two jobs. Both run offline via Ollama.

## Chat model — 7B

- Qwen2.5 7B, Q4, ~4.7 GB
- The household chat model
- Measured: ~12.2 tok/s generation, on the GTX 1060 *and* on the
  CPU — the old card buys nothing for a 7B on this box

## Triage model — 32B

- Qwen2.5 32B, Q4, ~19 GB
- The security analyst: reads flagged network events and gives a
  severity, a verdict, and an action
- Measured: ~2.9 tok/s on CPU/RAM, ~50 seconds per triage

## Head-to-head (4 scenarios, temp 0, JSON verdict)

| Scenario | 7B | 32B |
|---|---|---|
| Intruder, unknown host, port 4444, 812 MB up at 2am | Sev 4, suspicious | Sev 5, intruder, isolate |
| Benign, phone, routine update CDN | Sev 3, suspicious (false positive) | Sev 1, benign |
| Port scan, 214 attempts, 38 hosts | Sev 3, monitor | Sev 4, investigate and isolate |
| Camera uploading to the internet | Sev 3, investigate config | Sev 4, investigate and isolate |

Score: 32B 4/4 correct. 7B undercalled every real threat and
cried wolf on a routine update.

Conclusion: the 7B stays as the chat model. The 32B is the
triage brain. 50 seconds is fine for an alert — this isn't
inline packet blocking, it's a warning within a minute.
