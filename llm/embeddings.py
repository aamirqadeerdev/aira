from anthropic import Anthropic
from typing import List, Optional
from dotenv import load_dotenv
import os
import json

load_dotenv()

# ── AIRA EMBEDDINGS ──

class EmbeddingsGenerator:
    """
    AIRA's document embedding generator.
    Converts text documents into numerical vectors
    so ChromaDB can find similar documents by meaning.
    """

    def __init__(self):
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model  = "claude-sonnet-4-20250514"

    def chunk_text(
        self,
        text:       str,
        chunk_size: int = 500,
        overlap:    int = 50
    ) -> List[str]:
        """
        Split large documents into smaller overlapping chunks.
        This ensures no important information is cut off at boundaries.
        """
        words  = text.split()
        chunks = []
        start  = 0

        while start < len(words):
            end   = min(start + chunk_size, len(words))
            chunk = " ".join(words[start:end])
            chunks.append(chunk)
            start += chunk_size - overlap

        return chunks

    def prepare_policy_document(
        self,
        title:     str,
        content:   str,
        framework: Optional[str] = None,
        sector:    Optional[str] = None
    ) -> List[dict]:
        """
        Prepare a policy document for storage in ChromaDB.
        Returns list of chunks with metadata ready for RAG pipeline.
        """
        chunks   = self.chunk_text(content)
        prepared = []

        for i, chunk in enumerate(chunks):
            doc_id = f"{title.lower().replace(' ', '_')}_{i}"
            prepared.append({
                "id":       doc_id,
                "document": chunk,
                "metadata": {
                    "title":     title,
                    "chunk":     i,
                    "total":     len(chunks),
                    "framework": framework or "general",
                    "sector":    sector    or "all",
                }
            })

        return prepared

    def prepare_compliance_rule(
        self,
        rule_id:    str,
        rule_text:  str,
        framework:  str,
        sector:     str,
        severity:   str = "medium"
    ) -> dict:
        """
        Prepare a compliance rule for storage in ChromaDB.
        """
        return {
            "id":       f"rule_{rule_id}",
            "document": rule_text,
            "metadata": {
                "rule_id":   rule_id,
                "framework": framework,
                "sector":    sector,
                "severity":  severity,
                "type":      "compliance_rule"
            }
        }

    def prepare_identity_record(
        self,
        identity_id:   str,
        identity_type: str,
        description:   str,
        sector:        Optional[str] = None
    ) -> dict:
        """
        Prepare an identity record for storage in ChromaDB.
        """
        return {
            "id":       f"identity_{identity_id}",
            "document": description,
            "metadata": {
                "identity_id":   identity_id,
                "identity_type": identity_type,
                "sector":        sector or "all",
                "type":          "identity_record"
            }
        }

    def summarise_for_embedding(self, text: str) -> str:
        """
        Use Claude to create a clean summary of a document
        before storing it — improves retrieval quality.
        """
        try:
            response = self.client.messages.create(
                model      = self.model,
                max_tokens = 500,
                messages   = [{
                    "role":    "user",
                    "content": (
                        f"Summarise the following document in 3-5 clear sentences "
                        f"for an enterprise identity and risk management system. "
                        f"Focus on key rules, risks, and requirements.\n\n{text}"
                    )
                }]
            )
            return response.content[0].text
        except Exception as e:
            print(f"Summarise error: {e}")
            return text


# ── SINGLETON INSTANCE ──
embeddings = EmbeddingsGenerator()


# ── QUICK TEST ──
if __name__ == "__main__":
    print("Testing Embeddings Generator...")

    # Test chunking
    sample_text = "All users must use MFA. " * 100
    chunks = embeddings.chunk_text(sample_text)
    print(f"Text chunked into {len(chunks)} pieces")

    # Test policy preparation
    docs = embeddings.prepare_policy_document(
        title     = "MFA Policy",
        content   = "All privileged accounts must enable MFA immediately.",
        framework = "NIST",
        sector    = "IT"
    )
    print(f"Policy prepared with {len(docs)} chunk(s)")
    print(f"First chunk ID: {docs[0]['id']}")
    print("Embeddings Generator working correctly!")
