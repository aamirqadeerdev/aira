from typing import Optional, List
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

# ── AIRA THREAT AGENT ──

class ThreatAgent:
    """
    Threat & Anomaly Detection Agent.
    Detects identity-based threats in real time.
    Correlates threats across all identity types.
    Triggers automated responses to critical threats.
    """

    def __init__(self):
        from llm.claude_client import claude
        from llm.prompts       import THREAT_SYSTEM_PROMPT
        from llm.rag_pipeline  import rag
        from llm.memory        import agent_memories

        self.claude      = claude
        self.prompt      = THREAT_SYSTEM_PROMPT
        self.rag         = rag
        self.memory      = agent_memories.get("threat")
        self.agent_name  = "THREAT"
        self.run_history = []
        self.active_alerts = []

    def _run(self, task: str, context: str = "") -> str:
        """Send a task to Claude using Threat system prompt."""
        rag_context    = self.rag.build_context(task, "threats")
        memory_context = self.memory.get_context("alert") if self.memory else ""

        full_context = ""
        if rag_context:
            full_context += f"Threat Knowledge Base:\n{rag_context}\n\n"
        if memory_context and memory_context != "No relevant long term memories found.":
            full_context += f"Past Threat Alerts:\n{memory_context}\n\n"
        if context:
            full_context += f"Current Threat Data:\n{context}"

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

    # ── CORE THREAT FUNCTIONS ──

    def detect_anomaly(
        self,
        identity_id:    str,
        identity_name:  str,
        event_log:      List[str],
        baseline:       Optional[str] = None
    ) -> dict:
        """
        Detect anomalies in an identity's behaviour
        compared to their normal baseline.
        """
        events_text = "\n".join([
            f"- {event}" for event in event_log
        ])

        context = (
            f"Identity ID: {identity_id}\n"
            f"Identity Name: {identity_name}\n"
            f"Normal Baseline: {baseline or 'Not established'}\n"
            f"Recent Events:\n{events_text}"
        )

        task = (
            f"Analyse the behaviour of {identity_name} for anomalies. "
            f"Look for: unusual login times, impossible travel, "
            f"abnormal data access volumes, access to sensitive systems, "
            f"and deviation from normal patterns. "
            f"Rate the anomaly severity (0-100) and classify the threat type."
        )

        response = self._run(task, context)

        result = {
            "identity_id":   identity_id,
            "identity_name": identity_name,
            "events_count":  len(event_log),
            "analysis":      response,
            "detected_at":   datetime.utcnow().isoformat(),
            "agent":         self.agent_name
        }

        if self.memory:
            self.memory.memorise(
                memory_type = "alert",
                content     = f"Anomaly detected for {identity_name}: {response[:200]}",
                metadata    = {"identity_id": identity_id, "type": "anomaly"}
            )

        self.run_history.append(result)
        return result

    def detect_impossible_travel(
        self,
        identity_id:   str,
        identity_name: str,
        login_events:  List[dict]
    ) -> dict:
        """
        Detect impossible travel — when someone logs in
        from two locations that are physically impossible
        to travel between in the time difference.
        """
        events_text = "\n".join([
            f"- {e.get('time')} | {e.get('location')} | "
            f"IP: {e.get('ip', 'Unknown')}"
            for e in login_events
        ])

        context = (
            f"Identity: {identity_name} (ID: {identity_id})\n"
            f"Login Events:\n{events_text}"
        )

        task = (
            f"Check if {identity_name} has any impossible travel events. "
            f"Calculate if the time between logins allows physical travel "
            f"between the locations. Flag any impossible combinations "
            f"and rate the account takeover risk (0-100)."
        )

        response = self._run(task, context)

        result = {
            "identity_id":   identity_id,
            "identity_name": identity_name,
            "login_events":  len(login_events),
            "analysis":      response,
            "checked_at":    datetime.utcnow().isoformat(),
            "agent":         self.agent_name
        }

        self.run_history.append(result)
        return result

    def correlate_threats(
        self,
        threat_events: List[dict],
        timeframe:     str = "1 hour"
    ) -> dict:
        """
        Correlate multiple threat events across different
        identities and systems to detect coordinated attacks.
        """
        events_text = "\n".join([
            f"- Identity: {e.get('identity')} | "
            f"Event: {e.get('event')} | "
            f"Time: {e.get('time')} | "
            f"System: {e.get('system', 'Unknown')}"
            for e in threat_events
        ])

        context = (
            f"Timeframe: {timeframe}\n"
            f"Threat Events ({len(threat_events)} total):\n{events_text}"
        )

        task = (
            f"Correlate these {len(threat_events)} threat events "
            f"to identify coordinated attacks, insider threats, "
            f"or advanced persistent threats (APT). "
            f"Look for patterns, common targets, and attack sequences. "
            f"Provide an overall threat severity (0-100) and "
            f"MITRE ATT&CK technique mappings."
        )

        response = self._run(task, context)

        result = {
            "events_correlated": len(threat_events),
            "timeframe":         timeframe,
            "correlation":       response,
            "correlated_at":     datetime.utcnow().isoformat(),
            "agent":             self.agent_name
        }

        if self.memory:
            self.memory.memorise(
                memory_type = "alert",
                content     = f"Threat correlation: {response[:200]}",
                metadata    = {"events": len(threat_events), "type": "correlation"}
            )

        self.run_history.append(result)
        return result

    def generate_threat_response(
        self,
        threat_description: str,
        severity:           str,
        affected_identities: List[str]
    ) -> dict:
        """
        Generate an immediate threat response plan
        for a detected security incident.
        """
        context = (
            f"Threat Description: {threat_description}\n"
            f"Severity: {severity}\n"
            f"Affected Identities: {', '.join(affected_identities)}"
        )

        task = (
            f"Generate an immediate response plan for this {severity} threat. "
            f"Include: immediate containment steps, "
            f"accounts to disable or restrict, "
            f"systems to isolate, "
            f"evidence to preserve, "
            f"stakeholders to notify, "
            f"and recovery timeline."
        )

        response = self._run(task, context)

        result = {
            "threat_description":  threat_description,
            "severity":            severity,
            "affected_identities": affected_identities,
            "response_plan":       response,
            "generated_at":        datetime.utcnow().isoformat(),
            "agent":               self.agent_name
        }

        if self.memory:
            self.memory.memorise(
                memory_type = "alert",
                content     = f"Threat response for {severity} incident: {response[:200]}",
                metadata    = {
                    "severity":   severity,
                    "identities": len(affected_identities)
                }
            )

        self.run_history.append(result)
        return result

    def get_active_alerts(self) -> list:
        """Return all active threat alerts."""
        return self.active_alerts

    def status(self) -> dict:
        """Return current Threat agent status."""
        return {
            "agent":         self.agent_name,
            "description":   "Threat & Anomaly Detection",
            "active_alerts": len(self.active_alerts),
            "runs":          len(self.run_history),
            "memory":        self.memory.status() if self.memory else {}
        }


# ── SINGLETON INSTANCE ──
threat = ThreatAgent()


# ── QUICK TEST ──
if __name__ == "__main__":
    print("Testing Threat Agent...")
    print(f"Status: {threat.status()}")

    result = threat.detect_impossible_travel(
        identity_id   = "USR-042",
        identity_name = "Sarah Connor",
        login_events  = [
            {"time": "2026-05-05 08:00", "location": "Lahore, Pakistan",  "ip": "203.x.x.1"},
            {"time": "2026-05-05 08:45", "location": "New York, USA",     "ip": "198.x.x.2"},
            {"time": "2026-05-05 09:30", "location": "London, UK",        "ip": "82.x.x.3"},
        ]
    )
    print(f"\nImpossible Travel Analysis:")
    print(result["analysis"][:300])
    print("\nThreat Agent working correctly!")
