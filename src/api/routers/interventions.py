from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from src.api.core.database import get_connection

router = APIRouter(prefix="/interventions", tags=["Interventions"])


class InterventionCreate(BaseModel):
    prediction_id: Optional[int] = None
    ticket_reference: Optional[str] = None
    priority: str
    client: str
    service: str
    assigned_team: str
    risk_level: str
    breach_probability: float
    action_taken: str
    owner: Optional[str] = None
    status: str = "Open"
    notes: Optional[str] = None


class InterventionUpdate(BaseModel):
    status: Optional[str] = None
    owner: Optional[str] = None
    notes: Optional[str] = None


@router.get("/")
def get_interventions():
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM interventions ORDER BY created_at DESC"
        ).fetchall()

        return {"interventions": [dict(row) for row in rows]}
    finally:
        conn.close()


@router.get("/summary")
def get_intervention_summary():
    conn = get_connection()
    try:
        total = conn.execute(
            "SELECT COUNT(*) FROM interventions"
        ).fetchone()[0]

        open_count = conn.execute(
            "SELECT COUNT(*) FROM interventions WHERE status = 'Open'"
        ).fetchone()[0]

        progress_count = conn.execute(
            "SELECT COUNT(*) FROM interventions WHERE status = 'In Progress'"
        ).fetchone()[0]

        completed_count = conn.execute(
            "SELECT COUNT(*) FROM interventions WHERE status = 'Completed'"
        ).fetchone()[0]

        return {
            "total": total,
            "open": open_count,
            "in_progress": progress_count,
            "completed": completed_count,
        }
    finally:
        conn.close()


@router.post("/")
def create_intervention(data: InterventionCreate):
    conn = get_connection()

    try:
        cursor = conn.execute(
            """
            INSERT INTO interventions (
                prediction_id,
                ticket_reference,
                priority,
                client,
                service,
                assigned_team,
                risk_level,
                breach_probability,
                action_taken,
                owner,
                status,
                notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data.prediction_id,
                data.ticket_reference,
                data.priority,
                data.client,
                data.service,
                data.assigned_team,
                data.risk_level,
                data.breach_probability,
                data.action_taken,
                data.owner,
                data.status,
                data.notes,
            ),
        )

        conn.commit()

        return {
            "message": "Intervention created successfully",
            "intervention_id": cursor.lastrowid,
        }

    finally:
        conn.close()


@router.put("/{intervention_id}")
def update_intervention(intervention_id: int, data: InterventionUpdate):
    conn = get_connection()

    try:
        existing = conn.execute(
            "SELECT * FROM interventions WHERE intervention_id = ?",
            (intervention_id,),
        ).fetchone()

        if not existing:
            raise HTTPException(
                status_code=404,
                detail="Intervention not found",
            )

        conn.execute(
            """
            UPDATE interventions
            SET
                status = COALESCE(?, status),
                owner = COALESCE(?, owner),
                notes = COALESCE(?, notes),
                updated_at = CURRENT_TIMESTAMP
            WHERE intervention_id = ?
            """,
            (
                data.status,
                data.owner,
                data.notes,
                intervention_id,
            ),
        )

        conn.commit()

        return {"message": "Intervention updated successfully"}

    finally:
        conn.close()


@router.delete("/{intervention_id}")
def delete_intervention(intervention_id: int):
    conn = get_connection()

    try:
        existing = conn.execute(
            "SELECT * FROM interventions WHERE intervention_id = ?",
            (intervention_id,),
        ).fetchone()

        if not existing:
            raise HTTPException(
                status_code=404,
                detail="Intervention not found",
            )

        conn.execute(
            "DELETE FROM interventions WHERE intervention_id = ?",
            (intervention_id,),
        )

        conn.commit()

        return {"message": "Intervention deleted successfully"}

    finally:
        conn.close()