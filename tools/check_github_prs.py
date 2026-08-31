import subprocess
import urllib.request
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def check():
    p = subprocess.Popen(["git", "credential", "fill"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, cwd=str(ROOT))
    out, _ = p.communicate("protocol=https\nhost=github.com\n")
    token = None
    for line in out.splitlines():
        if line.startswith("password="):
            token = line.split("=", 1)[1].strip()

    repo = "Dhanunjay-narra/Smart-Home-Platform"
    req = urllib.request.Request(
        f"https://api.github.com/repos/{repo}/pulls?state=all",
        headers={"Authorization": f"Bearer {token}", "User-Agent": "checker", "Accept": "application/vnd.github+json"}
    )
    with urllib.request.urlopen(req) as res:
        prs = json.loads(res.read().decode('utf-8'))
        print("=================================================================")
        print(f" Total PRs on GitHub: {len(prs)}")
        print("=================================================================")
        for pr in prs:
            print(f" PR #{pr['number']} [{pr['state'].upper()}] (Merged: {pr.get('merged_at') is not None}) - {pr['title']}")
        print("=================================================================")

if __name__ == "__main__":
    check()
