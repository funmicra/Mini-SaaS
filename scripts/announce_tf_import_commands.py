#!/usr/bin/env python3

import json
import subprocess
import sys
import os

TERRAFORM_DIR = "terraform"

# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def require_env(var):
    if not os.environ.get(var):
        print(f"[ERROR] Required env var missing: {var}")
        sys.exit(1)

def tf_output(args):
    cmd = ["terraform", f"-chdir={TERRAFORM_DIR}", "output"] + args
    try:
        return subprocess.check_output(cmd, text=True).strip()
    except subprocess.CalledProcessError:
        print(f"[ERROR] Terraform command failed: {' '.join(cmd)}")
        sys.exit(1)

# ------------------------------------------------------------------
# Main
# ------------------------------------------------------------------

def main():
    # Validate AWS credentials (needed for Terraform)
    require_env("AWS_ACCESS_KEY_ID")
    require_env("AWS_SECRET_ACCESS_KEY")

    # Read outputs
    instance_ids_raw = tf_output(["-json", "instance_ids"])
    proxy_id = tf_output(["-raw", "proxy_id"])
    vpc_id = tf_output(["-raw", "vpc_id"])

    instance_ids = json.loads(instance_ids_raw)

    print("\n# ---- Terraform import commands ----\n")

    # Private instances
    for idx, instance_id in enumerate(instance_ids):
        print(f'terraform import "linode_instance.private[{idx}]" {instance_id}')

    # Proxy
    print(f'\nterraform import "linode_instance.proxy" {proxy_id}')

    # VPC
    print(f'terraform import "linode_vpc.private" {vpc_id}')

    print("\n# ---- End ----\n")


if __name__ == "__main__":
    main()
