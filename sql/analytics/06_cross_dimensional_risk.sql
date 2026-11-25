-- ============================================================
-- PulseOps | Phase 4.6: Cross-Dimensional & Risk Analytics
-- ============================================================


-- 1. Priority distribution by team
SELECT
    assigned_team,
    priority,
    COUNT(*) AS total_tickets,
    SUM(CASE WHEN status IN ('Open', 'In Progress', 'Pending')
             THEN 1 ELSE 0 END) AS backlog_tickets,
    SUM(CASE WHEN status IN ('Resolved', 'Closed')
             THEN 1 ELSE 0 END) AS completed_tickets
FROM tickets
GROUP BY assigned_team, priority
ORDER BY assigned_team, priority;


-- 2. Priority distribution by service
SELECT
    service,
    priority,
    COUNT(*) AS total_tickets,
    SUM(CASE WHEN status IN ('Open', 'In Progress', 'Pending')
             THEN 1 ELSE 0 END) AS backlog_tickets
FROM tickets
GROUP BY service, priority
ORDER BY service, priority;


-- 3. Priority distribution by client
SELECT
    client,
    priority,
    COUNT(*) AS total_tickets,
    SUM(CASE WHEN status IN ('Open', 'In Progress', 'Pending')
             THEN 1 ELSE 0 END) AS backlog_tickets
FROM tickets
GROUP BY client, priority
ORDER BY client, priority;


-- 4. SLA performance hotspots by service and priority
SELECT
    service,
    priority,

    COUNT(response_sla_met) AS response_eligible,
    SUM(response_sla_met) AS response_sla_met,
    COUNT(response_sla_met) - SUM(response_sla_met)
        AS response_sla_breached,
    ROUND(
        100.0 * SUM(response_sla_met) /
        NULLIF(COUNT(response_sla_met), 0),
        2
    ) AS response_compliance_pct,

    COUNT(resolution_sla_met) AS resolution_eligible,
    SUM(resolution_sla_met) AS resolution_sla_met,
    COUNT(resolution_sla_met) - SUM(resolution_sla_met)
        AS resolution_sla_breached,
    ROUND(
        100.0 * SUM(resolution_sla_met) /
        NULLIF(COUNT(resolution_sla_met), 0),
        2
    ) AS resolution_compliance_pct

FROM tickets
GROUP BY service, priority
ORDER BY resolution_compliance_pct ASC;


-- 5. High-priority backlog hotspots by team and service
SELECT
    assigned_team,
    service,
    COUNT(*) AS total_backlog,
    SUM(CASE WHEN priority = 'Critical' THEN 1 ELSE 0 END)
        AS critical_backlog,
    SUM(CASE WHEN priority = 'High' THEN 1 ELSE 0 END)
        AS high_backlog,
    SUM(CASE WHEN priority IN ('Critical', 'High')
             THEN 1 ELSE 0 END) AS high_risk_backlog,
    ROUND(
        100.0 * SUM(CASE WHEN priority IN ('Critical', 'High')
                          THEN 1 ELSE 0 END) / COUNT(*),
        2
    ) AS high_risk_backlog_pct
FROM tickets
WHERE status IN ('Open', 'In Progress', 'Pending')
GROUP BY assigned_team, service
ORDER BY high_risk_backlog DESC, high_risk_backlog_pct DESC;


-- 6. Exploratory team operational risk scorecard
-- Each indicator contributes 1 point.
-- Score range: 0 to 4.
-- This is an exploratory rule-based score, NOT a validated risk model.

WITH team_metrics AS (
    SELECT
        assigned_team,

        COUNT(*) AS total_tickets,

        COUNT(response_sla_met) AS response_eligible,
        ROUND(
            100.0 * SUM(response_sla_met) /
            NULLIF(COUNT(response_sla_met), 0),
            2
        ) AS response_compliance_pct,

        COUNT(resolution_sla_met) AS resolution_eligible,
        ROUND(
            100.0 * SUM(resolution_sla_met) /
            NULLIF(COUNT(resolution_sla_met), 0),
            2
        ) AS resolution_compliance_pct,

        SUM(is_reopened) AS reopened_tickets,
        ROUND(
            100.0 * SUM(is_reopened) / COUNT(*),
            2
        ) AS reopen_rate_pct,

        SUM(
            CASE WHEN status IN ('Open', 'In Progress', 'Pending')
                 THEN 1 ELSE 0 END
        ) AS total_backlog,

        SUM(
            CASE WHEN status IN ('Open', 'In Progress', 'Pending')
                 AND priority IN ('Critical', 'High')
                 THEN 1 ELSE 0 END
        ) AS high_risk_backlog

    FROM tickets
    GROUP BY assigned_team
),

team_scores AS (
    SELECT
        *,
        ROUND(
            100.0 * high_risk_backlog /
            NULLIF(total_backlog, 0),
            2
        ) AS high_risk_backlog_pct,

        CASE WHEN response_compliance_pct < 30
             THEN 1 ELSE 0 END AS response_risk_flag,

        CASE WHEN resolution_compliance_pct < 22
             THEN 1 ELSE 0 END AS resolution_risk_flag,

        CASE WHEN reopen_rate_pct > 15
             THEN 1 ELSE 0 END AS reopen_risk_flag,

        CASE WHEN 100.0 * high_risk_backlog /
                  NULLIF(total_backlog, 0) > 30
             THEN 1 ELSE 0 END AS backlog_risk_flag

    FROM team_metrics
)

SELECT
    assigned_team,
    total_tickets,
    response_compliance_pct,
    resolution_compliance_pct,
    reopen_rate_pct,
    total_backlog,
    high_risk_backlog,
    high_risk_backlog_pct,

    response_risk_flag,
    resolution_risk_flag,
    reopen_risk_flag,
    backlog_risk_flag,

    response_risk_flag
    + resolution_risk_flag
    + reopen_risk_flag
    + backlog_risk_flag AS exploratory_risk_score,

    CASE
        WHEN response_risk_flag
           + resolution_risk_flag
           + reopen_risk_flag
           + backlog_risk_flag >= 3
            THEN 'High'

        WHEN response_risk_flag
           + resolution_risk_flag
           + reopen_risk_flag
           + backlog_risk_flag = 2
            THEN 'Moderate'

        ELSE 'Low'
    END AS exploratory_risk_category

FROM team_scores
ORDER BY exploratory_risk_score DESC, assigned_team;
