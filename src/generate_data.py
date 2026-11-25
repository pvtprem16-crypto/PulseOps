import numpy as np
import pandas as pd

np.random.seed(42)

n_tickets = 5000

clients = ["Alpha Corp", "Beta Ltd", "Gamma Inc", "Delta Solutions", "Omega Systems"]
categories = ["Hardware", "Software", "Network", "Access", "Email", "Database"]
priorities = ["Low", "Medium", "High", "Critical"]
teams = ["Service Desk", "Network Team", "Security Team", "Application Team"]
statuses = ["Open", "In Progress", "Pending", "Resolved", "Closed"]

start_date = pd.Timestamp("2025-01-01").timestamp()
end_date = pd.Timestamp("2026-11-01").timestamp()

data = {
    "ticket_id": [f"TKT-{i:05d}" for i in range(1, n_tickets + 1)],
    "client": np.random.choice(clients, n_tickets),
    "category": np.random.choice(categories, n_tickets),
    "priority": np.random.choice(
        priorities, n_tickets, p=[0.35, 0.35, 0.20, 0.10]
    ),
    "assigned_team": np.random.choice(teams, n_tickets),
    "status": np.random.choice(
        statuses, n_tickets, p=[0.15, 0.25, 0.10, 0.30, 0.20]
    ),
    "created_at": pd.to_datetime(
        np.random.uniform(start_date, end_date, n_tickets),
        unit="s"
    )
}

df = pd.DataFrame(data)

df.to_csv("data/tickets.csv", index=False)

print("Dataset generated successfully!")
print("Total tickets:", len(df))
print("\nFirst 5 rows:")
print(df.head())
print("\nDataset shape:", df.shape)
print("\nColumn names:")
print(df.columns.tolist())