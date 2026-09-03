"""
Smart Home Platform — SQLite Persistent Database Engine
Handles schema creation, connection lifecycle, and persistent record synchronization.
"""

import sqlite3
import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

DB_DIR = Path("./data")
DB_PATH = DB_DIR / "smarthome.db"

def get_connection() -> sqlite3.Connection:
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database tables and indexes on disk."""
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = get_connection()
    try:
        cursor = conn.cursor()
        
        # 1. Users Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                full_name TEXT NOT NULL,
                phone_number TEXT,
                role TEXT NOT NULL,
                hashed_password TEXT NOT NULL,
                is_active INTEGER DEFAULT 1,
                created_at TEXT NOT NULL
            )
        """)

        # 2. Devices Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS devices (
                device_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                room_id TEXT,
                category TEXT NOT NULL,
                protocol TEXT NOT NULL,
                status TEXT NOT NULL,
                traits_json TEXT NOT NULL,
                state_json TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        # 3. Automation Rules Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rules (
                rule_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                trigger_type TEXT NOT NULL,
                trigger_config_json TEXT NOT NULL,
                conditions_json TEXT NOT NULL,
                actions_json TEXT NOT NULL,
                is_enabled INTEGER DEFAULT 1,
                priority INTEGER DEFAULT 50,
                updated_at TEXT NOT NULL
            )
        """)

        # 4. Preset Scenes Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scenes (
                scene_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                icon TEXT,
                actions_json TEXT NOT NULL
            )
        """)

        # 5. Audit Logs Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                log_id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                actor_id TEXT NOT NULL,
                actor_name TEXT NOT NULL,
                action TEXT NOT NULL,
                target_resource TEXT NOT NULL,
                ip_address TEXT,
                result TEXT NOT NULL,
                details_json TEXT
            )
        """)

        conn.commit()
    finally:
        conn.close()

# =====================================================================
# Persistence Helper Functions
# =====================================================================

def db_save_user(user: Any):
    """Save or update user record in SQLite."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (user_id, email, full_name, phone_number, role, hashed_password, is_active, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(email) DO UPDATE SET
                full_name=excluded.full_name,
                hashed_password=excluded.hashed_password,
                role=excluded.role,
                is_active=excluded.is_active
        """, (
            user.user_id,
            user.email.lower(),
            user.full_name,
            getattr(user, 'phone_number', '+1-555-0100'),
            user.role.value if hasattr(user.role, 'value') else str(user.role),
            user.hashed_password,
            1 if getattr(user, 'is_active', True) else 0,
            getattr(user, 'created_at', datetime.now(timezone.utc)).isoformat()
        ))
        conn.commit()
    finally:
        conn.close()

def db_load_users() -> List[Dict[str, Any]]:
    """Load all saved users from SQLite."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()

def db_save_device(device: Any):
    """Save or update device state in SQLite."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        traits_json = json.dumps([t.value if hasattr(t, 'value') else str(t) for t in getattr(device, 'traits', [])])
        state_json = json.dumps(getattr(device, 'state', {}))
        cursor.execute("""
            INSERT INTO devices (device_id, name, room_id, category, protocol, status, traits_json, state_json, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(device_id) DO UPDATE SET
                status=excluded.status,
                state_json=excluded.state_json,
                updated_at=excluded.updated_at
        """, (
            device.device_id,
            device.name,
            getattr(device, 'room_id', 'room-living'),
            device.category.value if hasattr(device.category, 'value') else str(device.category),
            device.protocol.value if hasattr(device.protocol, 'value') else str(device.protocol),
            device.status.value if hasattr(device.status, 'value') else str(device.status),
            traits_json,
            state_json,
            datetime.now(timezone.utc).isoformat()
        ))
        conn.commit()
    finally:
        conn.close()

def db_save_audit_log(log: Any):
    """Save an audit log entry in SQLite."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO audit_logs (log_id, timestamp, actor_id, actor_name, action, target_resource, ip_address, result, details_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            getattr(log, 'log_id', f"log-{int(datetime.now().timestamp()*1000)}"),
            getattr(log, 'timestamp', datetime.now(timezone.utc)).isoformat() if hasattr(getattr(log, 'timestamp', None), 'isoformat') else str(getattr(log, 'timestamp', datetime.now(timezone.utc))),
            getattr(log, 'actor_id', 'system'),
            getattr(log, 'actor_name', 'System'),
            getattr(log, 'action', 'ACTION'),
            getattr(log, 'target_resource', 'resource'),
            getattr(log, 'ip_address', '127.0.0.1'),
            getattr(log, 'result', 'SUCCESS'),
            json.dumps(getattr(log, 'details', {}))
        ))
        conn.commit()
    finally:
        conn.close()

