from datetime import datetime, timezone
from typing import Literal

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


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


INCIDENTS = [
    Incident(
        id=1,
        threat_type="Brute Force Attempt",
        severity="HIGH",
        confidence=0.94,
        source_ip="192.0.2.45",
        target_service="SSH",
        status="OPEN",
        detected_at=datetime.now(timezone.utc),
        evidence=["147 failed login attempts in 3 minutes", "Repeated SSH authentication failures"],
    ),
    Incident(
        id=2,
        threat_type="Port Scan",
        severity="MEDIUM",
        confidence=0.87,
        source_ip="198.51.100.17",
        target_service="Web Server",
        status="INVESTIGATING",
        detected_at=datetime.now(timezone.utc),
        evidence=["Multiple ports probed in a short time window", "Unusual connection pattern"],
    ),
    Incident(
        id=3,
        threat_type="Malware-like Network Activity",
        severity="CRITICAL",
        confidence=0.98,
        source_ip="203.0.113.9",
        target_service="Endpoint Network",
        status="OPEN",
        detected_at=datetime.now(timezone.utc),
        evidence=["Known suspicious command-and-control pattern", "Unexpected outbound traffic volume"],
    ),
]


@app.get("/")
def root():
    return {"message": "CyberGuard AI backend is running", "status": "online"}


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "cyberguard-api"}


@app.get("/api/v1/incidents", response_model=list[Incident])
def list_incidents():
    return INCIDENTS


@app.get("/api/v1/incidents/{incident_id}", response_model=Incident)
def get_incident(incident_id: int):
    for incident in INCIDENTS:
        if incident.id == incident_id:
            return incident

    return {"error": "Incident not found"}


@app.get("/api/v1/dashboard/summary")
def dashboard_summary():
    return {
        "total_threats": len(INCIDENTS),
        "critical_threats": sum(item.severity == "CRITICAL" for item in INCIDENTS),
        "high_threats": sum(item.severity == "HIGH" for item in INCIDENTS),
        "active_incidents": sum(item.status != "RESOLVED" for item in INCIDENTS),
        "system_status": "MONITORING",
    }