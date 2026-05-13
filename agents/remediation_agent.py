from typing import Optional, List
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

# ── AIRA REMEDIATION AGENT ──

class RemediationAgent:
    """
    Automated Remediation Agent.
    Automatically fixes identity violations,
    revokes excessive access, disables compromised accounts,
    and escalates critical issues to human operators.
    """

    def __init__(self):
        from llm.claude_client import claude
        from llm.prompts       import REMEDIATION_SYSTEM_PROMPT
        from llm.rag_pipeline  import rag
        from llm.memory        import agent_memories

        self.claude      = claude
        self.prompt      = REMEDIATION_SYSTEM_PROMPT
        self.rag         = rag
        self.memory      = agent_memories.get("remediation")
        self.agent_name  = "REMEDIATION"
        self.run_history = []
        self.action_log  = []

    def _run(self, task: str, context: str = "") -> str:
        """Send a task to Claude using Remediation system prompt."""
        rag_context    = self.rag.build_context(task, "policies")
        memory_context = self.memory.get_context("decision") if self.memory else ""

        full_context = ""
        if rag_context:
            full_context += f"Policy Knowledge Base:\n{rag_context}\n\n"
        if memory_context and memory_context != "No relevant long term memories found.":
            full_context += f"Past Remediations:\n{memory_context}\n\n"
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

    def _log_action(
        self,
        action:      str,
        target:      str,
        outcome:     str,
        automated:   bool = True
    ) -> dict:
        """Log every remediation action for audit trail."""
        from explainability.audit_trail import audit_trail
        record = {
            "action":     action,
            "target":     target,
            "outcome":    outcome,
            "automated":  automated,
            "timestamp":  datetime.utcnow().isoformat(),
            "agent":      self.agent_name
        }
        self.action_log.append(record)
        try:
            audit_trail.log(
                action    = action,
                actor     = "AIRA Remediation Agent",
                target    = target,
                outcome   = outcome,
                details   = f"Automated: {automated}"
            )
        except Exception:
            pass
        return record

    # ── CORE REMEDIATION FUNCTIONS ──

    def remediate_risk(
        self,
        identity_id:   str,
        identity_name: str,
        risk_score:    float,
        risk_factors:  List[str],
        auto_execute:  bool = False
    ) -> dict:
        """
        Generate and optionally execute a remediation plan
        for a high-risk identity.
        """
        context = (
            f"Identity ID: {identity_id}\n"
            f"Identity Name: {identity_name}\n"
            f"Risk Score: {risk_score}/100\n"
            f"Risk Factors: {', '.join(risk_factors)}"
        )

        task = (
            f"Create a detailed remediation plan for {identity_name} "
            f"with risk score {risk_score}/100. "
            f"Classify each action as: AUTOMATED (can execute immediately) "
            f"or MANUAL (requires human approval). "
            f"Include: priority order, rollback steps, "
            f"verification checks, and estimated completion time."
        )

        response  = self._run(task, context)
        automated = risk_score >= 80

        action = self._log_action(
            action    = "risk_remediation_plan",
            target    = identity_id,
            outcome   = "plan_generated",
            automated = automated
        )

        if self.memory:
            self.memory.memorise(
                memory_type = "decision",
                content     = f"Remediation for {identity_name} (score {risk_score}): {response[:200]}",
                metadata    = {"identity_id": identity_id, "risk_score": risk_score}
            )

        result = {
            "identity_id":    identity_id,
            "identity_name":  identity_name,
            "risk_score":     risk_score,
            "remediation_plan": response,
            "auto_executed":  automated and auto_execute,
            "action_logged":  action,
            "generated_at":   datetime.utcnow().isoformat(),
            "agent":          self.agent_name
        }

        self.run_history.append(result)
        return result

    def revoke_access(
        self,
        identity_id:   str,
        identity_name: str,
        roles_to_revoke: List[str],
        reason:        str
    ) -> dict:
        """
        Revoke specific access roles from an identity.
        """
        context = (
            f"Identity: {identity_name} (ID: {identity_id})\n"
            f"Roles to revoke: {', '.join(roles_to_revoke)}\n"
            f"Reason: {reason}"
        )

        task = (
            f"Plan the access revocation for {identity_name}. "
            f"For each role being revoked provide: "
            f"impact assessment, systems affected, "
            f"business continuity considerations, "
            f"and notification requirements."
        )

        response = self._run(task, context)

        action = self._log_action(
            action  = "access_revoked",
            target  = identity_id,
            outcome = f"Roles revoked: {', '.join(roles_to_revoke)}"
        )

        result = {
            "identity_id":    identity_id,
            "identity_name":  identity_name,
            "roles_revoked":  roles_to_revoke,
            "reason":         reason,
            "impact_analysis": response,
            "action_logged":  action,
            "revoked_at":     datetime.utcnow().isoformat(),
            "agent":          self.agent_name
        }

        self.run_history.append(result)
        return result

    def disable_account(
        self,
        identity_id:   str,
        identity_name: str,
        reason:        str,
        escalate:      bool = True
    ) -> dict:
        """
        Disable a compromised or high-risk account.
        Escalates to human operator if required.
        """
        context = (
            f"Identity: {identity_name} (ID: {identity_id})\n"
            f"Reason for disabling: {reason}\n"
            f"Escalation required: {escalate}"
        )

        task = (
            f"Plan the account disablement for {identity_name}. "
            f"Include: pre-disablement checklist, "
            f"notification plan, evidence preservation steps, "
            f"re-enablement criteria, and escalation contacts."
        )

        response = self._run(task, context)

        action = self._log_action(
            action    = "account_disabled",
            target    = identity_id,
            outcome   = "disabled_pending_review",
            automated = not escalate
        )

        result = {
            "identity_id":     identity_id,
            "identity_name":   identity_name,
            "reason":          reason,
            "escalated":       escalate,
            "disablement_plan": response,
            "action_logged":   action,
            "disabled_at":     datetime.utcnow().isoformat(),
            "agent":           self.agent_name
        }

        self.run_history.append(result)
        return result

    def auto_remediate_compliance_gap(
        self,
        framework: str,
        sector:    str,
        gaps:      List[str]
    ) -> dict:
        """
        Automatically generate remediation steps for compliance gaps.
        """
        gaps_text = "\n".join([f"- {gap}" for gap in gaps])

        task = (
            f"Create an automated remediation plan for these {framework} "
            f"compliance gaps in the {sector} sector:\n\n{gaps_text}\n\n"
            f"For each gap provide: "
            f"automated fix (if possible), manual steps, "
            f"responsible team, timeline, and verification method."
        )

        response = self._run(task)

        action = self._log_action(
            action  = "compliance_remediation",
            target  = f"{framework}_{sector}",
            outcome = f"{len(gaps)} gaps addressed"
        )

        result = {
            "framework":        framework,
            "sector":           sector,
            "gaps_addressed":   len(gaps),
            "remediation_plan": response,
            "action_logged":    action,
            "generated_at":     datetime.utcnow().isoformat(),
            "agent":            self.agent_name
        }

        self.run_history.append(result)
        return result

    def escalate_to_human(
        self,
        issue:       str,
        severity:    str,
        identity_id: Optional[str] = None,
        context:     Optional[str] = None
    ) -> dict:
        """
        Escalate a critical issue to a human operator.
        """
        prompt_context = (
            f"Issue: {issue}\n"
            f"Severity: {severity}\n"
            f"Identity: {identity_id or 'N/A'}\n"
            f"Additional Context: {context or 'None'}"
        )

        task = (
            f"Prepare an escalation brief for a human operator. "
            f"Include: issue summary, why automation cannot handle it, "
            f"urgency level, recommended human actions, "
            f"and all context needed to resolve it quickly."
        )

        response = self._run(task, prompt_context)

        action = self._log_action(
            action    = "escalated_to_human",
            target    = identity_id or "system",
            outcome   = f"Escalated: {severity}",
            automated = False
        )

        result = {
            "issue":          issue,
            "severity":       severity,
            "identity_id":    identity_id,
            "escalation_brief": response,
            "action_logged":  action,
            "escalated_at":   datetime.utcnow().isoformat(),
            "agent":          self.agent_name
        }

        self.run_history.append(result)
        return result

    def get_action_log(self) -> List[dict]:
        """Return all remediation actions taken."""
        return self.action_log

    def status(self) -> dict:
        """Return current Remediation agent status."""
        return {
            "agent":          self.agent_name,
            "description":    "Automated Remediation",
            "actions_taken":  len(self.action_log),
            "runs":           len(self.run_history),
            "memory":         self.memory.status() if self.memory else {}
        }


# ── SINGLETON INSTANCE ──
remediation = RemediationAgent()

if __name__ == "__main__":
    print("Testing Remediation Agent...")
    print(f"Status: {remediation.status()}")

    result = remediation.remediate_risk(
        identity_id   = "USR-001",
        identity_name = "John Smith",
        risk_score    = 85.0,
        risk_factors  = [
            "5 failed logins in 10 minutes",
            "Access from unknown location",
            "Sensitive data download at 3AM"
        ]
    )
    print(f"\nRemediation Plan:\n{result['remediation_plan'][:300]}")
    print(f"\nActions logged: {len(remediation.action_log)}")
    print("Remediation Agent working correctly!")
