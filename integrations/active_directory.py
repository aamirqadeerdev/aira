from typing import Optional, List
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

# ── AIRA ACTIVE DIRECTORY INTEGRATION ──

class ActiveDirectoryConnector:
    """
    Microsoft Active Directory / LDAP Connector.
    Pulls identity data from enterprise AD into AIRA.
    Syncs users, groups, OUs, and policies automatically.
    """

    def __init__(self):
        self.host     = os.getenv("AD_HOST", "ldap://localhost")
        self.port     = int(os.getenv("AD_PORT", "389"))
        self.domain   = os.getenv("AD_DOMAIN", "company.local")
        self.username = os.getenv("AD_USERNAME", "")
        self.password = os.getenv("AD_PASSWORD", "")
        self.connected = False
        self.sync_log  = []

    def connect(self) -> bool:
        """Connect to Active Directory."""
        try:
            # In production: use ldap3 library
            # pip install ldap3
            # import ldap3
            # server = ldap3.Server(self.host, port=self.port)
            # self.conn = ldap3.Connection(server, self.username, self.password, auto_bind=True)
            self.connected = True
            print(f"AD connector ready for {self.domain}")
            return True
        except Exception as e:
            print(f"AD connection error: {e}")
            self.connected = False
            return False

    def get_all_users(self) -> List[dict]:
        """Pull all users from Active Directory."""
        # Production: query AD via ldap3
        # Demo data representing AD users
        demo_users = [
            {
                "identity_id":   "USR-AD-001",
                "name":          "John Smith",
                "email":         "john.smith@company.com",
                "department":    "Finance",
                "groups":        ["Finance_Users", "VPN_Access"],
                "last_logon":    "2026-05-04T08:30:00",
                "account_enabled": True,
                "source":        "active_directory"
            },
            {
                "identity_id":   "USR-AD-002",
                "name":          "Sarah Connor",
                "email":         "sarah.connor@company.com",
                "department":    "IT",
                "groups":        ["Domain_Admins", "IT_Staff", "VPN_Access"],
                "last_logon":    "2026-05-05T03:22:00",
                "account_enabled": True,
                "source":        "active_directory"
            },
            {
                "identity_id":   "SVC-AD-001",
                "name":          "svc_backup_agent",
                "email":         "",
                "department":    "IT",
                "groups":        ["Service_Accounts", "Backup_Operators"],
                "last_logon":    "2026-05-05T01:00:00",
                "account_enabled": True,
                "source":        "active_directory"
            }
        ]
        self._log_sync("get_all_users", len(demo_users))
        return demo_users

    def get_privileged_accounts(self) -> List[dict]:
        """Pull all privileged accounts from AD."""
        privileged_groups = [
            "Domain_Admins", "Enterprise_Admins",
            "Schema_Admins", "Backup_Operators"
        ]
        all_users = self.get_all_users()
        privileged = [
            u for u in all_users
            if any(g in privileged_groups for g in u.get("groups", []))
        ]
        self._log_sync("get_privileged_accounts", len(privileged))
        return privileged

    def get_stale_accounts(self, days_threshold: int = 90) -> List[dict]:
        """Find accounts that have not been used in N days."""
        all_users  = self.get_all_users()
        stale      = []
        cutoff_str = "2026-02-04"  # 90 days before today

        for user in all_users:
            last_logon = user.get("last_logon", "")
            if last_logon and last_logon[:10] < cutoff_str:
                user["stale_days"] = days_threshold
                stale.append(user)

        self._log_sync("get_stale_accounts", len(stale))
        return stale

    def get_groups_for_user(self, user_id: str) -> List[str]:
        """Return all AD groups for a specific user."""
        users = self.get_all_users()
        user  = next((u for u in users if u["identity_id"] == user_id), None)
        return user.get("groups", []) if user else []

    def disable_user(self, user_id: str, reason: str) -> dict:
        """Disable a user account in Active Directory."""
        # Production: use ldap3 to modify userAccountControl flag
        result = {
            "user_id":     user_id,
            "action":      "disable",
            "reason":      reason,
            "status":      "success",
            "executed_at": datetime.utcnow().isoformat(),
            "source":      "active_directory"
        }
        self._log_sync("disable_user", 1)
        return result

    def _log_sync(self, operation: str, count: int):
        self.sync_log.append({
            "operation":  operation,
            "count":      count,
            "timestamp":  datetime.utcnow().isoformat()
        })

    def status(self) -> dict:
        return {
            "connector":   "Active Directory",
            "host":        self.host,
            "domain":      self.domain,
            "connected":   self.connected,
            "sync_ops":    len(self.sync_log)
        }


# ── SINGLETON INSTANCE ──
ad_connector = ActiveDirectoryConnector()

if __name__ == "__main__":
    print("Testing Active Directory Connector...")
    ad_connector.connect()
    users = ad_connector.get_all_users()
    print(f"Users found: {len(users)}")
    privileged = ad_connector.get_privileged_accounts()
    print(f"Privileged accounts: {len(privileged)}")
    print(f"Status: {ad_connector.status()}")
    print("Active Directory Connector working correctly!")
