#!/usr/bin/env python3

import subprocess
import sys
import json

TERRAFORM_DIR = "../terraform"
SSH_USER = "ansible"


def tf_output(name):
    cmd = ["terraform", f"-chdir={TERRAFORM_DIR}", "output", "-json", name]
    try:
        raw = subprocess.check_output(cmd, text=True).strip()
        value = json.loads(raw)
        # if value is a list, take first element
        if isinstance(value, list):
            return value[0]
        return value
    except subprocess.CalledProcessError:
        print(f"[ERROR] Failed to read terraform output: {name}")
        sys.exit(1)


def main():
    frontend_public_ip = tf_output("frontend_public_ip")
    frontend_private_ip = tf_output("frontend_private_ip")
    backend_private_ip = tf_output("backend_private_ip")

    print("\nSSH access paths (validated against Terraform state):\n")

    print("# Frontend (direct access)")
    print(f"ssh {SSH_USER}@{frontend_public_ip}\n")

    print("# Backend (via frontend jump host)")
    print(
        f"ssh -J {SSH_USER}@{frontend_public_ip} "
        f"{SSH_USER}@{backend_private_ip} -o StrictHostKeyChecking=no\n"
    )


if __name__ == "__main__":
    main()
