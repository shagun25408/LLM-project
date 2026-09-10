import json
from pathlib import Path

RESULTS_DIR = Path(__file__).resolve().parent / "results"

metrics_files = list(RESULTS_DIR.glob("*_metrics.json"))

if not metrics_files:
    raise FileNotFoundError("No metrics files found in ml/results.")

models = []

for file_path in metrics_files:
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)
        models.append(data)

models.sort(key=lambda item: item.get("f1_score", 0), reverse=True)

print("\nCyberGuard AI — Model Comparison")
print("=" * 72)

for index, model in enumerate(models, start=1):
    print(f"\n{index}. {model['model']}")
    print(f"   Accuracy:            {model['accuracy']:.4f}")
    print(f"   Precision:           {model['precision']:.4f}")
    print(f"   Recall:              {model['recall']:.4f}")
    print(f"   F1 Score:            {model['f1_score']:.4f}")
    print(f"   ROC-AUC:             {model['roc_auc']:.4f}")
    print(f"   False Positive Rate: {model['false_positive_rate']:.4f}")

winner = models[0]
print("\n" + "=" * 72)
print(f"Recommended model: {winner['model']}")
print("Reason: highest F1 score among the evaluated models.")