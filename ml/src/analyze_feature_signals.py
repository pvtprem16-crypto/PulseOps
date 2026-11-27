
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT / "ml" / "data" / "resolution_sla_dataset.csv"

df = pd.read_csv(DATA_PATH)

target = "sla_breach"

categorical_features = [
    "priority",
    "client",
    "service",
    "category",
    "subcategory",
    "assigned_team",
    "channel",
]

print("=" * 60)
print("PULSEOPS - FEATURE SIGNAL INVESTIGATION")
print("=" * 60)

print(f"\nTotal records: {len(df)}")
print(f"Overall breach rate: {df[target].mean():.2%}")

for feature in categorical_features:

    if feature not in df.columns:
        print(f"\nSkipping missing feature: {feature}")
        continue

    analysis = (
        df.groupby(feature, observed=True)[target]
        .agg(["count", "mean"])
        .sort_values("mean", ascending=False)
    )

    analysis["mean"] = analysis["mean"] * 100

    print(f"\n{'-' * 50}")
    print(f"FEATURE: {feature.upper()}")
    print("-" * 50)

    print(
        analysis.rename(
            columns={
                "count": "Ticket Count",
                "mean": "Breach Rate (%)"
            }
        ).round(2).to_string()
    )

print("\n" + "=" * 60)
print("INVESTIGATION COMPLETED")
print("=" * 60)
