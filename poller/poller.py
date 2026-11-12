#!/usr/bin/env python3
"""Elara security poller — LOG-ONLY, no alerts, no blocking.

Polls ntopng every 60s (via cron), applies deterministic rules first,
and sends at most one flagged event per run to a local LLM for triage.
Retention: 7 days rolling, auto-purge. Aggregates only after that.

Token: NTOPNG_TOKEN env, or a .ntopng-token file (0600) next to this
script. Never hardcoded. Never logged. Never committed.

Configure NTOPNG / OLLAMA / IFIDS / TRIAGE_MODEL below for your network.
"""
import json, os, sqlite3, ssl, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "poller.db")
LOG = os.path.join(HERE, "poller.log")

# --- Edit these for your network ---
NTOPNG = "https://<FIREWALL_HOST>:3000"
OLLAMA = "http://127.0.0.1:11434/api/generate"
TRIAGE_MODEL = "qwen2.5:32b"
IFIDS = [0, 1, 2]
# ----------------------------------

RETENTION_DAYS = 7
SUSPICIOUS_PORTS = {22, 3389, 4444, 8080, 5900}
LOCAL_PREFIXES = ("10.", "192.168.", "172.16.", "172.17.", "172.18.",
                  "172.19.", "172.2", "172.30.", "172.31.", "127.")


def log(msg):
    line = f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}"
    print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def token():
    t = os.environ.get("NTOPNG_TOKEN", "").strip()
    if t:
        return t
    with open(os.path.join(HERE, ".ntopng-token"), "r", encoding="utf-8") as f:
        return f.read().strip()


def ntop_get(path):
    req = urllib.request.Request(NTOPNG + path,
                                 headers={"Authorization": "Token " + token()})
    ctx = ssl._create_unverified_context()  # firewall self-signed cert; LAN-only
    with urllib.request.urlopen(req, timeout=15, context=ctx) as r:
        return json.load(r)


def paged(endpoint, ifid):
    out, seen, page = [], set(), 1
    while page <= 10:
        d = ntop_get(f"/lua/rest/v2/get/{endpoint}?ifid={ifid}"
                     f"&perPage=100&currentPage={page}")
        rows = d.get("rsp", {}).get("data", [])
        new = 0
        for row in rows:
            key = json.dumps(row, sort_keys=True)
            if key not in seen:
                seen.add(key); out.append(row); new += 1
        if len(rows) < 100 or new == 0:
            break
        page += 1
    return out


def is_local(ip):
    return str(ip).startswith(LOCAL_PREFIXES)


def triage(flag):
    system = ("You are a SOC analyst for a home network. Answer only from "
              "the data given. Output JSON only: {\"severity\": 1-5, "
              "\"verdict\": \"intruder|benign|suspicious\", \"action\": \"...\", "
              "\"reason\": \"one sentence\"}.")
    body = json.dumps({"model": TRIAGE_MODEL, "prompt": flag, "system": system,
                       "stream": False,
                       "options": {"temperature": 0, "num_predict": 200}}).encode()
    t0 = time.time()
    req = urllib.request.Request(OLLAMA, data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as r:
        d = json.load(r)
    secs = round(time.time() - t0, 1)
    ec, ed = d.get("eval_count", 0), d.get("eval_duration", 0) / 1e9
    return d.get("response", "").strip()[:800], secs, round(ec / ed, 2) if ed else None


def main():
    db = sqlite3.connect(DB)
    db.execute("""CREATE TABLE IF NOT EXISTS snapshots (
        ts INTEGER, ifid INTEGER, host TEXT, name TEXT, bps REAL, pps REAL,
        num_flows INTEGER, num_alerts INTEGER, is_blacklisted INTEGER)""")
    db.execute("""CREATE TABLE IF NOT EXISTS flags (
        ts INTEGER, ifid INTEGER, host TEXT, kind TEXT, detail TEXT)""")
    db.execute("""CREATE TABLE IF NOT EXISTS triage (
        ts INTEGER, host TEXT, kind TEXT, model TEXT, secs REAL,
        tok_s REAL, verdict TEXT)""")
    db.execute("""CREATE TABLE IF NOT EXISTS known_hosts (
        host TEXT PRIMARY KEY, first_seen INTEGER, last_seen INTEGER)""")
    now = int(time.time())
    flags = []
    for ifid in IFIDS:
        try:
            hosts = paged("host/active.lua", ifid)
            flows = paged("flow/active.lua", ifid)
        except Exception as e:
            log(f"ifid={ifid} poll failed: {e}")
            continue
        log(f"ifid={ifid} hosts={len(hosts)} flows={len(flows)}")
        for h in hosts:
            ip = h.get("ip") or h.get("name") or "?"
            name = h.get("name") or ""
            thpt = h.get("thpt") or {}
            db.execute("INSERT INTO snapshots VALUES (?,?,?,?,?,?,?,?,?)",
                       (now, ifid, str(ip), str(name),
                        float(thpt.get("bps") or 0),
                        float(thpt.get("pps") or 0),
                        int(h.get("num_flows") or 0)
                        if not isinstance(h.get("num_flows"), dict) else 0,
                        int(h.get("num_alerts") or 0),
                        1 if h.get("is_blacklisted") else 0))
            first = h.get("first_seen") or 0
            row = db.execute("SELECT 1 FROM known_hosts WHERE host=?",
                             (str(ip),)).fetchone()
            if not row:
                db.execute("INSERT INTO known_hosts VALUES (?,?,?)",
                           (str(ip), int(first or now), now))
                if first and now - int(first) < 600 and is_local(ip):
                    flags.append((ifid, str(ip), "NEW-HOST",
                                  f"first_seen {int(first)}, name={name}"))
            else:
                db.execute("UPDATE known_hosts SET last_seen=? WHERE host=?",
                           (now, str(ip)))
            if h.get("is_blacklisted"):
                flags.append((ifid, str(ip), "BLACKLISTED", f"name={name}"))
            if int(h.get("num_alerts") or 0) > 0:
                flags.append((ifid, str(ip), "NTOPNG-ALERT",
                              f"num_alerts={h.get('num_alerts')}"))
        for fl in flows:
            srv = fl.get("server") or {}
            cli = fl.get("client") or {}
            sport = srv.get("port")
            sip = srv.get("ip") or ""
            if sport in SUSPICIOUS_PORTS and sip and not is_local(sip):
                flags.append((ifid, str(cli.get("ip") or "?"),
                              "SUSPICIOUS-DEST",
                              f"client={cli.get('ip')} -> {sip}:{sport}"))
    for ifid, host, kind, detail in flags:
        db.execute("INSERT INTO flags VALUES (?,?,?,?,?)",
                   (now, ifid, host, kind, detail))
        log(f"FLAG {kind} {host} {detail}")
    db.commit()
    if flags:
        ifid, host, kind, detail = flags[0]
        try:
            verdict, secs, tok_s = triage(f"host {host} ifid={ifid} "
                                          f"flag={kind}: {detail}")
            db.execute("INSERT INTO triage VALUES (?,?,?,?,?,?,?)",
                       (now, host, kind, TRIAGE_MODEL, secs, tok_s, verdict))
            db.commit()
            log(f"TRIAGE {kind} {host} {secs}s {tok_s} tok/s: {verdict}")
        except Exception as e:
            log(f"TRIAGE failed {kind} {host}: {e}")
    cutoff = now - RETENTION_DAYS * 86400
    for tbl in ("snapshots", "flags", "triage"):
        db.execute(f"DELETE FROM {tbl} WHERE ts < ?", (cutoff,))
    db.commit()
    db.close()
    log("run done")


if __name__ == "__main__":
    main()
