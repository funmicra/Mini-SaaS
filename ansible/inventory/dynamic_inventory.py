#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path

# ------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------

ANSIBLE_USER = "ansible"  # matches cloud-init automation user

SCRIPT_DIR = Path(__file__).resolve().parent
TF_DIR = (SCRIPT_DIR / "../../terraform").resolve()
OUTPUT_FILE = SCRIPT_DIR / "hosts.ini"

# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def tf_output(name, json_output=False):
    cmd = ["terraform", f"-chdir={TF_DIR}", "output"]
    if json_output:
        cmd.append("-json")
    cmd.append(name)

    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] terraform output '{name}' failed", file=sys.stderr)
        print(e.stderr, file=sys.stderr)
        sys.exit(1)

    out = result.stdout.strip()
    return json.loads(out) if json_output else out

def normalize_ip(value):
    """Ensure the IP is a clean string with no quotes or whitespace."""
    if not value:
        return ""
    return str(value).strip().strip('"').strip("'")

# ------------------------------------------------------------------
# Main
# ------------------------------------------------------------------

def main():
    if not TF_DIR.exists():
        print(f"[ERROR] Terraform directory not found: {TF_DIR}", file=sys.stderr)
        sys.exit(1)

    # Fetch Terraform outputs
    frontend_ip = normalize_ip(tf_output("frontend_public_ip"))
    backend_ip = normalize_ip(tf_output("backend_private_ip"))

    if not frontend_ip:
        print("[ERROR] frontend_public_ip is empty", file=sys.stderr)
        sys.exit(1)

    if not backend_ip:
        print("[ERROR] backend_private_ip is empty", file=sys.stderr)
        sys.exit(1)

    # Build inventory
    inventory = [
        "[frontend]",
        frontend_ip,
        "",
        "[frontend:vars]",
        f"ansible_user={ANSIBLE_USER}",
        f"ansible_python_interpreter=/usr/bin/python3",
        f"ansible_ssh_common_args=-o ForwardAgent=yes -o StrictHostKeyChecking=no",
        "",
        "[backend]",
        backend_ip,
        "",
        "[backend:vars]",
        f"ansible_user={ANSIBLE_USER}",
        f"ansible_python_interpreter=/usr/bin/python3",
        f"ansible_ssh_common_args=-o ProxyJump={ANSIBLE_USER}@{frontend_ip} "
        "-o ForwardAgent=yes -o StrictHostKeyChecking=no",
        "",
    ]

    OUTPUT_FILE.write_text("\n".join(inventory))
    print(f"[OK] Static inventory written to {OUTPUT_FILE}")

# ------------------------------------------------------------------

if __name__ == "__main__":
    main()
