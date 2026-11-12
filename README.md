# Elara Vance Project

A local AI that watches my home network and cameras, figures out
what's normal, and warns me when something isn't — all running on a
server in my own house. Nothing leaves the LAN.

No cloud security service. No monthly fee. No footage or traffic
leaving my home.

## What this repo is

Breadcrumbs, not the whole blueprint. This repo documents what I've
built so far, in order, with dates — so the work is on the record
and others can follow along and build their own version.

The complete architecture stays private. What's here is what has
already been built and tested.

## What's in here

- `poller/` — the network watchdog: polls ntopng, applies rules,
  sends suspicious events to a local LLM for triage. Log-only.
- `docs/hardware.md` — the hardware this runs on.
- `docs/models.md` — which local models do what, and the measured
  head-to-head that decided it.
- `CHANGELOG.md` — the build diary, one line at a time.

## What's NOT in here

- No tokens, keys, passwords, or credentials of any kind.
- No public IPs, no VPN addresses, no MAC addresses, no camera feeds.
- No full network map. Internal addresses in code are placeholders
  you fill in for your own network.
- No next steps. This repo shows what has been done, not what is
  coming next.

## The idea, in one paragraph

A router watches the network. A small poller asks it every minute
what's active, checks the answer against a baseline of what's
normal, and only sends the suspicious bits to a local AI. The AI
explains it in plain language and gives it a severity. A home
automation system turns the serious ones into a phone notification.
Rules first, AI second, notify-only — no automatic blocking.

## Status

Log-only baseline phase. The poller watches and learns what's
normal. Alerts are not wired to a phone yet.

## License

MIT — see `LICENSE`. Use it, fork it, build your own.
