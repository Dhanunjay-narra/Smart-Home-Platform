import os
import sys
import subprocess
import json
import time
import zipfile
from pathlib import Path

ROOT = Path(".").resolve()

def write_code_file(rel_path, content):
    p = ROOT / rel_path
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

def run_cmd(cmd, check=True):
    print(f">> Executing: {cmd}")
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=str(ROOT))
    if check and res.returncode != 0:
        print(f"Error executing '{cmd}':")
        print(res.stderr)
        print(res.stdout)
        raise RuntimeError(f"Command failed: {cmd}")
    return res.stdout.strip()

print("Master Builder loaded successfully.")
