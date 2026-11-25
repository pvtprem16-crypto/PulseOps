import numpy as np
import pandas as pd

np.random.seed(42)

N_TICKETS = 5000

# -------------------------
# Reference data
# -------------------------

clients = [
    "Alpha Corp",
    "Beta Ltd",
    "Gamma Inc",
    "Delta Solutions",
    "Omega Systems",
]

services = [
    "Email Services",
    "Network Infrastructure",
    "Business Applications",
    "Database Services",
    "End User Support",
]

categories = [
    "Hardware",
    "Software",
    "Network",
    "Access",
    "Email",
    "Database",
]

subcategories = {
    "Hardware": ["Laptop", "Printer", "Desktop", "Peripheral"],
    "Software": ["Application Error", "Installation", "License"],
    "Network": ["Connectivity", "VPN", "Wi-Fi", "DNS"],
    "Access": ["Password Reset", "Permission", "Account Lock"],
    "Email": ["Delivery", "Mailbox", "Spam"],
    "Database": ["Query Failure", "Connection", "Performance"],
}

priorities = ["Low", "Medium", "High", "Critical"]

teams = [
    "Service Desk",
    "Network Team",
    "Security Team",
    "Application Team",
    "Database Team",
]

statuses = ["Open", "In Progress", "Pending", "Resolved", "Closed"]

channels = ["Email", "Portal", "Phone", "Monitoring"]

priority_probabilities = [0.35, 0.35, 0.20, 0.10]

status_probabilities = [0.15, 0.25, 0.10, 0.30, 0.20]

# SLA targets in hours
response_sla_hours = {
    "Low": 24,
    "Medium": 8,
    "High": 4,
    "Critical": 1,
}

resolution_sla_hours = {
    "Low": 72,
    "Medium": 24,
    "High": 8,
    "Critical": 4,
}

# -------------------------
# Generate ticket creation times
# -------------------------

start_timestamp = pd.Timestamp("2025-01-01").timestamp()
end_timestamp = pd.Timestamp("2026-11-25").timestamp()

created_at = pd.to_datetime(
    np.random.uniform(start_timestamp, end_timestamp, N_TICKETS),
    unit="s",
)

# -------------------------
# Generate base attributes
# -------------------------

ticket_priorities = np.random.choice(
    priorities,
    N_TICKETS,
    p=priority_probabilities,
)

ticket_statuses = np.random.choice(
    statuses,
    N_TICKETS,
    p=status_probabilities,
)

ticket_categories = np.random.choice(categories, N_TICKETS)

ticket_subcategories = [
    np.random.choice(subcategories[category])
    for category in ticket_categories
]

ticket_clients = np.random.choice(clients, N_TICKETS)

ticket_services = np.random.choice(services, N_TICKETS)

ticket_teams = np.random.choice(teams, N_TICKETS)

ticket_channels = np.random.choice(
    channels,
    N_TICKETS,
    p=[0.30, 0.40, 0.20, 0.10],
)

# -------------------------
# Generate lifecycle timestamps
# -------------------------

first_response_at = []
resolved_at = []
closed_at = []

for i in range(N_TICKETS):

    created = created_at[i]
    status = ticket_statuses[i]

    resolution_timestamp = pd.NaT
    closure_timestamp = pd.NaT
    response_timestamp = pd.NaT

    # Generate resolution first for resolved/closed tickets
    if status in ["Resolved", "Closed"]:

        resolution_minutes = np.random.randint(30, 10081)

        resolution_timestamp = created + pd.Timedelta(
            minutes=resolution_minutes
        )

        # Response must occur before resolution
        max_response_minutes = min(
            2880,
            resolution_minutes - 1
        )

        response_minutes = np.random.randint(
            5,
            max_response_minutes + 1
        )

        response_timestamp = created + pd.Timedelta(
            minutes=response_minutes
        )

    elif status in ["In Progress", "Pending"]:

        response_minutes = np.random.randint(5, 2881)

        response_timestamp = created + pd.Timedelta(
            minutes=response_minutes
        )

    # Open tickets remain unanswered in this simplified model

    if status == "Closed":

        closure_delay = np.random.randint(5, 1441)

        closure_timestamp = (
            resolution_timestamp
            + pd.Timedelta(minutes=closure_delay)
        )

    first_response_at.append(response_timestamp)
    resolved_at.append(resolution_timestamp)
    closed_at.append(closure_timestamp)

first_response_at = pd.to_datetime(first_response_at)
resolved_at = pd.to_datetime(resolved_at)
closed_at = pd.to_datetime(closed_at)


# -------------------------
# Generate SLA deadlines
# -------------------------

response_deadline = pd.Series(
    [
        created_at[i]
        + pd.Timedelta(hours=response_sla_hours[ticket_priorities[i]])
        for i in range(N_TICKETS)
    ]
)

resolution_deadline = pd.Series(
    [
        created_at[i]
        + pd.Timedelta(hours=resolution_sla_hours[ticket_priorities[i]])
        for i in range(N_TICKETS)
    ]
)

# -------------------------
# Calculate SLA indicators
# -------------------------

response_sla_met = []

for i in range(N_TICKETS):

    response = first_response_at[i]
    deadline = response_deadline[i]

    if pd.isna(response):
        response_sla_met.append(np.nan)
    else:
        response_sla_met.append(response <= deadline)

resolution_sla_met = []

for i in range(N_TICKETS):

    resolution = resolved_at[i]
    deadline = resolution_deadline[i]

    if pd.isna(resolution):
        resolution_sla_met.append(np.nan)
    else:
        resolution_sla_met.append(resolution <= deadline)

# -------------------------
# Calculate durations
# -------------------------

first_response_minutes = (
    (first_response_at - created_at)
    .total_seconds() / 60
)

resolution_minutes = (
    (resolved_at - created_at)
    .total_seconds() / 60
)

# -------------------------
# Generate reopen information
# -------------------------

reopen_count = np.random.choice(
    [0, 1, 2, 3],
    N_TICKETS,
    p=[0.85, 0.10, 0.04, 0.01],
)

is_reopened = reopen_count > 0

# -------------------------
# Create DataFrame
# -------------------------

df = pd.DataFrame({
    "ticket_id": [
        f"TKT-{i:05d}"
        for i in range(1, N_TICKETS + 1)
    ],
    "client": ticket_clients,
    "service": ticket_services,
    "category": ticket_categories,
    "subcategory": ticket_subcategories,
    "priority": ticket_priorities,
    "status": ticket_statuses,
    "assigned_team": ticket_teams,
    "channel": ticket_channels,
    "created_at": created_at,
    "first_response_at": first_response_at,
    "resolved_at": resolved_at,
    "closed_at": closed_at,
    "response_deadline": response_deadline,
    "resolution_deadline": resolution_deadline,
    "first_response_minutes": first_response_minutes,
    "resolution_minutes": resolution_minutes,
    "response_sla_met": response_sla_met,
    "resolution_sla_met": resolution_sla_met,
    "reopen_count": reopen_count,
    "is_reopened": is_reopened,
})

# -------------------------
# Export dataset
# -------------------------

df.to_csv("data/tickets.csv", index=False)

# -------------------------
# Summary
# -------------------------

print("=" * 50)
print("PULSEOPS DATA GENERATION")
print("=" * 50)

print(f"Total tickets generated: {len(df)}")
print(f"Total columns: {len(df.columns)}")

print("\nStatus distribution:")
print(df["status"].value_counts())

print("\nPriority distribution:")
print(df["priority"].value_counts())

print("\nDataset preview:")
print(df.head())

print("\nDataset shape:")
print(df.shape)

print("\nDataset saved to data/tickets.csv")    