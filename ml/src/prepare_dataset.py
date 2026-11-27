from pathlib import Path
import pandas as pd

# Locate project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_PATH = PROJECT_ROOT / "data" / "tickets.csv"
OUTPUT_PATH = PROJECT_ROOT / "ml" / "data" / "resolution_sla_dataset.csv"

# Load raw dataset
df = pd.read_csv(INPUT_PATH)

# Keep only tickets with known Resolution SLA outcomes
df = df.dropna(subset=["resolution_sla_met"]).copy()

# Create target variable
df["sla_breach"] = (df["resolution_sla_met"] == 0).astype(int)

# Convert created_at to datetime
df["created_at"] = pd.to_datetime(df["created_at"])

# Engineer date/time features
df["created_hour"] = df["created_at"].dt.hour
df["created_day_of_week"] = df["created_at"].dt.dayofweek
df["created_month"] = df["created_at"].dt.month

# Select features and target
feature_columns = [
    "priority",
    "client",
    "service",
    "category",
    "subcategory",
    "assigned_team",
    "channel",
    "created_hour",
    "created_day_of_week",
    "created_month",
]

target_column = "sla_breach"

ml_df = df[feature_columns + [target_column]].copy()

# Save prepared dataset
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
ml_df.to_csv(OUTPUT_PATH, index=False)

print("=" * 50)
print("PULSEOPS - ML DATA PREPARATION")
print("=" * 50)

print(f"\nPrepared records: {len(ml_df)}")
print(f"Features: {len(feature_columns)}")

print("\nTarget distribution:")
print(ml_df[target_column].value_counts())

print("\nTarget percentages:")
print(
    ml_df[target_column]
    .value_counts(normalize=True)
    .mul(100)
    .round(2)
)

print("\nMissing values:")
print(ml_df.isnull().sum())

print(f"\nDataset saved to:")
print(OUTPUT_PATH)

print("\nDATA PREPARATION COMPLETED")   