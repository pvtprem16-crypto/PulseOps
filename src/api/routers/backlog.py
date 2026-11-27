from fastapi import APIRouter
from src.api.core.database import get_connection

router = APIRouter(
    prefix="/api/v1/backlog",
    tags=["Backlog Analytics"],
)

REPORTING_CUTOFF = "2026-11-25 23:59:59"
BACKLOG_STATUSES = ("Open", "In Progress", "Pending")


@router.get("/overview")
def backlog_overview():
    conn = get_connection()

    try:
        row = conn.execute("""
            SELECT
                COUNT(*) AS backlog_tickets,

                ROUND(
                    AVG(
                        (julianday(?) - julianday(created_at))
                    ),
                    2
                ) AS avg_age_days,

                ROUND(
                    MAX(
                        (julianday(?) - julianday(created_at))
                    ),
                    2
                ) AS max_age_days

            FROM tickets
            WHERE status IN ('Open', 'In Progress', 'Pending')
        """, (REPORTING_CUTOFF, REPORTING_CUTOFF)).fetchone()

        return {
            "reporting_cutoff": REPORTING_CUTOFF,
            "backlog_tickets": row["backlog_tickets"],
            "avg_age_days": row["avg_age_days"],
            "max_age_days": row["max_age_days"],
        }

    finally:
        conn.close()


@router.get("/aging")
def backlog_aging():
    conn = get_connection()

    try:
        rows = conn.execute("""
            SELECT
                CASE
                    WHEN age_days < 3 THEN '0-2 Days'
                    WHEN age_days < 7 THEN '3-6 Days'
                    WHEN age_days < 14 THEN '7-13 Days'
                    WHEN age_days < 30 THEN '14-29 Days'
                    ELSE '30+ Days'
                END AS aging_bucket,

                COUNT(*) AS ticket_count

            FROM (
                SELECT
                    julianday(?) - julianday(created_at)
                    AS age_days

                FROM tickets

                WHERE status IN (
                    'Open', 'In Progress', 'Pending'
                )
            )

            GROUP BY aging_bucket

        """, (REPORTING_CUTOFF,)).fetchall()

        bucket_order = {
            "0-2 Days": 1,
            "3-6 Days": 2,
            "7-13 Days": 3,
            "14-29 Days": 4,
            "30+ Days": 5,
        }

        results = [
            {
                "aging_bucket": row["aging_bucket"],
                "ticket_count": row["ticket_count"],
            }
            for row in rows
        ]

        results.sort(
            key=lambda item: bucket_order[item["aging_bucket"]]
        )

        return {
            "reporting_cutoff": REPORTING_CUTOFF,
            "aging_buckets": results,
        }

    finally:
        conn.close()


@router.get("/by-priority")
def backlog_by_priority():
    conn = get_connection()

    try:
        rows = conn.execute("""
            SELECT
                priority,
                COUNT(*) AS backlog_tickets,

                ROUND(
                    AVG(
                        julianday(?) - julianday(created_at)
                    ),
                    2
                ) AS avg_age_days

            FROM tickets

            WHERE status IN (
                'Open', 'In Progress', 'Pending'
            )

            GROUP BY priority

        """, (REPORTING_CUTOFF,)).fetchall()

        priority_order = {
            "Critical": 1,
            "High": 2,
            "Medium": 3,
            "Low": 4,
        }

        results = [
            {
                "priority": row["priority"],
                "backlog_tickets": row["backlog_tickets"],
                "avg_age_days": row["avg_age_days"],
            }
            for row in rows
        ]

        results.sort(
            key=lambda item: priority_order.get(
                item["priority"], 99
            )
        )

        return {
            "reporting_cutoff": REPORTING_CUTOFF,
            "priorities": results,
        }

    finally:
        conn.close()


@router.get("/by-status")
def backlog_by_status():
    conn = get_connection()

    try:
        rows = conn.execute("""
            SELECT
                status,
                COUNT(*) AS backlog_tickets,

                ROUND(
                    AVG(
                        julianday(?) - julianday(created_at)
                    ),
                    2
                ) AS avg_age_days

            FROM tickets

            WHERE status IN (
                'Open', 'In Progress', 'Pending'
            )

            GROUP BY status

        """, (REPORTING_CUTOFF,)).fetchall()

        status_order = {
            "Open": 1,
            "In Progress": 2,
            "Pending": 3,
        }

        results = [
            {
                "status": row["status"],
                "backlog_tickets": row["backlog_tickets"],
                "avg_age_days": row["avg_age_days"],
            }
            for row in rows
        ]

        results.sort(
            key=lambda item: status_order[item["status"]]
        )

        return {
            "reporting_cutoff": REPORTING_CUTOFF,
            "statuses": results,
        }

    finally:
        conn.close()


@router.get("/oldest")
def oldest_backlog_tickets(limit: int = 20):
    if limit < 1 or limit > 100:
        return {
            "error": "Limit must be between 1 and 100"
        }

    conn = get_connection()

    try:
        rows = conn.execute("""
            SELECT
                ticket_id,
                client,
                service,
                priority,
                status,
                assigned_team,
                created_at,

                ROUND(
                    julianday(?) - julianday(created_at),
                    2
                ) AS age_days

            FROM tickets

            WHERE status IN (
                'Open', 'In Progress', 'Pending'
            )

            ORDER BY age_days DESC

            LIMIT ?

        """, (REPORTING_CUTOFF, limit)).fetchall()

        return {
            "reporting_cutoff": REPORTING_CUTOFF,
            "limit": limit,
            "tickets": [
                dict(row) for row in rows
            ],
        }

    finally:
        conn.close()

