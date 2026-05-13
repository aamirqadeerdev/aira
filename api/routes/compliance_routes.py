from fastapi import APIRouter, HTTPException, Depends
from api.auth import get_current_user, require_analyst
from api.schemas import ComplianceCheckRequest, ComplianceCheckResponse, APIResponse
from datetime import datetime

router = APIRouter(prefix="/compliance", tags=["Compliance"])

# ── SUPPORTED FRAMEWORKS ──
FRAMEWORKS = [
    "HIPAA", "GDPR", "PCI-DSS", "SOX", "NIST SP 800-53",
    "FISMA", "ITAR/EAR", "CMMC", "GLBA", "FDA 21 CFR Part 11",
    "FERPA", "NERC CIP", "IEC 62443", "ISO/SAE 21434"
]

# ── SUPPORTED SECTORS ──
SECTORS = [
    "IT", "Defense & Aerospace", "Finance & Insurance",
    "Real Estate & Infrastructure", "Retail & Consumer Goods",
    "Media & Entertainment", "Logistics & Manufacturing",
    "Pharma & Medical", "Education", "Automotive",
    "Energy", "Robots & Humanoid Manufacturing"
]

@router.get("/frameworks", tags=["Compliance"])
async def list_frameworks(current_user: dict = Depends(get_current_user)):
    """Return all 14 supported compliance frameworks."""
    return {"frameworks": FRAMEWORKS, "total": len(FRAMEWORKS)}

@router.get("/sectors", tags=["Compliance"])
async def list_sectors(current_user: dict = Depends(get_current_user)):
    """Return all 12 supported industry sectors."""
    return {"sectors": SECTORS, "total": len(SECTORS)}

@router.post("/check", tags=["Compliance"])
async def run_compliance_check(
    request:      ComplianceCheckRequest,
    current_user: dict = Depends(require_analyst)
):
    """Run a compliance check for a framework and sector."""
    if request.framework not in FRAMEWORKS:
        raise HTTPException(
            status_code=400,
            detail=f"Framework '{request.framework}' not supported. "
                   f"Supported: {', '.join(FRAMEWORKS)}"
        )
    try:
        from agents.orchestrator import orchestrator
        result = orchestrator.run_agent(
            agent_name = "compliance",
            task       = (
                f"Run a compliance check for {request.framework} "
                f"in the {request.sector} sector. "
                f"Identify gaps, violations, and provide a compliance score."
            ),
            collection = "compliance"
        )
        return {
            "success":    True,
            "framework":  request.framework,
            "sector":     request.sector,
            "result":     result,
            "checked_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/score/{sector}", tags=["Compliance"])
async def get_compliance_score(
    sector:       str,
    current_user: dict = Depends(get_current_user)
):
    """Return compliance scores for a sector across all frameworks."""
    # Demo scores — replaced by real agent data in production
    demo_scores = {
        "HIPAA":            88.5,
        "GDPR":             92.0,
        "PCI-DSS":          79.5,
        "SOX":              85.0,
        "NIST SP 800-53":   83.5,
        "FISMA":            78.0,
        "ITAR/EAR":         91.0,
        "CMMC":             76.5,
        "GLBA":             88.0,
        "FDA 21 CFR Part 11": 82.5,
        "FERPA":            90.0,
        "NERC CIP":         74.0,
        "IEC 62443":        80.5,
        "ISO/SAE 21434":    77.0
    }
    overall = round(sum(demo_scores.values()) / len(demo_scores), 1)
    return {
        "sector":         sector,
        "overall_score":  overall,
        "framework_scores": demo_scores,
        "total_frameworks": len(demo_scores)
    }
