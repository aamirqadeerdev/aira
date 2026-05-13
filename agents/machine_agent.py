from typing import Optional, List
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

# ── AIRA MACHINE IDENTITY AGENT ──

class MachineAgent:
    """
    Machine Identity Management Agent.
    AIRA's unique differentiator — manages identities for
    robots, IoT devices, APIs, service accounts, and humanoids.
    No competitor manages robot and humanoid identities at this level.
    """

    def __init__(self):
        from llm.claude_client import claude
        from llm.prompts       import MACHINE_SYSTEM_PROMPT
        from llm.rag_pipeline  import rag
        from llm.memory        import agent_memories

        self.claude      = claude
        self.prompt      = MACHINE_SYSTEM_PROMPT
        self.rag         = rag
        self.memory      = agent_memories.get("machine")
        self.agent_name  = "MACHINE"
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

    def register_machine_identity(
        self,
        machine_id:   str,
        machine_type: str,
        machine_name: str,
        sector:       str,
        capabilities: List[str]
    ) -> dict:
        """Register and risk-assess a new machine identity."""
        context = (
            f"Machine ID: {machine_id}\n"
            f"Type: {machine_type}\n"
            f"Name: {machine_name}\n"
            f"Sector: {sector}\n"
            f"Capabilities: {', '.join(capabilities)}"
        )
        task = (
            f"Register and assess the risk profile for new machine identity {machine_name}. "
            f"Determine: risk score, required access controls, "
            f"certificate requirements, monitoring frequency, "
            f"and compliance frameworks that apply."
        )
        response = self._run(task, context)
        result = {
            "machine_id":   machine_id,
            "machine_type": machine_type,
            "machine_name": machine_name,
            "sector":       sector,
            "capabilities": capabilities,
            "assessment":   response,
            "registered_at": datetime.utcnow().isoformat(),
            "agent":        self.agent_name
        }
        if self.memory:
            self.memory.memorise(
                memory_type = "decision",
                content     = f"Machine registered: {machine_name} ({machine_type})",
                metadata    = {"machine_id": machine_id, "type": machine_type}
            )
        self.run_history.append(result)
        return result

    def detect_rogue_device(
        self,
        network_scan: List[dict],
        known_devices: List[str]
    ) -> dict:
        """Detect unauthorised devices on the network."""
        scan_text = "\n".join([
            f"- IP: {d.get('ip')} | MAC: {d.get('mac')} | "
            f"Type: {d.get('type', 'Unknown')} | "
            f"First seen: {d.get('first_seen', 'Unknown')}"
            for d in network_scan
        ])
        task = (
            f"Analyse this network scan and identify rogue or unauthorised devices. "
            f"Known approved devices: {', '.join(known_devices[:5])}... "
            f"Flag any device not in the approved list, "
            f"rate the threat level, and recommend isolation steps."
        )
        response = self._run(task, scan_text)
        result = {
            "devices_scanned": len(network_scan),
            "known_devices":   len(known_devices),
            "analysis":        response,
            "scanned_at":      datetime.utcnow().isoformat(),
            "agent":           self.agent_name
        }
        self.run_history.append(result)
        return result

    def manage_certificate_lifecycle(
        self,
        machine_id:      str,
        machine_name:    str,
        cert_expiry:     str,
        cert_type:       str
    ) -> dict:
        """Manage machine certificate rotation and renewal."""
        context = (
            f"Machine ID: {machine_id}\n"
            f"Machine Name: {machine_name}\n"
            f"Certificate Type: {cert_type}\n"
            f"Certificate Expiry: {cert_expiry}"
        )
        task = (
            f"Create a certificate lifecycle management plan for {machine_name}. "
            f"Include: renewal timeline, rotation procedure, "
            f"systems to update, rollback plan, and monitoring alerts."
        )
        response = self._run(task, context)
        result = {
            "machine_id":   machine_id,
            "machine_name": machine_name,
            "cert_expiry":  cert_expiry,
            "cert_type":    cert_type,
            "lifecycle_plan": response,
            "planned_at":   datetime.utcnow().isoformat(),
            "agent":        self.agent_name
        }
        self.run_history.append(result)
        return result

    def assess_robot_humanoid_risk(
        self,
        robot_id:     str,
        robot_name:   str,
        robot_type:   str,
        access_zones: List[str],
        sector:       str
    ) -> dict:
        """
        Assess risk for robots and humanoid machines.
        AIRA's unique differentiator — no competitor does this.
        """
        context = (
            f"Robot ID: {robot_id}\n"
            f"Robot Name: {robot_name}\n"
            f"Robot Type: {robot_type}\n"
            f"Access Zones: {', '.join(access_zones)}\n"
            f"Sector: {sector}"
        )
        task = (
            f"Assess the identity and access risk for robot/humanoid {robot_name}. "
            f"Consider: physical access zones, data access, network connectivity, "
            f"firmware security, command injection risks, "
            f"and applicable compliance frameworks (IEC 62443, ISO/SAE 21434). "
            f"This is a unique AIRA capability — provide comprehensive robot IAM assessment."
        )
        response = self._run(task, context)
        result = {
            "robot_id":    robot_id,
            "robot_name":  robot_name,
            "robot_type":  robot_type,
            "access_zones": access_zones,
            "sector":      sector,
            "risk_assessment": response,
            "assessed_at": datetime.utcnow().isoformat(),
            "agent":       self.agent_name
        }
        if self.memory:
            self.memory.memorise(
                memory_type = "decision",
                content     = f"Robot risk assessed: {robot_name} ({robot_type}): {response[:150]}",
                metadata    = {"robot_id": robot_id, "sector": sector}
            )
        self.run_history.append(result)
        return result

    def status(self) -> dict:
        return {
            "agent":          self.agent_name,
            "description":    "Machine Identity Management",
            "differentiator": "Only AIRA manages robot and humanoid identities",
            "runs":           len(self.run_history),
            "memory":         self.memory.status() if self.memory else {}
        }


# ── SINGLETON INSTANCE ──
machine = MachineAgent()

if __name__ == "__main__":
    print("Testing Machine Identity Agent...")
    print(f"Status: {machine.status()}")
    result = machine.assess_robot_humanoid_risk(
        robot_id     = "BOT-007",
        robot_name   = "FANUC Assembly Robot AR-7",
        robot_type   = "Industrial Robot Arm",
        access_zones = ["Assembly Line A", "Parts Storage", "Quality Control"],
        sector       = "Logistics & Manufacturing"
    )
    print(f"\nRobot Risk Assessment:\n{result['risk_assessment'][:300]}")
    print("\nMachine Identity Agent working correctly!")
