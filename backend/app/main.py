from datetime import datetime, timezone
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError

from .database import Base, SessionLocal, engine, test_database_connection
from .models import IncidentModel
from .seed import seed_incidents
from .detection import analyze_login_event
from typing import Any
from app.ml_service import MODEL_PATH, predict_flow

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
    severity: Literal["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    confidence: float
    source_ip: str
    target_service: str
    status: Literal["OPEN", "INVESTIGATING", "RESOLVED"]
    detected_at: datetime
    evidence: list[str]

    model_config = ConfigDict(from_attributes=True)
    
class IncidentCreate(BaseModel):
    threat_type: str
    severity: Literal["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    confidence: float
    source_ip: str
    target_service: str
    status: Literal["OPEN", "INVESTIGATING", "RESOLVED"]
    evidence: list[str]
    detected_at: datetime | None = None
    
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


class FlowPredictionResponse(BaseModel):
    prediction: int
    classification: str
    attack_probability: float
    model: str


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
            detail="PostgreSQL database is unavailable.",
        ) from error
        
@app.post("/api/v1/detect/login", response_model=DetectionResponse)
def detect_login_threat(event: LoginEvent):
    detection = analyze_login_event(
        failed_login_attempts=event.failed_login_attempts,
        time_window_minutes=event.time_window_minutes,
        source_ip=event.source_ip,
        target_service=event.target_service,
    )

    if detection is None:
        return {
            "detected": False,
            "message": "No threat detected by the authentication rules.",
        }

    new_incident = IncidentModel(
        threat_type=detection["threat_type"],
        severity=detection["severity"],
        confidence=detection["confidence"],
        source_ip=event.source_ip,
        target_service=event.target_service,
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
            "message": "Threat detected and incident created.",
            "incident_id": new_incident.id,
            "threat_type": new_incident.threat_type,
            "severity": new_incident.severity,
            "confidence": new_incident.confidence,
        }
        
@app.post("/api/v1/incidents", response_model=Incident, status_code=201)
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


@app.get("/api/v1/incidents", response_model=list[Incident])
def list_incidents():
    with SessionLocal() as database_session:
        incidents = database_session.scalars(
            select(IncidentModel).order_by(IncidentModel.detected_at.desc())
        ).all()

        return incidents


@app.get("/api/v1/incidents/{incident_id}", response_model=Incident)
def get_incident(incident_id: int):
    with SessionLocal() as database_session:
        incident = database_session.get(IncidentModel, incident_id)

        if incident is None:
            raise HTTPException(status_code=404, detail="Incident not found.")

        return incident
    
@app.get("/api/v1/ml/status")
def ml_model_status():
    return {
        "status": "ready" if MODEL_PATH.exists() else "model_not_found",
        "model": "Random Forest",
        "model_path": str(MODEL_PATH),
    }


@app.post("/api/v1/ml/predict", response_model=FlowPredictionResponse)
def predict_network_flow(payload: FlowPredictionRequest):
    try:
        return predict_flow(payload.features)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error))
    except FileNotFoundError as error:
        raise HTTPException(status_code=503, detail=str(error))


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