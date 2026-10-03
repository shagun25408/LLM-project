import io
from datetime import datetime, timezone
from typing import Any, Literal

import pandas as pd
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError

from app.ai_analyst import analyze_incident
from app.database import Base, SessionLocal, engine, test_database_connection
from app.detection import analyze_login_event
from app.ml_service import MODEL_PATH, predict_flow, predict_flows
from app.models import IncidentModel
from app.seed import seed_incidents


Base.metadata.create_all(bind=engine)

with SessionLocal() as database_session:
    seed_incidents(database_session)


app = FastAPI(
    title="CyberGuard AI API",
    description="Backend API for cybersecurity threat detection and analysis.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Incident(BaseModel):
    id: int
    threat_type: str
    severity: str
    confidence: float
    source_ip: str
    target_service: str
    status: str
    detected_at: datetime
    evidence: list[str]

    model_config = ConfigDict(from_attributes=True)


class IncidentCreate(BaseModel):
    threat_type: str
    severity: str
    confidence: float = Field(ge=0, le=1)
    source_ip: str
    target_service: str
    status: str = "OPEN"
    detected_at: datetime | None = None
    evidence: list[str] = Field(default_factory=list)


class IncidentStatusUpdate(BaseModel):
    status: Literal["OPEN", "INVESTIGATING", "RESOLVED"]


class LoginEvent(BaseModel):
    source_ip: str
    target_service: str = "SSH"
    failed_login_attempts: int = Field(ge=0)
    time_window_minutes: int = Field(gt=0, le=1440)


class DetectionResponse(BaseModel):
    detected: bool
    message: str
    incident_id: int | None = None
    threat_type: str | None = None
    severity: str | None = None
    confidence: float | None = None


class FlowPredictionRequest(BaseModel):
    features: dict[str, Any]
    source_ip: str = "unknown"
    target_service: str = "Unknown Service"


class FlowPredictionResponse(BaseModel):
    prediction: int
    classification: str
    attack_probability: float
    model: str
    incident_id: int | None = None


@app.get("/")
def root():
    return {
        "message": "CyberGuard AI backend is running",
        "status": "online",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "cyberguard-api",
    }


@app.get("/health/database")
def database_health_check():
    try:
        test_database_connection()

        return {
            "status": "healthy",
            "database": "postgresql",
        }

    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=503,
            detail=f"Database connection failed: {error}",
        )


@app.get("/api/v1/incidents", response_model=list[Incident])
def list_incidents():
    with SessionLocal() as database_session:
        incidents = database_session.scalars(
            select(IncidentModel).order_by(
                IncidentModel.detected_at.desc()
            )
        ).all()

        return incidents


@app.get("/api/v1/incidents/{incident_id}", response_model=Incident)
def get_incident(incident_id: int):
    with SessionLocal() as database_session:
        incident = database_session.get(IncidentModel, incident_id)

        if incident is None:
            raise HTTPException(
                status_code=404,
                detail="Incident not found",
            )

        return incident


@app.get("/api/v1/incidents/{incident_id}/analysis")
def get_incident_analysis(incident_id: int):
    with SessionLocal() as database_session:
        incident = database_session.get(IncidentModel, incident_id)

        if incident is None:
            raise HTTPException(
                status_code=404,
                detail="Incident not found",
            )

        return analyze_incident(incident)


@app.patch(
    "/api/v1/incidents/{incident_id}/status",
    response_model=Incident,
)
def update_incident_status(
    incident_id: int,
    payload: IncidentStatusUpdate,
):
    with SessionLocal() as database_session:
        incident = database_session.get(IncidentModel, incident_id)

        if incident is None:
            raise HTTPException(
                status_code=404,
                detail="Incident not found",
            )

        incident.status = payload.status
        database_session.commit()
        database_session.refresh(incident)

        return incident


@app.post(
    "/api/v1/incidents",
    response_model=Incident,
    status_code=201,
)
def create_incident(payload: IncidentCreate):
    new_incident = IncidentModel(
        threat_type=payload.threat_type,
        severity=payload.severity,
        confidence=payload.confidence,
        source_ip=payload.source_ip,
        target_service=payload.target_service,
        status=payload.status,
        detected_at=payload.detected_at or datetime.now(timezone.utc),
        evidence=payload.evidence,
    )

    with SessionLocal() as database_session:
        database_session.add(new_incident)
        database_session.commit()
        database_session.refresh(new_incident)

        return new_incident


@app.get("/api/v1/dashboard/summary")
def dashboard_summary():
    with SessionLocal() as database_session:
        total_threats = database_session.scalar(
            select(func.count()).select_from(IncidentModel)
        ) or 0

        critical_threats = database_session.scalar(
            select(func.count())
            .select_from(IncidentModel)
            .where(IncidentModel.severity == "CRITICAL")
        ) or 0

        high_threats = database_session.scalar(
            select(func.count())
            .select_from(IncidentModel)
            .where(IncidentModel.severity == "HIGH")
        ) or 0

        active_incidents = database_session.scalar(
            select(func.count())
            .select_from(IncidentModel)
            .where(IncidentModel.status != "RESOLVED")
        ) or 0

        return {
            "total_threats": total_threats,
            "critical_threats": critical_threats,
            "high_threats": high_threats,
            "active_incidents": active_incidents,
            "system_status": "MONITORING",
        }


@app.post(
    "/api/v1/detect/login",
    response_model=DetectionResponse,
)
def detect_login_threat(payload: LoginEvent):
    detection = analyze_login_event(
        failed_login_attempts=payload.failed_login_attempts,
        time_window_minutes=payload.time_window_minutes,
        source_ip=payload.source_ip,
        target_service=payload.target_service,
    )

    if detection is None:
        return {
            "detected": False,
            "message": "No suspicious login activity detected.",
        }

    new_incident = IncidentModel(
        threat_type=detection["threat_type"],
        severity=detection["severity"],
        confidence=detection["confidence"],
        source_ip=payload.source_ip,
        target_service=payload.target_service,
        status="OPEN",
        detected_at=datetime.now(timezone.utc),
        evidence=detection["evidence"],
    )

    with SessionLocal() as database_session:
        database_session.add(new_incident)
        database_session.commit()
        database_session.refresh(new_incident)

        return {
            "detected": True,
            "message": "Threat detected and saved as an incident.",
            "incident_id": new_incident.id,
            "threat_type": new_incident.threat_type,
            "severity": new_incident.severity,
            "confidence": new_incident.confidence,
        }


@app.get("/api/v1/ml/status")
def ml_model_status():
    return {
        "status": "ready" if MODEL_PATH.exists() else "model_not_found",
        "model": "Random Forest",
        "model_path": str(MODEL_PATH),
    }


def severity_from_probability(probability: float) -> str:
    if probability >= 0.90:
        return "CRITICAL"

    if probability >= 0.75:
        return "HIGH"

    return "MEDIUM"


@app.post(
    "/api/v1/ml/predict",
    response_model=FlowPredictionResponse,
)
def predict_network_flow(payload: FlowPredictionRequest):
    try:
        result = predict_flow(payload.features)

        if result["prediction"] == 1:
            severity = severity_from_probability(
                result["attack_probability"]
            )

            new_incident = IncidentModel(
                threat_type="ML-Detected Network Attack",
                severity=severity,
                confidence=result["attack_probability"],
                source_ip=payload.source_ip,
                target_service=payload.target_service,
                status="OPEN",
                detected_at=datetime.now(timezone.utc),
                evidence=[
                    "Detected by the Random Forest network-traffic model.",
                    f"Attack probability: "
                    f"{result['attack_probability']:.2%}",
                    f"Source IP: {payload.source_ip}",
                    f"Target service: {payload.target_service}",
                ],
            )

            with SessionLocal() as database_session:
                database_session.add(new_incident)
                database_session.commit()
                database_session.refresh(new_incident)

                result["incident_id"] = new_incident.id

        return result

    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error))

    except FileNotFoundError as error:
        raise HTTPException(status_code=503, detail=str(error))


MAX_ROWS_PER_UPLOAD = 500
MAX_INCIDENTS_PER_UPLOAD = 10


@app.post("/api/v1/ml/predict/csv")
async def predict_csv_file(
    file: UploadFile = File(...),
    source_ip: str = Form("unknown"),
    target_service: str = Form("Network Gateway"),
):
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Please upload a CSV file.",
        )

    try:
        file_content = await file.read()

        traffic_data = pd.read_csv(
            io.BytesIO(file_content),
            nrows=MAX_ROWS_PER_UPLOAD,
        )

    except Exception as error:
        raise HTTPException(
            status_code=400,
            detail=f"Unable to read CSV file: {error}",
        )

    try:
        predictions = predict_flows(traffic_data)

    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error))

    attack_predictions = [
        prediction
        for prediction in predictions
        if prediction["prediction"] == 1
    ]

    incidents_to_create = attack_predictions[
        :MAX_INCIDENTS_PER_UPLOAD
    ]

    if incidents_to_create:
        with SessionLocal() as database_session:
            for prediction in incidents_to_create:
                new_incident = IncidentModel(
                    threat_type="ML-Detected Network Attack",
                    severity=severity_from_probability(
                        prediction["attack_probability"]
                    ),
                    confidence=prediction["attack_probability"],
                    source_ip=source_ip,
                    target_service=target_service,
                    status="OPEN",
                    detected_at=datetime.now(timezone.utc),
                    evidence=[
                        "Detected during batch CSV analysis.",
                        f"CSV row: {prediction['row_number']}",
                        f"Attack probability: "
                        f"{prediction['attack_probability']:.2%}",
                        "Model: Random Forest",
                    ],
                )

                database_session.add(new_incident)

            database_session.commit()

    return {
        "filename": file.filename,
        "rows_analyzed": len(predictions),
        "attacks_detected": len(attack_predictions),
        "normal_flows": len(predictions) - len(attack_predictions),
        "incidents_created": len(incidents_to_create),
    }