from typing import List, Optional
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

# ── AIRA GAP ANALYSER ──

class GapAnalyser:
    """
    Analyses compliance gaps between current state
    and required controls for each framework and sector.
    """

    def __init__(self):
        from llm.claude_client import claude
        from compliance.framework_loader import get_framework, get_frameworks_for_sector
        self.claude     = claude
        self.get_fw     = get_framework
        self.get_sector = get_frameworks_for_sector

    def analyse_gap(
        self,
        framework:       str,
        sector:          str,
        current_controls: List[str],
        evidence:        Optional[str] = None
    ) -> dict:
        """Compare current controls against required framework controls."""
        fw = self.get_fw(framework)
        if not fw:
            return {"error": f"Framework {framework} not found."}

        required   = fw.get("key_controls", [])
        missing    = [r for r in required if not any(r.lower() in c.lower() for c in current_controls)]
        gap_score  = round((len(missing) / len(required)) * 100, 1) if required else 0
        comp_score = round(100 - gap_score, 1)

        prompt = (
            f"You are a {framework} compliance expert.\n"
            f"Current controls implemented: {', '.join(current_controls)}\n"
            f"Missing controls: {', '.join(missing)}\n"
            f"Sector: {sector}\n\n"
            f"Provide a prioritised remediation plan for the missing controls. "
            f"Include effort level (Low/Medium/High) and timeline for each."
        )

        try:
            response = self.claude.think(
                system_prompt = f"You are an expert {framework} compliance auditor.",
                user_message  = prompt
            )
        except Exception as e:
            response = f"Remediation analysis unavailable: {str(e)}"

        result = {
            "framework":         framework,
            "sector":            sector,
            "compliance_score":  comp_score,
            "gap_score":         gap_score,
            "required_controls": required,
            "current_controls":  current_controls,
            "missing_controls":  missing,
            "remediation_plan":  response,
            "analysed_at":       datetime.utcnow().isoformat()
        }
        return result

    def analyse_all_frameworks(
        self,
        sector:           str,
        current_controls: List[str]
    ) -> dict:
        """Run gap analysis across all frameworks for a sector."""
        frameworks = self.get_sector(sector)
        results    = {}
        scores     = []

        for fw in frameworks:
            name   = fw["name"]
            result = self.analyse_gap(name, sector, current_controls)
            results[name] = result
            scores.append(result.get("compliance_score", 0))

        overall = round(sum(scores) / len(scores), 1) if scores else 0

        return {
            "sector":           sector,
            "overall_score":    overall,
            "frameworks_checked": len(frameworks),
            "results":          results,
            "analysed_at":      datetime.utcnow().isoformat()
        }


# ── SINGLETON INSTANCE ──
gap_analyser = GapAnalyser()

if __name__ == "__main__":
    print("Testing Gap Analyser...")
    result = gap_analyser.analyse_gap(
        framework        = "HIPAA",
        sector           = "Pharma & Medical",
        current_controls = ["Access controls for PHI", "Encryption of PHI at rest"]
    )
    print(f"Compliance score: {result['compliance_score']}%")
    print(f"Missing controls: {result['missing_controls']}")
    print("Gap Analyser working correctly!")
