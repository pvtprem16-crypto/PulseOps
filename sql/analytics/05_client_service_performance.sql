-- ============================================================
-- PulseOps | Phase 4.5: Client & Service Performance Analytics
-- ============================================================

-- 1. Ticket volume and lifecycle distribution by client
SELECT
    client,
    COUNT(*) AS total_tickets,
    SUM(CASE WHEN status = 'Open' THEN 1 ELSE 0 END) AS open_tickets,
    SUM(CASE WHEN status = 'In Progress' THEN 1 ELSE 0 END) AS in_progress_tickets,
    SUM(CASE WHEN status = 'Pending' THEN 1 ELSE 0 END) AS pending_tickets,
    SUM(CASE WHEN status = 'Resolved' THEN 1 ELSE 0 END) AS resolved_tickets,
    SUM(CASE WHEN status = 'Closed' THEN 1 ELSE 0 END) AS closed_tickets
FROM tickets
GROUP BY client
ORDER BY total_tickets DESC;


-- 2. Ticket volume and lifecycle distribution by service
SELECT
    service,
    COUNT(*) AS total_tickets,
    SUM(CASE WHEN status = 'Open' THEN 1 ELSE 0 END) AS open_tickets,
    SUM(CASE WHEN status = 'In Progress' THEN 1 ELSE 0 END) AS in_progress_tickets,
    SUM(CASE WHEN status = 'Pending' THEN 1 ELSE 0 END) AS pending_tickets,
    SUM(CASE WHEN status = 'Resolved' THEN 1 ELSE 0 END) AS resolved_tickets,
    SUM(CASE WHEN status = 'Closed' THEN 1 ELSE 0 END) AS closed_tickets
FROM tickets
GROUP BY service
ORDER BY total_tickets DESC;


-- 3. Response and resolution SLA performance by client
SELECT
    client,
    COUNT(response_sla_met) AS response_eligible,
    SUM(response_sla_met) AS response_sla_met,
    COUNT(response_sla_met) - SUM(response_sla_met) AS response_sla_breached,
    ROUND(
        100.0 * SUM(response_sla_met) / COUNT(response_sla_met),
        2
    ) AS response_compliance_pct,

    COUNT(resolution_sla_met) AS resolution_eligible,
    SUM(resolution_sla_met) AS resolution_sla_met,
    COUNT(resolution_sla_met) - SUM(resolution_sla_met) AS resolution_sla_breached,
    ROUND(
        100.0 * SUM(resolution_sla_met) / COUNT(resolution_sla_met),
        2
    ) AS resolution_compliance_pct
FROM tickets
GROUP BY client
ORDER BY response_compliance_pct ASC;


-- 4. Response and resolution SLA performance by service
SELECT
    service,
    COUNT(response_sla_met) AS response_eligible,
    SUM(response_sla_met) AS response_sla_met,
    COUNT(response_sla_met) - SUM(response_sla_met) AS response_sla_breached,
    ROUND(
        100.0 * SUM(response_sla_met) / COUNT(response_sla_met),
        2
    ) AS response_compliance_pct,

    COUNT(resolution_sla_met) AS resolution_eligible,
    SUM(resolution_sla_met) AS resolution_sla_met,
    COUNT(resolution_sla_met) - SUM(resolution_sla_met) AS resolution_sla_breached,
    ROUND(
        100.0 * SUM(resolution_sla_met) / COUNT(resolution_sla_met),
        2
    ) AS resolution_compliance_pct
FROM tickets
GROUP BY service
ORDER BY resolution_compliance_pct ASC;


-- 5. Average response and resolution times by client and service
SELECT
    client,
    service,
    COUNT(first_response_minutes) AS response_eligible,
    ROUND(AVG(first_response_minutes), 2) AS avg_response_minutes,
    COUNT(resolution_minutes) AS resolution_eligible,
    ROUND(AVG(resolution_minutes), 2) AS avg_resolution_minutes
FROM tickets
GROUP BY client, service
ORDER BY avg_resolution_minutes DESC;


-- 6. Reopen rate by client and service
SELECT
    client,
    service,
    COUNT(*) AS total_tickets,
    SUM(is_reopened) AS reopened_tickets,
    ROUND(
        100.0 * SUM(is_reopened) / COUNT(*),
        2
    ) AS reopen_rate_pct
FROM tickets
GROUP BY client, service
ORDER BY reopen_rate_pct DESC;
