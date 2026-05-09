"""
scoring.py — логика подсчёта риска на основе статистики VirusTotal.
Чем больше антивирусных движков помечают IOC как malicious,
тем выше уровень риска.
"""


def calculate_risk(stats: dict) -> tuple[str, str]:
    """
    Принимает словарь stats из VirusTotal.
    Возвращает кортеж (risk_level, recommendation).

    Логика:
    - malicious = 0            → Low
    - malicious 1–3            → Medium
    - malicious 4–10           → High
    - malicious > 10           → Critical
    """

    if not stats:
        return "Unknown", "No data available to assess risk."

    malicious = stats.get("malicious", 0)
    suspicious = stats.get("suspicious", 0)

    # Считаем общий "тревожный" счёт
    # suspicious весит меньше — не все движки точны
    threat_score = malicious + (suspicious * 0.5)

    if malicious == 0 and suspicious == 0:
        risk_level = "Low"
        recommendation = (
            "No threats detected. IOC appears clean according to VirusTotal. "
            "Continue standard monitoring procedures."
        )

    elif malicious == 0 and suspicious > 0:
        risk_level = "Low"
        recommendation = (
            f"Flagged as suspicious by {suspicious} engine(s) but no confirmed malicious detections. "
            "Monitor this IOC and correlate with other indicators."
        )

    elif 1 <= malicious <= 3:
        risk_level = "Medium"
        recommendation = (
            f"Detected as malicious by {malicious} engine(s). "
            "Investigate further. Check threat intelligence sources and correlate with logs. "
            "Consider blocking if context supports it."
        )

    elif 4 <= malicious <= 10:
        risk_level = "High"
        recommendation = (
            f"Detected as malicious by {malicious} engine(s). "
            "High confidence threat. Recommend immediate investigation, "
            "blocking at firewall/proxy, and escalation to Tier 2/3."
        )

    else:  # malicious > 10
        risk_level = "Critical"
        recommendation = (
            f"Detected as malicious by {malicious} engine(s). "
            "CRITICAL threat. Immediately isolate affected systems, block IOC at all controls, "
            "initiate incident response procedures, and notify stakeholders."
        )

    return risk_level, recommendation
