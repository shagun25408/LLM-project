import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
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

TARGET_COLUMN = "label"
DROP_COLUMNS = ["id", "attack_cat", TARGET_COLUMN]

X_train = train_data.drop(columns=DROP_COLUMNS)
y_train = train_data[TARGET_COLUMN]

X_test = test_data.drop(columns=DROP_COLUMNS)
y_test = test_data[TARGET_COLUMN]

categorical_features = ["proto", "service", "state"]
numeric_features = [
    column for column in X_train.columns
    if column not in categorical_features
]

numeric_pipeline = Pipeline(
    steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ]
)

categorical_pipeline = Pipeline(
    steps=[
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(handle_unknown="ignore")),
    ]
)

preprocessor = ColumnTransformer(
    transformers=[
        ("numeric", numeric_pipeline, numeric_features),
        ("categorical", categorical_pipeline, categorical_features),
    ]
)

model_pipeline = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        (
            "model",
            LogisticRegression(
                max_iter=1000,
                class_weight="balanced",
                solver="saga",
                random_state=42,
            ),
        ),
    ]
)

print("Training Logistic Regression baseline model...")
model_pipeline.fit(X_train, y_train)

predictions = model_pipeline.predict(X_test)
probabilities = model_pipeline.predict_proba(X_test)[:, 1]

tn, fp, fn, tp = confusion_matrix(y_test, predictions).ravel()

metrics = {
    "model": "Logistic Regression",
    "accuracy": round(float(accuracy_score(y_test, predictions)), 4),
    "precision": round(float(precision_score(y_test, predictions)), 4),
    "recall": round(float(recall_score(y_test, predictions)), 4),
    "f1_score": round(float(f1_score(y_test, predictions)), 4),
    "roc_auc": round(float(roc_auc_score(y_test, probabilities)), 4),
    "false_positive_rate": round(float(fp / (fp + tn)), 4),
    "true_negatives": int(tn),
    "false_positives": int(fp),
    "false_negatives": int(fn),
    "true_positives": int(tp),
}

model_path = MODEL_DIR / "logistic_regression_pipeline.joblib"
metrics_path = RESULTS_DIR / "logistic_regression_metrics.json"

joblib.dump(model_pipeline, model_path)

with open(metrics_path, "w", encoding="utf-8") as file:
    json.dump(metrics, file, indent=2)

print("\nEvaluation metrics:")
for metric, value in metrics.items():
    print(f"{metric}: {value}")

print(f"\nSaved model: {model_path}")
print(f"Saved metrics: {metrics_path}")