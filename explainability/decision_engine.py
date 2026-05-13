from typing import List, Optional, dict
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

# ── AIRA DECISION ENGINE ──

class DecisionEngine:
    """
    AIRA's decision support system.
    Converts raw risk data into clear recommended actions.
    Closes the Decision-Support Systems gap for OpenKyber.
    """

    def __init__(self):
        from llm.claude_client import claude
        self.claude    = claude
        self.decisions = []

    def _run(self, prompt: str) -> str:
        try:
            return self.claude.think(
                system_prompt = (
                    "You are AIRA's decision engine. You analyse risk data "
                    "and provide clear, prioritised, actionable decisions "
                    "for identity and access management teams."
                ),
                user_message = prompt
            )
        except Exception as e:
            return f"Decision unavailable: {str(e)}"

    def recommend_action(
        self,
        identity_id:  str,
        risk_score:   float,
        risk_factors: List[str],
        context:      Optional[str] = None
    ) -> dict:
        """
        Recommend the best action for a given identity risk score.
        """
        prompt = (
            f"Identity {identity_id} has a risk score of {risk_score}/100.\n"
            f"Risk factors: {', '.join(risk_factors)}\n"
            f"Context: {context or 'None'}\n\n"
            f"Recommend the best course of action. Choose from:\n"
            f"1. No action required\n"
            f"2. Monitor closely\n"
            f"3. Reduce privileges\n"
            f"4. Require additional authentication\n"
            f"5. Suspend account pending review\n"
            f"6. Immediately disable account\n\n"
            f"Provide: recommended action, reasoning, urgency level, "
            f"and step-by-step implementation guide."
        )

        response  = self._run(prompt)
        urgency   = "critical" if risk_score >= 80 else "high" if risk_score >= 60 else "medium" if risk_score >= 40 else "low"

        result = {
            "identity_id":  identity_id,
            "risk_score":   risk_score,
            "risk_factors": risk_factors,
            "urgency":      urgency,
            "recommendation": response,
            "decided_at":   datetime.utcnow().isoformat()
        }

        self.decisions.append(result)
        return result

    def triage_alerts(self, alerts: List[dict]) -> dict:
        """
        Prioritise and triage multiple alerts simultaneously.
        """
        alerts_text = "\n".join([
            f"- Alert {i+1}: {a.get('type')} | "
            f"Severity: {a.get('severity')} | "
            f"Identity: {a.get('identity')}"
            for i, a in enumerate(alerts)
        ])

        prompt = (
            f"Triage these {len(alerts)} security alerts in priority order:\n\n"
            f"{alerts_text}\n\n"
            f"For each alert provide:\n"
            f"1. Priority rank (1 = most urgent)\n"
            f"2. Recommended action\n"
            f"3. Estimated response time\n"
            f"4. Who should handle it (SOC analyst / manager / CISO)"
        )

        response = self._run(prompt)

        result = {
            "alerts_triaged": len(alerts),
            "triage_plan":    response,
            "triaged_at":     datetime.utcnow().isoformat()
        }

        self.decisions.append(result)
        return result

    def approve_or_deny_access(
        self,
        requester:   str,
        resource:    str,
        reason:      str,
        risk_score:  float
    ) -> dict:
        """
        Make an automated approve or deny decision for an access request.
        """
        prompt = (
            f"Access Request Details:\n"
            f"Requester: {requester}\n"
            f"Resource: {resource}\n"
            f"Reason: {reason}\n"
            f"Requester Risk Score: {risk_score}/100\n\n"
            f"Make a decision: APPROVE, DENY, or ESCALATE TO HUMAN.\n"
            f"Provide: decision, confidence level (0-100%), conditions if approved, "
            f"and reasoning."
        )

        response = self._run(prompt)
        decision = "APPROVE" if risk_score < 40 else "ESCALATE" if risk_score < 70 else "DENY"

        result = {
            "requester":   requester,
            "resource":    resource,
            "risk_score":  risk_score,
            "decision":    decision,
            "analysis":    response,
            "decided_at":  datetime.utcnow().isoformat()
        }

        self.decisions.append(result)
        return result

    def summary(self) -> dict:
        """Return decision engine summary."""
        return {
            "total_decisions": len(self.decisions),
            "approved":        len([d for d in self.decisions if d.get("decision") == "APPROVE"]),
            "denied":          len([d for d in self.decisions if d.get("decision") == "DENY"]),
            "escalated":       len([d for d in self.decisions if d.get("decision") == "ESCALATE"]),
        }


# ── SINGLETON INSTANCE ──
decision_engine = DecisionEngine()

if __name__ == "__main__":
    print("Testing Decision Engine...")
    result = decision_engine.recommend_action(
        identity_id  = "USR-001",
        risk_score   = 82.5,
        risk_factors = ["5 failed logins", "off-hours access", "new device"],
        context      = "Finance department user accessing payroll system"
    )
    print(f"Urgency: {result['urgency']}")
    print(f"Recommendation:\n{result['recommendation'][:300]}")
    print(f"\nSummary: {decision_engine.summary()}")
    print("Decision Engine working correctly!")
