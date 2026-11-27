CREATE TABLE IF NOT EXISTS interventions (
    intervention_id INTEGER PRIMARY KEY AUTOINCREMENT,
    prediction_id INTEGER,
    ticket_reference TEXT,
    priority TEXT,
    client TEXT,
    service TEXT,
    assigned_team TEXT,
    risk_level TEXT,
    breach_probability REAL,
    action_taken TEXT NOT NULL,
    owner TEXT,
    status TEXT DEFAULT 'Open',
    notes TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);