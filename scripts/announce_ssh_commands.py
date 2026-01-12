#!/usr/bin/env python3

import subprocess
import sys

TERRAFORM_DIR = "terraform"
SSH_USER = "ansible"


def tf_output(name):
    cmd = ["terraform", f"-chdir={TERRAFORM_DIR}", "output", "-raw", name]
    try:
        return subprocess.check_output(cmd, text=True).strip()
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
        f"{SSH_USER}@{backend_private_ip}\n"
    )


if __name__ == "__main__":
    main()
