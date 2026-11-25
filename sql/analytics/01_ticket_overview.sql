-- PulseOps: Ticket Overview Analytics
-- Phase 4.1: Foundational operational metrics

-- 1. Overall ticket volume and status distribution
SELECT
    COUNT(*) AS total_tickets,
    SUM(CASE WHEN status = 'Open' THEN 1 ELSE 0 END) AS open_tickets,
    SUM(CASE WHEN status = 'In Progress' THEN 1 ELSE 0 END) AS in_progress_tickets,
    SUM(CASE WHEN status = 'Pending' THEN 1 ELSE 0 END) AS pending_tickets,
    SUM(CASE WHEN status = 'Resolved' THEN 1 ELSE 0 END) AS resolved_tickets,
    SUM(CASE WHEN status = 'Closed' THEN 1 ELSE 0 END) AS closed_tickets
FROM tickets;

-- 2. Ticket distribution by priority
SELECT
    priority,
    COUNT(*) AS ticket_count
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

-- 3. Ticket distribution by status
SELECT
    status,
    COUNT(*) AS ticket_count
FROM tickets
GROUP BY status
ORDER BY ticket_count DESC;

-- 4. Reopened ticket overview
SELECT
    COUNT(*) AS total_tickets,
    SUM(is_reopened) AS reopened_tickets,
    ROUND(
        100.0 * SUM(is_reopened) / NULLIF(COUNT(*), 0),
        2
    ) AS reopen_rate_percentage
FROM tickets;
