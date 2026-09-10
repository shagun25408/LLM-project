import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import IsolationForest
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
MODEL_DIR = PROJECT_ROOT / "ml" / "models"
RESULTS_DIR = PROJECT_ROOT / "ml" / "results"

MODEL_DIR.mkdir(exist_ok=True)
RESULTS_DIR.mkdir(exist_ok=True)

train_data = pd.read_csv(RAW_DATA_DIR / "UNSW_NB15_training-set.csv")
test_data = pd.read_csv(RAW_DATA_DIR / "UNSW_NB15_testing-set.csv")

DROP_COLUMNS = ["id", "attack_cat", "label"]

X_train = train_data.drop(columns=DROP_COLUMNS)
y_train = train_data["label"]
X_test = test_data.drop(columns=DROP_COLUMNS)
y_test = test_data["label"]

categorical_features = ["proto", "service", "state"]
numeric_features = [
    column for column in X_train.columns
    if column not in categorical_features
]

preprocessor = ColumnTransformer(
    transformers=[
        (
            "numeric",
            Pipeline(
                steps=[
                    ("imputer", SimpleImputer(strategy="median")),
                    ("scaler", StandardScaler()),
                ]
            ),
            numeric_features,
        ),
        (
            "categorical",
            Pipeline(
                steps=[
                    ("imputer", SimpleImputer(strategy="most_frequent")),
                    ("encoder", OneHotEncoder(handle_unknown="ignore")),
                ]
            ),
            categorical_features,
        ),
    ]
)

# Isolation Forest learns only normal traffic.
normal_training_data = X_train[y_train == 0]

print("Preparing normal network traffic for anomaly detection...")
X_normal_processed = preprocessor.fit_transform(normal_training_data)
X_test_processed = preprocessor.transform(X_test)

model = IsolationForest(
    n_estimators=200,
    max_samples=10000,
    contamination="auto",
    n_jobs=-1,
    random_state=42,
)

print("Training Isolation Forest anomaly model...")
model.fit(X_normal_processed)

# Higher score = more anomalous.
normal_scores = -model.score_samples(X_normal_processed)
test_scores = -model.score_samples(X_test_processed)

# Permit about 5% anomalies among the normal training flows.
threshold = float(np.quantile(normal_scores, 0.95))
predictions = (test_scores >= threshold).astype(int)

tn, fp, fn, tp = confusion_matrix(y_test, predictions).ravel()

metrics = {
    "model": "Isolation Forest",
    "threshold": round(threshold, 4),
    "accuracy": round(float(accuracy_score(y_test, predictions)), 4),
    "precision": round(float(precision_score(y_test, predictions)), 4),
    "recall": round(float(recall_score(y_test, predictions)), 4),
    "f1_score": round(float(f1_score(y_test, predictions)), 4),
    "roc_auc": round(float(roc_auc_score(y_test, test_scores)), 4),
    "false_positive_rate": round(float(fp / (fp + tn)), 4),
    "true_negatives": int(tn),
    "false_positives": int(fp),
    "false_negatives": int(fn),
    "true_positives": int(tp),
}

joblib.dump(
    {
        "preprocessor": preprocessor,
        "model": model,
        "threshold": threshold,
    },
    MODEL_DIR / "isolation_forest_pipeline.joblib",
)

with open(RESULTS_DIR / "isolation_forest_metrics.json", "w", encoding="utf-8") as file:
    json.dump(metrics, file, indent=2)

print("\nEvaluation metrics:")
for metric, value in metrics.items():
    print(f"{metric}: {value}")