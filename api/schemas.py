from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum

# ── ENUMS ──

class UserRole(str, Enum):
    admin        = "admin"
    analyst      = "analyst"
    auditor      = "auditor"
    viewer       = "viewer"

class RiskLevel(str, Enum):
    critical     = "critical"
    high         = "high"
    medium       = "medium"
    low          = "low"

class AgentStatus(str, Enum):
    online       = "online"
    warning      = "warning"
    alert        = "alert"
    offline      = "offline"

class ComplianceStatus(str, Enum):
    compliant    = "compliant"
    gap          = "gap"
    violation    = "violation"

# ── AUTH SCHEMAS ──

class LoginRequest(BaseModel):
    email:    EmailStr
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "email":    "admin@enterprise.com",
                "password": "SecurePassword123"
            }
        }

class TokenResponse(BaseModel):
    access_token:  str
    token_type:    str = "bearer"
    expires_in:    int = 3600
    user_email:    str
    user_role:     UserRole

# ── USER SCHEMAS ──

class UserBase(BaseModel):
    email:        EmailStr
    full_name:    str
    role:         UserRole
    sector:       Optional[str] = None
    organisation: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id:         int
    is_active:  bool
    created_at: datetime

    class Config:
        from_attributes = True

# ── IDENTITY SCHEMAS ──

class IdentityBase(BaseModel):
    identity_id:   str
    identity_type: str   # human, machine, robot, service_account
    name:          str
    department:    Optional[str] = None
    sector:        Optional[str] = None

class IdentityCreate(IdentityBase):
    pass

class IdentityResponse(IdentityBase):
    id:         int
    risk_score: float
    risk_level: RiskLevel
    created_at: datetime
    last_active: Optional[datetime] = None

    class Config:
        from_attributes = True

# ── RISK SCHEMAS ──

class RiskScoreRequest(BaseModel):
    identity_id: str
    context:     Optional[str] = None

class RiskScoreResponse(BaseModel):
    identity_id:  str
    risk_score:   float
    risk_level:   RiskLevel
    risk_factors: List[str]
    recommendation: str
    computed_at:  datetime

# ── AGENT SCHEMAS ──

class AgentStatusResponse(BaseModel):
    agent_name:    str
    status:        AgentStatus
    last_run:      Optional[datetime] = None
    identities_processed: int = 0
    alerts_raised: int = 0

class AgentRunRequest(BaseModel):
    agent_name:  str
    target_id:   Optional[str] = None
    sector:      Optional[str] = None

# ── COMPLIANCE SCHEMAS ──

class ComplianceCheckRequest(BaseModel):
    framework:   str   # HIPAA, GDPR, PCI-DSS, SOX, NIST etc.
    sector:      str
    identity_id: Optional[str] = None

class ComplianceCheckResponse(BaseModel):
    framework:       str
    sector:          str
    status:          ComplianceStatus
    score:           float
    gaps:            List[str]
    recommendations: List[str]
    checked_at:      datetime

# ── ALERT SCHEMAS ──

class AlertResponse(BaseModel):
    alert_id:    int
    identity_id: str
    alert_type:  str
    risk_level:  RiskLevel
    message:     str
    resolved:    bool = False
    created_at:  datetime

    class Config:
        from_attributes = True

# ── GENERAL RESPONSE ──

class APIResponse(BaseModel):
    success: bool
    message: str
    data:    Optional[dict] = None
