from fastapi import APIRouter
from src.api.core.database import get_connection

router = APIRouter(
    prefix="/api/v1/teams",
    tags=["Team Analytics"],
)


@router.get("/overview")
def team_overview():
    conn = get_connection()

    try:
        rows = conn.execute("""
            SELECT
                assigned_team,
                COUNT(*) AS total_tickets,

                SUM(CASE WHEN status = 'Open'
                    THEN 1 ELSE 0 END) AS open_tickets,

                SUM(CASE WHEN status = 'In Progress'
                    THEN 1 ELSE 0 END) AS in_progress_tickets,

                SUM(CASE WHEN status = 'Pending'
                    THEN 1 ELSE 0 END) AS pending_tickets,

                SUM(CASE WHEN status = 'Resolved'
                    THEN 1 ELSE 0 END) AS resolved_tickets,

                SUM(CASE WHEN status = 'Closed'
                    THEN 1 ELSE 0 END) AS closed_tickets

            FROM tickets
            GROUP BY assigned_team
            ORDER BY total_tickets DESC
        """).fetchall()

        return {
            "teams": [dict(row) for row in rows]
        }

    finally:
        conn.close()


@router.get("/sla")
def team_sla():
    conn = get_connection()

    try:
        rows = conn.execute("""
            SELECT
                assigned_team,

                COUNT(response_sla_met)
                    AS response_eligible,

                SUM(CASE
                    WHEN response_sla_met = 1
                    THEN 1 ELSE 0
                END) AS response_met,

                COUNT(resolution_sla_met)
                    AS resolution_eligible,

                SUM(CASE
                    WHEN resolution_sla_met = 1
                    THEN 1 ELSE 0
                END) AS resolution_met

            FROM tickets
            GROUP BY assigned_team

        """).fetchall()

        results = []

        for row in rows:
            response_eligible = row["response_eligible"]
            response_met = row["response_met"] or 0

            resolution_eligible = row["resolution_eligible"]
            resolution_met = row["resolution_met"] or 0

            results.append({
                "assigned_team": row["assigned_team"],

                "response_sla": {
                    "eligible_tickets": response_eligible,
                    "met_tickets": response_met,
                    "breached_tickets": (
                        response_eligible - response_met
                    ),
                    "compliance_percent": round(
                        response_met / response_eligible * 100,
                        2
                    ) if response_eligible else 0,
                },

                "resolution_sla": {
                    "eligible_tickets": resolution_eligible,
                    "met_tickets": resolution_met,
                    "breached_tickets": (
                        resolution_eligible - resolution_met
                    ),
                    "compliance_percent": round(
                        resolution_met / resolution_eligible * 100,
                        2
                    ) if resolution_eligible else 0,
                },
            })

        return {
            "teams": results
        }

    finally:
        conn.close()


@router.get("/times")
def team_times():
    conn = get_connection()

    try:
        rows = conn.execute("""
            SELECT
                assigned_team,

                ROUND(
                    AVG(first_response_minutes), 2
                ) AS avg_response_minutes,

                ROUND(
                    AVG(resolution_minutes), 2
                ) AS avg_resolution_minutes

            FROM tickets

            GROUP BY assigned_team

            ORDER BY avg_resolution_minutes DESC
        """).fetchall()

        return {
            "teams": [dict(row) for row in rows]
        }

    finally:
        conn.close()


@router.get("/reopens")
def team_reopens():
    conn = get_connection()

    try:
        rows = conn.execute("""
            SELECT
                assigned_team,
                COUNT(*) AS total_tickets,

                SUM(
                    CASE
                        WHEN is_reopened = 1
                        THEN 1 ELSE 0
                    END
                ) AS reopened_tickets

            FROM tickets

            GROUP BY assigned_team

        """).fetchall()

        results = []

        for row in rows:
            total = row["total_tickets"]
            reopened = row["reopened_tickets"] or 0

            results.append({
                "assigned_team": row["assigned_team"],
                "total_tickets": total,
                "reopened_tickets": reopened,
                "reopen_rate_percent": round(
                    reopened / total * 100, 2
                ) if total else 0,
            })

        results.sort(
            key=lambda item: item["reopen_rate_percent"],
            reverse=True
        )

        return {
            "teams": results
        }

    finally:
        conn.close()
