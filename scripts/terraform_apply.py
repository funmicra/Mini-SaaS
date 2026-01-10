#!/usr/bin/env python3

import os
import subprocess
import sys
from pathlib import Path

TERRAFORM_DIR = Path("terraform")

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

# ------------------------------------------------------------------
# Main
# ------------------------------------------------------------------

def main():
    # Validate required envs
    for var in ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"]:
        require_env(var)

    if not TERRAFORM_DIR.exists():
        print(f"[ERROR] Terraform directory not found: {TERRAFORM_DIR}")
        sys.exit(1)

    # Terraform init + plan + apply
    run(["terraform", "init"], cwd=TERRAFORM_DIR)
    run(["terraform", "plan", "-out=tfplan"], cwd=TERRAFORM_DIR)
    run(["terraform", "apply", "-auto-approve", "tfplan"], cwd=TERRAFORM_DIR)

    print("[INFO] Terraform apply completed successfully")

if __name__ == "__main__":
    main()
