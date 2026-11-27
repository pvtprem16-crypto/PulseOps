from fastapi import APIRouter
from src.api.core.database import get_connection

router = APIRouter(
    prefix="/api/v1/sla",
    tags=["SLA Analytics"],
)


@router.get("/by-priority")
def sla_by_priority():
    conn = get_connection()

    try:
        rows = conn.execute("""
            SELECT
                priority,

                COUNT(response_sla_met)
                    AS response_eligible,

                SUM(
                    CASE
                        WHEN response_sla_met = 1
                        THEN 1 ELSE 0
                    END
                ) AS response_met,

                COUNT(resolution_sla_met)
                    AS resolution_eligible,

                SUM(
                    CASE
                        WHEN resolution_sla_met = 1
                        THEN 1 ELSE 0
                    END
                ) AS resolution_met

            FROM tickets
            GROUP BY priority

        """).fetchall()

        priority_order = {
            "Critical": 1,
            "High": 2,
            "Medium": 3,
            "Low": 4,
        }

        results = []

        for row in rows:
            response_eligible = row["response_eligible"]
            response_met = row["response_met"] or 0

            resolution_eligible = row["resolution_eligible"]
            resolution_met = row["resolution_met"] or 0

            response_compliance = (
                response_met / response_eligible * 100
                if response_eligible else 0
            )

            resolution_compliance = (
                resolution_met / resolution_eligible * 100
                if resolution_eligible else 0
            )

            results.append({
                "priority": row["priority"],

                "response_sla": {
                    "eligible_tickets": response_eligible,
                    "met_tickets": response_met,
                    "breached_tickets": (
                        response_eligible - response_met
                    ),
                    "compliance_percent": round(
                        response_compliance, 2
                    ),
                },

                "resolution_sla": {
                    "eligible_tickets": resolution_eligible,
                    "met_tickets": resolution_met,
                    "breached_tickets": (
                        resolution_eligible - resolution_met
                    ),
                    "compliance_percent": round(
                        resolution_compliance, 2
                    ),
                },
            })

        results.sort(
            key=lambda item: priority_order.get(
                item["priority"], 99
            )
        )

        return {
            "priorities": results
        }

    finally:
        conn.close()


@router.get("/summary")
def sla_summary():
    conn = get_connection()

    try:
        row = conn.execute("""
            SELECT
                COUNT(response_sla_met)
                    AS response_eligible,

                SUM(
                    CASE
                        WHEN response_sla_met = 1
                        THEN 1 ELSE 0
                    END
                ) AS response_met,

                COUNT(resolution_sla_met)
                    AS resolution_eligible,

                SUM(
                    CASE
                        WHEN resolution_sla_met = 1
                        THEN 1 ELSE 0
                    END
                ) AS resolution_met

            FROM tickets
        """).fetchone()

        response_eligible = row["response_eligible"]
        response_met = row["response_met"] or 0

        resolution_eligible = row["resolution_eligible"]
        resolution_met = row["resolution_met"] or 0

        return {
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
        }

    finally:
        conn.close()
