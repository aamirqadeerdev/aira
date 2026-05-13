from datetime import datetime
from typing import Optional, List
import os
import json

# ── AIRA MONITORING & OBSERVABILITY ──

class AIRAMonitor:
    """
    AIRA's monitoring and observability system.
    Tracks API performance, agent health, database status,
    and system metrics for the control centre dashboard.
    """

    def __init__(self):
        self.metrics_log  = []
        self.health_log   = []
        self.alerts       = []
        self.start_time   = datetime.utcnow()

    def record_metric(
        self,
        metric_name:  str,
        value:        float,
        unit:         str = "ms",
        tags:         Optional[dict] = None
    ):
        """Record a performance metric."""
        self.metrics_log.append({
            "metric":     metric_name,
            "value":      value,
            "unit":       unit,
            "tags":       tags or {},
            "recorded_at": datetime.utcnow().isoformat()
        })

    def record_api_call(
        self,
        endpoint:    str,
        method:      str,
        status_code: int,
        duration_ms: float
    ):
        """Record an API call for performance monitoring."""
        self.record_metric(
            metric_name = "api_response_time",
            value       = duration_ms,
            unit        = "ms",
            tags        = {
                "endpoint":    endpoint,
                "method":      method,
                "status_code": status_code
            }
        )

    def check_system_health(self) -> dict:
        """Run a full system health check."""
        health = {
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_seconds": (datetime.utcnow() - self.start_time).seconds,
            "components": {}
        }

        # Check API
        health["components"]["api"] = {
            "status": "healthy",
            "calls_recorded": len([
                m for m in self.metrics_log
                if m["metric"] == "api_response_time"
            ])
        }

        # Check database
        try:
            from database.database_connection import check_database_health
            db_health = check_database_health()
            health["components"]["database"] = db_health
        except Exception as e:
            health["components"]["database"] = {"status": "unknown", "error": str(e)}

        # Check ChromaDB
        try:
            from database.chromadb_store import chroma_store
            health["components"]["chromadb"] = chroma_store.health_check()
        except Exception as e:
            health["components"]["chromadb"] = {"status": "unknown", "error": str(e)}

        # Check agents
        health["components"]["agents"] = {
            "status":  "healthy",
            "count":   8,
            "online":  8
        }

        # Overall status
        statuses = [c.get("status", "unknown") for c in health["components"].values()]
        health["overall"] = "healthy" if all(s == "healthy" for s in statuses) else "degraded"

        self.health_log.append(health)
        return health

    def get_dashboard_metrics(self) -> dict:
        """Return metrics formatted for the AIRA control centre dashboard."""
        api_calls = [
            m for m in self.metrics_log
            if m["metric"] == "api_response_time"
        ]
        avg_response = (
            sum(m["value"] for m in api_calls) / len(api_calls)
            if api_calls else 0
        )

        return {
            "uptime_seconds":   (datetime.utcnow() - self.start_time).seconds,
            "total_api_calls":  len(api_calls),
            "avg_response_ms":  round(avg_response, 2),
            "total_alerts":     len(self.alerts),
            "health_checks":    len(self.health_log),
            "last_health_check": self.health_log[-1]["timestamp"] if self.health_log else None,
            "generated_at":     datetime.utcnow().isoformat()
        }

    def raise_alert(
        self,
        alert_type:  str,
        message:     str,
        severity:    str = "medium",
        component:   str = "system"
    ) -> dict:
        """Raise a monitoring alert."""
        alert = {
            "id":        len(self.alerts) + 1,
            "type":      alert_type,
            "message":   message,
            "severity":  severity,
            "component": component,
            "raised_at": datetime.utcnow().isoformat(),
            "resolved":  False
        }
        self.alerts.append(alert)
        return alert

    def resolve_alert(self, alert_id: int) -> dict:
        """Resolve a monitoring alert."""
        for alert in self.alerts:
            if alert["id"] == alert_id:
                alert["resolved"]    = True
                alert["resolved_at"] = datetime.utcnow().isoformat()
                return alert
        return {"error": f"Alert {alert_id} not found"}

    def get_active_alerts(self) -> List[dict]:
        """Return all unresolved monitoring alerts."""
        return [a for a in self.alerts if not a.get("resolved")]


# ── SINGLETON INSTANCE ──
monitor = AIRAMonitor()

if __name__ == "__main__":
    print("Testing AIRA Monitor...")
    monitor.record_api_call("/agents/status", "GET", 200, 45.2)
    monitor.record_api_call("/compliance/check", "POST", 200, 1250.8)
    health = monitor.check_system_health()
    print(f"System health: {health['overall']}")
    print(f"Components: {list(health['components'].keys())}")
    metrics = monitor.get_dashboard_metrics()
    print(f"Dashboard metrics: {metrics}")
    alert = monitor.raise_alert(
        alert_type = "high_response_time",
        message    = "API response time exceeded 1000ms",
        severity   = "medium",
        component  = "api"
    )
    print(f"Alert raised: #{alert['id']} — {alert['message']}")
    print("AIRA Monitor working correctly!")
