from pathlib import Path
import pandas as pd

# Locate project root automatically
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = PROJECT_ROOT / "data" / "tickets.csv"

# Load dataset
df = pd.read_csv(DATA_PATH)

print("=" * 50)
print("PULSEOPS - ML DATASET AUDIT")
print("=" * 50)

print(f"\nTotal tickets: {len(df)}")

target_column = "resolution_sla_met"

print(f"\nMissing target values: {df[target_column].isna().sum()}")

# Only tickets with known outcomes
eligible_df = df.dropna(subset=[target_column]).copy()

print(f"Eligible tickets: {len(eligible_df)}")

# Create target
eligible_df["sla_breach"] = (
    eligible_df[target_column] == 0
).astype(int)

# Class distribution
breach_count = eligible_df["sla_breach"].sum()
met_count = (eligible_df["sla_breach"] == 0).sum()

print("\n--- Target Distribution ---")
print(f"SLA Breached: {breach_count}")
print(f"SLA Met: {met_count}")

print("\n--- Target Percentage ---")
print(f"SLA Breached: {breach_count / len(eligible_df) * 100:.2f}%")
print(f"SLA Met: {met_count / len(eligible_df) * 100:.2f}%")

# Missing values
print("\n--- Missing Values ---")
print(df.isnull().sum().sort_values(ascending=False))

# Eligible tickets by status
print("\n--- Eligible Tickets by Status ---")
print(eligible_df["status"].value_counts())

print("\n" + "=" * 50)
print("AUDIT COMPLETED")
print("=" * 50)