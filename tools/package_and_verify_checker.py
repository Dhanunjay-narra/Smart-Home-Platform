import os
import sys
import zipfile
import json
from pathlib import Path
import urllib.request
import urllib.parse
import mimetypes
import uuid

ROOT = Path(__file__).resolve().parent.parent

def create_zip(zip_name="Smart Home Platform.zip"):
    zip_path = ROOT / zip_name
    print(f"Creating zip archive at: {zip_path}")
    
    # Exclude only temporary caches if any, BUT KEEP .git
    exclude_dirs = {"__pycache__", ".pytest_cache", "node_modules", ".venv", "venv"}
    
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(ROOT):
            # Don't recurse into excluded dirs
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            for file in files:
                if file == zip_name:
                    continue
                file_path = Path(root) / file
                rel_path = file_path.relative_to(ROOT)
                zipf.write(file_path, arcname=str(rel_path))
    
    file_size_mb = os.path.getsize(zip_path) / (1024 * 1024)
    print(f"Zip created successfully: {file_size_mb:.2f} MB")
    return zip_path

def upload_and_check(zip_path, checker_url="https://train-plex-checker-bot-1--ttejaswar1234.replit.app/api/check"):
    print(f"Uploading {zip_path.name} to {checker_url}...")
    boundary = f"----WebKitFormBoundary{uuid.uuid4().hex}"
    
    with open(zip_path, "rb") as f:
        file_bytes = f.read()

    body = []
    body.append(f"--{boundary}".encode('utf-8'))
    body.append(f'Content-Disposition: form-data; name="file"; filename="{zip_path.name}"'.encode('utf-8'))
    body.append(b"Content-Type: application/zip")
    body.append(b"")
    body.append(file_bytes)
    body.append(f"--{boundary}--".encode('utf-8'))
    body.append(b"")
    
    payload = b"\r\n".join(body)
    
    req = urllib.request.Request(
        checker_url,
        data=payload,
        headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Content-Length": str(len(payload))
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as response:
            res_body = response.read().decode('utf-8')
            data = json.loads(res_body)
            print("=================================================================")
            print(" TRAINPLEX CHECKER BOT RESULTS:")
            print("=================================================================")
            tp = data.get("trainplex", {})
            summary = tp.get("summary", {})
            print(f" Status:           {summary.get('overall')}")
            print(f" Compliance Score: {summary.get('score')}%")
            print(f" Total Checks:     {summary.get('total')}")
            print(f" Passed:           {summary.get('passed')}")
            print(f" Warned:           {summary.get('warned')}")
            print(f" Failed:           {summary.get('failed')}")
            print(f" LOC Count:        {summary.get('loc')}")
            print(f" Git Commits:      {summary.get('git', {}).get('commits')}")
            print(f" Git PR Merges:    {summary.get('git', {}).get('prs')}")
            print("=================================================================")
            
            print("\nDetailed Checks Breakdown:")
            for check in tp.get("checks", []):
                status_icon = "[PASS]" if check.get("status") == "pass" else "[WARN]" if check.get("status") == "warn" else "[FAIL]"
                print(f" {status_icon} {check.get('name')}: {check.get('value')} (Required: {check.get('required')})")
                if check.get("status") != "pass":
                    print(f"        Fix Hint: {check.get('fix')}")
            
            return data
    except Exception as e:
        print(f"Upload failed: {e}")
        return None

if __name__ == "__main__":
    zpath = create_zip("Smart Home Platform.zip")
    upload_and_check(zpath)
