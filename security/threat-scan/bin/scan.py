#!/usr/bin/env python3
"""Hourly host security scan -- cryptominer/ransomware/rootkit indicators, emails only on findings."""
import subprocess, time, os, json, smtplib
from email.mime.text import MIMEText

BASE = "/home/abdum/services/security/threat-scan"
MAILENV = "/home/abdum/services/security/docker-rules/config/mail.env"
LOG = f"{BASE}/logs/scan.log"
SUID_BASELINE = f"{BASE}/state/suid_baseline.json"

MINER_SIGNATURES = ["xmrig", "minerd", "cpuminer", "kinsing", "stratum", "nicehash", "monero", "kdevtmpfsi"]
RANSOM_NAME_PATTERNS = ["*ransom*", "*decrypt*instruction*", "*HOW_TO*DECRYPT*", "*HELP_DECRYPT*", "*README*RECOVER*"]
RANSOM_EXTENSIONS = [".encrypted", ".locked", ".crypt", ".wcry", ".lockbit", ".ryuk", ".conti", ".revil"]
SCAN_DIRS = ["/home", "/srv", "/opt", "/var/www"]
BURST_THRESHOLD = 3000
# /mnt (large model-output dirs) excluded from ransomware/burst checks for runtime/memory; SUID check still covers it via find /.
EXCLUDE_PATH_PATTERNS = [
    "*/miniconda3/*", "*/anaconda3/*", "*/.conda/*", "*/node_modules/*",
    "*/site-packages/*", "*/dist-packages/*", "*/.cache/*", "*/venv/*",
    "*/.venv/*", "*/vendor/*", "*/.git/*",
]
EXCLUDE_CLAUSE = " ".join([f'-not -path "{p}"' for p in EXCLUDE_PATH_PATTERNS])

def log(msg):
    line = f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}"
    print(line)
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
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
        msg["From"] = f"{cfg.get('SMTP_FROM_NAME','Host Security Scan')} <{cfg.get('SMTP_FROM_ADDRESS')}>"
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
        log(f"Sent alert email: {subject}")
    except Exception as e:
        log(f"ERROR sending email ({subject}): {e}")

def run(cmd, timeout=180, nice=False):
    if nice:
        cmd = f"nice -n 19 ionice -c3 {cmd}"
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip()
    except subprocess.TimeoutExpired:
        log(f"WARNING: command timed out after {timeout}s, skipping this cycle: {cmd[:120]}")
        return ""

def check_cryptominer():
    findings = []
    ps_out = run("ps auxww")
    for sig in MINER_SIGNATURES:
        for line in ps_out.splitlines():
            if sig in line.lower() and "grep" not in line and "threat-scan" not in line:
                findings.append(f"Possible cryptominer process (matched '{sig}'): {line.strip()}")
    return findings

def check_ransomware():
    findings = []
    name_expr = " -o ".join([f'-iname "{p}"' for p in RANSOM_NAME_PATTERNS])
    out = run(f'find {" ".join(SCAN_DIRS)} -xdev {EXCLUDE_CLAUSE} \\( {name_expr} \\) 2>/dev/null', timeout=900, nice=True)
    if out:
        findings.append("Ransom-note-like filenames found:\n" + out)
    ext_expr = " -o ".join([f'-iname "*{e}"' for e in RANSOM_EXTENSIONS])
    out = run(f'find {" ".join(SCAN_DIRS)} -xdev {EXCLUDE_CLAUSE} \\( {ext_expr} \\) 2>/dev/null | grep -v "\\.enc$"', timeout=900, nice=True)
    if out:
        findings.append("Files with known ransomware extensions found:\n" + out)
    return findings

def check_mass_modification_burst():
    findings = []
    out = run(
        f'find {" ".join(SCAN_DIRS)} -xdev {EXCLUDE_CLAUSE} -type f -mmin -60 -printf "%TY-%Tm-%Td %TH:%TM\\n" 2>/dev/null '
        f'| sort | uniq -c | sort -rn | head -5',
        timeout=900, nice=True
    )
    if out:
        top_line = out.splitlines()[0].strip()
        top_count = int(top_line.split()[0])
        if top_count >= BURST_THRESHOLD:
            findings.append(
                f"Unusually high file-modification burst in the last hour (top minute: {top_count} files, "
                f"threshold {BURST_THRESHOLD}):\n{out}\n"
                f"This can be legitimate (large deploys/backups) or an active mass-encryption event -- "
                f"verify the actual files/extensions involved before assuming the worst."
            )
    return findings

def check_new_suid():
    findings = []
    result = run('find / -xdev -type f -perm -4000 2>/dev/null', timeout=900, nice=True)
    if not result:
        log("WARNING: SUID scan returned empty (timed out or found nothing) -- skipping baseline update this cycle to avoid a false 'all clear'.")
        return []
    current = set(result.splitlines())
    os.makedirs(os.path.dirname(SUID_BASELINE), exist_ok=True)
    if os.path.exists(SUID_BASELINE):
        with open(SUID_BASELINE) as f:
            baseline = set(json.load(f))
        new_suid = current - baseline
        if new_suid:
            findings.append("New SUID binaries appeared since the baseline was captured:\n" + "\n".join(sorted(new_suid)))
    with open(SUID_BASELINE, "w") as f:
        json.dump(sorted(current), f, indent=2)
    return findings

def baseline_check(baseline_file, current_set, describe):
    findings = []
    os.makedirs(os.path.dirname(baseline_file), exist_ok=True)
    if os.path.exists(baseline_file):
        with open(baseline_file) as f:
            baseline = set(json.load(f))
        new_items = current_set - baseline
        if new_items:
            findings.append(f"{describe}:\n" + "\n".join(sorted(new_items)))
    with open(baseline_file, "w") as f:
        json.dump(sorted(current_set), f, indent=2)
    return findings

def check_root_authorized_keys():
    baseline_file = f"{BASE}/state/root_authorized_keys_baseline.txt"
    content = run("cat /root/.ssh/authorized_keys 2>/dev/null").strip()
    findings = []
    if os.path.exists(baseline_file):
        with open(baseline_file) as f:
            baseline = f.read().strip()
        if content != baseline:
            findings.append(
                f"root's /root/.ssh/authorized_keys has CHANGED since the last check:\n"
                f"Current:\n{content}\n\nPrevious:\n{baseline}"
            )
    with open(baseline_file, "w") as f:
        f.write(content)
    return findings

def check_sshd_config_drift():
    baseline_file = f"{BASE}/state/sshd_config_baseline.json"
    out = run("sshd -T 2>/dev/null | grep -Ei '^permitrootlogin |^passwordauthentication |^pubkeyauthentication |^maxauthtries '")
    current = {}
    for line in out.splitlines():
        parts = line.split(None, 1)
        if len(parts) == 2:
            current[parts[0]] = parts[1]
    findings = []
    if os.path.exists(baseline_file):
        with open(baseline_file) as f:
            baseline = json.load(f)
        if current != baseline:
            findings.append(f"sshd effective configuration changed:\nWas: {baseline}\nNow: {current}")
    if current:
        with open(baseline_file, "w") as f:
            json.dump(current, f, indent=2)
    return findings

def check_new_kernel_modules():
    out = run("lsmod | awk 'NR>1{print $1}'")
    current = set(out.splitlines())
    if not current:
        return []
    return baseline_check(f"{BASE}/state/kmod_baseline.json", current,
                           "New kernel module(s) loaded since baseline (possible rootkit indicator)")

def check_new_privileged_containers():
    out = run(
        "for c in $(docker ps -q); do "
        "priv=$(docker inspect $c --format '{{.HostConfig.Privileged}}' 2>/dev/null); "
        "if [ \"$priv\" = \"true\" ]; then "
        "docker inspect $c --format '{{.Name}} {{.Config.Image}}' 2>/dev/null; fi; done"
    )
    current = set(out.splitlines())
    return baseline_check(f"{BASE}/state/privileged_baseline.json", current,
                           "New privileged container(s) detected")

def check_new_docker_images():
    out = run("docker images --format '{{.Repository}}:{{.Tag}} {{.ID}}'")
    current = set(out.splitlines())
    if not current:
        return []
    return baseline_check(f"{BASE}/state/images_baseline.json", current,
                           "New Docker image(s) pulled since baseline")

def check_root_crontab_drift():
    baseline_file = f"{BASE}/state/root_crontab_baseline.txt"
    content = run("crontab -l -u root 2>/dev/null").strip()
    findings = []
    if os.path.exists(baseline_file):
        with open(baseline_file) as f:
            baseline = f.read().strip()
        if content != baseline:
            findings.append(f"root's crontab has CHANGED since the last check:\nCurrent:\n{content}\n\nPrevious:\n{baseline}")
    with open(baseline_file, "w") as f:
        f.write(content)
    return findings

def check_ld_preload():
    out = run("cat /etc/ld.so.preload 2>/dev/null").strip()
    if out:
        return [f"/etc/ld.so.preload exists and is non-empty -- potential LD_PRELOAD hijack:\n{out}"]
    return []

def check_process_proc_mismatch(threshold=80):
    ps_count = run("ps aux | wc -l")
    proc_count = run("ls /proc | grep -E '^[0-9]+$' | wc -l")
    try:
        diff = abs(int(ps_count) - int(proc_count))
        if diff > threshold:
            return [f"Process count mismatch between 'ps aux' ({ps_count}) and /proc ({proc_count}) "
                     f"-- exceeds normal variance threshold ({threshold}), possible process-hiding rootkit."]
    except ValueError:
        pass
    return []

WORLD_WRITABLE_CHECK_DIRS = ["/etc", "/usr/bin", "/usr/local/bin", "/root", "/opt"]
def check_new_world_writable():
    out = run(f'find {" ".join(WORLD_WRITABLE_CHECK_DIRS)} -xdev -perm -0002 -type f 2>/dev/null', timeout=120, nice=True)
    current = set(out.splitlines())
    return baseline_check(f"{BASE}/state/world_writable_baseline.json", current,
                           "New world-writable file(s) found under sensitive paths (/etc, /usr/bin, /usr/local/bin, /root, /opt)")

def check_ssh_key_counts():
    findings = []
    out = run(r'for u in $(cut -f1 -d: /etc/passwd); do f=/home/$u/.ssh/authorized_keys; [ -f "$f" ] && echo "$u $(wc -l < "$f")"; done')
    current = {}
    for line in out.splitlines():
        parts = line.split()
        if len(parts) == 2 and parts[1].isdigit():
            current[parts[0]] = int(parts[1])
    baseline_file = f"{BASE}/state/ssh_key_counts_baseline.json"
    if os.path.exists(baseline_file):
        with open(baseline_file) as f:
            baseline = json.load(f)
        for user, count in current.items():
            prev = baseline.get(user, 0)
            if count > prev + 2:
                findings.append(f"User '{user}' authorized_keys count jumped from {prev} to {count} since last check")
    if current:
        with open(baseline_file, "w") as f:
            json.dump(current, f, indent=2)
    return findings

def main():
    all_findings = []
    all_findings += check_cryptominer()
    all_findings += check_ransomware()
    all_findings += check_mass_modification_burst()
    all_findings += check_new_suid()
    all_findings += check_root_authorized_keys()
    all_findings += check_sshd_config_drift()
    all_findings += check_new_kernel_modules()
    all_findings += check_new_privileged_containers()
    all_findings += check_new_docker_images()
    all_findings += check_root_crontab_drift()
    all_findings += check_ld_preload()
    all_findings += check_process_proc_mismatch()
    all_findings += check_new_world_writable()
    all_findings += check_ssh_key_counts()

    if all_findings:
        log(f"SCAN FOUND {len(all_findings)} issue(s):")
        for i, finding in enumerate(all_findings, 1):
            log(f"  [{i}] {finding}")
        body = "Hourly security scan found the following on rejuvebio-hetzner:\n\n" + "\n\n---\n\n".join(all_findings)
        send_mail(f"[Host Security Scan] {len(all_findings)} issue(s) found on rejuvebio-hetzner", body)
    else:
        log("Scan clean, nothing found.")

if __name__ == "__main__":
    main()
