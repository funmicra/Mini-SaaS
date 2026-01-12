#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path
import ipaddress

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

def run_terraform_output():
    """Fetch all terraform outputs as JSON."""
    cmd = ["terraform", f"-chdir={TF_DIR}", "output", "-json"]
    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True
        )
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Terraform output failed:\n{e.stderr}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"[ERROR] Failed to parse Terraform JSON output:\n{e}", file=sys.stderr)
        sys.exit(1)

def normalize_ip(ip):
    """Clean IP string and validate."""
    ip = str(ip).strip().strip('"\'')
    try:
        ipaddress.ip_address(ip)
    except ValueError:
        print(f"[ERROR] Invalid IP address: {ip}", file=sys.stderr)
        sys.exit(1)
    return ip

def add_group(inventory_lines, group_name, hosts, vars_dict=None):
    """Append a group and its vars to inventory."""
    inventory_lines.append(f"[{group_name}]")
    inventory_lines.extend(hosts)
    inventory_lines.append("")
    if vars_dict:
        inventory_lines.append(f"[{group_name}:vars]")
        for k, v in vars_dict.items():
            inventory_lines.append(f"{k}={v}")
        inventory_lines.append("")

# ------------------------------------------------------------------
# Main
# ------------------------------------------------------------------

def main():
    if not TF_DIR.exists():
        print(f"[ERROR] Terraform directory not found: {TF_DIR}", file=sys.stderr)
        sys.exit(1)

    outputs = run_terraform_output()
    
    # Identify groups dynamically
    inventory = []

    frontend_ips = outputs.get("frontend_ips", {}).get("value", [])
    backend_ips = outputs.get("backend_ips", {}).get("value", [])

    if not frontend_ips:
        print("[ERROR] No frontend IPs found in Terraform output", file=sys.stderr)
        sys.exit(1)

    frontend_ips = [normalize_ip(ip) for ip in frontend_ips]
    backend_ips = [normalize_ip(ip) for ip in backend_ips]

    # Frontend group
    add_group(
        inventory,
        "frontend",
        frontend_ips,
        vars_dict={
            "ansible_user": ANSIBLE_USER,
            "ansible_python_interpreter": "/usr/bin/python3",
            "ansible_ssh_common_args": "-o ForwardAgent=yes -o StrictHostKeyChecking=no",
        }
    )

    # Backend group
    if backend_ips:
        proxy_jump = frontend_ips[0]  # use first frontend as jump host
        add_group(
            inventory,
            "backend",
            backend_ips,
            vars_dict={
                "ansible_user": ANSIBLE_USER,
                "ansible_python_interpreter": "/usr/bin/python3",
                "ansible_ssh_common_args": (
                    f"-o ProxyJump={ANSIBLE_USER}@{proxy_jump} "
                    "-o ForwardAgent=yes -o StrictHostKeyChecking=no"
                ),
            }
        )

    # Write inventory
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text("\n".join(inventory))
    print(f"[OK] Dynamic inventory written to {OUTPUT_FILE}")

# ------------------------------------------------------------------

if __name__ == "__main__":
    main()
