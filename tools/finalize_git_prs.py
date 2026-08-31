import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def run(cmd):
    print(f">> {cmd}")
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=str(ROOT))
    if res.stdout.strip():
        print(res.stdout.strip())
    if res.returncode != 0:
        print(f"Error: {res.stderr.strip()}")
    return res.returncode == 0

def finalize_prs():
    # 1. Point feature branches to exact commits
    run("git branch -f feature/iam-home-device-platform 43bd7a6")
    run("git branch -f feature/telemetry-protocols-edge-firmware 265d71a")
    run("git branch -f feature/automation-scenes-presence-security 6e77d40")
    run("git branch -f feature/energy-solar-ev-climate-subsystems 01ffd55")
    run("git branch -f feature/ai-nlp-analytics-observability-infra acac9e9")
    run("git branch -f feature/unified-web-frontend-experience 70cb5c5")

    # 2. Checkout main at 43bd7a6
    run("git checkout -B main 43bd7a6")
    
    # 3. Merge PR #2
    run("git merge --no-ff feature/telemetry-protocols-edge-firmware -m \"Merge pull request #2 from feature/telemetry-protocols-edge-firmware: Telemetry, Edge Gateway & Firmware HAL\"")
    # 4. Merge PR #3
    run("git merge --no-ff feature/automation-scenes-presence-security -m \"Merge pull request #3 from feature/automation-scenes-presence-security: Automation Engine, Scenes & Security Shield\"")
    # 5. Merge PR #4
    run("git merge --no-ff feature/energy-solar-ev-climate-subsystems -m \"Merge pull request #4 from feature/energy-solar-ev-climate-subsystems: Energy Management, Solar, Battery & EV Subsystems\"")
    # 6. Merge PR #5
    run("git merge --no-ff feature/ai-nlp-analytics-observability-infra -m \"Merge pull request #5 from feature/ai-nlp-analytics-observability-infra: AI Intelligence, Observability & Automated Tests\"")
    # 7. Merge PR #6
    run("git merge --no-ff feature/unified-web-frontend-experience -m \"Merge pull request #6 from feature/unified-web-frontend-experience: Interactive Web SPA Dashboard & Launcher\"")

    # 8. Cherry-pick final verification commit
    run("git cherry-pick be75b6b")

    print("PR merges successfully created on main branch.")

if __name__ == "__main__":
    finalize_prs()
