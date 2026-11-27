import sqlite3
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/prediction-history", tags=["Prediction History"])

ROOT_DIR = Path(__file__).resolve().parents[3]
DB_PATH = ROOT_DIR / "data" / "pulseops.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_history_table():
    conn = get_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS prediction_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            priority TEXT,
            client TEXT,
            service TEXT,
            category TEXT,
            subcategory TEXT,
            assigned_team TEXT,
            channel TEXT,
            created_hour INTEGER,
            created_day_of_week INTEGER,
            created_month INTEGER,
            sla_breach_probability REAL,
            risk_level TEXT,
            model TEXT,
            predicted_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


initialize_history_table()


class PredictionHistoryInput(BaseModel):
    priority: str
    client: str
    service: str
    category: str
    subcategory: str
    assigned_team: str
    channel: str
    created_hour: int
    created_day_of_week: int
    created_month: int
    sla_breach_probability: float
    risk_level: str
    model: str


@router.post("/")
def save_prediction(data: PredictionHistoryInput):
    conn = get_connection()

    try:
        cursor = conn.execute("""
            INSERT INTO prediction_history (
                priority,
                client,
                service,
                category,
                subcategory,
                assigned_team,
                channel,
                created_hour,
                created_day_of_week,
                created_month,
                sla_breach_probability,
                risk_level,
                model
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.priority,
            data.client,
            data.service,
            data.category,
            data.subcategory,
            data.assigned_team,
            data.channel,
            data.created_hour,
            data.created_day_of_week,
            data.created_month,
            data.sla_breach_probability,
            data.risk_level,
            data.model,
        ))

        conn.commit()

        return {
            "message": "Prediction saved successfully",
            "id": cursor.lastrowid,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        conn.close()


@router.get("/")
def get_prediction_history(limit: int = 100):
    conn = get_connection()

    try:
        rows = conn.execute("""
            SELECT *
            FROM prediction_history
            ORDER BY id DESC
            LIMIT ?
        """, (limit,)).fetchall()

        return {
            "total": len(rows),
            "predictions": [dict(row) for row in rows],
        }

    finally:
        conn.close()


@router.get("/summary")
def get_prediction_summary():
    conn = get_connection()

    try:
        total = conn.execute("""
            SELECT COUNT(*) FROM prediction_history
        """).fetchone()[0]

        high = conn.execute("""
            SELECT COUNT(*) FROM prediction_history
            WHERE risk_level = 'High'
        """).fetchone()[0]

        moderate = conn.execute("""
            SELECT COUNT(*) FROM prediction_history
            WHERE risk_level = 'Moderate'
        """).fetchone()[0]

        low = conn.execute("""
            SELECT COUNT(*) FROM prediction_history
            WHERE risk_level = 'Low'
        """).fetchone()[0]

        avg_probability = conn.execute("""
            SELECT AVG(sla_breach_probability)
            FROM prediction_history
        """).fetchone()[0]

        return {
            "total_predictions": total,
            "high_risk": high,
            "moderate_risk": moderate,
            "low_risk": low,
            "average_breach_probability": round(
                avg_probability or 0, 4
            ),
        }

    finally:
        conn.close()