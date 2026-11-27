from fastapi import APIRouter
from src.api.core.database import get_connection

router = APIRouter(
    prefix="/api/v1/clients",
    tags=["Client Analytics"],
)


@router.get("/overview")
def client_overview():
    conn = get_connection()

    try:
        rows = conn.execute("""
            SELECT
                client,
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

            GROUP BY client

            ORDER BY total_tickets DESC
        """).fetchall()

        return {
            "clients": [dict(row) for row in rows]
        }

    finally:
        conn.close()


@router.get("/sla")
def client_sla():
    conn = get_connection()

    try:
        rows = conn.execute("""
            SELECT
                client,

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

            GROUP BY client

        """).fetchall()

        results = []

        for row in rows:
            response_eligible = row["response_eligible"]
            response_met = row["response_met"] or 0

            resolution_eligible = row["resolution_eligible"]
            resolution_met = row["resolution_met"] or 0

            results.append({
                "client": row["client"],

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
            "clients": results
        }

    finally:
        conn.close()
@router.get("/services")
def client_service_analytics():
    conn = get_connection()

    try:
        rows = conn.execute("""
            SELECT
                client,
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
                    THEN 1 ELSE 0 END) AS closed_tickets,

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

            GROUP BY client, service

            ORDER BY client, service

        """).fetchall()

        results = []

        for row in rows:
            response_eligible = row["response_eligible"]
            response_met = row["response_met"] or 0

            resolution_eligible = row["resolution_eligible"]
            resolution_met = row["resolution_met"] or 0

            results.append({
                "client": row["client"],
                "service": row["service"],
                "total_tickets": row["total_tickets"],

                "status_distribution": {
                    "open": row["open_tickets"],
                    "in_progress": row["in_progress_tickets"],
                    "pending": row["pending_tickets"],
                    "resolved": row["resolved_tickets"],
                    "closed": row["closed_tickets"],
                },

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
            "client_service_analysis": results
        }

    finally:
        conn.close()