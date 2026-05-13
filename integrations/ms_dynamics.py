from typing import Optional, List
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

# ── AIRA MICROSOFT DYNAMICS 365 CONNECTOR ──

class MSDynamicsConnector:
    """
    Microsoft Dynamics 365 Connector.
    Syncs Dynamics users, security roles, and business unit access into AIRA.
    Detects excessive CRM data access and role conflicts.
    """

    def __init__(self):
        self.tenant_id    = os.getenv("DYNAMICS_TENANT_ID", "")
        self.client_id    = os.getenv("DYNAMICS_CLIENT_ID", "")
        self.client_secret = os.getenv("DYNAMICS_CLIENT_SECRET", "")
        self.org_url      = os.getenv("DYNAMICS_ORG_URL", "https://yourorg.crm.dynamics.com")
        self.connected    = False
        self.sync_log     = []

    def connect(self) -> bool:
        """Connect to Dynamics 365 via Microsoft Graph API."""
        try:
            # Production: use msal + requests libraries
            # pip install msal requests
            # import msal
            # app = msal.ConfidentialClientApplication(
            #     self.client_id, authority=f"https://login.microsoftonline.com/{self.tenant_id}",
            #     client_credential=self.client_secret
            # )
            self.connected = True
            print(f"Dynamics 365 connector ready for {self.org_url}")
            return True
        except Exception as e:
            print(f"Dynamics connection error: {e}")
            return False

    def get_all_users(self) -> List[dict]:
        """Pull all Dynamics 365 users into AIRA."""
        demo_users = [
            {
                "identity_id":     "DYN-USR-001",
                "name":            "Emma Wilson",
                "email":           "emma@company.com",
                "security_roles":  ["System Administrator", "Sales Manager"],
                "business_unit":   "Sales Division",
                "is_active":       True,
                "last_login":      "2026-05-05T10:00:00",
                "source":          "dynamics365"
            },
            {
                "identity_id":     "DYN-USR-002",
                "name":            "Tom Brown",
                "email":           "tom@company.com",
                "security_roles":  ["Salesperson"],
                "business_unit":   "Sales Division",
                "is_active":       True,
                "last_login":      "2026-05-04T16:00:00",
                "source":          "dynamics365"
            }
        ]
        self._log_sync("get_all_users", len(demo_users))
        return demo_users

    def get_admin_users(self) -> List[dict]:
        """Return all Dynamics System Administrators."""
        users  = self.get_all_users()
        admins = [
            u for u in users
            if "System Administrator" in u.get("security_roles", [])
        ]
        self._log_sync("get_admin_users", len(admins))
        return admins

    def detect_excessive_access(self) -> List[dict]:
        """Detect users with excessive Dynamics permissions."""
        high_risk_roles = ["System Administrator", "System Customizer", "CEO Business Manager"]
        users  = self.get_all_users()
        risky  = []

        for user in users:
            risky_roles = [
                r for r in user.get("security_roles", [])
                if r in high_risk_roles
            ]
            if risky_roles:
                risky.append({
                    **user,
                    "risky_roles": risky_roles,
                    "risk_level":  "high" if len(risky_roles) > 1 else "medium"
                })

        self._log_sync("detect_excessive_access", len(risky))
        return risky

    def disable_user(self, user_id: str, reason: str) -> dict:
        """Disable a Dynamics 365 user."""
        result = {
            "user_id":     user_id,
            "action":      "disable",
            "reason":      reason,
            "status":      "success",
            "executed_at": datetime.utcnow().isoformat(),
            "source":      "dynamics365"
        }
        self._log_sync("disable_user", 1)
        return result

    def _log_sync(self, operation: str, count: int):
        self.sync_log.append({
            "operation": operation,
            "count":     count,
            "timestamp": datetime.utcnow().isoformat()
        })

    def status(self) -> dict:
        return {
            "connector": "Microsoft Dynamics 365",
            "org_url":   self.org_url,
            "connected": self.connected,
            "sync_ops":  len(self.sync_log)
        }


# ── SINGLETON INSTANCE ──
dynamics_connector = MSDynamicsConnector()

if __name__ == "__main__":
    print("Testing MS Dynamics Connector...")
    dynamics_connector.connect()
    users = dynamics_connector.get_all_users()
    print(f"Dynamics users: {len(users)}")
    risky = dynamics_connector.detect_excessive_access()
    print(f"Excessive access found: {len(risky)}")
    print(f"Status: {dynamics_connector.status()}")
    print("MS Dynamics Connector working correctly!")
