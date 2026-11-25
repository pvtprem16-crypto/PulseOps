-- PulseOps: SLA Performance Analytics

-- 1. Overall response SLA performance
SELECT
    COUNT(response_sla_met) AS eligible_tickets,
    SUM(response_sla_met) AS sla_met,
    COUNT(response_sla_met) - SUM(response_sla_met) AS sla_breached,
    ROUND(
        100.0 * SUM(response_sla_met) / NULLIF(COUNT(response_sla_met), 0),
        2
    ) AS compliance_percentage
FROM tickets;

-- 2. Overall resolution SLA performance
SELECT
    COUNT(resolution_sla_met) AS eligible_tickets,
    SUM(resolution_sla_met) AS sla_met,
    COUNT(resolution_sla_met) - SUM(resolution_sla_met) AS sla_breached,
    ROUND(
        100.0 * SUM(resolution_sla_met) / NULLIF(COUNT(resolution_sla_met), 0),
        2
    ) AS compliance_percentage
FROM tickets;

-- 3. Response SLA performance by priority
SELECT
    priority,
    COUNT(response_sla_met) AS eligible_tickets,
    SUM(response_sla_met) AS sla_met,
    COUNT(response_sla_met) - SUM(response_sla_met) AS sla_breached,
    ROUND(
        100.0 * SUM(response_sla_met) / NULLIF(COUNT(response_sla_met), 0),
        2
    ) AS compliance_percentage
FROM tickets
GROUP BY priority
ORDER BY
    CASE priority
        WHEN 'Critical' THEN 1
        WHEN 'High' THEN 2
        WHEN 'Medium' THEN 3
        WHEN 'Low' THEN 4
        ELSE 5
    END;

-- 4. Resolution SLA performance by priority
SELECT
    priority,
    COUNT(resolution_sla_met) AS eligible_tickets,
    SUM(resolution_sla_met) AS sla_met,
    COUNT(resolution_sla_met) - SUM(resolution_sla_met) AS sla_breached,
    ROUND(
        100.0 * SUM(resolution_sla_met) / NULLIF(COUNT(resolution_sla_met), 0),
        2
    ) AS compliance_percentage
FROM tickets
GROUP BY priority
ORDER BY
    CASE priority
        WHEN 'Critical' THEN 1
        WHEN 'High' THEN 2
        WHEN 'Medium' THEN 3
        WHEN 'Low' THEN 4
        ELSE 5
    END;
