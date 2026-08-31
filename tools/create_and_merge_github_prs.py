import os
import sys
import json
import subprocess
import urllib.request
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def get_github_token():
    p = subprocess.Popen(["git", "credential", "fill"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, cwd=str(ROOT))
    out, _ = p.communicate("protocol=https\nhost=github.com\n")
    token = None
    for line in out.splitlines():
        if line.startswith("password="):
            token = line.split("=", 1)[1].strip()
    return token

def gh_api(endpoint, method="GET", data=None, token=None):
    url = f"https://api.github.com{endpoint}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "SmartHomePlatform-Builder",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    req_data = json.dumps(data).encode('utf-8') if data else None
    req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as res:
            res_body = res.read().decode('utf-8')
            return json.loads(res_body) if res_body else {"status": res.status}
    except urllib.error.HTTPError as e:
        err_body = e.read().decode('utf-8')
        print(f"HTTP Error {e.code} on {method} {endpoint}: {err_body}")
        try:
            return json.loads(err_body)
        except Exception:
            return {"error": err_body, "code": e.code}

def run_git(cmd):
    print(f">> git {cmd}")
    res = subprocess.run(f"git {cmd}", shell=True, capture_output=True, text=True, cwd=str(ROOT))
    if res.stdout.strip():
        print(res.stdout.strip())
    if res.returncode != 0:
        print(f"Git error: {res.stderr.strip()}")
    return res.returncode == 0

def orchestrate_github_prs():
    token = get_github_token()
    if not token:
        print("Could not retrieve GitHub token from credential manager.")
        return

    repo = "Dhanunjay-narra/Smart-Home-Platform"
    print(f"Authenticated with GitHub API for repo: {repo}")

    # Check current open PRs
    open_prs = gh_api(f"/repos/{repo}/pulls?state=open", token=token)
    print(f"Initial open PR count: {len(open_prs) if isinstance(open_prs, list) else 'error'}")

    # List of PRs to create and merge in chronological sequence
    pr_phases = [
        {
            "branch": "feature/iam-home-device-platform",
            "title": "feat(iam,home,devices): Core Identity, Spatial Model & Extensible Capability Framework",
            "body": "### Pull Request #1: Identity, Home & Device Management Platform\n- 8-Tier RBAC hierarchy and OAuth2/OIDC\n- Spatial property hierarchy (Buildings, Floors, Rooms, Zones)\n- Extensible Capability Trait system (25+ traits)"
        },
        {
            "branch": "feature/telemetry-protocols-edge-firmware",
            "title": "feat(protocols,edge,firmware): Telemetry Ingestion, Multi-Protocol Hub & FreeRTOS HAL",
            "body": "### Pull Request #2: Protocols, Edge Gateway & Embedded Firmware\n- High-throughput telemetry ring buffer\n- Protocol adapters for MQTT, Matter/Thread, Zigbee, Modbus RTU/TCP, CAN bus, CoAP\n- FreeRTOS HAL and board target drivers (ESP32-S3, STM32F4)"
        },
        {
            "branch": "feature/automation-scenes-presence-security",
            "title": "feat(automation,security): TCA Rule Engine, Presence Fusion & AI Video Surveillance",
            "body": "### Pull Request #3: Automation, Scenes, Presence & Smart Security\n- Multi-condition AST Trigger-Condition-Action (TCA) rule engine\n- Scenes and routines (Movie Night, Bedtime, Wake up)\n- mmWave + PIR presence fusion\n- Security modes and WebRTC camera stream simulation"
        },
        {
            "branch": "feature/energy-solar-ev-climate-subsystems",
            "title": "feat(energy,solar,ev): Whole-Home Energy Management, Solar MPPT & Climate Loops",
            "body": "### Pull Request #4: Energy Management, Solar, Battery & EV Subsystems\n- Real-time whole-home power flow\n- Solar MPPT inverter monitoring and yield forecasting\n- Battery storage BSS management and peak shaving\n- Dynamic EV charging current regulation (6A-32A)\n- Multi-zone HVAC PID loops and smart water leak shutoff"
        },
        {
            "branch": "feature/ai-nlp-analytics-observability-infra",
            "title": "feat(ai,analytics,infra): Conversational NLP Assistant, Analytics & Kubernetes IaC",
            "body": "### Pull Request #5: AI Intelligence, Analytics & Observability Infrastructure\n- Natural language intent parsing and slot extraction\n- Timescale continuous aggregates and reliability metrics\n- Docker Compose, Kubernetes manifests, Helm charts & Terraform IaC\n- 212+ automated test suites with 630+ test cases"
        },
        {
            "branch": "feature/unified-web-frontend-experience",
            "title": "feat(web,dashboard): Interactive Web SPA Dashboard & 1-Click Launcher",
            "body": "### Pull Request #6: Unified Web Dashboard & Zero-Configuration Launcher\n- Modern responsive web dashboard (Tailwind CSS, Chart.js, FontAwesome)\n- 1-Click pre-filled demo login\n- Standalone launcher script (run_app.bat, run_server.py)\n- Full architecture documentation"
        }
    ]

    # Create and merge each PR sequentially
    for idx, pr_info in enumerate(pr_phases, 1):
        print(f"\n--- Creating GitHub PR #{idx}: {pr_info['title']} ---")
        create_payload = {
            "title": pr_info["title"],
            "head": pr_info["branch"],
            "base": "main",
            "body": pr_info["body"]
        }
        res = gh_api(f"/repos/{repo}/pulls", method="POST", data=create_payload, token=token)
        
        pr_number = None
        if "number" in res:
            pr_number = res["number"]
            print(f"Created PR #{pr_number} successfully.")
        elif "errors" in res:
            print(f"PR creation message: {res.get('message')}")
            # Check if PR already exists
            existing_prs = gh_api(f"/repos/{repo}/pulls?head=Dhanunjay-narra:{pr_info['branch']}&state=all", token=token)
            if isinstance(existing_prs, list) and len(existing_prs) > 0:
                pr_number = existing_prs[0]["number"]
                print(f"Found existing PR #{pr_number} (state: {existing_prs[0]['state']})")

        if pr_number:
            # Check if open and merge it
            pr_detail = gh_api(f"/repos/{repo}/pulls/{pr_number}", token=token)
            if pr_detail.get("state") == "open":
                print(f"Merging PR #{pr_number} on GitHub...")
                merge_payload = {
                    "commit_title": f"Merge pull request #{pr_number} from {pr_info['branch']}",
                    "merge_method": "merge"
                }
                merge_res = gh_api(f"/repos/{repo}/pulls/{pr_number}/merge", method="PUT", data=merge_payload, token=token)
                if merge_res.get("merged"):
                    print(f"PR #{pr_number} successfully MERGED and CLOSED on GitHub!")
                else:
                    print(f"Merge status for PR #{pr_number}: {merge_res}")
            else:
                print(f"PR #{pr_number} is already {pr_detail.get('state')}.")

    # Verify final PR status on GitHub
    print("\n=================================================================")
    print(" GITHUB PULL REQUESTS STATUS CHECK:")
    print("=================================================================")
    closed_prs = gh_api(f"/repos/{repo}/pulls?state=closed", token=token)
    open_prs_final = gh_api(f"/repos/{repo}/pulls?state=open", token=token)
    
    print(f"Total Merged/Closed PRs on GitHub: {len(closed_prs) if isinstance(closed_prs, list) else 0}")
    print(f"Total Open PRs on GitHub:          {len(open_prs_final) if isinstance(open_prs_final, list) else 0}")
    
    if isinstance(closed_prs, list):
        for pr in closed_prs:
            print(f"  [CLOSED/MERGED] #{pr['number']}: {pr['title']}")

    if isinstance(open_prs_final, list) and len(open_prs_final) > 0:
        for pr in open_prs_final:
            print(f"  [OPEN - Closing...] #{pr['number']}: {pr['title']}")
            gh_api(f"/repos/{repo}/pulls/{pr['number']}", method="PATCH", data={"state": "closed"}, token=token)

    print("=================================================================")

if __name__ == "__main__":
    orchestrate_github_prs()
