from typing import List, Optional
from datetime import datetime
from dotenv import load_dotenv
import json
import os

load_dotenv()

# ── AIRA AGENT MEMORY SYSTEM ──

class ShortTermMemory:
    """
    Short term memory for AIRA agents.
    Holds the last 20 conversations in RAM.
    Cleared when the session ends.
    """

    def __init__(self, max_messages: int = 20):
        self.max_messages = max_messages
        self.messages:    List[dict] = []

    def add(self, role: str, content: str) -> None:
        """Add a message to short term memory."""
        self.messages.append({
            "role":      role,
            "content":   content,
            "timestamp": datetime.utcnow().isoformat()
        })
        # Keep only the last max_messages
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]

    def get_history(self) -> List[dict]:
        """Return conversation history for Claude API."""
        return [
            {"role": m["role"], "content": m["content"]}
            for m in self.messages
        ]

    def get_last(self, n: int = 5) -> List[dict]:
        """Return the last n messages."""
        return self.messages[-n:]

    def clear(self) -> None:
        """Clear all short term memory."""
        self.messages = []

    def summary(self) -> str:
        """Return a quick summary of current memory state."""
        return (
            f"Short term memory: {len(self.messages)} messages "
            f"(max {self.max_messages})"
        )


class LongTermMemory:
    """
    Long term memory for AIRA agents.
    Stores important decisions, patterns, and outcomes
    permanently on disk as JSON files.
    Persists across sessions.
    """

    def __init__(self, agent_name: str):
        self.agent_name  = agent_name
        self.memory_dir  = f"./database/memory/{agent_name}"
        self.memory_file = f"{self.memory_dir}/memory.json"
        self._ensure_dir()
        self.memories: List[dict] = self._load()

    def _ensure_dir(self) -> None:
        """Create memory directory if it does not exist."""
        os.makedirs(self.memory_dir, exist_ok=True)

    def _load(self) -> List[dict]:
        """Load memories from disk."""
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file, "r") as f:
                    return json.load(f)
            return []
        except Exception:
            return []

    def _save(self) -> None:
        """Save memories to disk."""
        try:
            with open(self.memory_file, "w") as f:
                json.dump(self.memories, f, indent=2)
        except Exception as e:
            print(f"Long term memory save error: {e}")

    def store(
        self,
        memory_type: str,
        content:     str,
        metadata:    Optional[dict] = None
    ) -> None:
        """
        Store an important decision or pattern in long term memory.
        memory_type: decision, pattern, alert, compliance, remediation
        """
        self.memories.append({
            "id":          len(self.memories) + 1,
            "agent":       self.agent_name,
            "type":        memory_type,
            "content":     content,
            "metadata":    metadata or {},
            "stored_at":   datetime.utcnow().isoformat()
        })
        self._save()

    def recall(
        self,
        memory_type: Optional[str] = None,
        limit:       int = 10
    ) -> List[dict]:
        """
        Recall memories from long term storage.
        Optionally filter by memory type.
        """
        memories = self.memories
        if memory_type:
            memories = [
                m for m in memories
                if m.get("type") == memory_type
            ]
        return memories[-limit:]

    def recall_as_context(
        self,
        memory_type: Optional[str] = None,
        limit:       int = 5
    ) -> str:
        """
        Return memories as a formatted context string
        ready to pass to Claude agents.
        """
        memories = self.recall(memory_type, limit)
        if not memories:
            return "No relevant long term memories found."

        context_parts = []
        for m in memories:
            context_parts.append(
                f"[{m['type'].upper()} — {m['stored_at'][:10]}]\n"
                f"{m['content']}"
            )
        return "\n\n".join(context_parts)

    def count(self) -> int:
        """Return total number of memories stored."""
        return len(self.memories)

    def clear(self) -> None:
        """Clear all long term memories for this agent."""
        self.memories = []
        self._save()

    def summary(self) -> str:
        """Return a quick summary of long term memory state."""
        return (
            f"Long term memory [{self.agent_name}]: "
            f"{len(self.memories)} memories stored on disk"
        )


class AgentMemory:
    """
    Combined memory system for each AIRA agent.
    Provides both short term (RAM) and long term (disk) memory.
    """

    def __init__(self, agent_name: str, max_short_term: int = 20):
        self.agent_name  = agent_name
        self.short_term  = ShortTermMemory(max_short_term)
        self.long_term   = LongTermMemory(agent_name)

    def remember(self, role: str, content: str) -> None:
        """Add to short term memory."""
        self.short_term.add(role, content)

    def memorise(
        self,
        memory_type: str,
        content:     str,
        metadata:    Optional[dict] = None
    ) -> None:
        """Store important information in long term memory."""
        self.long_term.store(memory_type, content, metadata)

    def get_conversation(self) -> List[dict]:
        """Get current conversation for Claude API."""
        return self.short_term.get_history()

    def get_context(self, memory_type: Optional[str] = None) -> str:
        """Get long term context for agent decision making."""
        return self.long_term.recall_as_context(memory_type)

    def status(self) -> dict:
        """Return memory status for both short and long term."""
        return {
            "agent":       self.agent_name,
            "short_term":  self.short_term.summary(),
            "long_term":   self.long_term.summary(),
        }


# ── MEMORY FACTORY ──
# Creates one AgentMemory instance per agent

def create_agent_memories() -> dict:
    """Create memory instances for all 8 AIRA agents."""
    agents = [
        "iga", "pam", "ciam", "frontline",
        "machine", "threat", "compliance", "remediation"
    ]
    return {agent: AgentMemory(agent) for agent in agents}

# Initialise all agent memories
agent_memories = create_agent_memories()


# ── QUICK TEST ──
if __name__ == "__main__":
    print("Testing Agent Memory System...")

    # Test short term memory
    mem = AgentMemory("test_agent")
    mem.remember("user", "Check identity risk for user john@company.com")
    mem.remember("assistant", "Risk score: 72. High risk due to excessive privileges.")

    print(f"Short term: {len(mem.short_term.messages)} messages")

    # Test long term memory
    mem.memorise(
        memory_type = "decision",
        content     = "Revoked admin access for john@company.com due to risk score 72.",
        metadata    = {"identity": "john@company.com", "action": "revoke"}
    )
    print(f"Long term: {mem.long_term.count()} memories stored")
    print(f"Status: {mem.status()}")
    print("Agent Memory System working correctly!")
