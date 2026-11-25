-- PulseOps: Backlog & Ticket Aging Analytics
-- Reporting snapshot: 2026-11-25 23:59:59
-- Backlog definition: Open, In Progress, Pending

-- 1. Overall backlog summary
SELECT
    COUNT(*) AS backlog_tickets,
    ROUND(AVG(
        julianday('2026-11-25 23:59:59') - julianday(created_at)
    ), 2) AS average_backlog_age_days,
    ROUND(MAX(
        julianday('2026-11-25 23:59:59') - julianday(created_at)
    ), 2) AS maximum_backlog_age_days
FROM tickets
WHERE status IN ('Open', 'In Progress', 'Pending');

-- 2. Backlog aging buckets
SELECT
    CASE
        WHEN julianday('2026-11-25 23:59:59') - julianday(created_at) < 3
            THEN '0-2 Days'
        WHEN julianday('2026-11-25 23:59:59') - julianday(created_at) < 7
            THEN '3-6 Days'
        WHEN julianday('2026-11-25 23:59:59') - julianday(created_at) < 14
            THEN '7-13 Days'
        WHEN julianday('2026-11-25 23:59:59') - julianday(created_at) < 30
            THEN '14-29 Days'
        ELSE '30+ Days'
    END AS aging_bucket,
    COUNT(*) AS ticket_count
FROM tickets
WHERE status IN ('Open', 'In Progress', 'Pending')
GROUP BY aging_bucket
ORDER BY
    CASE aging_bucket
        WHEN '0-2 Days' THEN 1
        WHEN '3-6 Days' THEN 2
        WHEN '7-13 Days' THEN 3
        WHEN '14-29 Days' THEN 4
        WHEN '30+ Days' THEN 5
    END;

-- 3. Backlog by priority
SELECT
    priority,
    COUNT(*) AS backlog_tickets,
    ROUND(AVG(
        julianday('2026-11-25 23:59:59') - julianday(created_at)
    ), 2) AS average_age_days
FROM tickets
WHERE status IN ('Open', 'In Progress', 'Pending')
GROUP BY priority
ORDER BY
    CASE priority
        WHEN 'Critical' THEN 1
        WHEN 'High' THEN 2
        WHEN 'Medium' THEN 3
        WHEN 'Low' THEN 4
    END;

-- 4. Backlog by status
SELECT
    status,
    COUNT(*) AS backlog_tickets,
    ROUND(AVG(
        julianday('2026-11-25 23:59:59') - julianday(created_at)
    ), 2) AS average_age_days
FROM tickets
WHERE status IN ('Open', 'In Progress', 'Pending')
GROUP BY status
ORDER BY backlog_tickets DESC;

-- 5. Top 20 oldest backlog tickets
SELECT
    ticket_id,
    client,
    service,
    priority,
    status,
    assigned_team,
    created_at,
    ROUND(
        julianday('2026-11-25 23:59:59') - julianday(created_at),
        2
    ) AS age_days
FROM tickets
WHERE status IN ('Open', 'In Progress', 'Pending')
ORDER BY age_days DESC
LIMIT 20;
