import chromadb
from typing import List, Optional
from datetime import datetime
import os

# ── AIRA CHROMADB STORE MANAGER ──

class ChromaDBStore:
    """
    Manages ChromaDB vector store for AIRA's RAG pipeline.
    Handles all 5 knowledge collections:
    policies, compliance, identities, threats, reports.
    """

    COLLECTIONS = [
        "aira_policies",
        "aira_compliance",
        "aira_identities",
        "aira_threats",
        "aira_reports"
    ]

    def __init__(self):
        self.store_path = "./database/chromadb_store"
        os.makedirs(self.store_path, exist_ok=True)
        self.client = chromadb.PersistentClient(path=self.store_path)
        self._init_collections()

    def _init_collections(self):
        """Initialise all 5 AIRA knowledge collections."""
        self.collections = {}
        for name in self.COLLECTIONS:
            self.collections[name] = self.client.get_or_create_collection(
                name     = name,
                metadata = {"hnsw:space": "cosine"}
            )
        print(f"ChromaDB: {len(self.collections)} collections ready.")

    def seed_sample_data(self):
        """Seed ChromaDB with sample AIRA knowledge for testing."""
        # Sample policies
        policies_col = self.collections["aira_policies"]
        if policies_col.count() == 0:
            policies_col.add(
                documents = [
                    "All privileged accounts must use MFA. Passwords rotated every 90 days.",
                    "Least privilege access principle must be enforced across all systems.",
                    "All access changes must be logged and reviewed quarterly.",
                    "Service accounts must not be used for interactive logins.",
                    "Remote access requires VPN and MFA without exception."
                ],
                ids       = ["pol_001", "pol_002", "pol_003", "pol_004", "pol_005"],
                metadatas = [
                    {"framework": "NIST", "type": "access_control"},
                    {"framework": "NIST", "type": "least_privilege"},
                    {"framework": "SOX",  "type": "audit"},
                    {"framework": "NIST", "type": "service_account"},
                    {"framework": "NIST", "type": "remote_access"}
                ]
            )
            print("Policies collection seeded.")

        # Sample compliance rules
        compliance_col = self.collections["aira_compliance"]
        if compliance_col.count() == 0:
            compliance_col.add(
                documents = [
                    "HIPAA 164.312(a)(1): Unique user identification required for PHI access.",
                    "GDPR Article 25: Data protection by design and by default.",
                    "PCI-DSS 8.2: Proper identification and authentication for all users.",
                    "SOX Section 302: CEO/CFO must certify internal controls over financial reporting.",
                    "NIST AC-2: Account Management — manage information system accounts."
                ],
                ids       = ["comp_001", "comp_002", "comp_003", "comp_004", "comp_005"],
                metadatas = [
                    {"framework": "HIPAA",    "control": "164.312(a)(1)"},
                    {"framework": "GDPR",     "control": "Article 25"},
                    {"framework": "PCI-DSS",  "control": "8.2"},
                    {"framework": "SOX",      "control": "Section 302"},
                    {"framework": "NIST",     "control": "AC-2"}
                ]
            )
            print("Compliance collection seeded.")

        # Sample threats
        threats_col = self.collections["aira_threats"]
        if threats_col.count() == 0:
            threats_col.add(
                documents = [
                    "Impossible travel: User logged in from two countries within 30 minutes.",
                    "Credential stuffing: 50+ failed logins from same IP in 5 minutes.",
                    "Lateral movement: Admin account accessed 15 different servers in 10 minutes.",
                    "Data exfiltration: User downloaded 10GB of sensitive data outside business hours.",
                    "Privilege escalation: Standard user account granted admin rights without approval."
                ],
                ids       = ["thr_001", "thr_002", "thr_003", "thr_004", "thr_005"],
                metadatas = [
                    {"type": "impossible_travel",    "severity": "critical"},
                    {"type": "credential_stuffing",  "severity": "high"},
                    {"type": "lateral_movement",     "severity": "critical"},
                    {"type": "data_exfiltration",    "severity": "critical"},
                    {"type": "privilege_escalation", "severity": "high"}
                ]
            )
            print("Threats collection seeded.")

    def get_collection_stats(self) -> dict:
        """Return document counts for all collections."""
        stats = {}
        for name, col in self.collections.items():
            stats[name] = col.count()
        return {
            "collections": stats,
            "total_documents": sum(stats.values()),
            "checked_at": datetime.utcnow().isoformat()
        }

    def health_check(self) -> dict:
        """Check ChromaDB health."""
        try:
            stats = self.get_collection_stats()
            return {
                "status":      "healthy",
                "store_path":  self.store_path,
                "collections": len(self.collections),
                "documents":   stats["total_documents"]
            }
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}


# ── SINGLETON INSTANCE ──
chroma_store = ChromaDBStore()

if __name__ == "__main__":
    print("Testing ChromaDB Store...")
    chroma_store.seed_sample_data()
    stats = chroma_store.get_collection_stats()
    print(f"Collection stats: {stats}")
    health = chroma_store.health_check()
    print(f"Health: {health}")
    print("ChromaDB Store working correctly!")
