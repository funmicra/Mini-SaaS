#!/usr/bin/env python3

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


def tf_output(name):
    """
    Read a raw terraform output value.
    """
    env = os.environ.copy()
    cmd = ["terraform", f"-chdir={TERRAFORM_DIR}", "output", "-raw", name]
    try:
        return subprocess.check_output(cmd, text=True, env=env).strip()
    except subprocess.CalledProcessError:
        print(f"[ERROR] Failed to read terraform output: {name}")
        sys.exit(1)

# ------------------------------------------------------------------
# Main
# ------------------------------------------------------------------

def main():
    # Jenkins / CI guardrails
    aws_access_key = require_env("AWS_ACCESS_KEY_ID")
    require_env("AWS_SECRET_ACCESS_KEY")

    print(f"[INFO] AWS credentials detected ({aws_access_key[:4]}*** masked)")

    # Terraform outputs
    frontend_instance_id = tf_output("frontend_instance_id")
    backend_instance_id = tf_output("backend_instance_id")
    nat_gateway_id = tf_output("nat_gateway_id")
    vpc_id = tf_output("vpc_id")
    public_subnet_id = tf_output("public_subnet_id")
    private_subnet_id = tf_output("private_subnet_id")

    print("\n# ---- Terraform import commands ----\n")

    # EC2 instances
    print(f'terraform import aws_instance.frontend {frontend_instance_id}')
    print(f'terraform import aws_instance.backend {backend_instance_id}')

    # Networking
    print(f'\nterraform import aws_nat_gateway.main {nat_gateway_id}')
    print(f'terraform import aws_vpc.main {vpc_id}')
    print(f'terraform import aws_subnet.public {public_subnet_id}')
    print(f'terraform import aws_subnet.private {private_subnet_id}')

    print("\n# ---- End ----\n")


if __name__ == "__main__":
    main()
