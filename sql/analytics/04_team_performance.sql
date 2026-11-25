-- ============================================================
-- PulseOps | Phase 4.4: Team Performance Analytics
-- ============================================================

-- 1. Workload and lifecycle distribution by team
SELECT
    assigned_team,
    COUNT(*) AS total_tickets,
    SUM(CASE WHEN status = 'Open' THEN 1 ELSE 0 END) AS open_tickets,
    SUM(CASE WHEN status = 'In Progress' THEN 1 ELSE 0 END) AS in_progress_tickets,
    SUM(CASE WHEN status = 'Pending' THEN 1 ELSE 0 END) AS pending_tickets,
    SUM(CASE WHEN status = 'Resolved' THEN 1 ELSE 0 END) AS resolved_tickets,
    SUM(CASE WHEN status = 'Closed' THEN 1 ELSE 0 END) AS closed_tickets
FROM tickets
GROUP BY assigned_team
ORDER BY total_tickets DESC;


-- 2. Average response and resolution times by team
SELECT
    assigned_team,
    COUNT(first_response_minutes) AS response_eligible,
    ROUND(AVG(first_response_minutes), 2) AS avg_response_minutes,
    COUNT(resolution_minutes) AS resolution_eligible,
    ROUND(AVG(resolution_minutes), 2) AS avg_resolution_minutes
FROM tickets
GROUP BY assigned_team
ORDER BY assigned_team;


-- 3. Response SLA performance by team
SELECT
    assigned_team,
    COUNT(response_sla_met) AS eligible_tickets,
    SUM(response_sla_met) AS sla_met,
    COUNT(response_sla_met) - SUM(response_sla_met) AS sla_breached,
    ROUND(
        100.0 * SUM(response_sla_met) / COUNT(response_sla_met),
        2
    ) AS response_sla_compliance_pct
FROM tickets
WHERE response_sla_met IS NOT NULL
GROUP BY assigned_team
ORDER BY response_sla_compliance_pct ASC;


-- 4. Resolution SLA performance by team
SELECT
    assigned_team,
    COUNT(resolution_sla_met) AS eligible_tickets,
    SUM(resolution_sla_met) AS sla_met,
    COUNT(resolution_sla_met) - SUM(resolution_sla_met) AS sla_breached,
    ROUND(
        100.0 * SUM(resolution_sla_met) / COUNT(resolution_sla_met),
        2
    ) AS resolution_sla_compliance_pct
FROM tickets
WHERE resolution_sla_met IS NOT NULL
GROUP BY assigned_team
ORDER BY resolution_sla_compliance_pct ASC;


-- 5. Reopened tickets by team
SELECT
    assigned_team,
    COUNT(*) AS total_tickets,
    SUM(is_reopened) AS reopened_tickets,
    ROUND(
        100.0 * SUM(is_reopened) / COUNT(*),
        2
    ) AS reopen_rate_pct
FROM tickets
GROUP BY assigned_team
ORDER BY reopen_rate_pct DESC;


-- 6. Priority distribution by team
SELECT
    assigned_team,
    SUM(CASE WHEN priority = 'Critical' THEN 1 ELSE 0 END) AS critical,
    SUM(CASE WHEN priority = 'High' THEN 1 ELSE 0 END) AS high,
    SUM(CASE WHEN priority = 'Medium' THEN 1 ELSE 0 END) AS medium,
    SUM(CASE WHEN priority = 'Low' THEN 1 ELSE 0 END) AS low
FROM tickets
GROUP BY assigned_team
ORDER BY assigned_team;