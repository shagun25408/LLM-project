from pathlib import Path
from typing import Any

import joblib
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = PROJECT_ROOT / "ml" / "models" / "random_forest_pipeline.joblib"

EXPECTED_FEATURES = [
    "dur", "proto", "service", "state", "spkts", "dpkts",
    "sbytes", "dbytes", "rate", "sttl", "dttl", "sload",
    "dload", "sloss", "dloss", "sinpkt", "dinpkt", "sjit",
    "djit", "swin", "stcpb", "dtcpb", "dwin", "tcprtt",
    "synack", "ackdat", "smean", "dmean", "trans_depth",
    "response_body_len", "ct_srv_src", "ct_state_ttl",
    "ct_dst_ltm", "ct_src_dport_ltm", "ct_dst_sport_ltm",
    "ct_dst_src_ltm", "is_ftp_login", "ct_ftp_cmd",
    "ct_flw_http_mthd", "ct_src_ltm", "ct_srv_dst",
    "is_sm_ips_ports",
]


def get_model():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Random Forest model was not found at: {MODEL_PATH}"
        )

    return joblib.load(MODEL_PATH)


def predict_flow(features: dict[str, Any]) -> dict[str, Any]:
    missing_features = [
        feature for feature in EXPECTED_FEATURES
        if feature not in features
    ]

    if missing_features:
        raise ValueError(
            "Missing required features: " + ", ".join(missing_features)
        )

    model = get_model()
    flow_data = pd.DataFrame([features])[EXPECTED_FEATURES]

    prediction = int(model.predict(flow_data)[0])
    attack_probability = float(model.predict_proba(flow_data)[0][1])

    return {
        "prediction": prediction,
        "classification": "ATTACK" if prediction == 1 else "NORMAL",
        "attack_probability": round(attack_probability, 4),
        "model": "Random Forest",
    }