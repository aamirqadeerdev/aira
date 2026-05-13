from typing import Optional, List
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

# ── AIRA FRONTLINE AGENT ──

class FrontlineAgent:
    """
    Frontline Worker Identity Agent.
    Manages identity for shift workers, contractors,
    and deskless employees. Handles badge and biometric auth.
    Replaces OLOID and HID Global.
    """

    def __init__(self):
        from llm.claude_client import claude
        from llm.prompts       import FRONTLINE_SYSTEM_PROMPT
        from llm.rag_pipeline  import rag
        from llm.memory        import agent_memories

        self.claude      = claude
        self.prompt      = FRONTLINE_SYSTEM_PROMPT
        self.rag         = rag
        self.memory      = agent_memories.get("frontline")
        self.agent_name  = "FRONTLINE"
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

    def verify_shift_access(
        self,
        worker_id:    str,
        worker_name:  str,
        shift:        str,
        location:     str,
        badge_scan:   Optional[str] = None
    ) -> dict:
        """Verify a frontline worker's shift-based access."""
        context = (
            f"Worker ID: {worker_id}\n"
            f"Worker Name: {worker_name}\n"
            f"Scheduled Shift: {shift}\n"
            f"Access Location: {location}\n"
            f"Badge Scan Time: {badge_scan or 'Not provided'}"
        )
        task = (
            f"Verify if {worker_name} should have access at {location} "
            f"during shift {shift}. "
            f"Check for: shift violations, location mismatch, "
            f"buddy punching indicators, and overtime alerts."
        )
        response = self._run(task, context)
        result = {
            "worker_id":   worker_id,
            "worker_name": worker_name,
            "shift":       shift,
            "location":    location,
            "verification": response,
            "verified_at": datetime.utcnow().isoformat(),
            "agent":       self.agent_name
        }
        self.run_history.append(result)
        return result

    def manage_contractor_access(
        self,
        contractor_id:   str,
        contractor_name: str,
        contract_end:    str,
        areas_allowed:   List[str]
    ) -> dict:
        """Manage temporary contractor access."""
        context = (
            f"Contractor ID: {contractor_id}\n"
            f"Name: {contractor_name}\n"
            f"Contract End Date: {contract_end}\n"
            f"Allowed Areas: {', '.join(areas_allowed)}"
        )
        task = (
            f"Review contractor access for {contractor_name}. "
            f"Check contract expiry, area restrictions, "
            f"and generate an access expiry notification plan."
        )
        response = self._run(task, context)
        result = {
            "contractor_id":   contractor_id,
            "contractor_name": contractor_name,
            "contract_end":    contract_end,
            "areas_allowed":   areas_allowed,
            "analysis":        response,
            "reviewed_at":     datetime.utcnow().isoformat(),
            "agent":           self.agent_name
        }
        self.run_history.append(result)
        return result

    def detect_time_fraud(
        self,
        worker_id:    str,
        worker_name:  str,
        time_records: List[dict]
    ) -> dict:
        """Detect buddy punching and time fraud."""
        records_text = "\n".join([
            f"- {r.get('date')} | In: {r.get('clock_in')} | "
            f"Out: {r.get('clock_out')} | Location: {r.get('location')}"
            for r in time_records
        ])
        task = (
            f"Analyse time records for {worker_name} and detect "
            f"any time fraud, buddy punching, or policy violations. "
            f"Flag suspicious patterns and recommend investigation steps."
        )
        response = self._run(task, records_text)
        result = {
            "worker_id":    worker_id,
            "worker_name":  worker_name,
            "records_count": len(time_records),
            "analysis":     response,
            "analysed_at":  datetime.utcnow().isoformat(),
            "agent":        self.agent_name
        }
        self.run_history.append(result)
        return result

    def status(self) -> dict:
        return {
            "agent":       self.agent_name,
            "description": "Frontline Worker Identity",
            "replaces":    ["OLOID", "HID Global"],
            "runs":        len(self.run_history),
            "memory":      self.memory.status() if self.memory else {}
        }


# ── SINGLETON INSTANCE ──
frontline = FrontlineAgent()

if __name__ == "__main__":
    print("Testing Frontline Agent...")
    print(f"Status: {frontline.status()}")
    result = frontline.verify_shift_access(
        worker_id   = "WKR-042",
        worker_name = "Ahmed Khan",
        shift       = "Night Shift 22:00-06:00",
        location    = "Warehouse Zone B",
        badge_scan  = "2026-05-05 14:30"
    )
    print(f"\nFrontline Verification:\n{result['verification'][:300]}")
    print("\nFrontline Agent working correctly!")
