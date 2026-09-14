#!/usr/bin/env python3
"""Checks local-deployment prerequisites (no uv - only staging/production need it)."""
import shutil
import subprocess
import sys
import os
import grp


def ask_yes_no(question, default_no=True):
    """Prompt for confirmation. Defaults to No if input isn't available."""
    suffix = " [y/N] " if default_no else " [Y/n] "
    try:
        answer = input(question + suffix).strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        return False
    if not answer:
        return not default_no
    return answer in ("y", "yes")


def run(cmd, timeout=15, shell=False):
    try:
        return subprocess.run(cmd, shell=shell, capture_output=True, text=True, timeout=timeout)
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        return subprocess.CompletedProcess(cmd, 1, "", str(e))


# --- Detection: pure checks, no prompting, no side effects ---

def detect_docker():
    if not shutil.which("docker"):
        return False
    return run(["docker", "info"]).returncode == 0

def detect_docker_group_membership():
    try:
        docker_group = grp.getgrnam("docker")
    except KeyError:
        return False
    return os.getenv("USER") in docker_group.gr_mem

def detect_community_docker_collection():
    result = run(["ansible-galaxy", "collection", "list", "community.docker"])
    return result.returncode == 0 and "community.docker" in result.stdout

def detect_docker_compose():
    if run(["docker", "compose", "version"]).returncode == 0:
        return True
    return shutil.which("docker-compose") is not None


# --- Remediation: only called after the user explicitly agrees ---

def install_docker():
    print("Installing Docker...")
    result = run("curl -fsSL https://get.docker.com | sudo sh", timeout=300, shell=True)
    if result.returncode != 0:
        print(f"[FAIL] Docker installation failed: {result.stderr}")
        return False
    print("[OK] Docker installed.")
    run(["sudo", "systemctl", "enable", "--now", "docker"], timeout=30)
    return True

def install_docker_group_membership():
    try:
        grp.getgrnam("docker")
    except KeyError:
        result = run(["sudo", "groupadd", "docker"])
        if result.returncode != 0 and "exists" not in result.stderr.lower():
            print(f"[FAIL] Failed to create docker group: {result.stderr}")
            return False

    result = run(["sudo", "usermod", "-aG", "docker", os.getenv("USER")])
    if result.returncode != 0:
        print(f"[FAIL] Failed to add user to docker group: {result.stderr}")
        return False
    print("[OK] Added to docker group (the playbook itself works around needing a")
    print("   fresh login by running docker via `sg docker`).")
    return True

def install_community_docker_collection():
    result = run(["ansible-galaxy", "collection", "install", "community.docker"], timeout=120)
    if result.returncode == 0:
        print("[OK] community.docker collection installed.")
        return True
    print(f"[FAIL] Install failed: {result.stderr}")
    return False

# --- Orchestration ---

ITEMS = [
    {"key": "docker", "name": "Docker", "detect": detect_docker,
     "install": install_docker, "needs_sudo": True,
     "manual": "https://docs.docker.com/engine/install/"},
    {"key": "docker_group", "name": "User in docker group (so docker needs no sudo)",
     "detect": detect_docker_group_membership, "install": install_docker_group_membership,
     "needs_sudo": True, "manual": "sudo usermod -aG docker $USER   # then re-login",
     "depends_on": "docker"},
    {"key": "community_docker", "name": "community.docker Ansible collection",
     "detect": detect_community_docker_collection, "install": install_community_docker_collection,
     "needs_sudo": False, "manual": "ansible-galaxy collection install community.docker"},
    {"key": "docker_compose", "name": "Docker Compose", "detect": detect_docker_compose,
     "install": None, "needs_sudo": False,
     "manual": "https://docs.docker.com/compose/install/", "depends_on": "docker"},
]


def main():
    print("Checking prerequisites...")
    print("=" * 60)

    status = {}
    for item in ITEMS:
        if item.get("depends_on") and not status.get(item["depends_on"], False):
            status[item["key"]] = False
            continue
        status[item["key"]] = item["detect"]()

    print("\nStatus:")
    for item in ITEMS:
        print(f"  [{'OK' if status[item['key']] else 'MISSING'}] {item['name']}")
    print()

    missing = [item for item in ITEMS if not status[item["key"]]]
    if not missing:
        print("[OK] All prerequisites are already installed. Proceeding...")
        sys.exit(0)

    print("=" * 60)
    print(f"{len(missing)} missing. Choose per item: install now, or do it yourself.")
    print("=" * 60 + "\n")

    still_missing = []
    for item in missing:
        sudo_note = " (requires sudo)" if item["needs_sudo"] else " (no sudo needed)"
        print(f"[MISSING] {item['name']}{sudo_note}")

        if item["install"] is None:
            print(f"   Install yourself: {item['manual']}")
            still_missing.append(item)
            print()
            continue

        if ask_yes_no("   Install it now?", default_no=item["needs_sudo"]):
            if not item["install"]():
                still_missing.append(item)
        else:
            print(f"   Skipped. Install yourself, then rerun: {item['manual']}")
            still_missing.append(item)
        print()

    print("=" * 60)
    if still_missing:
        print("NOTE: Still missing, install these and rerun the playbook:\n")
        for item in still_missing:
            print(f"  - {item['name']}: {item['manual']}")
        sys.exit(1)

    print("[OK] All prerequisites are now installed. Proceeding...")
    sys.exit(0)


if __name__ == "__main__":
    main()
