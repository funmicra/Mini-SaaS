#!/usr/bin/env python3

import os
import subprocess
import sys
import time
from pathlib import Path
import json
import boto3

TERRAFORM_DIR = Path("terraform")
# ANSIBLE_INVENTORY = Path("ansible/hosts.ini")
# ANSIBLE_USER = "deploy"  # cloud-init user

# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def run(cmd, cwd=None):
    print(f"[INFO] Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, check=True, text=True, capture_output=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)

def require_env(var):
    if not os.environ.get(var):
        print(f"[ERROR] Required env var missing: {var}")
        sys.exit(1)

def tf_output(name):
    """Get Terraform output in JSON"""
    cmd = ["terraform", "-chdir=" + str(TERRAFORM_DIR), "output", "-json", name]
    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    return json.loads(result.stdout)

def wait_for_instance(instance_id, timeout=300):
    ec2 = boto3.client("ec2")
    start = time.time()
    while time.time() - start < timeout:
        resp = ec2.describe_instance_status(InstanceIds=[instance_id])
        statuses = resp.get("InstanceStatuses", [])
        if statuses and statuses[0]["InstanceState"]["Name"] == "running":
            print(f"[INFO] Instance {instance_id} is running")
            return
        time.sleep(5)
    print(f"[WARN] Timeout waiting for instance {instance_id}")

# def generate_inventory(frontend_ip, backend_ip):
#     inventory = [
#         "[frontend]",
#         frontend_ip,
#         "",
#         "[frontend:vars]",
#         f"ansible_user={ANSIBLE_USER}",
#         "",
#         "[backend]",
#         backend_ip,
#         "",
#         "[backend:vars]",
#         f"ansible_user={ANSIBLE_USER}",
#         f"ansible_ssh_common_args=-o ProxyJump={ANSIBLE_USER}@{frontend_ip} -o ForwardAgent=yes -o StrictHostKeyChecking=no",
#         "",
#     ]
#     ANSIBLE_INVENTORY.write_text("\n".join(inventory))
#     print(f"[INFO] Ansible inventory written to {ANSIBLE_INVENTORY}")

# ------------------------------------------------------------------
# Main
# ------------------------------------------------------------------

def main():
    # Check env
    for var in ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"]:
        require_env(var)

    if not TERRAFORM_DIR.exists():
        print(f"[ERROR] Terraform directory not found: {TERRAFORM_DIR}")
        sys.exit(1)

    # Terraform init + plan + apply
    run(["terraform", "init"], cwd=TERRAFORM_DIR)
    run(["terraform", "plan", "-out=tfplan"], cwd=TERRAFORM_DIR)
    run(["terraform", "apply", "-auto-approve", "tfplan"], cwd=TERRAFORM_DIR)

    print("[INFO] Terraform apply completed. Fetching instance info...")

    # # Get frontend/backend IPs & IDs from Terraform outputs
    # frontend_ip = tf_output("frontend_public_ip")["value"]
    # backend_ip = tf_output("backend_private_ip")["value"]
    # frontend_id = tf_output("frontend_instance_id")["value"]
    # backend_id = tf_output("backend_instance_id")["value"]

    # # Wait for EC2 instances to be running
    # wait_for_instance(frontend_id)
    # wait_for_instance(backend_id)

    # # Generate Ansible inventory
    # generate_inventory(frontend_ip, backend_ip)

    # print("[INFO] Deployment complete. You can now run Ansible playbooks using hosts.ini")

if __name__ == "__main__":
    main()

