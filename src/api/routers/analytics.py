from fastapi import APIRouter
from src.api.core.database import get_connection

router = APIRouter(
    prefix="/api/v1/analytics",
    tags=["Cross-Dimensional Analytics"],
)


@router.get("/team-priority")
def team_priority_analytics():
    conn = get_connection()

    try:
        rows = conn.execute("""
            SELECT
                assigned_team,
                priority,
                COUNT(*) AS total_tickets

            FROM tickets

            GROUP BY assigned_team, priority

            ORDER BY
                assigned_team,
                CASE priority
                    WHEN 'Critical' THEN 1
                    WHEN 'High' THEN 2
                    WHEN 'Medium' THEN 3
                    WHEN 'Low' THEN 4
                    ELSE 5
                END

        """).fetchall()

        return {
            "team_priority_analysis": [
                dict(row) for row in rows
            ]
        }

    finally:
        conn.close()
@router.get("/service-priority")
def service_priority_analytics():
    conn = get_connection()

    try:
        rows = conn.execute("""
            SELECT
                service,
                priority,
                COUNT(*) AS total_tickets

            FROM tickets

            GROUP BY service, priority

            ORDER BY
                service,
                CASE priority
                    WHEN 'Critical' THEN 1
                    WHEN 'High' THEN 2
                    WHEN 'Medium' THEN 3
                    WHEN 'Low' THEN 4
                    ELSE 5
                END

        """).fetchall()

        return {
            "service_priority_analysis": [
                dict(row) for row in rows
            ]
        }

    finally:
        conn.close()
@router.get("/client-priority")
def client_priority_analytics():
    conn = get_connection()

    try:
        rows = conn.execute("""
            SELECT
                client,
                priority,
                COUNT(*) AS total_tickets

            FROM tickets

            GROUP BY client, priority

            ORDER BY
                client,
                CASE priority
                    WHEN 'Critical' THEN 1
                    WHEN 'High' THEN 2
                    WHEN 'Medium' THEN 3
                    WHEN 'Low' THEN 4
                    ELSE 5
                END

        """).fetchall()

        return {
            "client_priority_analysis": [
                dict(row) for row in rows
            ]
        }

    finally:
        conn.close()

@router.get("/team-service-backlog")
def team_service_backlog():
    conn = get_connection()

    try:
        rows = conn.execute("""
            SELECT
                assigned_team,
                service,

                COUNT(*) AS backlog_tickets,

                SUM(CASE
                    WHEN priority IN ('Critical', 'High')
                    THEN 1 ELSE 0
                END) AS high_risk_backlog,

                SUM(CASE
                    WHEN priority = 'Critical'
                    THEN 1 ELSE 0
                END) AS critical_backlog,

                SUM(CASE
                    WHEN priority = 'High'
                    THEN 1 ELSE 0
                END) AS high_backlog,

                SUM(CASE
                    WHEN priority = 'Medium'
                    THEN 1 ELSE 0
                END) AS medium_backlog,

                SUM(CASE
                    WHEN priority = 'Low'
                    THEN 1 ELSE 0
                END) AS low_backlog

            FROM tickets

            WHERE status IN ('Open', 'In Progress', 'Pending')

            GROUP BY assigned_team, service

            ORDER BY high_risk_backlog DESC, backlog_tickets DESC

        """).fetchall()

        return {
            "team_service_backlog_analysis": [
                dict(row) for row in rows
            ]
        }

    finally:
        conn.close()

@router.get("/team-risk-scorecard")
def team_risk_scorecard():
    conn = get_connection()

    try:
        rows = conn.execute("""
            WITH team_metrics AS (
                SELECT
                    assigned_team,
                    COUNT(*) AS total_tickets,

                    SUM(CASE WHEN first_response_minutes IS NOT NULL
                        THEN 1 ELSE 0 END) AS response_eligible,

                    SUM(CASE WHEN first_response_minutes IS NOT NULL
                              AND response_sla_met = 1
                        THEN 1 ELSE 0 END) AS response_sla_met,

                    SUM(CASE WHEN resolved_at IS NOT NULL
                        THEN 1 ELSE 0 END) AS resolution_eligible,

                    SUM(CASE WHEN resolved_at IS NOT NULL
                              AND resolution_sla_met = 1
                        THEN 1 ELSE 0 END) AS resolution_sla_met,

                    SUM(is_reopened) AS reopened_tickets

                FROM tickets
                GROUP BY assigned_team
            ),

            backlog_metrics AS (
                SELECT
                    assigned_team,
                    COUNT(*) AS backlog_tickets,

                    SUM(CASE WHEN priority IN ('Critical', 'High')
                        THEN 1 ELSE 0 END) AS high_risk_backlog

                FROM tickets
                WHERE status IN ('Open', 'In Progress', 'Pending')
                GROUP BY assigned_team
            )

            SELECT
                t.*,
                COALESCE(b.backlog_tickets, 0) AS backlog_tickets,
                COALESCE(b.high_risk_backlog, 0) AS high_risk_backlog

            FROM team_metrics t
            LEFT JOIN backlog_metrics b
                ON t.assigned_team = b.assigned_team

            ORDER BY t.assigned_team
        """).fetchall()

        scorecard = []

        for row in rows:
            data = dict(row)

            response_rate = (
                data["response_sla_met"] / data["response_eligible"] * 100
                if data["response_eligible"] else 0
            )

            resolution_rate = (
                data["resolution_sla_met"] / data["resolution_eligible"] * 100
                if data["resolution_eligible"] else 0
            )

            reopen_rate = (
                data["reopened_tickets"] / data["total_tickets"] * 100
                if data["total_tickets"] else 0
            )

            high_risk_backlog_rate = (
                data["high_risk_backlog"] / data["backlog_tickets"] * 100
                if data["backlog_tickets"] else 0
            )

            risk_score = 0

            if response_rate < 30:
                risk_score += 1

            if resolution_rate < 22:
                risk_score += 1

            if reopen_rate > 15:
                risk_score += 1

            if high_risk_backlog_rate > 30:
                risk_score += 1

            if risk_score >= 3:
                risk_level = "High"
            elif risk_score == 2:
                risk_level = "Moderate"
            else:
                risk_level = "Low"

            scorecard.append({
                "assigned_team": data["assigned_team"],
                "total_tickets": data["total_tickets"],
                "response_sla_compliance": round(response_rate, 2),
                "resolution_sla_compliance": round(resolution_rate, 2),
                "reopen_rate": round(reopen_rate, 2),
                "backlog_tickets": data["backlog_tickets"],
                "high_risk_backlog": data["high_risk_backlog"],
                "high_risk_backlog_rate": round(
                    high_risk_backlog_rate, 2
                ),
                "risk_score": risk_score,
                "risk_level": risk_level
            })

        return {
            "team_risk_scorecard": scorecard,
            "scoring_note": (
                "Exploratory rule-based scorecard. "
                "Not a validated predictive model."
            )
        }

    finally:
        conn.close()