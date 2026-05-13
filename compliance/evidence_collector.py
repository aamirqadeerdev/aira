from typing import List, Optional
from datetime import datetime
import os

# ── AIRA EVIDENCE COLLECTOR ──

class EvidenceCollector:
    """
    Automatically collects and organises compliance evidence
    for each framework control across all sectors.
    """

    def __init__(self):
        from llm.claude_client import claude
        self.claude       = claude
        self.evidence_log = []

    def collect(
        self,
        framework:   str,
        control_id:  str,
        evidence_type: str,
        content:     str,
        collected_by: str = "AIRA"
    ) -> dict:
        """Record a piece of compliance evidence."""
        record = {
            "id":            len(self.evidence_log) + 1,
            "framework":     framework,
            "control_id":    control_id,
            "evidence_type": evidence_type,
            "content":       content,
            "collected_by":  collected_by,
            "collected_at":  datetime.utcnow().isoformat(),
            "status":        "collected"
        }
        self.evidence_log.append(record)
        return record

    def get_evidence_for_framework(self, framework: str) -> List[dict]:
        """Return all evidence collected for a framework."""
        return [e for e in self.evidence_log if e["framework"] == framework]

    def generate_evidence_checklist(
        self,
        framework: str,
        sector:    str
    ) -> dict:
        """Generate a checklist of evidence required for a framework audit."""
        prompt = (
            f"Generate a detailed evidence checklist for a {framework} audit "
            f"in the {sector} sector. "
            f"For each required control list: "
            f"evidence type, document name, collection method, and responsible team."
        )
        try:
            response = self.claude.think(
                system_prompt = f"You are a {framework} compliance auditor.",
                user_message  = prompt
            )
        except Exception as e:
            response = f"Checklist generation unavailable: {str(e)}"

        return {
            "framework":  framework,
            "sector":     sector,
            "checklist":  response,
            "created_at": datetime.utcnow().isoformat()
        }

    def summary(self) -> dict:
        """Return evidence collection summary."""
        return {
            "total_evidence":  len(self.evidence_log),
            "frameworks":      list(set(e["framework"] for e in self.evidence_log)),
            "collected_today": len([
                e for e in self.evidence_log
                if e["collected_at"][:10] == datetime.utcnow().date().isoformat()
            ])
        }


# ── SINGLETON INSTANCE ──
evidence_collector = EvidenceCollector()

if __name__ == "__main__":
    print("Testing Evidence Collector...")
    record = evidence_collector.collect(
        framework    = "HIPAA",
        control_id   = "164.312(a)(1)",
        evidence_type = "Policy Document",
        content      = "Access control policy v2.1 approved by CISO on 2026-01-15",
        collected_by  = "AIRA Compliance Agent"
    )
    print(f"Evidence collected: {record['id']} — {record['evidence_type']}")
    print(f"Summary: {evidence_collector.summary()}")
    print("Evidence Collector working correctly!")
