def analyze_login_event(
    failed_login_attempts: int,
    time_window_minutes: int,
    source_ip: str,
    target_service: str,
):
    attempts_per_minute = failed_login_attempts / time_window_minutes

    if failed_login_attempts >= 100 and time_window_minutes <= 10:
        return {
            "threat_type": "Brute Force Attempt",
            "severity": "HIGH",
            "confidence": 0.94,
            "evidence": [
                f"{failed_login_attempts} failed login attempts in {time_window_minutes} minutes",
                f"High authentication-failure rate: {attempts_per_minute:.1f} attempts/minute",
                f"Target service: {target_service}",
            ],
        }

    if failed_login_attempts >= 20:
        return {
            "threat_type": "Suspicious Login Activity",
            "severity": "MEDIUM",
            "confidence": 0.81,
            "evidence": [
                f"{failed_login_attempts} failed login attempts detected",
                f"Source IP: {source_ip}",
                "Threshold for suspicious authentication activity exceeded",
            ],
        }

    return None