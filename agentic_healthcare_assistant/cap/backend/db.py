"""SQLite connection + schema for the Agentic Healthcare Assistant.

A single SQLite database holds the patient table plus the doctor and
appointment tables (the appointment data mirrors the external scheduling API).
"""

import os
import sqlite3
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = Path(os.environ.get("HEALTHCARE_DB_PATH", REPO_ROOT / "data" / "app.db"))

SCHEMA = """
CREATE TABLE IF NOT EXISTS patients (
    id          TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    age         INTEGER,
    sex         TEXT,
    summary     TEXT,
    diagnoses   TEXT,   -- JSON list of {condition, since}
    medications TEXT,   -- JSON list of strings
    allergies   TEXT,   -- JSON list of strings
    alerts      TEXT,   -- JSON list of strings
    visits      TEXT    -- JSON list of {date, provider, note} (unstructured notes)
);

CREATE TABLE IF NOT EXISTS doctors (
    id          TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    specialty   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS appointments (
    id          TEXT PRIMARY KEY,
    patient_id  TEXT NOT NULL REFERENCES patients(id),
    doctor_id   TEXT NOT NULL REFERENCES doctors(id),
    start_ts    TEXT NOT NULL,   -- ISO 8601
    end_ts      TEXT NOT NULL,   -- ISO 8601
    status      TEXT NOT NULL DEFAULT 'booked',
    reason      TEXT
);
"""


def get_connection() -> sqlite3.Connection:
    """Open a connection with row access by column name and FK enforcement."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    """Create tables if they do not already exist."""
    with get_connection() as conn:
        conn.executescript(SCHEMA)
