from anthropic import Anthropic
from typing import List, Optional
from dotenv import load_dotenv
from datetime import datetime
import os
import json

load_dotenv()

# ── AIRA NLP PROCESSOR ──

class NLPProcessor:
    """
    AIRA's Natural Language Processing engine.
    Reads and understands policies, compliance reports,
    and identity documents — extracting rules, risks,
    and actions automatically.
    """

    def __init__(self):
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model  = "claude-sonnet-4-20250514"

    def _ask_claude(self, prompt: str, max_tokens: int = 1000) -> str:
        """Send a prompt to Claude and return the response."""
        try:
            response = self.client.messages.create(
                model      = self.model,
                max_tokens = max_tokens,
                messages   = [{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            return f"NLP error: {str(e)}"

    # ── POLICY ANALYSIS ──

    def extract_rules_from_policy(self, policy_text: str) -> List[str]:
        """
        Extract all rules and requirements from a policy document.
        Returns a clean list of rules.
        """
        prompt = (
            f"You are an expert policy analyst for an enterprise IAM system.\n"
            f"Extract all rules, requirements, and obligations from this policy.\n"
            f"Return ONLY a JSON array of strings — one rule per item.\n"
            f"Example: [\"Rule 1\", \"Rule 2\"]\n\n"
            f"Policy:\n{policy_text}"
        )
        response = self._ask_claude(prompt)
        try:
            # Clean response and parse JSON
            clean = response.strip()
            if clean.startswith("```"):
                clean = clean.split("```")[1]
                if clean.startswith("json"):
                    clean = clean[4:]
            return json.loads(clean)
        except Exception:
            return [response]

    def classify_policy_type(self, policy_text: str) -> dict:
        """
        Classify a policy by type, framework, and sector.
        """
        prompt = (
            f"Classify this policy document for an enterprise IAM system.\n"
            f"Return ONLY a JSON object with these keys:\n"
            f"type, framework, sector, severity, summary\n\n"
            f"Policy:\n{policy_text[:1000]}"
        )
        response = self._ask_claude(prompt)
        try:
            clean = response.strip()
            if clean.startswith("```"):
                clean = clean.split("```")[1]
                if clean.startswith("json"):
                    clean = clean[4:]
            return json.loads(clean)
        except Exception:
            return {
                "type":      "unknown",
                "framework": "general",
                "sector":    "all",
                "severity":  "medium",
                "summary":   response[:200]
            }

    # ── COMPLIANCE REPORT ANALYSIS ──

    def analyse_compliance_report(
        self,
        report_text: str,
        framework:   str,
        sector:      str
    ) -> dict:
        """
        Analyse a compliance report and extract gaps, scores, and actions.
        """
        prompt = (
            f"You are a {framework} compliance expert for the {sector} sector.\n"
            f"Analyse this compliance report and return a JSON object with:\n"
            f"score (0-100), gaps (list), violations (list), "
            f"recommendations (list), summary (string)\n\n"
            f"Report:\n{report_text}"
        )
        response = self._ask_claude(prompt, max_tokens=1500)
        try:
            clean = response.strip()
            if clean.startswith("```"):
                clean = clean.split("```")[1]
                if clean.startswith("json"):
                    clean = clean[4:]
            return json.loads(clean)
        except Exception:
            return {
                "score":           0,
                "gaps":            [],
                "violations":      [],
                "recommendations": [],
                "summary":         response[:300]
            }

    # ── IDENTITY RISK ANALYSIS ──

    def analyse_identity_risk(
        self,
        identity_description: str,
        access_history:       Optional[str] = None
    ) -> dict:
        """
        Analyse an identity's risk profile from description and access history.
        """
        context = identity_description
        if access_history:
            context += f"\n\nAccess History:\n{access_history}"

        prompt = (
            f"You are an identity risk analyst for an enterprise IAM system.\n"
            f"Analyse this identity and return a JSON object with:\n"
            f"risk_score (0-100), risk_level (critical/high/medium/low), "
            f"risk_factors (list), recommendations (list)\n\n"
            f"Identity:\n{context}"
        )
        response = self._ask_claude(prompt)
        try:
            clean = response.strip()
            if clean.startswith("```"):
                clean = clean.split("```")[1]
                if clean.startswith("json"):
                    clean = clean[4:]
            return json.loads(clean)
        except Exception:
            return {
                "risk_score":      50,
                "risk_level":      "medium",
                "risk_factors":    [],
                "recommendations": []
            }

    # ── THREAT ANALYSIS ──

    def analyse_threat(self, threat_description: str) -> dict:
        """
        Analyse a security threat and classify its severity and type.
        """
        prompt = (
            f"You are a cybersecurity threat analyst.\n"
            f"Analyse this threat and return a JSON object with:\n"
            f"severity (critical/high/medium/low), threat_type (string), "
            f"affected_systems (list), immediate_actions (list), "
            f"mitre_attack_technique (string)\n\n"
            f"Threat:\n{threat_description}"
        )
        response = self._ask_claude(prompt)
        try:
            clean = response.strip()
            if clean.startswith("```"):
                clean = clean.split("```")[1]
                if clean.startswith("json"):
                    clean = clean[4:]
            return json.loads(clean)
        except Exception:
            return {
                "severity":               "medium",
                "threat_type":            "unknown",
                "affected_systems":       [],
                "immediate_actions":      [],
                "mitre_attack_technique": "unknown"
            }

    # ── PLAIN ENGLISH SUMMARY ──

    def generate_board_summary(
        self,
        technical_report: str,
        report_type:      str = "risk"
    ) -> str:
        """
        Convert a technical report into a plain English board-level summary.
        Suitable for non-technical executives and board members.
        """
        prompt = (
            f"Convert this technical {report_type} report into a clear, "
            f"plain English summary suitable for a board of directors.\n"
            f"Use simple language. Maximum 5 sentences. "
            f"Focus on business impact and required decisions.\n\n"
            f"Report:\n{technical_report}"
        )
        return self._ask_claude(prompt, max_tokens=300)


# ── SINGLETON INSTANCE ──
nlp = NLPProcessor()


# ── QUICK TEST ──
if __name__ == "__main__":
    print("Testing NLP Processor...")

    sample_policy = (
        "All employees must use multi-factor authentication. "
        "Passwords must be at least 12 characters. "
        "Privileged accounts must be reviewed quarterly. "
        "Access to sensitive data requires manager approval."
    )

    rules = nlp.extract_rules_from_policy(sample_policy)
    print(f"Extracted {len(rules)} rules from policy")
    for i, rule in enumerate(rules, 1):
        print(f"  Rule {i}: {rule}")

    print("NLP Processor working correctly!")
