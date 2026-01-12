#!/usr/bin/env python3

import os
import subprocess
import sys

HOSTS_FILE = "ansible/inventory/hosts.ini"
PLAYBOOK = "ansible/site.yaml"


def run(cmd, env=None):
    print("[INFO] Running:", " ".join(cmd))
    subprocess.run(cmd, env=env, check=True)


def start_ssh_agent():
    output = subprocess.check_output(["ssh-agent", "-s"], text=True)
    for line in output.splitlines():
        if "=" in line and line.startswith(("SSH_AUTH_SOCK", "SSH_AGENT_PID")):
            key, value = line.split(";")[0].split("=")
            os.environ[key] = value
    print("[INFO] ssh-agent started")


def add_private_key(key_path):
    run(["ssh-add", key_path])
    print("[INFO] SSH private key added")


def run_playbook():
    run([
        "ansible-playbook",
        "-i", HOSTS_FILE,
        PLAYBOOK,
        "-vv"
    ])
    print("[INFO] Playbook finished successfully")


def main():
    ansible_key = os.environ.get("ANSIBLE_PRIVATE_KEY")

    if not ansible_key:
        print("[ERROR] ANSIBLE_PRIVATE_KEY not set")
        sys.exit(1)

    if not os.path.exists(ansible_key):
        print(f"[ERROR] SSH key not found: {ansible_key}")
        sys.exit(1)

    start_ssh_agent()
    add_private_key(ansible_key)
    run_playbook()


if __name__ == "__main__":
    main()
