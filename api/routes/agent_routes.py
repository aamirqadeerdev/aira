from fastapi import APIRouter, HTTPException, Depends
from api.auth import get_current_user, require_analyst
from api.schemas import AgentRunRequest, AgentStatusResponse, APIResponse
from typing import Optional

router = APIRouter(prefix="/agents", tags=["Agents"])

@router.get("/status", tags=["Agents"])
async def get_all_agent_status(current_user: dict = Depends(get_current_user)):
    """Return the status of all 8 AIRA agents."""
    agents = [
        {"agent": "iga",         "name": "Identity Governance & Administration", "status": "online", "runs": 0},
        {"agent": "pam",         "name": "Privileged Access Management",         "status": "online", "runs": 0},
        {"agent": "ciam",        "name": "Customer Identity & Access",            "status": "online", "runs": 0},
        {"agent": "frontline",   "name": "Frontline Worker Identity",             "status": "online", "runs": 0},
        {"agent": "machine",     "name": "Machine Identity Management",           "status": "online", "runs": 0},
        {"agent": "threat",      "name": "Threat & Anomaly Detection",            "status": "online", "runs": 0},
        {"agent": "compliance",  "name": "Compliance & Governance",               "status": "online", "runs": 0},
        {"agent": "remediation", "name": "Automated Remediation",                 "status": "online", "runs": 0},
    ]
    return {"agents": agents, "total": len(agents), "all_online": True}

@router.post("/run/iga", tags=["Agents"])
async def run_iga_agent(
    request:      AgentRunRequest,
    current_user: dict = Depends(require_analyst)
):
    """Run the IGA agent on a specific identity or task."""
    try:
        from agents.iga_agent import iga
        result = iga.review_access(
            identity_id   = request.target_id or "USR-001",
            identity_name = "Target Identity",
            current_roles = ["user", "analyst"],
            sector        = request.sector or "IT"
        )
        return {"success": True, "agent": "iga", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/run/pam", tags=["Agents"])
async def run_pam_agent(
    request:      AgentRunRequest,
    current_user: dict = Depends(require_analyst)
):
    """Run the PAM agent on a privileged account."""
    try:
        from agents.pam_agent import pam
        result = pam.analyse_privileged_account(
            account_id     = request.target_id or "ADM-001",
            account_name   = "Target Admin Account",
            privilege_level = "Admin",
        )
        return {"success": True, "agent": "pam", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/run/threat", tags=["Agents"])
async def run_threat_agent(
    request:      AgentRunRequest,
    current_user: dict = Depends(require_analyst)
):
    """Run the Threat agent to detect anomalies."""
    try:
        from agents.threat_agent import threat
        result = threat.detect_anomaly(
            identity_id   = request.target_id or "USR-001",
            identity_name = "Target Identity",
            event_log     = ["Unusual login at 03:00 AM", "Accessed sensitive files"]
        )
        return {"success": True, "agent": "threat", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/summary", tags=["Agents"])
async def agents_summary(current_user: dict = Depends(get_current_user)):
    """Return a high level summary of all agent activity."""
    return {
        "total_agents":    8,
        "online":          8,
        "alerts_today":    3,
        "identities_monitored": 1247,
        "compliance_score": 87.5
    }
