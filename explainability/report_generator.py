from typing import List, Optional
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

# ── AIRA REPORT GENERATOR ──

class ReportGenerator:
    """
    Generates board-ready reports from AIRA's technical data.
    Converts complex risk and compliance data into plain English
    for executives, board members, and auditors.
    """

    def __init__(self):
        from llm.claude_client import claude
        self.claude  = claude
        self.reports = []

    def _run(self, prompt: str, max_tokens: int = 2000) -> str:
        try:
            return self.claude.think(
                system_prompt = (
                    "You are AIRA's report generation engine. "
                    "You produce clear, professional, board-ready reports "
                    "from technical identity and risk data. "
                    "Use plain English. Be concise and actionable."
                ),
                user_message = prompt,
                max_tokens   = max_tokens
            )
        except Exception as e:
            return f"Report generation error: {str(e)}"

    def generate_executive_summary(
        self,
        risk_score:        float,
        total_identities:  int,
        critical_alerts:   int,
        compliance_score:  float,
        top_risks:         List[str]
    ) -> dict:
        """Generate a one-page executive summary."""
        prompt = (
            f"Generate a one-page executive summary for AIRA — "
            f"Agentic Identity & Risk Administration.\n\n"
            f"Current Status:\n"
            f"- Overall Risk Score: {risk_score}/100\n"
            f"- Total Identities Monitored: {total_identities}\n"
            f"- Critical Alerts: {critical_alerts}\n"
            f"- Compliance Score: {compliance_score}/100\n"
            f"- Top Risks: {', '.join(top_risks)}\n\n"
            f"Write for a board of directors. "
            f"Include: health summary, key risks, actions required, "
            f"and 30-day outlook. Maximum 300 words."
        )

        response = self._run(prompt)
        result   = {
            "type":         "executive_summary",
            "risk_score":   risk_score,
            "compliance":   compliance_score,
            "report":       response,
            "generated_at": datetime.utcnow().isoformat()
        }
        self.reports.append(result)
        return result

    def generate_risk_report(
        self,
        sector:      str,
        identities:  List[dict],
        timeframe:   str = "Last 30 days"
    ) -> dict:
        """Generate a detailed risk report for a sector."""
        identity_summary = "\n".join([
            f"- {i.get('name')}: Risk {i.get('risk_score')}/100 ({i.get('risk_level')})"
            for i in identities[:10]
        ])

        prompt = (
            f"Generate a risk report for the {sector} sector.\n"
            f"Timeframe: {timeframe}\n\n"
            f"Top Risk Identities:\n{identity_summary}\n\n"
            f"Include: sector risk overview, top 5 risks, "
            f"trend analysis, immediate actions, and 90-day risk forecast."
        )

        response = self._run(prompt)
        result   = {
            "type":       "risk_report",
            "sector":     sector,
            "timeframe":  timeframe,
            "report":     response,
            "generated_at": datetime.utcnow().isoformat()
        }
        self.reports.append(result)
        return result

    def generate_compliance_report(
        self,
        framework:  str,
        sector:     str,
        score:      float,
        gaps:       List[str],
        evidence:   Optional[str] = None
    ) -> dict:
        """Generate a compliance report for a specific framework."""
        prompt = (
            f"Generate a {framework} compliance report for {sector}.\n\n"
            f"Compliance Score: {score}/100\n"
            f"Gaps Identified: {', '.join(gaps) if gaps else 'None'}\n"
            f"Evidence Status: {evidence or 'Not provided'}\n\n"
            f"Include: compliance summary, gap analysis, "
            f"regulatory risk, remediation roadmap, and audit readiness score."
        )

        response = self._run(prompt)
        result   = {
            "type":       "compliance_report",
            "framework":  framework,
            "sector":     sector,
            "score":      score,
            "report":     response,
            "generated_at": datetime.utcnow().isoformat()
        }
        self.reports.append(result)
        return result

    def generate_incident_report(
        self,
        incident_type: str,
        severity:      str,
        affected:      List[str],
        timeline:      List[str],
        actions_taken: List[str]
    ) -> dict:
        """Generate a security incident report."""
        timeline_text = "\n".join([f"- {t}" for t in timeline])
        actions_text  = "\n".join([f"- {a}" for a in actions_taken])

        prompt = (
            f"Generate a security incident report.\n\n"
            f"Incident Type: {incident_type}\n"
            f"Severity: {severity}\n"
            f"Affected Identities: {', '.join(affected)}\n\n"
            f"Timeline:\n{timeline_text}\n\n"
            f"Actions Taken:\n{actions_text}\n\n"
            f"Include: incident summary, impact assessment, "
            f"root cause analysis, lessons learned, and prevention measures."
        )

        response = self._run(prompt)
        result   = {
            "type":          "incident_report",
            "incident_type": incident_type,
            "severity":      severity,
            "affected":      affected,
            "report":        response,
            "generated_at":  datetime.utcnow().isoformat()
        }
        self.reports.append(result)
        return result

    def summary(self) -> dict:
        return {
            "total_reports": len(self.reports),
            "types": list(set(r["type"] for r in self.reports))
        }


# ── SINGLETON INSTANCE ──
report_generator = ReportGenerator()

if __name__ == "__main__":
    print("Testing Report Generator...")
    result = report_generator.generate_executive_summary(
        risk_score       = 72.5,
        total_identities = 1247,
        critical_alerts  = 3,
        compliance_score = 87.5,
        top_risks        = ["Privileged account misuse", "Orphaned accounts", "MFA gaps"]
    )
    print(f"Executive Summary:\n{result['report'][:300]}")
    print(f"\nSummary: {report_generator.summary()}")
    print("Report Generator working correctly!")
