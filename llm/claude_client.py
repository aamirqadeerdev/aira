import anthropic
from typing import Optional
from dotenv import load_dotenv
import os

load_dotenv()

# ── CLAUDE CLIENT ──

class ClaudeClient:
    """
    AIRA's connection to Anthropic Claude API.
    All 8 agents use this client to think and decide.
    """

    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in .env file.")
        self.client  = anthropic.Anthropic(api_key=self.api_key)
        self.model   = "claude-sonnet-4-20250514"
        self.max_tokens = 4096

    def think(
        self,
        system_prompt: str,
        user_message:  str,
        max_tokens:    Optional[int] = None
    ) -> str:
        """
        Send a message to Claude and get a response.
        Used by all AIRA agents to make decisions.
        """
        try:
            response = self.client.messages.create(
                model      = self.model,
                max_tokens = max_tokens or self.max_tokens,
                system     = system_prompt,
                messages   = [
                    {"role": "user", "content": user_message}
                ]
            )
            return response.content[0].text

        except anthropic.AuthenticationError:
            raise ValueError("Invalid Anthropic API key. Check your .env file.")
        except anthropic.RateLimitError:
            raise ValueError("Anthropic API rate limit reached. Please wait and try again.")
        except anthropic.APIError as e:
            raise ValueError(f"Anthropic API error: {str(e)}")

    def think_with_history(
        self,
        system_prompt: str,
        messages:      list,
        max_tokens:    Optional[int] = None
    ) -> str:
        """
        Send a conversation history to Claude.
        Used for multi-turn agent conversations.
        """
        try:
            response = self.client.messages.create(
                model      = self.model,
                max_tokens = max_tokens or self.max_tokens,
                system     = system_prompt,
                messages   = messages
            )
            return response.content[0].text

        except anthropic.APIError as e:
            raise ValueError(f"Anthropic API error: {str(e)}")

    def analyse(
        self,
        context:    str,
        question:   str,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Analyse a piece of text and answer a question about it.
        Used by compliance and threat agents.
        """
        system_prompt = (
            "You are AIRA — an expert Agentic Identity & Risk Administration system. "
            "You analyse identity data, compliance records, and security threats "
            "with precision and provide clear, actionable recommendations."
        )
        user_message = f"Context:\n{context}\n\nQuestion:\n{question}"
        return self.think(system_prompt, user_message, max_tokens)


# ── SINGLETON INSTANCE ──
# All agents import this single instance
claude = ClaudeClient()


# ── QUICK TEST ──
if __name__ == "__main__":
    print("Testing Claude connection...")
    response = claude.think(
        system_prompt = "You are AIRA, an enterprise IAM platform.",
        user_message  = "Say hello and confirm you are operational in one sentence."
    )
    print(f"Claude says: {response}")
