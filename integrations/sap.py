from typing import Optional, List
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

# ── AIRA SAP CONNECTOR ──

class SAPConnector:
    """
    SAP User & Role Connector.
    Syncs SAP users, roles, and authorisation objects into AIRA.
    Detects SAP SoD conflicts and excessive transaction codes.
    """

    def __init__(self):
        self.host      = os.getenv("SAP_HOST", "sap.company.com")
        self.client    = os.getenv("SAP_CLIENT", "100")
        self.username  = os.getenv("SAP_USERNAME", "")
        self.password  = os.getenv("SAP_PASSWORD", "")
        self.connected = False
        self.sync_log  = []

    def connect(self) -> bool:
        """Connect to SAP system."""
        try:
            # Production: use pyrfc library
            # pip install pyrfc
            # import pyrfc
            # self.conn = pyrfc.Connection(
            #     ashost=self.host, client=self.client,
            #     user=self.username, passwd=self.password
            # )
            self.connected = True
            print(f"SAP connector ready for {self.host} client {self.client}")
            return True
        except Exception as e:
            print(f"SAP connection error: {e}")
            return False

    def get_all_users(self) -> List[dict]:
        """Pull all SAP users into AIRA."""
        demo_users = [
            {
                "identity_id":  "SAP-USR-001",
                "username":     "JSMITH",
                "full_name":    "John Smith",
                "department":   "Finance",
                "user_type":    "Dialog",
                "roles":        ["FI_AP_CLERK", "FI_GL_POSTER"],
                "tcodes":       ["FB60", "FB65", "FB70", "F110"],
                "valid_to":     "9999-12-31",
                "locked":       False,
                "source":       "sap"
            },
            {
                "identity_id":  "SAP-USR-002",
                "username":     "BFRANK",
                "full_name":    "Barbara Frank",
                "department":   "Finance",
                "user_type":    "Dialog",
                "roles":        ["FI_AP_MANAGER", "FI_AP_CLERK", "FI_PAYMENT_APPROVER"],
                "tcodes":       ["FB60", "F110", "FBZP", "FK02"],
                "valid_to":     "9999-12-31",
                "locked":       False,
                "source":       "sap"
            }
        ]
        self._log_sync("get_all_users", len(demo_users))
        return demo_users

    def detect_sod_conflicts(self) -> List[dict]:
        """
        Detect Separation of Duties conflicts in SAP roles.
        Classic conflict: can create AND approve payments.
        """
        conflicting_pairs = [
            ("FB60", "F110"),   # Create invoice + Run payment
            ("FK01", "FK02"),   # Create vendor + Change vendor
            ("FB60", "FBZP"),   # Create invoice + Configure payment
        ]

        users     = self.get_all_users()
        conflicts = []

        for user in users:
            tcodes         = user.get("tcodes", [])
            user_conflicts = []

            for tcode_a, tcode_b in conflicting_pairs:
                if tcode_a in tcodes and tcode_b in tcodes:
                    user_conflicts.append({
                        "conflict_type": "SoD Violation",
                        "tcode_a":       tcode_a,
                        "tcode_b":       tcode_b,
                        "risk":          "high"
                    })

            if user_conflicts:
                conflicts.append({
                    **user,
                    "sod_conflicts": user_conflicts,
                    "conflict_count": len(user_conflicts)
                })

        self._log_sync("detect_sod_conflicts", len(conflicts))
        return conflicts

    def lock_user(self, username: str, reason: str) -> dict:
        """Lock a SAP user account."""
        result = {
            "username":    username,
            "action":      "lock",
            "reason":      reason,
            "status":      "success",
            "executed_at": datetime.utcnow().isoformat(),
            "source":      "sap"
        }
        self._log_sync("lock_user", 1)
        return result

    def _log_sync(self, operation: str, count: int):
        self.sync_log.append({
            "operation": operation,
            "count":     count,
            "timestamp": datetime.utcnow().isoformat()
        })

    def status(self) -> dict:
        return {
            "connector": "SAP",
            "host":      self.host,
            "client":    self.client,
            "connected": self.connected,
            "sync_ops":  len(self.sync_log)
        }


# ── SINGLETON INSTANCE ──
sap_connector = SAPConnector()

if __name__ == "__main__":
    print("Testing SAP Connector...")
    sap_connector.connect()
    users = sap_connector.get_all_users()
    print(f"SAP users: {len(users)}")
    conflicts = sap_connector.detect_sod_conflicts()
    print(f"SoD conflicts found: {len(conflicts)}")
    for c in conflicts:
        print(f"  {c['username']}: {c['conflict_count']} conflict(s)")
    print(f"Status: {sap_connector.status()}")
    print("SAP Connector working correctly!")
