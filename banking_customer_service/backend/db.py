import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "banking.db"
SCHEMA_TEXT = (Path(__file__).parent / "schema.sql").read_text()


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.executescript(SCHEMA_TEXT)
