from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import IncidentModel


def seed_incidents(db: Session):
    existing_incident = db.scalar(select(IncidentModel.id).limit(1))

    if existing_incident is not None:
        return

    db.add_all(
        [
            IncidentModel(
                threat_type="Brute Force Attempt",
                severity="HIGH",
                confidence=0.94,
                source_ip="192.0.2.45",
                target_service="SSH",
                status="OPEN",
                detected_at=datetime.now(timezone.utc),
                evidence=[
                    "147 failed login attempts in 3 minutes",
                    "Repeated SSH authentication failures",
                ],
            ),
            IncidentModel(
                threat_type="Port Scan",
                severity="MEDIUM",
                confidence=0.87,
                source_ip="198.51.100.17",
                target_service="Web Server",
                status="INVESTIGATING",
                detected_at=datetime.now(timezone.utc),
                evidence=[
                    "Multiple ports probed in a short time window",
                    "Unusual connection pattern",
                ],
            ),
            IncidentModel(
                threat_type="Malware-like Network Activity",
                severity="CRITICAL",
                confidence=0.98,
                source_ip="203.0.113.9",
                target_service="Endpoint Network",
                status="OPEN",
                detected_at=datetime.now(timezone.utc),
                evidence=[
                    "Known suspicious command-and-control pattern",
                    "Unexpected outbound traffic volume",
                ],
            ),
        ]
    )
    db.commit()