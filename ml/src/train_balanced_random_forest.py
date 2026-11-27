
import pandas as pd
import numpy as np

from pathlib import Path
import joblib

from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    classification_report,
    confusion_matrix
)

# --------------------------------------------------
# PATHS
# --------------------------------------------------

ROOT = Path(__file__).resolve().parents[2]

DATA_PATH = ROOT / "ml" / "data" / "resolution_sla_dataset.csv"
MODEL_PATH = ROOT / "ml" / "models" / "balanced_random_forest.pkl"
REPORT_PATH = ROOT / "ml" / "reports" / "balanced_rf_results.csv"

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

df = pd.read_csv(DATA_PATH)

X = df.drop(columns=["sla_breach"])
y = df["sla_breach"]

categorical_features = [
    "priority",
    "client",
    "service",
    "category",
    "subcategory",
    "assigned_team",
    "channel",
]

numeric_features = [
    "created_hour",
    "created_day_of_week",
    "created_month",
]

# --------------------------------------------------
# PREPROCESSING
# --------------------------------------------------

preprocessor = ColumnTransformer(
    transformers=[
        ("categorical", OneHotEncoder(handle_unknown="ignore"), categorical_features),
        ("numeric", StandardScaler(), numeric_features),
    ]
)

pipeline = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        (
            "model",
            RandomForestClassifier(
                random_state=42,
                n_jobs=-1
            )
        )
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
    stratify=y
)

# --------------------------------------------------
# HYPERPARAMETER SEARCH
# --------------------------------------------------

param_distributions = {
    "model__n_estimators": [200, 300, 500],
    "model__max_depth": [5, 10, 15, 20, None],
    "model__min_samples_split": [2, 5, 10],
    "model__min_samples_leaf": [1, 2, 4, 8],
    "model__max_features": ["sqrt", "log2"],
    "model__class_weight": ["balanced", "balanced_subsample", None],
}

search = RandomizedSearchCV(
    estimator=pipeline,
    param_distributions=param_distributions,
    n_iter=25,
    scoring="balanced_accuracy",
    cv=5,
    random_state=42,
    n_jobs=-1,
    verbose=1
)

print("=" * 60)
print("PULSEOPS - BALANCED RANDOM FOREST")
print("=" * 60)

print("\nStarting hyperparameter tuning...")

search.fit(X_train, y_train)

best_model = search.best_estimator_

# --------------------------------------------------
# EVALUATION
# --------------------------------------------------

y_pred = best_model.predict(X_test)
y_prob = best_model.predict_proba(X_test)[:, 1]

accuracy = accuracy_score(y_test, y_pred)
balanced_acc = balanced_accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred, zero_division=0)
recall = recall_score(y_test, y_pred, zero_division=0)
f1 = f1_score(y_test, y_pred, zero_division=0)
roc_auc = roc_auc_score(y_test, y_prob)

# --------------------------------------------------
# BASELINE
# --------------------------------------------------

majority_class = y_train.mode()[0]
baseline_predictions = np.full(len(y_test), majority_class)

baseline_accuracy = accuracy_score(y_test, baseline_predictions)
baseline_balanced_accuracy = balanced_accuracy_score(
    y_test,
    baseline_predictions
)

# --------------------------------------------------
# OUTPUT
# --------------------------------------------------

print("\n--- BEST PARAMETERS ---")
print(search.best_params_)

print("\n--- BEST CROSS-VALIDATED BALANCED ACCURACY ---")
print(round(search.best_score_, 4))

print("\n--- CLASSIFICATION REPORT ---")
print(classification_report(y_test, y_pred, zero_division=0))

print("\n--- CONFUSION MATRIX ---")
print(confusion_matrix(y_test, y_pred))

print("\n--- MODEL METRICS ---")
print(f"Accuracy:          {accuracy:.4f}")
print(f"Balanced Accuracy: {balanced_acc:.4f}")
print(f"Precision:         {precision:.4f}")
print(f"Recall:            {recall:.4f}")
print(f"F1 Score:          {f1:.4f}")
print(f"ROC-AUC:           {roc_auc:.4f}")

print("\n--- BASELINE ---")
print(f"Baseline Accuracy:          {baseline_accuracy:.4f}")
print(f"Baseline Balanced Accuracy: {baseline_balanced_accuracy:.4f}")

# --------------------------------------------------
# SAVE MODEL
# --------------------------------------------------

MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

joblib.dump(best_model, MODEL_PATH)

results = pd.DataFrame(
    [{
        "model": "Balanced Random Forest",
        "cv_balanced_accuracy": search.best_score_,
        "accuracy": accuracy,
        "balanced_accuracy": balanced_acc,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "roc_auc": roc_auc,
        "baseline_accuracy": baseline_accuracy,
        "baseline_balanced_accuracy": baseline_balanced_accuracy,
    }]
)

results.to_csv(REPORT_PATH, index=False)

print("\n--- SAVED FILES ---")
print(f"Model: {MODEL_PATH}")
print(f"Report: {REPORT_PATH}")

print("\n" + "=" * 60)
print("BALANCED RANDOM FOREST EXPERIMENT COMPLETED")
print("=" * 60)
