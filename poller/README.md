# Security poller

Polls ntopng on the firewall every 60 seconds, applies deterministic
rules first, and sends only flagged events to a local LLM for triage.

**Log-only.** It writes to a local SQLite database and a log file.
It sends no alerts, blocks nothing, and talks to nothing outside
the local network.

## How it works

1. Poll active hosts and flows from ntopng (all interfaces).
2. Rules, in memory: new local host, blacklisted host, ntopng alert,
   flow to an external IP on a sensitive port (22/3389/4444/8080).
3. At most one flagged event per run goes to the local LLM
   (32B model, temperature 0, JSON verdict: severity 1-5, verdict,
   action, reason). The verdict is logged, nothing else happens.
4. Snapshots, flags, and triage verdicts are purged after 7 days,
   rolling. Only baseline aggregates survive that.

## Install

```bash
mkdir -p ~/elara-poller
cp poller.py ~/elara-poller/
# Put your ntopng API token in ~/elara-poller/.ntopng-token
# (mode 0600, owned by the user running the poller).
# The token is NEVER in this repo and NEVER in the code.
chmod 600 ~/elara-poller/.ntopng-token
```

Cron, every minute (with a lock so runs can't overlap):

```
* * * * * /usr/bin/flock -n ~/elara-poller/poller.lock \
  /usr/bin/python3 ~/elara-poller/poller.py \
  >> ~/elara-poller/poller.log 2>&1
```

## Configuration

Edit the constants at the top of `poller.py` for your network:

- `NTOPNG` — your ntopng base URL, e.g. `https://<firewall>:3000`
- `OLLAMA` — your Ollama API URL, e.g. `http://127.0.0.1:11434/api/generate`
- `IFIDS` — your ntopng interface IDs
- `TRIAGE_MODEL` — your local triage model

Python 3, standard library only. No dependencies to install.
