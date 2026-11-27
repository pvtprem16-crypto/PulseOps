import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATABASE_PATH = PROJECT_ROOT / "data" / "pulseops.db"


def get_connection():
    if not DATABASE_PATH.exists():
        raise FileNotFoundError(
            f"PulseOps database not found: {DATABASE_PATH}"
        )

    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row

    return conn
