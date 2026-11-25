# PulseOps

**IT Service Intelligence & Early-Warning Platform**

PulseOps is a data analytics platform for analyzing IT support ticket operations, monitoring Service Level Agreements (SLAs), identifying recurring incidents, tracking backlog health, and eventually predicting potential SLA breaches.

## Objectives

- Monitor SLA compliance and breach trends.
- Analyze ticket volume and backlog aging.
- Track response and resolution times.
- Identify recurring incident patterns.
- Analyze workload distribution.
- Predict potential SLA breaches using machine learning.
- Provide actionable, data-driven operational insights.

## Technology Stack

- Python, Pandas, NumPy
- SQLite (current development database)
- SQL
- Scikit-learn (planned analytics/modeling)
- FastAPI (planned API)
- React & TypeScript (planned frontend)
- Git & GitHub

## Current foundation

- Synthetic dataset generator (`src/generate_data.py`)
- Data-quality checks and JSON report (`src/data_quality.py`)
- SQLite schema (`sql/schema.sql`)
- Database initializer (`src/init_db.py`)
- Transactional full-refresh loader (`src/load_data.py`)
- Basic automated tests (`tests/`)

The generated dataset uses a fixed snapshot cutoff of **2026-11-25 23:59:59**. Lifecycle timestamps beyond this cutoff are prevented by the generator and checked by the quality engine.

## Setup

Create and activate a virtual environment, then install:

```powershell
pip install pandas numpy
```

From the project root, run:

```powershell
python src/generate_data.py
python src/init_db.py
python src/load_data.py
python src/data_quality.py
python -m unittest discover -s tests -v
```

### Pipeline notes

- `init_db.py` creates the tickets table if it does not already exist.
- `load_data.py` performs a **transactional full refresh**: it deletes the current table contents and loads the current CSV. If loading fails, the transaction is rolled back. Run it only when you intend to replace the database snapshot.
- The quality report is exported to `data/processed/data_quality_report.json`.
- The local SQLite database (`*.db`) is excluded from Git.

## Project roadmap

1. Requirements and business rules
2. Synthetic data engineering and validation
3. Database schema and ETL
4. SQL/Python analytics and KPI reconciliation
5. FastAPI backend
6. React dashboard
7. SLA breach prediction and explainability
8. Recommendations and intervention tracking
9. Integration, testing, deployment and documentation
