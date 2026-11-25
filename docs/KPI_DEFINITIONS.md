# PulseOps — KPI Definitions & Analytical Rules

## 1. Project Context

PulseOps is an IT Service Intelligence & Early-Warning Platform designed to analyze ticket operations, monitor service performance, identify operational risk areas and support data-driven decision-making.

This document defines the analytical rules and KPI calculations used throughout the project.

Dataset: 5,000 synthetic IT service tickets.
Reporting snapshot: 2026-11-25 23:59:59.

---

## 2. Ticket Volume

### Total Tickets
The total number of records in the tickets dataset.

Formula:
COUNT(*)

### Status Distribution
Tickets are classified into:
- Open
- In Progress
- Pending
- Resolved
- Closed

Status counts must reconcile to the total ticket count.

---

## 3. Priority Classification

Ticket priorities:
- Critical
- High
- Medium
- Low

Recommended analytical ordering:
Critical > High > Medium > Low.

---

## 4. Backlog Definition

A ticket is considered part of the operational backlog when its status is:

- Open
- In Progress
- Pending

Resolved and Closed tickets are excluded from the backlog.

### Backlog Volume
Count of tickets whose status is Open, In Progress or Pending.

### Backlog Aging
Age is calculated as:

Reporting Snapshot - Ticket Creation Timestamp

Age is measured in days.

### Aging Buckets
- 0-2 Days
- 3-6 Days
- 7-13 Days
- 14-29 Days
- 30+ Days

---

## 5. Response SLA

### Eligibility
A ticket is eligible for response SLA measurement when response_sla_met is not NULL.

### SLA Met
response_sla_met = 1.

### SLA Breached
response_sla_met = 0.

### Response SLA Compliance

(Response SLA Met / Response SLA Eligible Tickets) * 100

Ineligible tickets must not be counted as breaches.

---

## 6. Resolution SLA

### Eligibility
A ticket is eligible for resolution SLA measurement when resolution_sla_met is not NULL.

### SLA Met
resolution_sla_met = 1.

### SLA Breached
resolution_sla_met = 0.

### Resolution SLA Compliance

(Resolution SLA Met / Resolution SLA Eligible Tickets) * 100

Ineligible tickets must not be counted as breaches.

---

## 7. Reopen Metrics

### Reopened Ticket
A ticket is classified as reopened when is_reopened = 1.

### Reopen Rate

(Reopened Tickets / Total Tickets) * 100

Reopen tracking in this dataset is simplified synthetic tracking and does not represent complete event-level lifecycle history.

---

## 8. Average Response Time

Average response time is calculated using first_response_minutes.

Only records with a non-NULL response time are included.

---

## 9. Average Resolution Time

Average resolution time is calculated using resolution_minutes.

Only records with a non-NULL resolution time are included.

---

## 10. Dimensional Analytics

Metrics may be aggregated by:

- Assigned Team
- Client
- Service
- Priority
- Status
- Team and Priority
- Client and Priority
- Service and Priority
- Team and Service

Aggregated totals must be reconciled against the underlying dataset wherever the aggregation represents a complete partition.

---

## 11. Exploratory Team Risk Scorecard

This is a rule-based exploratory indicator, not a validated predictive model.

Each condition contributes one point.

### Indicators

1. Response SLA compliance below 30%.
2. Resolution SLA compliance below 22%.
3. Reopen rate above 15%.
4. Critical + High backlog exceeds 30% of total team backlog.

### Score

Sum of the four risk indicators.

Possible score: 0 to 4.

### Exploratory Categories

- High: score >= 3
- Moderate: score = 2
- Low: score <= 1

Thresholds are exploratory and may require calibration.

---

## 12. Reporting Snapshot

Reporting cutoff:

2026-11-25 23:59:59

Backlog aging calculations use this snapshot.

The reporting cutoff should be centralized and configurable in future application components rather than duplicated throughout production logic.

---

## 13. Data Quality Rules

- Ticket IDs must be unique.
- Total records must reconcile to 5,000.
- Status totals must reconcile to the dataset.
- Priority totals must reconcile to the dataset.
- Team, client and service totals must reconcile to the dataset.
- SLA eligibility must be represented separately from SLA breach.
- Lifecycle timestamps must not precede ticket creation.
- Resolution timestamps must not precede first response timestamps where both exist.
- Missing values in critical categorical fields must be investigated.
- SQLite database integrity must pass.

---

## 14. Dataset Limitations

- Dataset is synthetic and does not represent real organization performance.
- Ticket lifecycle history is simplified.
- Reopen tracking is simplified.
- The dataset is a snapshot, not a full event-driven ticket history.
- Exploratory risk thresholds are not statistically validated.
- Analytical correlations must not automatically be interpreted as causation.
- Predictive models must avoid data leakage.

---

## 15. KPI Governance

This document serves as the initial source of truth for KPI definitions and analytical rules.

Changes to KPI logic should be documented and reconciled across:

- SQL analytics
- Python analytical pipelines
- FastAPI endpoints
- Frontend dashboards
- Machine-learning pipelines
