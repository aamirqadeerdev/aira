from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Enum as SAEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

# ── ENUMS ──

class UserRoleEnum(enum.Enum):
    admin    = "admin"
    analyst  = "analyst"
    auditor  = "auditor"
    viewer   = "viewer"

class RiskLevelEnum(enum.Enum):
    critical = "critical"
    high     = "high"
    medium   = "medium"
    low      = "low"

class IdentityTypeEnum(enum.Enum):
    human           = "human"
    machine         = "machine"
    robot           = "robot"
    service_account = "service_account"
    iot_device      = "iot_device"

class AlertStatusEnum(enum.Enum):
    open     = "open"
    resolved = "resolved"
    ignored  = "ignored"

class ComplianceStatusEnum(enum.Enum):
    compliant = "compliant"
    gap       = "gap"
    violation = "violation"

# ── USER TABLE ──

class User(Base):
    __tablename__ = "users"

    id           = Column(Integer, primary_key=True, index=True)
    email        = Column(String(255), unique=True, index=True, nullable=False)
    full_name    = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role         = Column(SAEnum(UserRoleEnum), default=UserRoleEnum.viewer)
    organisation = Column(String(255), nullable=True)
    sector       = Column(String(100), nullable=True)
    is_active    = Column(Boolean, default=True)
    created_at   = Column(DateTime, default=datetime.utcnow)
    last_login   = Column(DateTime, nullable=True)

    # Relationships
    alerts       = relationship("Alert", back_populates="assigned_to_user")

    def __repr__(self):
        return f"<User {self.email} | {self.role.value}>"

# ── IDENTITY TABLE ──

class Identity(Base):
    __tablename__ = "identities"

    id             = Column(Integer, primary_key=True, index=True)
    identity_id    = Column(String(100), unique=True, index=True, nullable=False)
    identity_type  = Column(SAEnum(IdentityTypeEnum), nullable=False)
    name           = Column(String(255), nullable=False)
    department     = Column(String(100), nullable=True)
    sector         = Column(String(100), nullable=True)
    organisation   = Column(String(255), nullable=True)
    email          = Column(String(255), nullable=True)
    risk_score     = Column(Float, default=0.0)
    risk_level     = Column(SAEnum(RiskLevelEnum), default=RiskLevelEnum.low)
    is_active      = Column(Boolean, default=True)
    created_at     = Column(DateTime, default=datetime.utcnow)
    last_active    = Column(DateTime, nullable=True)

    # Relationships
    access_logs    = relationship("AccessLog", back_populates="identity")
    alerts         = relationship("Alert", back_populates="identity")
    compliance_records = relationship("ComplianceRecord", back_populates="identity")

    def __repr__(self):
        return f"<Identity {self.identity_id} | {self.identity_type.value} | Risk: {self.risk_level.value}>"

# ── ACCESS LOG TABLE ──

class AccessLog(Base):
    __tablename__ = "access_logs"

    id           = Column(Integer, primary_key=True, index=True)
    identity_id  = Column(Integer, ForeignKey("identities.id"), nullable=False)
    resource     = Column(String(255), nullable=False)
    action       = Column(String(100), nullable=False)
    ip_address   = Column(String(50), nullable=True)
    location     = Column(String(100), nullable=True)
    success      = Column(Boolean, default=True)
    risk_score   = Column(Float, default=0.0)
    timestamp    = Column(DateTime, default=datetime.utcnow)

    # Relationships
    identity     = relationship("Identity", back_populates="access_logs")

    def __repr__(self):
        return f"<AccessLog {self.action} on {self.resource} at {self.timestamp}>"

# ── ALERT TABLE ──

class Alert(Base):
    __tablename__ = "alerts"

    id              = Column(Integer, primary_key=True, index=True)
    identity_id     = Column(Integer, ForeignKey("identities.id"), nullable=False)
    assigned_to     = Column(Integer, ForeignKey("users.id"), nullable=True)
    alert_type      = Column(String(100), nullable=False)
    risk_level      = Column(SAEnum(RiskLevelEnum), nullable=False)
    message         = Column(Text, nullable=False)
    details         = Column(Text, nullable=True)
    status          = Column(SAEnum(AlertStatusEnum), default=AlertStatusEnum.open)
    resolved_at     = Column(DateTime, nullable=True)
    created_at      = Column(DateTime, default=datetime.utcnow)

    # Relationships
    identity        = relationship("Identity", back_populates="alerts")
    assigned_to_user = relationship("User", back_populates="alerts")

    def __repr__(self):
        return f"<Alert {self.alert_type} | {self.risk_level.value} | {self.status.value}>"

# ── COMPLIANCE RECORD TABLE ──

class ComplianceRecord(Base):
    __tablename__ = "compliance_records"

    id           = Column(Integer, primary_key=True, index=True)
    identity_id  = Column(Integer, ForeignKey("identities.id"), nullable=True)
    framework    = Column(String(100), nullable=False)
    sector       = Column(String(100), nullable=False)
    status       = Column(SAEnum(ComplianceStatusEnum), nullable=False)
    score        = Column(Float, default=0.0)
    gaps         = Column(Text, nullable=True)
    evidence     = Column(Text, nullable=True)
    checked_at   = Column(DateTime, default=datetime.utcnow)
    checked_by   = Column(String(100), nullable=True)

    # Relationships
    identity     = relationship("Identity", back_populates="compliance_records")

    def __repr__(self):
        return f"<ComplianceRecord {self.framework} | {self.sector} | {self.status.value}>"

# ── AGENT RUN LOG TABLE ──

class AgentRunLog(Base):
    __tablename__ = "agent_run_logs"

    id             = Column(Integer, primary_key=True, index=True)
    agent_name     = Column(String(100), nullable=False)
    status         = Column(String(50), nullable=False)
    identities_processed = Column(Integer, default=0)
    alerts_raised  = Column(Integer, default=0)
    duration_ms    = Column(Integer, default=0)
    error_message  = Column(Text, nullable=True)
    started_at     = Column(DateTime, default=datetime.utcnow)
    completed_at   = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<AgentRunLog {self.agent_name} | {self.status} | {self.started_at}>"
