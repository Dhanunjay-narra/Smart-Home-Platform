"""
Smart Home Platform — Database Inspector Script
Run this script anytime to inspect all data saved in data/smarthome.db
Usage: python check_db.py
"""

import sqlite3
from pathlib import Path

DB_PATH = Path("./data/smarthome.db")

def check_database():
    if not DB_PATH.exists():
        print(f"\n[ERROR] Database file not found at: {DB_PATH.resolve()}")
        print("Please run 'python run_server.py' first to initialize the database.")
        return

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print("\n" + "="*70)
    print("  SMART HOME PLATFORM — SQLITE DATABASE INSPECTION REPORT")
    print(f"  File Path: {DB_PATH.resolve()}")
    print("="*70)

    # 1. Users Table
    print("\n--- [1] SAVED USERS (users table) ---")
    cursor.execute("SELECT user_id, email, full_name, role, is_active, created_at FROM users")
    users = cursor.fetchall()
    if users:
        print(f"{'User ID':<18} | {'Email':<24} | {'Full Name':<28} | {'Role':<15}")
        print("-" * 90)
        for u in users:
            print(f"{u['user_id']:<18} | {u['email']:<24} | {u['full_name']:<28} | {u['role']:<15}")
    else:
        print("No users found.")

    # 2. Audit Logs Table
    print("\n--- [2] RECENT AUDIT LOGS (audit_logs table) ---")
    cursor.execute("SELECT log_id, timestamp, actor_name, action, target_resource, result FROM audit_logs ORDER BY timestamp DESC LIMIT 10")
    logs = cursor.fetchall()
    if logs:
        print(f"{'Timestamp':<25} | {'Actor':<15} | {'Action':<20} | {'Target':<20} | {'Result':<10}")
        print("-" * 95)
        for l in logs:
            ts = l['timestamp'][:19] if l['timestamp'] else ""
            print(f"{ts:<25} | {l['actor_name']:<15} | {l['action']:<20} | {l['target_resource']:<20} | {l['result']:<10}")
    else:
        print("No audit logs yet. Log in or perform an action on the dashboard to generate logs.")

    # 3. Devices Table
    print("\n--- [3] REGISTERED DEVICES (devices table) ---")
    cursor.execute("SELECT device_id, name, category, status, updated_at FROM devices")
    devices = cursor.fetchall()
    if devices:
        print(f"{'Device ID':<22} | {'Name':<24} | {'Category':<15} | {'Status':<10}")
        print("-" * 75)
        for d in devices:
            print(f"{d['device_id']:<22} | {d['name']:<24} | {d['category']:<15} | {d['status']:<10}")
    else:
        print("No devices stored in DB yet.")

    print("\n" + "="*70)
    print("  DATABASE STATUS: ONLINE & PERSISTING (OK)")
    print("="*70 + "\n")
    conn.close()

if __name__ == "__main__":
    check_database()

