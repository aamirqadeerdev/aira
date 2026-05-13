from typing import List, Optional
from datetime import datetime

# ── AIRA SECTOR MAPPER ──

SECTOR_FRAMEWORK_MAP = {
    "IT": [
        "NIST SP 800-53", "FISMA", "GDPR", "SOX"
    ],
    "Defense & Aerospace": [
        "CMMC", "ITAR/EAR", "NIST SP 800-53", "FISMA"
    ],
    "Finance & Insurance": [
        "SOX", "GLBA", "PCI-DSS", "GDPR", "NIST SP 800-53"
    ],
    "Real Estate & Infrastructure": [
        "GDPR", "NIST SP 800-53", "SOX"
    ],
    "Retail & Consumer Goods": [
        "PCI-DSS", "GDPR", "CCPA"
    ],
    "Media & Entertainment": [
        "GDPR", "CCPA", "NIST SP 800-53"
    ],
    "Logistics & Manufacturing": [
        "IEC 62443", "NIST SP 800-53", "GDPR"
    ],
    "Pharma & Medical": [
        "HIPAA", "FDA 21 CFR Part 11", "GDPR", "NIST SP 800-53"
    ],
    "Education": [
        "FERPA", "GDPR", "NIST SP 800-53", "COPPA"
    ],
    "Automotive": [
        "ISO/SAE 21434", "GDPR", "NIST SP 800-53"
    ],
    "Energy": [
        "NERC CIP", "IEC 62443", "NIST SP 800-53", "FISMA"
    ],
    "Robots & Humanoid Manufacturing": [
        "IEC 62443", "ISO/SAE 21434", "NIST SP 800-53", "GDPR"
    ]
}

SECTOR_RISK_PROFILES = {
    "IT":                             {"base_risk": 65, "top_threat": "Data breach"},
    "Defense & Aerospace":            {"base_risk": 90, "top_threat": "Nation-state attack"},
    "Finance & Insurance":            {"base_risk": 85, "top_threat": "Fraud and insider threat"},
    "Real Estate & Infrastructure":   {"base_risk": 60, "top_threat": "Ransomware"},
    "Retail & Consumer Goods":        {"base_risk": 70, "top_threat": "POS system compromise"},
    "Media & Entertainment":          {"base_risk": 55, "top_threat": "IP theft"},
    "Logistics & Manufacturing":      {"base_risk": 72, "top_threat": "OT/IT convergence attack"},
    "Pharma & Medical":               {"base_risk": 80, "top_threat": "PHI data breach"},
    "Education":                      {"base_risk": 58, "top_threat": "Student data exposure"},
    "Automotive":                     {"base_risk": 75, "top_threat": "Vehicle system compromise"},
    "Energy":                         {"base_risk": 88, "top_threat": "Critical infrastructure attack"},
    "Robots & Humanoid Manufacturing":{"base_risk": 78, "top_threat": "Machine identity compromise"}
}


def get_frameworks_for_sector(sector: str) -> List[str]:
    """Return all compliance frameworks for a sector."""
    return SECTOR_FRAMEWORK_MAP.get(sector, [])


def get_risk_profile(sector: str) -> Optional[dict]:
    """Return the risk profile for a sector."""
    return SECTOR_RISK_PROFILES.get(sector)


def get_all_sectors() -> List[str]:
    """Return all 12 AIRA sectors."""
    return list(SECTOR_FRAMEWORK_MAP.keys())


def get_sector_summary(sector: str) -> dict:
    """Return a complete sector summary including frameworks and risk."""
    return {
        "sector":     sector,
        "frameworks": get_frameworks_for_sector(sector),
        "risk":       get_risk_profile(sector),
        "queried_at": datetime.utcnow().isoformat()
    }


def get_all_sector_summaries() -> List[dict]:
    """Return summaries for all 12 sectors."""
    return [get_sector_summary(s) for s in get_all_sectors()]


if __name__ == "__main__":
    print("Testing Sector Mapper...")
    print(f"Total sectors: {len(get_all_sectors())}")
    summary = get_sector_summary("Finance & Insurance")
    print(f"Finance frameworks: {summary['frameworks']}")
    print(f"Finance risk: {summary['risk']}")
    print("Sector Mapper working correctly!")
