from typing import Optional, List
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

# ── AIRA COMPLIANCE AGENT ──

class ComplianceAgent:
    """
    Compliance & Governance Agent.
    Covers 14 frameworks across 12 sectors.
    Detects gaps, violations, and generates evidence.
    """

    def __init__(self):
        from llm.claude_client import claude
        from llm.prompts       import COMPLIANCE_SYSTEM_PROMPT
        from llm.rag_pipeline  import rag
        from llm.memory        import agent_memories

        self.claude      = claude
        self.prompt      = COMPLIANCE_SYSTEM_PROMPT
        self.rag         = rag
        self.memory      = agent_memories.get("compliance")
        self.agent_name  = "COMPLIANCE"
        self.run_history = []

        self.frameworks = [
            "HIPAA", "GDPR", "PCI-DSS", "SOX", "NIST SP 800-53",
            "FISMA", "ITAR/EAR", "CMMC", "GLBA", "FDA 21 CFR Part 11",
            "FERPA", "NERC CIP", "IEC 62443", "ISO/SAE 21434"
        ]

        self.sectors = [
            "IT", "Defense & Aerospace", "Finance & Insurance",
            "Real Estate & Infrastructure", "Retail & Consumer Goods",
            "Media & Entertainment", "Logistics & Manufacturing",
            "Pharma & Medical", "Education", "Automotive",
            "Energy", "Robots & Humanoid Manufacturing"
        ]

    def _run(self, task: str, context: str = "") -> str:
        rag_context    = self.rag.build_context(task, "compliance")
        memory_context = self.memory.get_context("compliance") if self.memory else ""

        full_context = ""
        if rag_context:
            full_context += f"Compliance Knowledge Base:\n{rag_context}\n\n"
        if memory_context and memory_context != "No relevant long term memories found.":
            full_context += f"Past Compliance Checks:\n{memory_context}\n\n"
        if context:
            full_context += f"Current Data:\n{context}"

        user_message = f"Context:\n{full_context}\n\nTask:\n{task}"

        if self.memory:
            self.memory.remember("user", task)

        response = self.claude.think(
            system_prompt = self.prompt,
            user_message  = user_message
        )

        if self.memory:
            self.memory.remember("assistant", response)

        return response

    def check_framework_compliance(
        self,
        framework: str,
        sector:    str,
        evidence:  Optional[str] = None
    ) -> dict:
        context = (
            f"Framework: {framework}\n"
            f"Sector: {sector}\n"
            f"Evidence Provided: {evidence or 'None'}"
        )
        task = (
            f"Run a full {framework} compliance check for the {sector} sector. "
            f"Provide: compliance score (0-100), gaps found, violations, "
            f"required controls, and prioritised remediation steps."
        )
        response = self._run(task, context)
        result = {
            "framework":    framework,
            "sector":       sector,
            "analysis":     response,
            "checked_at":   datetime.utcnow().isoformat(),
            "agent":        self.agent_name
        }
        if self.memory:
            self.memory.memorise(
                memory_type = "compliance",
                content     = f"{framework} check for {sector}: {response[:200]}",
                metadata    = {"framework": framework, "sector": sector}
            )
        self.run_history.append(result)
        return result

    def map_sector_to_frameworks(self, sector: str) -> dict:
        task = (
            f"List all mandatory and recommended compliance frameworks "
            f"for the {sector} sector. Explain why each framework applies "
            f"and the penalties for non-compliance."
        )
        response = self._run(task)
        return {
            "sector":     sector,
            "mapping":    response,
            "mapped_at":  datetime.utcnow().isoformat(),
            "agent":      self.agent_name
        }

    def collect_evidence(
        self,
        framework:   str,
        control_id:  str,
        description: str
    ) -> dict:
        context = (
            f"Framework: {framework}\n"
            f"Control ID: {control_id}\n"
            f"Control Description: {description}"
        )
        task = (
            f"Define what evidence is required to demonstrate compliance "
            f"with {framework} control {control_id}. "
            f"List: required documents, system logs, screenshots, "
            f"policies, and how to collect each piece of evidence."
        )
        response = self._run(task, context)
        return {
            "framework":    framework,
            "control_id":   control_id,
            "evidence_plan": response,
            "created_at":   datetime.utcnow().isoformat(),
            "agent":        self.agent_name
        }

    def generate_board_compliance_report(
        self,
        sector: str
    ) -> dict:
        task = (
            f"Generate a board-ready compliance summary report for the {sector} sector. "
            f"Include: overall compliance health score, top 3 risks, "
            f"framework scores, urgent actions required, and 90-day roadmap. "
            f"Use plain English suitable for non-technical board members."
        )
        response = self._run(task)
        return {
            "sector":       sector,
            "report":       response,
            "generated_at": datetime.utcnow().isoformat(),
            "agent":        self.agent_name
        }

    def status(self) -> dict:
        return {
            "agent":       self.agent_name,
            "description": "Compliance & Governance",
            "frameworks":  len(self.frameworks),
            "sectors":     len(self.sectors),
            "runs":        len(self.run_history),
            "memory":      self.memory.status() if self.memory else {}
        }


# ── SINGLETON INSTANCE ──
compliance = ComplianceAgent()

if __name__ == "__main__":
    print("Testing Compliance Agent...")
    print(f"Status: {compliance.status()}")
    result = compliance.check_framework_compliance(
        framework = "HIPAA",
        sector    = "Pharma & Medical"
    )
    print(f"\nHIPAA Check:\n{result['analysis'][:300]}")
    print("\nCompliance Agent working correctly!")
