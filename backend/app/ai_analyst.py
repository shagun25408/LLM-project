from app.models import IncidentModel


def get_recommended_actions(threat_type: str) -> list[str]:
    threat = threat_type.lower()

    if "brute force" in threat or "login" in threat:
        return [
            "Temporarily block or rate-limit the source IP address.",
            "Review authentication logs for affected accounts.",
            "Require multi-factor authentication for targeted accounts.",
            "Reset credentials if account compromise is suspected.",
        ]

    if "port scan" in threat:
        return [
            "Review firewall logs for reconnaissance activity.",
            "Block repeated scan sources when appropriate.",
            "Verify that unnecessary ports are closed.",
            "Monitor the source IP for follow-up attack activity.",
        ]

    if "malware" in threat or "network attack" in threat:
        return [
            "Investigate the affected host and network session.",
            "Preserve relevant logs for incident-response review.",
            "Block suspicious network indicators if validated.",
            "Check endpoint-protection alerts and isolate affected assets if needed.",
        ]

    return [
        "Review the incident evidence and related security logs.",
        "Validate whether the source IP is expected.",
        "Monitor for repeated activity from the same source.",
        "Escalate to the security team if the activity continues.",
    ]


def get_severity_reason(incident: IncidentModel) -> str:
    confidence_percent = round(incident.confidence * 100, 1)

    if incident.severity == "CRITICAL":
        return (
            f"This is CRITICAL because the detection confidence is "
            f"{confidence_percent}% and the incident may require urgent "
            f"containment."
        )

    if incident.severity == "HIGH":
        return (
            f"This is HIGH severity because the detection confidence is "
            f"{confidence_percent}% and the activity indicates a meaningful "
            f"security risk."
        )

    if incident.severity == "MEDIUM":
        return (
            f"This is MEDIUM severity because the confidence is "
            f"{confidence_percent}%. Investigation is recommended before "
            f"taking broader action."
        )

    return (
        f"This is LOW severity with {confidence_percent}% confidence. "
        f"Continue monitoring for repeated or escalating activity."
    )


def analyze_incident(incident: IncidentModel) -> dict:
    confidence_percent = round(incident.confidence * 100, 1)

    return {
        "analyst": "CyberGuard AI Analyst",
        "threat_summary": (
            f"{incident.threat_type} was detected against "
            f"{incident.target_service} from source {incident.source_ip}."
        ),
        "attack_type": incident.threat_type,
        "severity_reason": get_severity_reason(incident),
        "confidence": confidence_percent,
        "recommended_actions": get_recommended_actions(incident.threat_type),
        "automation_note": (
            "Recommendations are advisory only. CyberGuard AI does not "
            "automatically block systems or modify infrastructure."
        ),
    }