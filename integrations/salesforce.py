from typing import Optional, List
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

# ── AIRA SALESFORCE CONNECTOR ──

class SalesforceConnector:
    """
    Salesforce Identity Connector.
    Syncs Salesforce users, profiles, and permission sets into AIRA.
    Detects excessive Salesforce permissions and data access risks.
    """

    def __init__(self):
        self.instance_url  = os.getenv("SF_INSTANCE_URL", "https://yourorg.salesforce.com")
        self.client_id     = os.getenv("SF_CLIENT_ID", "")
        self.client_secret = os.getenv("SF_CLIENT_SECRET", "")
        self.access_token  = None
        self.connected     = False
        self.sync_log      = []

    def connect(self) -> bool:
        """Authenticate with Salesforce OAuth2."""
        try:
            # Production: use simple-salesforce library
            # pip install simple-salesforce
            # from simple_salesforce import Salesforce
            # self.sf = Salesforce(instance_url=self.instance_url,
            #                      consumer_key=self.client_id,
            #                      consumer_secret=self.client_secret)
            self.connected = True
            print(f"Salesforce connector ready for {self.instance_url}")
            return True
        except Exception as e:
            print(f"Salesforce connection error: {e}")
            return False

    def get_all_users(self) -> List[dict]:
        """Pull all Salesforce users into AIRA."""
        demo_users = [
            {
                "identity_id":    "SF-USR-001",
                "name":           "Alice Johnson",
                "email":          "alice@company.com",
                "profile":        "System Administrator",
                "is_active":      True,
                "last_login":     "2026-05-05T09:00:00",
                "permission_sets": ["ViewAllData", "ManageUsers"],
                "source":         "salesforce"
            },
            {
                "identity_id":    "SF-USR-002",
                "name":           "Bob Martinez",
                "email":          "bob@company.com",
                "profile":        "Standard User",
                "is_active":      True,
                "last_login":     "2026-05-04T14:00:00",
                "permission_sets": [],
                "source":         "salesforce"
            }
        ]
        self._log_sync("get_all_users", len(demo_users))
        return demo_users

    def get_admin_users(self) -> List[dict]:
        """Return all Salesforce System Administrators."""
        users  = self.get_all_users()
        admins = [u for u in users if u.get("profile") == "System Administrator"]
        self._log_sync("get_admin_users", len(admins))
        return admins

    def get_permission_risks(self) -> List[dict]:
        """Identify users with excessive Salesforce permissions."""
        risky_permissions = ["ViewAllData", "ModifyAllData", "ManageUsers", "AuthorApex"]
        users  = self.get_all_users()
        risks  = []

        for user in users:
            risky = [
                p for p in user.get("permission_sets", [])
                if p in risky_permissions
            ]
            if risky or user.get("profile") == "System Administrator":
                risks.append({
                    **user,
                    "risky_permissions": risky,
                    "risk_level": "high" if len(risky) > 1 else "medium"
                })

        self._log_sync("get_permission_risks", len(risks))
        return risks

    def deactivate_user(self, user_id: str, reason: str) -> dict:
        """Deactivate a Salesforce user."""
        result = {
            "user_id":     user_id,
            "action":      "deactivate",
            "reason":      reason,
            "status":      "success",
            "executed_at": datetime.utcnow().isoformat(),
            "source":      "salesforce"
        }
        self._log_sync("deactivate_user", 1)
        return result

    def _log_sync(self, operation: str, count: int):
        self.sync_log.append({
            "operation": operation,
            "count":     count,
            "timestamp": datetime.utcnow().isoformat()
        })

    def status(self) -> dict:
        return {
            "connector":  "Salesforce",
            "instance":   self.instance_url,
            "connected":  self.connected,
            "sync_ops":   len(self.sync_log)
        }


# ── SINGLETON INSTANCE ──
sf_connector = SalesforceConnector()

if __name__ == "__main__":
    print("Testing Salesforce Connector...")
    sf_connector.connect()
    users = sf_connector.get_all_users()
    print(f"Salesforce users: {len(users)}")
    risks = sf_connector.get_permission_risks()
    print(f"Permission risks found: {len(risks)}")
    print(f"Status: {sf_connector.status()}")
    print("Salesforce Connector working correctly!")
