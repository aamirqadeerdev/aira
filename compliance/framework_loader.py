from typing import Optional
from datetime import datetime

# ── AIRA FRAMEWORK LOADER ──

FRAMEWORKS = {
    "HIPAA": {
        "full_name":   "Health Insurance Portability and Accountability Act",
        "sectors":     ["Pharma & Medical", "IT"],
        "region":      "USA",
        "penalty":     "Up to $1.9M per violation category per year",
        "key_controls": [
            "Access controls for PHI",
            "Audit logs for all PHI access",
            "Encryption of PHI at rest and in transit",
            "Business Associate Agreements",
            "Workforce training"
        ]
    },
    "GDPR": {
        "full_name":   "General Data Protection Regulation",
        "sectors":     ["All sectors operating in EU"],
        "region":      "European Union",
        "penalty":     "Up to 4% of global annual turnover or €20M",
        "key_controls": [
            "Lawful basis for processing",
            "Data subject rights management",
            "Data breach notification within 72 hours",
            "Privacy by design",
            "Data Protection Officer appointment"
        ]
    },
    "PCI-DSS": {
        "full_name":   "Payment Card Industry Data Security Standard",
        "sectors":     ["Finance & Insurance", "Retail & Consumer Goods"],
        "region":      "Global",
        "penalty":     "$5,000 to $100,000 per month",
        "key_controls": [
            "Firewall configuration",
            "No default system passwords",
            "Protect stored cardholder data",
            "Encrypt transmission of cardholder data",
            "Maintain vulnerability management program"
        ]
    },
    "SOX": {
        "full_name":   "Sarbanes-Oxley Act",
        "sectors":     ["Finance & Insurance", "IT"],
        "region":      "USA",
        "penalty":     "Up to $5M fine and 20 years imprisonment",
        "key_controls": [
            "Internal controls over financial reporting",
            "CEO/CFO certification of financial statements",
            "Audit committee independence",
            "Real-time disclosure of material changes",
            "Document retention policies"
        ]
    },
    "NIST SP 800-53": {
        "full_name":   "NIST Security and Privacy Controls for Federal Systems",
        "sectors":     ["IT", "Defense & Aerospace", "Energy"],
        "region":      "USA",
        "penalty":     "Loss of federal contracts",
        "key_controls": [
            "Access control",
            "Audit and accountability",
            "Configuration management",
            "Incident response",
            "Risk assessment"
        ]
    },
    "CMMC": {
        "full_name":   "Cybersecurity Maturity Model Certification",
        "sectors":     ["Defense & Aerospace"],
        "region":      "USA",
        "penalty":     "Loss of DoD contracts",
        "key_controls": [
            "Access control",
            "Asset management",
            "Audit and accountability",
            "Configuration management",
            "Incident response"
        ]
    },
    "NERC CIP": {
        "full_name":   "North American Electric Reliability Corporation Critical Infrastructure Protection",
        "sectors":     ["Energy"],
        "region":      "North America",
        "penalty":     "Up to $1M per violation per day",
        "key_controls": [
            "BES Cyber System categorisation",
            "Security management controls",
            "Personnel and training",
            "Electronic security perimeters",
            "Physical security of BES Cyber Systems"
        ]
    },
    "IEC 62443": {
        "full_name":   "Industrial Automation and Control Systems Security",
        "sectors":     ["Logistics & Manufacturing", "Energy"],
        "region":      "Global",
        "penalty":     "Regulatory and reputational risk",
        "key_controls": [
            "Security management system",
            "Risk assessment",
            "System architecture",
            "Access control",
            "Incident response"
        ]
    },
    "ISO/SAE 21434": {
        "full_name":   "Road Vehicles Cybersecurity Engineering",
        "sectors":     ["Automotive"],
        "region":      "Global",
        "penalty":     "Market access restrictions",
        "key_controls": [
            "Cybersecurity management system",
            "Risk assessment methods",
            "Concept phase security",
            "Product development security",
            "Post-development security"
        ]
    },
    "FERPA": {
        "full_name":   "Family Educational Rights and Privacy Act",
        "sectors":     ["Education"],
        "region":      "USA",
        "penalty":     "Loss of federal funding",
        "key_controls": [
            "Student record access controls",
            "Parental rights management",
            "Directory information policies",
            "Third party disclosure controls",
            "Annual notification requirements"
        ]
    },
    "FISMA": {
        "full_name":   "Federal Information Security Management Act",
        "sectors":     ["IT", "Defense & Aerospace"],
        "region":      "USA",
        "penalty":     "Loss of federal funding and contracts",
        "key_controls": [
            "Information system inventory",
            "Risk categorisation",
            "Security plan",
            "Security controls implementation",
            "Annual security reviews"
        ]
    },
    "GLBA": {
        "full_name":   "Gramm-Leach-Bliley Act",
        "sectors":     ["Finance & Insurance"],
        "region":      "USA",
        "penalty":     "Up to $100,000 per violation",
        "key_controls": [
            "Financial privacy notices",
            "Opt-out rights",
            "Safeguards rule compliance",
            "Pretexting protection",
            "Data security program"
        ]
    },
    "FDA 21 CFR Part 11": {
        "full_name":   "FDA Electronic Records and Electronic Signatures",
        "sectors":     ["Pharma & Medical"],
        "region":      "USA",
        "penalty":     "Warning letters and product seizure",
        "key_controls": [
            "Electronic record controls",
            "Audit trail requirements",
            "Electronic signature controls",
            "System validation",
            "Authority checks"
        ]
    },
    "ITAR/EAR": {
        "full_name":   "International Traffic in Arms Regulations / Export Administration Regulations",
        "sectors":     ["Defense & Aerospace"],
        "region":      "USA",
        "penalty":     "Up to $1M per violation and criminal charges",
        "key_controls": [
            "Export licence management",
            "Technology control plans",
            "Foreign national access controls",
            "Record keeping",
            "Training programmes"
        ]
    }
}


def get_framework(name: str) -> Optional[dict]:
    """Return framework details by name."""
    return FRAMEWORKS.get(name)


def get_frameworks_for_sector(sector: str) -> list:
    """Return all frameworks applicable to a sector."""
    applicable = []
    for name, details in FRAMEWORKS.items():
        if sector in details["sectors"] or "All sectors operating in EU" in details["sectors"]:
            applicable.append({"name": name, **details})
    return applicable


def list_all_frameworks() -> list:
    """Return all 14 framework names."""
    return list(FRAMEWORKS.keys())


def get_framework_summary() -> dict:
    """Return a summary of all frameworks."""
    return {
        "total":      len(FRAMEWORKS),
        "frameworks": list(FRAMEWORKS.keys()),
        "loaded_at":  datetime.utcnow().isoformat()
    }


if __name__ == "__main__":
    print("Testing Framework Loader...")
    print(f"Total frameworks loaded: {len(FRAMEWORKS)}")
    hipaa = get_framework("HIPAA")
    print(f"HIPAA controls: {len(hipaa['key_controls'])}")
    pharma = get_frameworks_for_sector("Pharma & Medical")
    print(f"Pharma & Medical frameworks: {len(pharma)}")
    print("Framework Loader working correctly!")
