from typing import Optional, List
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

# ── AIRA IGA AGENT ──

class IGAAgent:
    """
    Identity Governance & Administration Agent.
    Reviews, certifies, and governs all user access rights.
    Replaces SailPoint IdentityNow and Saviynt.
    """

    def __init__(self):
        from llm.claude_client import claude
        from llm.prompts       import IGA_SYSTEM_PROMPT
        from llm.rag_pipeline  import rag
        from llm.memory        import agent_memories

        self.claude      = claude
        self.prompt      = IGA_SYSTEM_PROMPT
        self.rag         = rag
        self.memory      = agent_memories.get("iga")
        self.agent_name  = "IGA"
        self.run_history = []

    def _run(self, task: str, context: str = "") -> str:
        """Send a task to Claude using IGA system prompt."""
        rag_context = self.rag.build_context(
            query      = task,
            collection = "policies"
        )
        memory_context = self.memory.get_context("decision") if self.memory else ""

        full_context = ""
        if rag_context:
            full_context += f"Policy Knowledge Base:\n{rag_context}\n\n"
        if memory_context and memory_context != "No relevant long term memories found.":
            full_context += f"Past IGA Decisions:\n{memory_context}\n\n"
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

    # ── CORE IGA FUNCTIONS ──

    def review_access(
        self,
        identity_id:   str,
        identity_name: str,
        current_roles: List[str],
        department:    Optional[str] = None,
        sector:        Optional[str] = None
    ) -> dict:
        """
        Review an identity's current access rights.
        Detects excessive privileges and policy violations.
        """
        context = (
            f"Identity ID: {identity_id}\n"
            f"Name: {identity_name}\n"
            f"Department: {department or 'Unknown'}\n"
            f"Sector: {sector or 'General'}\n"
            f"Current Roles: {', '.join(current_roles)}"
        )

        task = (
            f"Review the access rights for {identity_name}. "
            f"Identify excessive privileges, policy violations, "
            f"and separation of duties conflicts. "
            f"Provide a risk score (0-100) and recommended actions."
        )

        response = self._run(task, context)

        result = {
            "identity_id":   identity_id,
            "identity_name": identity_name,
            "roles_reviewed": current_roles,
            "analysis":      response,
            "reviewed_at":   datetime.utcnow().isoformat(),
            "agent":         self.agent_name
        }

        # Store important decisions in long term memory
        if self.memory:
            self.memory.memorise(
                memory_type = "decision",
                content     = f"Access review for {identity_name}: {response[:200]}",
                metadata    = {"identity_id": identity_id, "action": "review"}
            )

        self.run_history.append(result)
        return result

    def certify_access(
        self,
        identity_id:   str,
        identity_name: str,
        roles:         List[str],
        certifier:     str
    ) -> dict:
        """
        Certify that an identity's access is appropriate and approved.
        """
        context = (
            f"Identity: {identity_name} (ID: {identity_id})\n"
            f"Roles to certify: {', '.join(roles)}\n"
            f"Certifier: {certifier}"
        )

        task = (
            f"Certify the access rights for {identity_name}. "
            f"Confirm each role is appropriate for their job function. "
            f"Flag any roles that should NOT be certified."
        )

        response = self._run(task, context)

        result = {
            "identity_id":   identity_id,
            "identity_name": identity_name,
            "certified_by":  certifier,
            "roles":         roles,
            "certification": response,
            "certified_at":  datetime.utcnow().isoformat(),
            "agent":         self.agent_name
        }

        if self.memory:
            self.memory.memorise(
                memory_type = "decision",
                content     = f"Access certified for {identity_name} by {certifier}",
                metadata    = {"identity_id": identity_id, "action": "certify"}
            )

        self.run_history.append(result)
        return result

    def detect_orphaned_accounts(
        self,
        accounts: List[dict]
    ) -> dict:
        """
        Detect orphaned accounts — accounts with no active owner.
        Common after employee departures.
        """
        accounts_text = "\n".join([
            f"- {a.get('name', 'Unknown')} | "
            f"Last login: {a.get('last_login', 'Never')} | "
            f"Status: {a.get('status', 'Unknown')}"
            for a in accounts
        ])

        task = (
            f"Analyse these {len(accounts)} accounts and identify "
            f"which ones are orphaned, stale, or should be disabled. "
            f"An orphaned account has no active owner or has not been "
            f"used in over 90 days. Provide a prioritised list."
        )

        response = self._run(task, accounts_text)

        return {
            "accounts_analysed": len(accounts),
            "analysis":          response,
            "analysed_at":       datetime.utcnow().isoformat(),
            "agent":             self.agent_name
        }

    def check_separation_of_duties(
        self,
        identity_name: str,
        roles:         List[str]
    ) -> dict:
        """
        Check if an identity has conflicting roles that
        violate separation of duties policies.
        """
        context = (
            f"Identity: {identity_name}\n"
            f"Roles held: {', '.join(roles)}"
        )

        task = (
            f"Check if {identity_name} has any separation of duties "
            f"conflicts in their current roles. "
            f"For example: a person should not be able to both "
            f"create and approve financial transactions. "
            f"List all conflicts found and recommended resolutions."
        )

        response = self._run(task, context)

        return {
            "identity_name": identity_name,
            "roles_checked": roles,
            "sod_analysis":  response,
            "checked_at":    datetime.utcnow().isoformat(),
            "agent":         self.agent_name
        }

    def generate_access_review_report(
        self,
        sector:    str,
        framework: str = "SOX"
    ) -> dict:
        """
        Generate a board-ready access review report
        for a specific sector and compliance framework.
        """
        task = (
            f"Generate a comprehensive access review report for the "
            f"{sector} sector aligned to {framework} compliance requirements. "
            f"Include: overall access risk score, key findings, "
            f"policy violations summary, and recommended actions. "
            f"Format for board-level presentation."
        )

        response = self._run(task)

        return {
            "sector":       sector,
            "framework":    framework,
            "report":       response,
            "generated_at": datetime.utcnow().isoformat(),
            "agent":        self.agent_name
        }

    def status(self) -> dict:
        """Return current IGA agent status."""
        return {
            "agent":       self.agent_name,
            "description": "Identity Governance & Administration",
            "replaces":    ["SailPoint", "Saviynt"],
            "runs":        len(self.run_history),
            "memory":      self.memory.status() if self.memory else {}
        }


# ── SINGLETON INSTANCE ──
iga = IGAAgent()


# ── QUICK TEST ──
if __name__ == "__main__":
    print("Testing IGA Agent...")
    print(f"Status: {iga.status()}")

    # Test access review
    result = iga.review_access(
        identity_id   = "USR-001",
        identity_name = "John Smith",
        current_roles = ["admin", "finance_approver", "finance_creator"],
        department    = "Finance",
        sector        = "Finance & Insurance"
    )
    print(f"\nAccess Review for John Smith:")
    print(result["analysis"][:300])
    print("\nIGA Agent working correctly!")
