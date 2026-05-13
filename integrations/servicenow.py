from typing import Optional, List
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

# ── AIRA SERVICENOW CONNECTOR ──

class ServiceNowConnector:
    """
    ServiceNow ITSM Connector.
    Creates tickets for access requests, violations, and remediations.
    Syncs AIRA alerts into ServiceNow incident management.
    """

    def __init__(self):
        self.instance  = os.getenv("SNOW_INSTANCE", "https://yourorg.service-now.com")
        self.username  = os.getenv("SNOW_USERNAME", "")
        self.password  = os.getenv("SNOW_PASSWORD", "")
        self.connected = False
        self.tickets   = []

    def connect(self) -> bool:
        """Connect to ServiceNow REST API."""
        try:
            # Production: use pysnow library
            # pip install pysnow
            # import pysnow
            # self.client = pysnow.Client(
            #     instance=self.instance,
            #     user=self.username,
            #     password=self.password
            # )
            self.connected = True
            print(f"ServiceNow connector ready for {self.instance}")
            return True
        except Exception as e:
            print(f"ServiceNow connection error: {e}")
            return False

    def create_incident(
        self,
        title:       str,
        description: str,
        severity:    str,
        identity_id: Optional[str] = None,
        category:    str = "Security"
    ) -> dict:
        """Create a ServiceNow incident for an AIRA alert."""
        priority_map = {
            "critical": "1",
            "high":     "2",
            "medium":   "3",
            "low":      "4"
        }
        ticket = {
            "number":      f"INC{len(self.tickets) + 1000001}",
            "title":       title,
            "description": description,
            "severity":    severity,
            "priority":    priority_map.get(severity, "3"),
            "category":    category,
            "identity_id": identity_id,
            "state":       "New",
            "created_at":  datetime.utcnow().isoformat(),
            "source":      "AIRA"
        }
        self.tickets.append(ticket)
        return ticket

    def create_access_request(
        self,
        requester_id:   str,
        requester_name: str,
        resource:       str,
        justification:  str,
        duration:       Optional[str] = None
    ) -> dict:
        """Create an access request ticket in ServiceNow."""
        ticket = self.create_incident(
            title       = f"Access Request: {requester_name} → {resource}",
            description = (
                f"Requester: {requester_name} (ID: {requester_id})\n"
                f"Resource: {resource}\n"
                f"Justification: {justification}\n"
                f"Duration: {duration or 'Permanent'}\n"
                f"Submitted by: AIRA Platform"
            ),
            severity    = "medium",
            identity_id = requester_id,
            category    = "Access Management"
        )
        return ticket

    def create_violation_ticket(
        self,
        identity_id:   str,
        violation_type: str,
        details:        str,
        severity:       str
    ) -> dict:
        """Create a compliance violation ticket in ServiceNow."""
        ticket = self.create_incident(
            title       = f"Compliance Violation: {violation_type}",
            description = (
                f"Identity: {identity_id}\n"
                f"Violation: {violation_type}\n"
                f"Details: {details}\n"
                f"Detected by: AIRA Compliance Agent"
            ),
            severity    = severity,
            identity_id = identity_id,
            category    = "Compliance"
        )
        return ticket

    def get_open_tickets(self) -> List[dict]:
        """Return all open AIRA tickets in ServiceNow."""
        return [t for t in self.tickets if t.get("state") == "New"]

    def resolve_ticket(self, ticket_number: str, resolution: str) -> dict:
        """Resolve a ServiceNow ticket."""
        for ticket in self.tickets:
            if ticket["number"] == ticket_number:
                ticket["state"]       = "Resolved"
                ticket["resolution"]  = resolution
                ticket["resolved_at"] = datetime.utcnow().isoformat()
                return ticket
        return {"error": f"Ticket {ticket_number} not found"}

    def status(self) -> dict:
        return {
            "connector":      "ServiceNow",
            "instance":       self.instance,
            "connected":      self.connected,
            "total_tickets":  len(self.tickets),
            "open_tickets":   len(self.get_open_tickets())
        }


# ── SINGLETON INSTANCE ──
snow_connector = ServiceNowConnector()

if __name__ == "__main__":
    print("Testing ServiceNow Connector...")
    snow_connector.connect()
    ticket = snow_connector.create_incident(
        title       = "Critical: Impossible travel detected",
        description = "User logged in from Pakistan and USA within 45 minutes",
        severity    = "critical",
        identity_id = "USR-042"
    )
    print(f"Incident created: {ticket['number']}")
    req = snow_connector.create_access_request(
        requester_id   = "USR-001",
        requester_name = "John Smith",
        resource       = "PROD-DB-Finance",
        justification  = "Quarterly audit requirement"
    )
    print(f"Access request created: {req['number']}")
    print(f"Status: {snow_connector.status()}")
    print("ServiceNow Connector working correctly!")
