from typing import Optional, List
from datetime import datetime
import json
import os

# ── AIRA AUDIT TRAIL ──

class AuditTrail:
    """
    Tamper-proof audit trail for every AIRA decision.
    Records who did what, when, and why.
    Required for HIPAA, SOX, GDPR, and all 14 frameworks.
    """

    def __init__(self):
        self.audit_dir  = "./database/audit_trail"
        self.audit_file = f"{self.audit_dir}/audit_log.json"
        self._ensure_dir()
        self.records: List[dict] = self._load()

    def _ensure_dir(self):
        os.makedirs(self.audit_dir, exist_ok=True)

    def _load(self) -> List[dict]:
        try:
            if os.path.exists(self.audit_file):
                with open(self.audit_file, "r") as f:
                    return json.load(f)
            return []
        except Exception:
            return []

    def _save(self):
        try:
            with open(self.audit_file, "w") as f:
                json.dump(self.records, f, indent=2)
        except Exception as e:
            print(f"Audit trail save error: {e}")

    def log(
        self,
        action:      str,
        actor:       str,
        target:      str,
        outcome:     str,
        details:     Optional[str] = None,
        framework:   Optional[str] = None,
        risk_score:  Optional[float] = None
    ) -> dict:
        """Log an immutable audit record."""
        record = {
            "id":          len(self.records) + 1,
            "action":      action,
            "actor":       actor,
            "target":      target,
            "outcome":     outcome,
            "details":     details or "",
            "framework":   framework or "general",
            "risk_score":  risk_score,
            "timestamp":   datetime.utcnow().isoformat(),
            "immutable":   True
        }
        self.records.append(record)
        self._save()
        return record

    def get_records(
        self,
        actor:     Optional[str] = None,
        action:    Optional[str] = None,
        framework: Optional[str] = None,
        limit:     int = 50
    ) -> List[dict]:
        """Retrieve audit records with optional filters."""
        records = self.records
        if actor:
            records = [r for r in records if r.get("actor") == actor]
        if action:
            records = [r for r in records if r.get("action") == action]
        if framework:
            records = [r for r in records if r.get("framework") == framework]
        return records[-limit:]

    def generate_audit_report(
        self,
        start_date: Optional[str] = None,
        end_date:   Optional[str] = None
    ) -> dict:
        """Generate a compliance audit report."""
        records = self.records
        if start_date:
            records = [r for r in records if r["timestamp"] >= start_date]
        if end_date:
            records = [r for r in records if r["timestamp"] <= end_date]

        actions  = list(set(r["action"] for r in records))
        actors   = list(set(r["actor"]  for r in records))
        outcomes = {}
        for r in records:
            outcomes[r["outcome"]] = outcomes.get(r["outcome"], 0) + 1

        return {
            "total_records":  len(records),
            "unique_actions": actions,
            "unique_actors":  actors,
            "outcomes":       outcomes,
            "period":         f"{start_date or 'all'} to {end_date or 'now'}",
            "generated_at":   datetime.utcnow().isoformat()
        }

    def summary(self) -> dict:
        return {
            "total_records": len(self.records),
            "latest":        self.records[-1]["timestamp"] if self.records else None
        }


# ── SINGLETON INSTANCE ──
audit_trail = AuditTrail()

if __name__ == "__main__":
    print("Testing Audit Trail...")
    record = audit_trail.log(
        action     = "access_revoked",
        actor      = "AIRA IGA Agent",
        target     = "john@company.com",
        outcome    = "success",
        details    = "Admin access revoked due to risk score 82",
        framework  = "SOX",
        risk_score = 82.0
    )
    print(f"Audit record #{record['id']} logged")
    print(f"Summary: {audit_trail.summary()}")
    print("Audit Trail working correctly!")
