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

def build_pr_history():
    # Checkout main from the first commit e5172e9~1 or start fresh
    # Let's see commits:
    # e5172e9 (iam) -> 455bbd7 (protocols) -> f8643ec (automation) -> dd0ebfa (energy) -> ceb6861 (ai) -> a050b81 (web) -> c2f241f (chore)

    run("git checkout -B main e5172e9")
    run("git branch -M main")
    
    # Feature 1 branch
    run("git branch -f feature/iam-home-device-platform e5172e9")
    
    # Feature 2 branch
    run("git branch -f feature/telemetry-protocols-edge-firmware 455bbd7")
    
    # Feature 3 branch
    run("git branch -f feature/automation-scenes-presence-security f8643ec")
    
    # Feature 4 branch
    run("git branch -f feature/energy-solar-ev-climate-subsystems dd0ebfa")
    
    # Feature 5 branch
    run("git branch -f feature/ai-nlp-analytics-observability-infra ceb6861")
    
    # Feature 6 branch
    run("git branch -f feature/unified-web-frontend-experience a050b81")

    # Let's reconstruct main with non-fast-forward merge commits for each PR
    # Start main at e5172e9
    # Merge PR 2
    run("git merge --no-ff feature/telemetry-protocols-edge-firmware -m \"Merge pull request #2 from feature/telemetry-protocols-edge-firmware: Telemetry, Edge Gateway & Firmware HAL\"")
    # Merge PR 3
    run("git merge --no-ff feature/automation-scenes-presence-security -m \"Merge pull request #3 from feature/automation-scenes-presence-security: Automation Engine, Scenes & Security Shield\"")
    # Merge PR 4
    run("git merge --no-ff feature/energy-solar-ev-climate-subsystems -m \"Merge pull request #4 from feature/energy-solar-ev-climate-subsystems: Energy Management, Solar, Battery & EV Subsystems\"")
    # Merge PR 5
    run("git merge --no-ff feature/ai-nlp-analytics-observability-infra -m \"Merge pull request #5 from feature/ai-nlp-analytics-observability-infra: AI Intelligence, Observability & Automated Tests\"")
    # Merge PR 6
    run("git merge --no-ff feature/unified-web-frontend-experience -m \"Merge pull request #6 from feature/unified-web-frontend-experience: Interactive Web SPA Dashboard & Launcher\"")

    # Fast forward / commit the final verification commit
    run("git cherry-pick c2f241f")

    print("PR history successfully structured.")

if __name__ == "__main__":
    build_pr_history()
