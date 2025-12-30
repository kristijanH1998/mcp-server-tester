import sqlite3
import json
from pathlib import Path
from datetime import datetime
import os

DB_PATH = Path(os.getenv("DB_PATH", "data.db"))

def get_conn():
    return sqlite3.connect(DB_PATH)

def init_db():
    with get_conn() as conn:
        cur = conn.cursor()

        cur.execute("""
        CREATE TABLE IF NOT EXISTS servers (
            id TEXT PRIMARY KEY,
            url TEXT NOT NULL,
            created_at TEXT
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS experiments (
            id TEXT PRIMARY KEY,
            server_id TEXT,
            tool TEXT,
            arguments TEXT,
            iterations INTEGER,
            avg_ms REAL,
            errors INTEGER,
            timings_ms TEXT,
            responses TEXT,
            created_at TEXT
        )
        """)

        conn.commit()
