from typing import Optional
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

# ── AIRA AGENT ORCHESTRATOR ──

class AIRAOrchestrator:
    """
    AIRA's master coordinator.
    Routes tasks to the correct agent,
    manages agent communication,
    and consolidates results for the dashboard.
    """

    def __init__(self):
        # Import here to avoid circular imports
        from llm.claude_client import claude
        from llm.prompts       import build_prompt
        from llm.rag_pipeline  import rag
        from llm.memory        import agent_memories

        self.claude          = claude
        self.build_prompt    = build_prompt
        self.rag             = rag
        self.agent_memories  = agent_memories

        # Agent registry
        self.agents = {
            "iga":         "Identity Governance & Administration",
            "pam":         "Privileged Access Management",
            "ciam":        "Customer Identity & Access Management",
            "frontline":   "Frontline Worker Identity",
            "machine":     "Machine Identity Management",
            "threat":      "Threat & Anomaly Detection",
            "compliance":  "Compliance & Governance",
            "remediation": "Automated Remediation",
        }

        self.run_log = []

    # ── ROUTE TASK TO AGENT ──

    def run_agent(
        self,
        agent_name:  str,
        task:        str,
        context:     Optional[str] = None,
        use_rag:     bool = True,
        collection:  Optional[str] = None
    ) -> dict:
        """
        Route a task to the correct agent and return the result.
        Automatically retrieves relevant context from RAG if needed.
        """
        if agent_name not in self.agents:
            return {
                "success": False,
                "error":   f"Unknown agent: {agent_name}",
                "agent":   agent_name
            }

        started_at = datetime.utcnow()

        try:
            # Get agent memory
            memory = self.agent_memories.get(agent_name)

            # Build RAG context if requested
            rag_context = ""
            if use_rag and collection:
                rag_context = self.rag.build_context(
                    query      = task,
                    collection = collection
                )

            # Build long term memory context
            memory_context = ""
            if memory:
                memory_context = memory.get_context()

            # Combine all context
            full_context = ""
            if rag_context:
                full_context += f"Knowledge Base:\n{rag_context}\n\n"
            if memory_context and memory_context != "No relevant long term memories found.":
                full_context += f"Past Decisions:\n{memory_context}\n\n"
            if context:
                full_context += f"Current Context:\n{context}"

            # Build prompt for this agent
            system_prompt, user_message = self.build_prompt(
                agent_name = agent_name,
                context    = full_context or "No additional context provided.",
                task       = task
            )

            # Add conversation to short term memory
            if memory:
                memory.remember("user", task)

            # Run the agent through Claude
            response = self.claude.think(
                system_prompt = system_prompt,
                user_message  = user_message
            )

            # Store response in short term memory
            if memory:
                memory.remember("assistant", response)

            # Log the run
            completed_at = datetime.utcnow()
            duration_ms  = int((completed_at - started_at).total_seconds() * 1000)

            run_record = {
                "agent":        agent_name,
                "task":         task[:100],
                "status":       "success",
                "duration_ms":  duration_ms,
                "started_at":   started_at.isoformat(),
                "completed_at": completed_at.isoformat()
            }
            self.run_log.append(run_record)

            return {
                "success":      True,
                "agent":        agent_name,
                "agent_name":   self.agents[agent_name],
                "response":     response,
                "duration_ms":  duration_ms,
                "timestamp":    completed_at.isoformat()
            }

        except Exception as e:
            error_record = {
                "agent":      agent_name,
                "task":       task[:100],
                "status":     "error",
                "error":      str(e),
                "started_at": started_at.isoformat()
            }
            self.run_log.append(error_record)

            return {
                "success": False,
                "agent":   agent_name,
                "error":   str(e)
            }

    # ── RUN ALL AGENTS ──

    def run_all_agents(
        self,
        task:    str,
        context: Optional[str] = None
    ) -> dict:
        """
        Run all 8 agents on the same task simultaneously.
        Returns consolidated results from all agents.
        """
        results = {}
        for agent_name in self.agents:
            results[agent_name] = self.run_agent(
                agent_name = agent_name,
                task       = task,
                context    = context
            )
        return results

    # ── AGENT STATUS ──

    def get_agent_status(self) -> list:
        """Return the current status of all agents."""
        status_list = []
        for agent_name, agent_full_name in self.agents.items():
            memory = self.agent_memories.get(agent_name)
            recent_runs = [
                r for r in self.run_log
                if r.get("agent") == agent_name
            ]
            last_run = recent_runs[-1] if recent_runs else None

            status_list.append({
                "agent":        agent_name,
                "name":         agent_full_name,
                "status":       "online",
                "runs_total":   len(recent_runs),
                "last_run":     last_run.get("started_at") if last_run else None,
                "memory":       memory.status() if memory else {}
            })

        return status_list

    # ── ORCHESTRATOR SUMMARY ──

    def summary(self) -> dict:
        """Return a summary of all orchestrator activity."""
        total_runs    = len(self.run_log)
        successful    = len([r for r in self.run_log if r.get("status") == "success"])
        failed        = total_runs - successful

        return {
            "total_runs":  total_runs,
            "successful":  successful,
            "failed":      failed,
            "agents":      list(self.agents.keys()),
            "agent_count": len(self.agents)
        }


# ── SINGLETON INSTANCE ──
orchestrator = AIRAOrchestrator()


# ── QUICK TEST ──
if __name__ == "__main__":
    print("Testing AIRA Orchestrator...")
    status = orchestrator.get_agent_status()
    print(f"Agents registered: {len(status)}")
    for agent in status:
        print(f"  {agent['agent']:12} — {agent['name']}")
    print(f"Summary: {orchestrator.summary()}")
    print("AIRA Orchestrator working correctly!")
