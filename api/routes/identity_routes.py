from fastapi import APIRouter, HTTPException, Depends
from api.schemas import IdentityCreate, IdentityResponse, APIResponse
from api.auth import get_current_user, require_analyst
from typing import List, Optional

router = APIRouter(prefix="/identities", tags=["Identities"])

# ── DEMO DATA ──
DEMO_IDENTITIES = [
    {
        "id": 1, "identity_id": "USR-001", "identity_type": "human",
        "name": "John Smith", "department": "Finance",
        "sector": "Finance & Insurance", "risk_score": 72.5,
        "risk_level": "high", "is_active": True
    },
    {
        "id": 2, "identity_id": "SVC-001", "identity_type": "service_account",
        "name": "svc_database_admin", "department": "IT",
        "sector": "IT", "risk_score": 88.0,
        "risk_level": "critical", "is_active": True
    },
    {
        "id": 3, "identity_id": "BOT-001", "identity_type": "robot",
        "name": "Assembly Robot AR-7", "department": "Manufacturing",
        "sector": "Logistics & Manufacturing", "risk_score": 35.0,
        "risk_level": "low", "is_active": True
    },
]

@router.get("/", tags=["Identities"])
async def list_identities(
    sector:        Optional[str] = None,
    risk_level:    Optional[str] = None,
    identity_type: Optional[str] = None,
    current_user:  dict = Depends(get_current_user)
):
    """Return all identities with optional filters."""
    identities = DEMO_IDENTITIES
    if sector:
        identities = [i for i in identities if i.get("sector") == sector]
    if risk_level:
        identities = [i for i in identities if i.get("risk_level") == risk_level]
    if identity_type:
        identities = [i for i in identities if i.get("identity_type") == identity_type]
    return {"identities": identities, "total": len(identities)}

@router.get("/{identity_id}", tags=["Identities"])
async def get_identity(
    identity_id:  str,
    current_user: dict = Depends(get_current_user)
):
    """Return a single identity by ID."""
    identity = next(
        (i for i in DEMO_IDENTITIES if i["identity_id"] == identity_id), None
    )
    if not identity:
        raise HTTPException(status_code=404, detail=f"Identity {identity_id} not found.")
    return identity

@router.get("/stats/summary", tags=["Identities"])
async def identity_stats(current_user: dict = Depends(get_current_user)):
    """Return identity statistics for the dashboard."""
    return {
        "total":          len(DEMO_IDENTITIES),
        "human":          len([i for i in DEMO_IDENTITIES if i["identity_type"] == "human"]),
        "machine":        len([i for i in DEMO_IDENTITIES if i["identity_type"] in ["robot", "service_account"]]),
        "critical_risk":  len([i for i in DEMO_IDENTITIES if i["risk_level"] == "critical"]),
        "high_risk":      len([i for i in DEMO_IDENTITIES if i["risk_level"] == "high"]),
        "medium_risk":    len([i for i in DEMO_IDENTITIES if i["risk_level"] == "medium"]),
        "low_risk":       len([i for i in DEMO_IDENTITIES if i["risk_level"] == "low"]),
    }
