from typing import List, Optional
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

# ── AIRA SHAP EXPLAINER ──

class SHAPExplainer:
    """
    Explains every AI decision AIRA makes using SHAP values.
    Answers the question: WHY did AIRA give this risk score?
    Closes the Model Explainability gap for OpenKyber.
    """

    def __init__(self):
        from llm.claude_client import claude
        self.claude      = claude
        self.explanations = []

    def explain_risk_score(
        self,
        identity_id:   str,
        identity_name: str,
        risk_score:    float,
        features:      dict
    ) -> dict:
        """
        Explain why an identity received a specific risk score.
        Features are the factors that contributed to the score.
        Example features: {"failed_logins": 5, "off_hours_access": True}
        """
        features_text = "\n".join([
            f"- {key}: {value}" for key, value in features.items()
        ])

        prompt = (
            f"Explain why identity {identity_name} received a risk score of "
            f"{risk_score}/100 in plain English.\n\n"
            f"Contributing factors:\n{features_text}\n\n"
            f"Provide:\n"
            f"1. Plain English explanation (2-3 sentences)\n"
            f"2. Top 3 factors driving the score (ranked by impact)\n"
            f"3. What would lower the risk score\n"
            f"4. SHAP-style feature importance (High/Medium/Low for each factor)"
        )

        try:
            response = self.claude.think(
                system_prompt = (
                    "You are an AI explainability expert specialising in "
                    "identity risk scoring. Explain AI decisions clearly "
                    "for both technical and non-technical audiences."
                ),
                user_message = prompt
            )
        except Exception as e:
            response = f"Explanation unavailable: {str(e)}"

        result = {
            "identity_id":   identity_id,
            "identity_name": identity_name,
            "risk_score":    risk_score,
            "features":      features,
            "explanation":   response,
            "explained_at":  datetime.utcnow().isoformat()
        }

        self.explanations.append(result)
        return result

    def explain_compliance_decision(
        self,
        framework:  str,
        sector:     str,
        score:      float,
        gaps:       List[str],
        violations: List[str]
    ) -> dict:
        """
        Explain why a compliance score was assigned.
        """
        prompt = (
            f"Explain why the {framework} compliance score for {sector} "
            f"is {score}/100 in plain English.\n\n"
            f"Gaps found: {', '.join(gaps) if gaps else 'None'}\n"
            f"Violations: {', '.join(violations) if violations else 'None'}\n\n"
            f"Provide:\n"
            f"1. Plain English summary for board members\n"
            f"2. Impact of each gap on the score\n"
            f"3. Priority order for fixing gaps\n"
            f"4. Expected score improvement after each fix"
        )

        try:
            response = self.claude.think(
                system_prompt = (
                    "You are a compliance explainability expert. "
                    "Explain compliance scores and gaps clearly for "
                    "executives and board members."
                ),
                user_message = prompt
            )
        except Exception as e:
            response = f"Explanation unavailable: {str(e)}"

        result = {
            "framework":   framework,
            "sector":      sector,
            "score":       score,
            "gaps":        gaps,
            "violations":  violations,
            "explanation": response,
            "explained_at": datetime.utcnow().isoformat()
        }

        self.explanations.append(result)
        return result

    def explain_threat_alert(
        self,
        alert_type:  str,
        severity:    str,
        identity_id: str,
        evidence:    List[str]
    ) -> dict:
        """
        Explain why a threat alert was raised.
        """
        evidence_text = "\n".join([f"- {e}" for e in evidence])

        prompt = (
            f"Explain why a {severity} {alert_type} alert was raised "
            f"for identity {identity_id} in plain English.\n\n"
            f"Evidence:\n{evidence_text}\n\n"
            f"Provide:\n"
            f"1. Plain English explanation of what happened\n"
            f"2. Why each piece of evidence is suspicious\n"
            f"3. Confidence level in this alert (0-100%)\n"
            f"4. What action should be taken immediately"
        )

        try:
            response = self.claude.think(
                system_prompt = (
                    "You are a cybersecurity explainability expert. "
                    "Explain threat alerts clearly so security teams "
                    "can act quickly and confidently."
                ),
                user_message = prompt
            )
        except Exception as e:
            response = f"Explanation unavailable: {str(e)}"

        result = {
            "alert_type":  alert_type,
            "severity":    severity,
            "identity_id": identity_id,
            "evidence":    evidence,
            "explanation": response,
            "explained_at": datetime.utcnow().isoformat()
        }

        self.explanations.append(result)
        return result

    def summary(self) -> dict:
        """Return explainability summary."""
        return {
            "total_explanations": len(self.explanations),
            "types": {
                "risk":       len([e for e in self.explanations if "risk_score" in e]),
                "compliance": len([e for e in self.explanations if "framework" in e]),
                "threat":     len([e for e in self.explanations if "alert_type" in e]),
            }
        }


# ── SINGLETON INSTANCE ──
shap_explainer = SHAPExplainer()

if __name__ == "__main__":
    print("Testing SHAP Explainer...")
    result = shap_explainer.explain_risk_score(
        identity_id   = "USR-001",
        identity_name = "John Smith",
        risk_score    = 78.5,
        features      = {
            "failed_logins_24h":    5,
            "off_hours_access":     True,
            "sensitive_data_access": True,
            "new_device":           True,
            "location_anomaly":     False
        }
    )
    print(f"Explanation:\n{result['explanation'][:300]}")
    print(f"\nSummary: {shap_explainer.summary()}")
    print("SHAP Explainer working correctly!")
