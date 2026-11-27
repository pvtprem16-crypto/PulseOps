from fastapi import APIRouter
from src.api.core.database import get_connection

router = APIRouter(
    prefix="/api/v1/dashboard",
    tags=["Dashboard"],
)


@router.get("/overview")
def dashboard_overview():
    conn = get_connection()

    try:
        cursor = conn.cursor()

        overview = cursor.execute("""
            SELECT
                COUNT(*) AS total_tickets,

                SUM(
                    CASE
                        WHEN status IN ('Open', 'In Progress', 'Pending')
                        THEN 1 ELSE 0
                    END
                ) AS backlog_tickets,

                SUM(is_reopened) AS reopened_tickets,

                AVG(first_response_minutes)
                    AS avg_response_minutes,

                AVG(resolution_minutes)
                    AS avg_resolution_minutes,

                COUNT(response_sla_met)
                    AS response_sla_eligible,

                SUM(
                    CASE
                        WHEN response_sla_met = 1
                        THEN 1 ELSE 0
                    END
                ) AS response_sla_met,

                COUNT(resolution_sla_met)
                    AS resolution_sla_eligible,

                SUM(
                    CASE
                        WHEN resolution_sla_met = 1
                        THEN 1 ELSE 0
                    END
                ) AS resolution_sla_met

            FROM tickets
        """).fetchone()

        total_tickets = overview["total_tickets"]
        reopened_tickets = overview["reopened_tickets"] or 0

        response_eligible = overview["response_sla_eligible"]
        response_met = overview["response_sla_met"] or 0

        resolution_eligible = overview["resolution_sla_eligible"]
        resolution_met = overview["resolution_sla_met"] or 0

        reopen_rate = (
            (reopened_tickets / total_tickets) * 100
            if total_tickets else 0
        )

        response_compliance = (
            (response_met / response_eligible) * 100
            if response_eligible else 0
        )

        resolution_compliance = (
            (resolution_met / resolution_eligible) * 100
            if resolution_eligible else 0
        )

        return {
            "total_tickets": total_tickets,
            "backlog_tickets": overview["backlog_tickets"],
            "reopened_tickets": reopened_tickets,
            "reopen_rate_percent": round(reopen_rate, 2),

            "response_sla": {
                "eligible_tickets": response_eligible,
                "met_tickets": response_met,
                "compliance_percent": round(
                    response_compliance, 2
                ),
            },

            "resolution_sla": {
                "eligible_tickets": resolution_eligible,
                "met_tickets": resolution_met,
                "compliance_percent": round(
                    resolution_compliance, 2
                ),
            },

            "avg_response_minutes": round(
                overview["avg_response_minutes"] or 0, 2
            ),

            "avg_resolution_minutes": round(
                overview["avg_resolution_minutes"] or 0, 2
            ),
        }

    finally:
        conn.close()
