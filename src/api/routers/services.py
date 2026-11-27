from fastapi import APIRouter
from src.api.core.database import get_connection

router = APIRouter(
    prefix="/api/v1/services",
    tags=["Service Analytics"],
)

@router.get("/overview")
def service_overview():
    conn = get_connection()

    try:
        rows = conn.execute("""
            SELECT
                service,
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

            GROUP BY service

            ORDER BY total_tickets DESC
        """).fetchall()

        return {
            "services": [dict(row) for row in rows]
        }

    finally:
        conn.close()

@router.get("/sla")
def service_sla():
    conn = get_connection()

    try:
        rows = conn.execute("""
            SELECT
                service,

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

            GROUP BY service

        """).fetchall()

        results = []

        for row in rows:
            response_eligible = row["response_eligible"]
            response_met = row["response_met"] or 0

            resolution_eligible = row["resolution_eligible"]
            resolution_met = row["resolution_met"] or 0

            results.append({
                "service": row["service"],

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
            "services": results
        }

    finally:
        conn.close()
