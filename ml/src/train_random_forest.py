from pathlib import Path

import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
)


# --------------------------------------------------
# PATHS
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_PATH = PROJECT_ROOT / "ml" / "data" / "resolution_sla_dataset.csv"
MODEL_PATH = PROJECT_ROOT / "ml" / "models" / "random_forest.pkl"


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

df = pd.read_csv(DATA_PATH)

X = df.drop(columns=["sla_breach"])
y = df["sla_breach"]


# --------------------------------------------------
# FEATURES
# --------------------------------------------------

categorical_features = [
    "priority",
    "client",
    "service",
    "category",
    "subcategory",
    "assigned_team",
    "channel",
]

numerical_features = [
    "created_hour",
    "created_day_of_week",
    "created_month",
]


# --------------------------------------------------
# PREPROCESSING
# --------------------------------------------------

preprocessor = ColumnTransformer(
    transformers=[
        (
            "categorical",
            OneHotEncoder(handle_unknown="ignore"),
            categorical_features,
        ),
        (
            "numerical",
            "passthrough",
            numerical_features,
        ),
    ]
)


# --------------------------------------------------
# RANDOM FOREST PIPELINE
# --------------------------------------------------

model_pipeline = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        (
            "model",
            RandomForestClassifier(
                n_estimators=300,
                max_depth=None,
                min_samples_split=2,
                min_samples_leaf=1,
                class_weight=None,
                random_state=42,
                n_jobs=-1,
            ),
        ),
    ]
)


# --------------------------------------------------
# TRAIN / TEST SPLIT
# --------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y,
)


print("=" * 60)
print("PULSEOPS - RANDOM FOREST")
print("=" * 60)

print(f"\nTraining records: {len(X_train)}")
print(f"Testing records: {len(X_test)}")


# --------------------------------------------------
# TRAIN
# --------------------------------------------------

model_pipeline.fit(X_train, y_train)

print("\nTraining completed!")


# --------------------------------------------------
# PREDICTIONS
# --------------------------------------------------

y_pred = model_pipeline.predict(X_test)
y_prob = model_pipeline.predict_proba(X_test)[:, 1]


# --------------------------------------------------
# EVALUATION
# --------------------------------------------------

print("\n--- Classification Report ---")

print(
    classification_report(
        y_test,
        y_pred,
        zero_division=0,
    )
)

print("\n--- Confusion Matrix ---")
print(confusion_matrix(y_test, y_pred))


print("\n--- Metrics ---")

print(f"Accuracy:  {accuracy_score(y_test, y_pred):.4f}")
print(f"Precision: {precision_score(y_test, y_pred, zero_division=0):.4f}")
print(f"Recall:    {recall_score(y_test, y_pred, zero_division=0):.4f}")
print(f"F1 Score:  {f1_score(y_test, y_pred, zero_division=0):.4f}")
print(f"ROC-AUC:   {roc_auc_score(y_test, y_prob):.4f}")


# --------------------------------------------------
# MAJORITY BASELINE
# --------------------------------------------------

baseline_predictions = [1] * len(y_test)

print("\n--- Majority Baseline ---")

print(f"Accuracy: {accuracy_score(y_test, baseline_predictions):.4f}")
print(f"Precision: {precision_score(y_test, baseline_predictions, zero_division=0):.4f}")
print(f"Recall: {recall_score(y_test, baseline_predictions, zero_division=0):.4f}")
print(f"F1 Score: {f1_score(y_test, baseline_predictions, zero_division=0):.4f}")


# --------------------------------------------------
# SAVE MODEL
# --------------------------------------------------

MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)

joblib.dump(model_pipeline, MODEL_PATH)

print("\nModel saved:")
print(MODEL_PATH)

print("\n" + "=" * 60)
print("RANDOM FOREST COMPLETED")
print("=" * 60)