from typing import Optional, List
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

# ── AIRA CIAM AGENT ──

class CIAMAgent:
    """
    Customer Identity & Access Management Agent.
    Manages customer authentication, detects account takeovers,
    enforces MFA, and protects customer privacy.
    Replaces Auth0 and Okta Customer Identity.
    """

    def __init__(self):
        from llm.claude_client import claude
        from llm.prompts       import CIAM_SYSTEM_PROMPT
        from llm.rag_pipeline  import rag
        from llm.memory        import agent_memories

        self.claude      = claude
        self.prompt      = CIAM_SYSTEM_PROMPT
        self.rag         = rag
        self.memory      = agent_memories.get("ciam")
        self.agent_name  = "CIAM"
        self.run_history = []

    def _run(self, task: str, context: str = "") -> str:
        rag_context    = self.rag.build_context(task, "policies")
        memory_context = self.memory.get_context() if self.memory else ""

        full_context = ""
        if rag_context:
            full_context += f"Policy Knowledge Base:\n{rag_context}\n\n"
        if memory_context and memory_context != "No relevant long term memories found.":
            full_context += f"Past Decisions:\n{memory_context}\n\n"
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

    def detect_account_takeover(
        self,
        customer_id:   str,
        login_events:  List[dict]
    ) -> dict:
        """Detect if a customer account has been taken over."""
        events_text = "\n".join([
            f"- {e.get('time')} | {e.get('location')} | "
            f"Device: {e.get('device', 'Unknown')} | "
            f"Success: {e.get('success', True)}"
            for e in login_events
        ])
        task = (
            f"Analyse login events for customer {customer_id} "
            f"and determine if account takeover is occurring. "
            f"Look for: credential stuffing, password spraying, "
            f"impossible travel, new device fingerprints. "
            f"Rate account takeover risk (0-100)."
        )
        response = self._run(task, events_text)
        result = {
            "customer_id":  customer_id,
            "events_count": len(login_events),
            "analysis":     response,
            "analysed_at":  datetime.utcnow().isoformat(),
            "agent":        self.agent_name
        }
        self.run_history.append(result)
        return result

    def enforce_mfa_policy(
        self,
        customer_id:  str,
        risk_score:   float,
        sector:       str
    ) -> dict:
        """Determine and enforce the appropriate MFA level."""
        context = (
            f"Customer ID: {customer_id}\n"
            f"Risk Score: {risk_score}/100\n"
            f"Sector: {sector}"
        )
        task = (
            f"Determine the appropriate MFA policy for customer {customer_id}. "
            f"Based on risk score and sector, recommend: "
            f"MFA method (SMS/TOTP/FIDO2/Biometric), "
            f"frequency, and step-up authentication triggers."
        )
        response = self._run(task, context)
        result = {
            "customer_id": customer_id,
            "risk_score":  risk_score,
            "sector":      sector,
            "mfa_policy":  response,
            "enforced_at": datetime.utcnow().isoformat(),
            "agent":       self.agent_name
        }
        self.run_history.append(result)
        return result

    def check_privacy_compliance(
        self,
        customer_id: str,
        data_held:   List[str],
        frameworks:  List[str]
    ) -> dict:
        """Check customer data privacy compliance."""
        context = (
            f"Customer ID: {customer_id}\n"
            f"Data Held: {', '.join(data_held)}\n"
            f"Frameworks: {', '.join(frameworks)}"
        )
        task = (
            f"Check if holding this customer data complies with "
            f"{', '.join(frameworks)}. "
            f"Identify any data that should not be held, "
            f"consent requirements, and data subject rights obligations."
        )
        response = self._run(task, context)
        result = {
            "customer_id": customer_id,
            "frameworks":  frameworks,
            "analysis":    response,
            "checked_at":  datetime.utcnow().isoformat(),
            "agent":       self.agent_name
        }
        self.run_history.append(result)
        return result

    def status(self) -> dict:
        return {
            "agent":       self.agent_name,
            "description": "Customer Identity & Access Management",
            "replaces":    ["Auth0", "Okta Customer Identity"],
            "runs":        len(self.run_history),
            "memory":      self.memory.status() if self.memory else {}
        }


# ── SINGLETON INSTANCE ──
ciam = CIAMAgent()

if __name__ == "__main__":
    print("Testing CIAM Agent...")
    print(f"Status: {ciam.status()}")
    result = ciam.detect_account_takeover(
        customer_id  = "CUST-001",
        login_events = [
            {"time": "2026-05-05 08:00", "location": "Lahore",   "device": "iPhone", "success": True},
            {"time": "2026-05-05 08:15", "location": "New York",  "device": "Unknown PC", "success": True},
            {"time": "2026-05-05 08:20", "location": "London",    "device": "Unknown PC", "success": False},
        ]
    )
    print(f"\nCIAM Analysis:\n{result['analysis'][:300]}")
    print("\nCIAM Agent working correctly!")
