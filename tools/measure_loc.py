"""
Smart Home Platform — LOC & Quality Metrics Analyzer
"""

import os
from pathlib import Path

EXTENSIONS = {'.py', '.js', '.jsx', '.ts', '.tsx', '.html', '.css', '.c', '.h', '.cpp', '.hpp', '.tf', '.yml', '.yaml', '.sql', '.md', '.json'}
EXCLUDE_DIRS = {'.git', '__pycache__', 'node_modules', '.pytest_cache', 'dist', 'build', '.venv', 'venv'}

def count_loc(root_dir="."):
    root = Path(root_dir).resolve()
    stats = {}
    total_loc = 0
    total_files = 0

    for current, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for f in files:
            p = Path(current) / f
            if p.suffix in EXTENSIONS:
                try:
                    with open(p, 'r', encoding='utf-8', errors='ignore') as fp:
                        lines = len([l for l in fp.readlines() if l.strip()])
                        stats[p.suffix] = stats.get(p.suffix, 0) + lines
                        total_loc += lines
                        total_files += 1
                except Exception:
                    pass

    print("==================================================")
    print(" Smart Home Platform — Codebase Measurement")
    print("==================================================")
    print(f" Total Source Files: {total_files}")
    print(f" Total Meaningful LOC: {total_loc:,}")
    print(" Breakdown by Language/Type:")
    for ext, cnt in sorted(stats.items(), key=lambda x: x[1], reverse=True):
        print(f"   {ext:<8}: {cnt:,} LOC")
    print("==================================================")
    return total_loc

if __name__ == "__main__":
    count_loc()
