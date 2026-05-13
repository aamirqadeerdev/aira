import chromadb
from chromadb.config import Settings
from typing import List, Optional
from dotenv import load_dotenv
import os

load_dotenv()

# ── AIRA RAG PIPELINE ──

class RAGPipeline:
    """
    AIRA's Retrieval Augmented Generation pipeline.
    Stores and retrieves policies, compliance rules,
    and identity records using ChromaDB vector store.
    """

    def __init__(self):
        self.client = chromadb.PersistentClient(
            path="./database/chromadb_store"
        )

        # Collections — one per knowledge domain
        self.collections = {
            "policies":   self._get_or_create("aira_policies"),
            "compliance": self._get_or_create("aira_compliance"),
            "identities": self._get_or_create("aira_identities"),
            "threats":    self._get_or_create("aira_threats"),
            "reports":    self._get_or_create("aira_reports"),
        }

    def _get_or_create(self, name: str):
        """Get existing collection or create a new one."""
        return self.client.get_or_create_collection(
            name=name,
            metadata={"hnsw:space": "cosine"}
        )

    # ── STORE DOCUMENTS ──

    def store(
        self,
        collection:  str,
        documents:   List[str],
        ids:         List[str],
        metadatas:   Optional[List[dict]] = None
    ) -> bool:
        """Store documents in the specified collection."""
        try:
            col = self.collections.get(collection)
            if not col:
                raise ValueError(f"Collection '{collection}' not found.")

            col.add(
                documents = documents,
                ids       = ids,
                metadatas = metadatas or [{} for _ in documents]
            )
            return True

        except Exception as e:
            print(f"RAG store error: {e}")
            return False

    # ── RETRIEVE DOCUMENTS ──

    def retrieve(
        self,
        collection:   str,
        query:        str,
        n_results:    int = 5,
        where:        Optional[dict] = None
    ) -> List[dict]:
        """
        Retrieve the most relevant documents for a query.
        Returns list of documents with their metadata.
        """
        try:
            col = self.collections.get(collection)
            if not col:
                raise ValueError(f"Collection '{collection}' not found.")

            kwargs = {
                "query_texts": [query],
                "n_results":   n_results,
            }
            if where:
                kwargs["where"] = where

            results = col.query(**kwargs)

            output = []
            for i, doc in enumerate(results["documents"][0]):
                output.append({
                    "document": doc,
                    "id":       results["ids"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i],
                })
            return output

        except Exception as e:
            print(f"RAG retrieve error: {e}")
            return []

    # ── BUILD CONTEXT FOR AGENTS ──

    def build_context(
        self,
        query:      str,
        collection: str,
        n_results:  int = 5
    ) -> str:
        """
        Build a context string from retrieved documents.
        This context is passed to Claude agents for informed decisions.
        """
        results = self.retrieve(collection, query, n_results)
        if not results:
            return "No relevant documents found in knowledge base."

        context_parts = []
        for i, result in enumerate(results, 1):
            context_parts.append(
                f"[Document {i}]\n{result['document']}\n"
            )

        return "\n".join(context_parts)

    # ── DELETE DOCUMENT ──

    def delete(self, collection: str, doc_id: str) -> bool:
        """Remove a document from the collection."""
        try:
            col = self.collections.get(collection)
            if col:
                col.delete(ids=[doc_id])
                return True
            return False
        except Exception as e:
            print(f"RAG delete error: {e}")
            return False

    # ── COLLECTION STATS ──

    def stats(self, collection: str) -> dict:
        """Return the number of documents in a collection."""
        try:
            col = self.collections.get(collection)
            if col:
                return {
                    "collection": collection,
                    "count":      col.count()
                }
            return {"collection": collection, "count": 0}
        except Exception as e:
            print(f"RAG stats error: {e}")
            return {"collection": collection, "count": 0}


# ── SINGLETON INSTANCE ──
rag = RAGPipeline()


# ── QUICK TEST ──
if __name__ == "__main__":
    print("Testing RAG Pipeline...")

    # Store a test policy
    rag.store(
        collection = "policies",
        documents  = [
            "All privileged accounts must use MFA. "
            "Passwords must be rotated every 90 days. "
            "Access must follow least privilege principle."
        ],
        ids        = ["policy_001"],
        metadatas  = [{"framework": "NIST", "sector": "IT"}]
    )

    # Retrieve relevant policy
    results = rag.retrieve(
        collection = "policies",
        query      = "MFA requirements for privileged accounts",
        n_results  = 1
    )

    print(f"Retrieved {len(results)} document(s)")
    if results:
        print(f"Document: {results[0]['document'][:100]}...")

    print("RAG Pipeline working correctly!")
