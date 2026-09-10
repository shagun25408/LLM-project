from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"

DATASETS = [
    "UNSW_NB15_training-set.csv",
    "UNSW_NB15_testing-set.csv",
]

for filename in DATASETS:
    filepath = RAW_DATA_DIR / filename
    dataset = pd.read_csv(filepath)

    print("\n" + "=" * 70)
    print(f"Dataset: {filename}")
    print(f"Rows and columns: {dataset.shape}")

    print("\nColumns:")
    print(dataset.columns.tolist())

    print("\nBinary label distribution (0 = normal, 1 = attack):")
    print(dataset["label"].value_counts().sort_index())

    print("\nAttack category distribution:")
    print(dataset["attack_cat"].fillna("Normal").value_counts())

    print("\nTop missing-value counts:")
    print(dataset.isnull().sum().sort_values(ascending=False).head(10))