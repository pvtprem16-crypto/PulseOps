from pathlib import Path

import pandas as pd
import joblib

from sklearn.model_selection import (
    train_test_split,
    StratifiedKFold,
    RandomizedSearchCV,
)

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder

from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
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
MODEL_PATH = PROJECT_ROOT / "ml" / "models" / "tuned_random_forest.pkl"
REPORT_PATH = PROJECT_ROOT / "ml" / "reports" / "rf_tuning_results.csv"


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

df = pd.read_csv(DATA_PATH)

X = df.drop(columns=["sla_breach"])
y = df["sla_breach"]


# --------------------------------------------------
# FEATURE DEFINITIONS
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
# PIPELINE
# --------------------------------------------------

pipeline = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        (
            "model",
            RandomForestClassifier(
                random_state=42,
                n_jobs=-1,
            ),
        ),
    ]
)


# --------------------------------------------------
# PARAMETER SEARCH
# --------------------------------------------------

param_distributions = {
    "model__n_estimators": [100, 200, 300, 500],
    "model__max_depth": [None, 5, 10, 15, 20],
    "model__min_samples_split": [2, 5, 10, 20],
    "model__min_samples_leaf": [1, 2, 4, 8],
    "model__max_features": ["sqrt", "log2", None],
    "model__class_weight": [None, "balanced"],
}


# --------------------------------------------------
# TRAINING / TEST SPLIT
# --------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y,
)


# --------------------------------------------------
# CROSS VALIDATION
# --------------------------------------------------

cv = StratifiedKFold(
    n_splits=5,
    shuffle=True,
    random_state=42,
)


# --------------------------------------------------
# RANDOMIZED SEARCH
# --------------------------------------------------

search = RandomizedSearchCV(
    estimator=pipeline,
    param_distributions=param_distributions,
    n_iter=30,
    scoring="accuracy",
    cv=cv,
    random_state=42,
    n_jobs=-1,
    verbose=2,
    return_train_score=True,
)


# --------------------------------------------------
# TRAIN
# --------------------------------------------------

print("=" * 60)
print("PULSEOPS - RANDOM FOREST HYPERPARAMETER TUNING")
print("=" * 60)

print("\nStarting Randomized Search...")
print("30 configurations | 5-fold CV")
print("This may take some time.\n")

search.fit(X_train, y_train)


# --------------------------------------------------
# SEARCH RESULTS
# --------------------------------------------------

print("\n--- BEST CONFIGURATION ---")
print(search.best_params_)

print("\n--- BEST CROSS-VALIDATED ACCURACY ---")
print(f"{search.best_score_:.4f}")


# --------------------------------------------------
# EVALUATE BEST MODEL
# --------------------------------------------------

best_model = search.best_estimator_

y_pred = best_model.predict(X_test)
y_prob = best_model.predict_proba(X_test)[:, 1]


print("\n--- TEST SET EVALUATION ---")

print(classification_report(y_test, y_pred, zero_division=0))

print("\n--- CONFUSION MATRIX ---")
print(confusion_matrix(y_test, y_pred))


print("\n--- METRICS ---")

print(f"Accuracy:  {accuracy_score(y_test, y_pred):.4f}")
print(f"Precision: {precision_score(y_test, y_pred, zero_division=0):.4f}")
print(f"Recall:    {recall_score(y_test, y_pred, zero_division=0):.4f}")
print(f"F1 Score:  {f1_score(y_test, y_pred, zero_division=0):.4f}")
print(f"ROC-AUC:   {roc_auc_score(y_test, y_prob):.4f}")


# --------------------------------------------------
# BASELINE
# --------------------------------------------------

baseline_predictions = [1] * len(y_test)

print("\n--- MAJORITY BASELINE ---")

print(
    f"Baseline Accuracy: "
    f"{accuracy_score(y_test, baseline_predictions):.4f}"
)


# --------------------------------------------------
# SAVE MODEL
# --------------------------------------------------

MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

joblib.dump(best_model, MODEL_PATH)

# Save all search results
results_df = pd.DataFrame(search.cv_results_)

results_df = results_df.sort_values(
    by="mean_test_score",
    ascending=False,
)

results_df.to_csv(REPORT_PATH, index=False)


print("\n--- SAVED FILES ---")
print(f"Model: {MODEL_PATH}")
print(f"Search results: {REPORT_PATH}")

print("\n" + "=" * 60)
print("HYPERPARAMETER TUNING COMPLETED")
print("=" * 60)