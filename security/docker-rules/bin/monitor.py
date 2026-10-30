#!/usr/bin/env python3
"""Docker 0.0.0.0 exposure monitor -- 2-minute grace period."""
import json, subprocess, time, smtplib, sys, os
from email.mime.text import MIMEText

BASE = "/home/abdum/services/security/docker-rules"
ALLOWLIST = f"{BASE}/config/allowlist.conf"
STATE = f"{BASE}/state/state.json"
MAILENV = f"{BASE}/config/mail.env"
LOG = f"{BASE}/logs/monitor.log"
GRACE_SECONDS = 120

def log(msg):
    line = f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}"
    print(line)
    with open(LOG, "a") as f:
        f.write(line + "\n")

def load_mail_env():
    cfg = {}
    with open(MAILENV) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            cfg[k] = v.strip().strip('"').strip("'")
    return cfg

def send_mail(subject, body):
    try:
        cfg = load_mail_env()
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = f"{cfg.get('SMTP_FROM_NAME','Docker Exposure Monitor')} <{cfg.get('SMTP_FROM_ADDRESS')}>"
        msg["To"] = cfg["ALERT_TO"]
        port = int(cfg["SMTP_PORT"])
        if port == 465:
            with smtplib.SMTP_SSL(cfg["SMTP_HOST"], port, timeout=15) as s:
                s.login(cfg["SMTP_USERNAME"], cfg["SMTP_PASSWORD"])
                s.sendmail(cfg.get("SMTP_FROM_ADDRESS"), [cfg["ALERT_TO"]], msg.as_string())
        else:
            with smtplib.SMTP(cfg["SMTP_HOST"], port, timeout=15) as s:
                s.starttls()
                s.login(cfg["SMTP_USERNAME"], cfg["SMTP_PASSWORD"])
                s.sendmail(cfg.get("SMTP_FROM_ADDRESS"), [cfg["ALERT_TO"]], msg.as_string())
        log(f"Sent email: {subject}")
    except Exception as e:
        log(f"ERROR sending email ({subject}): {e}")

def load_allowlist():
    allowed = set()
    if os.path.exists(ALLOWLIST):
        with open(ALLOWLIST) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    allowed.add(line)
    return allowed

def load_state():
    if os.path.exists(STATE):
        with open(STATE) as f:
            return json.load(f)
    return {}

def save_state(state):
    with open(STATE, "w") as f:
        json.dump(state, f, indent=2)

# Keyed by "container:hostport", for every binding where HostIp is 0.0.0.0 (or empty).
def get_exposed_ports():
    exposed = {}
    out = subprocess.run(["docker", "ps", "--format", "{{.Names}}"], capture_output=True, text=True).stdout
    names = [n for n in out.strip().split("\n") if n]
    for name in names:
        inspect = subprocess.run(
            ["docker", "inspect", name, "--format",
             "{{json .NetworkSettings.Ports}}|{{range .NetworkSettings.Networks}}{{.IPAddress}} {{end}}|{{.Config.Image}}"],
            capture_output=True, text=True
        ).stdout.strip()
        if not inspect:
            continue
        try:
            ports_json, ips, image = inspect.split("|", 2)
            ports = json.loads(ports_json) if ports_json != "null" else {}
        except Exception:
            continue
        internal_ip = ips.strip().split(" ")[0] if ips.strip() else ""
        for cport, bindings in (ports or {}).items():
            if not bindings:
                continue
            for b in bindings:
                if b.get("HostIp") in ("0.0.0.0", "") and b.get("HostPort"):
                    hostport = b["HostPort"]
                    key = f"{name}:{hostport}"
                    proto_port = cport.split("/")[0]
                    exposed[key] = {"ip": internal_ip, "container_port": proto_port,
                                     "image": image, "container": name, "hostport": hostport}
    return exposed

# DOCKER-USER is the hook chain Docker won't override.
def block_rule_exists(ip, port):
    r = subprocess.run(["iptables", "-C", "DOCKER-USER", "-d", ip, "-p", "tcp", "--dport", str(port), "-j", "DROP"],
                        capture_output=True)
    return r.returncode == 0

def apply_block(ip, port):
    if ip and not block_rule_exists(ip, port):
        subprocess.run(["iptables", "-I", "DOCKER-USER", "-d", ip, "-p", "tcp", "--dport", str(port), "-j", "DROP"])

def remove_block(ip, port):
    if ip and block_rule_exists(ip, port):
        subprocess.run(["iptables", "-D", "DOCKER-USER", "-d", ip, "-p", "tcp", "--dport", str(port), "-j", "DROP"])

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--init":
        exposed = get_exposed_ports()
        with open(ALLOWLIST, "w") as f:
            f.write("# Docker exposure monitor allowlist\n")
            f.write("# One 'container:port' per line. Anything here is allowed on 0.0.0.0 without restriction.\n")
            f.write("# Remove a line to start a 1-hour grace period before it gets auto-blocked.\n")
            for key in sorted(exposed):
                f.write(key + "\n")
        log(f"Initialized allowlist with {len(exposed)} currently-exposed entries.")
        print(f"Seeded {ALLOWLIST} with {len(exposed)} entries.")
        return

    allowed = load_allowlist()
    state = load_state()
    exposed = get_exposed_ports()
    now = time.time()

    for key, info in exposed.items():
        if key in allowed:
            if key in state:
                was_blocked = state[key].get("blocked")
                if was_blocked:
                    remove_block(state[key].get("ip", info["ip"]), info["container_port"])
                log(f"APPROVED: {key} added to allowlist{' (was blocked, now unblocked)' if was_blocked else ''}.")
                send_mail(
                    f"[Docker Exposure Monitor] Added to allowlist: {key}",
                    f"Container '{info['container']}' (image: {info['image']}) on port {info['hostport']} "
                    f"has been added to the allowlist.{' It was previously blocked; the block has now been removed.' if was_blocked else ''}\n"
                )
                del state[key]
            continue

        if key not in state:
            state[key] = {"first_seen": now, "blocked": False, "ip": info["ip"],
                           "container_port": info["container_port"], "image": info["image"]}
            log(f"NEW UNAPPROVED EXPOSURE: {key} (image: {info['image']}, ip: {info['ip']})")
            send_mail(
                f"[Docker Exposure Monitor] New exposure detected: {key}",
                f"Container '{info['container']}' (image: {info['image']}) just appeared bound to 0.0.0.0 "
                f"on port {info['hostport']}, and is NOT on the allowlist.\n\n"
                f"You have 2 minutes to approve it, or it will be automatically blocked.\n\n"
                f"To approve (allow permanently):\n  docker-exposure-approve {info['container']} {info['hostport']}\n\n"
                f"To block immediately instead of waiting:\n  docker-exposure-deny {info['container']} {info['hostport']}\n"
            )
        else:
            entry = state[key]
            entry["ip"] = info["ip"]
            elapsed = now - entry["first_seen"]
            if elapsed >= GRACE_SECONDS and not entry.get("blocked"):
                apply_block(info["ip"], info["container_port"])
                entry["blocked"] = True
                log(f"GRACE PERIOD EXPIRED: {key} -> blocked.")
                send_mail(
                    f"[Docker Exposure Monitor] Grace period expired, blocked: {key}",
                    f"Container '{info['container']}' (image: {info['image']}) on port {info['hostport']} "
                    f"was not approved within 2 minutes and has now been blocked from external access.\n\n"
                    f"To approve it later (allow + unblock):\n  docker-exposure-approve {info['container']} {info['hostport']}\n"
                )

    for key in list(state.keys()):
        if key not in exposed and key not in allowed:
            entry = state[key]
            if entry.get("blocked"):
                remove_block(entry.get("ip"), entry.get("container_port"))
                log(f"CLEANUP: {key} no longer running, removed stale block rule.")
            del state[key]

    save_state(state)

if __name__ == "__main__":
    main()
