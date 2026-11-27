
import pandas as pd
import joblib
from pathlib import Path

# --------------------------------------------------
# PATHS
# --------------------------------------------------

ROOT = Path(__file__).resolve().parents[2]

MODEL_PATH = ROOT / "ml" / "models" / "balanced_random_forest.pkl"
DATA_PATH = ROOT / "ml" / "data" / "resolution_sla_dataset.csv"
REPORT_PATH = ROOT / "ml" / "reports" / "feature_importance.csv"
COMPARISON_PATH = ROOT / "ml" / "reports" / "model_comparison.csv"

# --------------------------------------------------
# LOAD MODEL
# --------------------------------------------------

print("=" * 60)
print("PULSEOPS - MODEL ANALYSIS")
print("=" * 60)

model = joblib.load(MODEL_PATH)
df = pd.read_csv(DATA_PATH)

# --------------------------------------------------
# FEATURE IMPORTANCE
# --------------------------------------------------

preprocessor = model.named_steps["preprocessor"]
rf_model = model.named_steps["model"]

feature_names = preprocessor.get_feature_names_out()
importance_values = rf_model.feature_importances_

importance_df = pd.DataFrame({
    "feature": feature_names,
    "importance": importance_values
})

importance_df = importance_df.sort_values(
    by="importance",
    ascending=False
).reset_index(drop=True)

# Clean feature names
importance_df["feature"] = (
    importance_df["feature"]
    .str.replace("categorical__", "", regex=False)
    .str.replace("numeric__", "", regex=False)
)

REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

importance_df.to_csv(REPORT_PATH, index=False)

print("\n--- TOP 15 FEATURES ---")
print(importance_df.head(15).to_string(index=False))

print(f"\nFeature importance saved to: {REPORT_PATH}")

# --------------------------------------------------
# MODEL COMPARISON
# --------------------------------------------------

comparison = pd.DataFrame([
    {
        "Model": "Logistic Regression",
        "Accuracy": 0.6774,
        "Balanced Accuracy": None,
        "Precision (Breach)": 0.8824,
        "Recall (Breach)": 0.6693,
        "F1 (Breach)": 0.7612,
        "ROC-AUC": 0.7065
    },
    {
        "Model": "Random Forest",
        "Accuracy": 0.7440,
        "Balanced Accuracy": None,
        "Precision (Breach)": 0.7835,
        "Recall (Breach)": 0.9213,
        "F1 (Breach)": 0.8468,
        "ROC-AUC": 0.6824
    },
    {
        "Model": "Tuned Random Forest",
        "Accuracy": 0.7641,
        "Balanced Accuracy": None,
        "Precision (Breach)": 0.7672,
        "Recall (Breach)": 0.9948,
        "F1 (Breach)": 0.8663,
        "ROC-AUC": 0.6917
    },
    {
        "Model": "Balanced Random Forest",
        "Accuracy": 0.6835,
        "Balanced Accuracy": 0.6847,
        "Precision (Breach)": 0.8784,
        "Recall (Breach)": 0.6824,
        "F1 (Breach)": 0.7681,
        "ROC-AUC": 0.6922
    }
])

comparison.to_csv(COMPARISON_PATH, index=False)

print("\n--- MODEL COMPARISON ---")
print(comparison.to_string(index=False))

print(f"\nComparison saved to: {COMPARISON_PATH}")

# --------------------------------------------------
# SUMMARY
# --------------------------------------------------

print("\n" + "=" * 60)
print("MODEL ANALYSIS COMPLETED")
print("=" * 60)
