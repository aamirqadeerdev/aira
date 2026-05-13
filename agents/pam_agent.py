from typing import Optional, List
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

# ── AIRA PAM AGENT ──

class PAMAgent:
    """
    Privileged Access Management Agent.
    Monitors and controls privileged accounts,
    detects credential misuse and lateral movement.
    Replaces CyberArk and BeyondTrust.
    """

    def __init__(self):
        from llm.claude_client import claude
        from llm.prompts       import PAM_SYSTEM_PROMPT
        from llm.rag_pipeline  import rag
        from llm.memory        import agent_memories

        self.claude      = claude
        self.prompt      = PAM_SYSTEM_PROMPT
        self.rag         = rag
        self.memory      = agent_memories.get("pam")
        self.agent_name  = "PAM"
        self.run_history = []

    def _run(self, task: str, context: str = "") -> str:
        """Send a task to Claude using PAM system prompt."""
        rag_context    = self.rag.build_context(task, "policies")
        memory_context = self.memory.get_context("decision") if self.memory else ""

        full_context = ""
        if rag_context:
            full_context += f"Policy Knowledge Base:\n{rag_context}\n\n"
        if memory_context and memory_context != "No relevant long term memories found.":
            full_context += f"Past PAM Decisions:\n{memory_context}\n\n"
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

    # ── CORE PAM FUNCTIONS ──

    def analyse_privileged_account(
        self,
        account_id:    str,
        account_name:  str,
        privilege_level: str,
        last_activity: Optional[str] = None,
        access_history: Optional[List[str]] = None
    ) -> dict:
        """
        Analyse a privileged account for misuse and risk.
        """
        history_text = "\n".join(access_history) if access_history else "No history provided"

        context = (
            f"Account ID: {account_id}\n"
            f"Account Name: {account_name}\n"
            f"Privilege Level: {privilege_level}\n"
            f"Last Activity: {last_activity or 'Unknown'}\n"
            f"Recent Access History:\n{history_text}"
        )

        task = (
            f"Analyse privileged account {account_name} for signs of "
            f"misuse, credential sharing, or suspicious activity. "
            f"Provide a privilege risk score (0-100), detected anomalies, "
            f"and recommended actions including whether to revoke or restrict access."
        )

        response = self._run(task, context)

        result = {
            "account_id":      account_id,
            "account_name":    account_name,
            "privilege_level": privilege_level,
            "analysis":        response,
            "analysed_at":     datetime.utcnow().isoformat(),
            "agent":           self.agent_name
        }

        if self.memory:
            self.memory.memorise(
                memory_type = "decision",
                content     = f"PAM analysis for {account_name}: {response[:200]}",
                metadata    = {"account_id": account_id, "action": "analyse"}
            )

        self.run_history.append(result)
        return result

    def check_lateral_movement(
        self,
        identity_id:    str,
        access_pattern: List[str],
        timeframe:      str = "24 hours"
    ) -> dict:
        """
        Detect lateral movement — when an attacker moves
        from one system to another using stolen credentials.
        """
        pattern_text = "\n".join([
            f"- {access}" for access in access_pattern
        ])

        context = (
            f"Identity ID: {identity_id}\n"
            f"Timeframe: {timeframe}\n"
            f"Access Pattern:\n{pattern_text}"
        )

        task = (
            f"Analyse this access pattern for signs of lateral movement. "
            f"Look for: rapid access across multiple systems, "
            f"access at unusual times, access to systems not in job role, "
            f"and credential hopping. Rate the lateral movement risk (0-100)."
        )

        response = self._run(task, context)

        result = {
            "identity_id":     identity_id,
            "timeframe":       timeframe,
            "systems_accessed": len(access_pattern),
            "analysis":        response,
            "checked_at":      datetime.utcnow().isoformat(),
            "agent":           self.agent_name
        }

        self.run_history.append(result)
        return result

    def enforce_just_in_time_access(
        self,
        requester_id:   str,
        requester_name: str,
        resource:       str,
        duration_hours: int,
        justification:  str
    ) -> dict:
        """
        Evaluate and approve or deny a just-in-time
        privileged access request.
        """
        context = (
            f"Requester ID: {requester_id}\n"
            f"Requester Name: {requester_name}\n"
            f"Requested Resource: {resource}\n"
            f"Requested Duration: {duration_hours} hours\n"
            f"Justification: {justification}"
        )

        task = (
            f"Evaluate this just-in-time privileged access request. "
            f"Determine if the request is legitimate, "
            f"whether the duration is appropriate, "
            f"and what conditions should apply. "
            f"Provide: APPROVE or DENY decision with reasoning."
        )

        response = self._run(task, context)

        result = {
            "requester_id":   requester_id,
            "requester_name": requester_name,
            "resource":       resource,
            "duration_hours": duration_hours,
            "decision":       response,
            "requested_at":   datetime.utcnow().isoformat(),
            "agent":          self.agent_name
        }

        if self.memory:
            self.memory.memorise(
                memory_type = "decision",
                content     = f"JIT access for {requester_name} to {resource}: {response[:150]}",
                metadata    = {"requester_id": requester_id, "resource": resource}
            )

        self.run_history.append(result)
        return result

    def rotate_credentials(
        self,
        account_id:   str,
        account_name: str,
        account_type: str
    ) -> dict:
        """
        Generate a credential rotation plan for a privileged account.
        """
        context = (
            f"Account ID: {account_id}\n"
            f"Account Name: {account_name}\n"
            f"Account Type: {account_type}"
        )

        task = (
            f"Create a credential rotation plan for privileged account {account_name}. "
            f"Include: rotation frequency, steps to rotate safely, "
            f"systems that need updating, rollback procedure, "
            f"and verification steps after rotation."
        )

        response = self._run(task, context)

        return {
            "account_id":    account_id,
            "account_name":  account_name,
            "account_type":  account_type,
            "rotation_plan": response,
            "planned_at":    datetime.utcnow().isoformat(),
            "agent":         self.agent_name
        }

    def status(self) -> dict:
        """Return current PAM agent status."""
        return {
            "agent":       self.agent_name,
            "description": "Privileged Access Management",
            "replaces":    ["CyberArk", "BeyondTrust"],
            "runs":        len(self.run_history),
            "memory":      self.memory.status() if self.memory else {}
        }


# ── SINGLETON INSTANCE ──
pam = PAMAgent()


# ── QUICK TEST ──
if __name__ == "__main__":
    print("Testing PAM Agent...")
    print(f"Status: {pam.status()}")

    result = pam.analyse_privileged_account(
        account_id     = "ADM-001",
        account_name   = "svc_database_admin",
        privilege_level = "Domain Admin",
        last_activity  = "2026-05-04 03:22:00",
        access_history = [
            "Logged into PROD-DB-01 at 03:22",
            "Exported user table at 03:25",
            "Accessed PROD-DB-02 at 03:28",
            "Attempted access to FINANCE-DB at 03:31"
        ]
    )
    print(f"\nPAM Analysis:")
    print(result["analysis"][:300])
    print("\nPAM Agent working correctly!")
