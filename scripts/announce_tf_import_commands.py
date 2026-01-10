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
    value = os.environ.get(var)
    if not value:
        print(f"[ERROR] Required environment variable missing: {var}")
        sys.exit(1)
    return value

def tf_output(args):
    """
    Run terraform output with AWS credentials from environment.
    """
    env = os.environ.copy()
    cmd = ["terraform", f"-chdir={TERRAFORM_DIR}", "output"] + args
    try:
        return subprocess.check_output(cmd, text=True, env=env).strip()
    except subprocess.CalledProcessError:
        print(f"[ERROR] Terraform command failed: {' '.join(cmd)}")
        sys.exit(1)

# ------------------------------------------------------------------
# Main
# ------------------------------------------------------------------

def main():
    # Validate Jenkins-injected AWS credentials
    aws_access_key = require_env("AWS_ACCESS_KEY_ID")
    aws_secret_key = require_env("AWS_SECRET_ACCESS_KEY")

    print(f"[INFO] Using AWS_ACCESS_KEY_ID={aws_access_key[:4]}*** (masked)")

    # Read Terraform outputs
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
