from typing import List, Optional
from datetime import datetime

# ── AIRA VISUALISATIONS ──
# Data preparation for Chart.js, D3.js, and Canvas API
# in the AIRA frontend dashboard.

class VisualisationBuilder:
    """
    Prepares data structures for all AIRA dashboard charts.
    Outputs JSON-ready data for Chart.js, D3.js, and Canvas API.
    """

    # ── RISK SCORE GAUGE DATA ──

    def risk_gauge(self, score: float) -> dict:
        """Prepare data for a Canvas API risk gauge."""
        if score >= 80:
            color, label = "#FF3355", "Critical"
        elif score >= 60:
            color, label = "#FF6B35", "High"
        elif score >= 40:
            color, label = "#FFD700", "Medium"
        else:
            color, label = "#00FF88", "Low"

        return {
            "type":  "gauge",
            "score": score,
            "color": color,
            "label": label,
            "max":   100
        }

    # ── IDENTITY DISTRIBUTION DONUT ──

    def identity_donut(self, counts: dict) -> dict:
        """Prepare donut chart data for identity type distribution."""
        return {
            "type": "donut",
            "labels": list(counts.keys()),
            "data":   list(counts.values()),
            "colors": ["#2E2EFF", "#00D4FF", "#00FF88", "#FF6B35", "#CC44FF"]
        }

    # ── RISK TREND LINE CHART ──

    def risk_trend(
        self,
        labels: List[str],
        scores: List[float]
    ) -> dict:
        """Prepare line chart data for risk score trend over time."""
        return {
            "type":   "line",
            "labels": labels,
            "datasets": [{
                "label":           "Risk Score",
                "data":            scores,
                "borderColor":     "#2E2EFF",
                "backgroundColor": "rgba(46,46,255,0.1)",
                "tension":         0.4,
                "fill":            True
            }]
        }

    # ── COMPLIANCE HEAT MAP DATA ──

    def compliance_heatmap(
        self,
        sectors:    List[str],
        frameworks: List[str],
        scores:     List[List[float]]
    ) -> dict:
        """Prepare heat map data for compliance scores."""
        cells = []
        for s_idx, sector in enumerate(sectors):
            for f_idx, framework in enumerate(frameworks):
                score = scores[s_idx][f_idx] if s_idx < len(scores) and f_idx < len(scores[s_idx]) else 0
                cells.append({
                    "sector":    sector,
                    "framework": framework,
                    "score":     score,
                    "color":     self._score_to_color(score)
                })
        return {
            "type":      "heatmap",
            "sectors":   sectors,
            "frameworks": frameworks,
            "cells":     cells
        }

    # ── AGENT STATUS NETWORK ──

    def agent_network(self, agent_statuses: List[dict]) -> dict:
        """Prepare D3.js network data for agent relationships."""
        nodes = [{"id": "AIRA", "type": "core", "size": 20}]
        links = []

        for agent in agent_statuses:
            nodes.append({
                "id":     agent["agent"],
                "name":   agent["name"],
                "status": agent.get("status", "online"),
                "size":   10,
                "color":  "#00FF88" if agent.get("status") == "online" else "#FF3355"
            })
            links.append({
                "source": "AIRA",
                "target": agent["agent"]
            })

        return {
            "type":  "network",
            "nodes": nodes,
            "links": links
        }

    # ── SECTOR RISK BAR CHART ──

    def sector_risk_bars(
        self,
        sectors: List[str],
        scores:  List[float]
    ) -> dict:
        """Prepare bar chart data for sector risk comparison."""
        colors = [
            "#FF3355" if s >= 80 else
            "#FF6B35" if s >= 60 else
            "#FFD700" if s >= 40 else
            "#00FF88"
            for s in scores
        ]
        return {
            "type":   "bar",
            "labels": sectors,
            "datasets": [{
                "label":           "Risk Score",
                "data":            scores,
                "backgroundColor": colors,
                "borderRadius":    4
            }]
        }

    # ── SHAP WATERFALL DATA ──

    def shap_waterfall(
        self,
        features:    List[str],
        impacts:     List[float],
        base_score:  float
    ) -> dict:
        """Prepare SHAP waterfall chart data."""
        bars = []
        running = base_score
        for feature, impact in zip(features, impacts):
            bars.append({
                "feature": feature,
                "impact":  impact,
                "start":   running,
                "end":     running + impact,
                "color":   "#FF3355" if impact > 0 else "#00FF88"
            })
            running += impact

        return {
            "type":       "waterfall",
            "base_score": base_score,
            "final_score": running,
            "bars":       bars
        }

    def _score_to_color(self, score: float) -> str:
        """Convert a score to a heat map color."""
        if score >= 80: return "#1D9E75"
        if score >= 60: return "#5BC8A0"
        if score >= 40: return "#EF9F27"
        return "#E24B4A"

    def dashboard_data(
        self,
        risk_score:       float,
        identity_counts:  dict,
        risk_trend_data:  dict,
        agent_statuses:   List[dict]
    ) -> dict:
        """Build complete dashboard data payload."""
        return {
            "gauge":         self.risk_gauge(risk_score),
            "identity_donut": self.identity_donut(identity_counts),
            "risk_trend":    self.risk_trend(
                                risk_trend_data.get("labels", []),
                                risk_trend_data.get("scores", [])
                             ),
            "agent_network": self.agent_network(agent_statuses),
            "generated_at":  datetime.utcnow().isoformat()
        }


# ── SINGLETON INSTANCE ──
viz = VisualisationBuilder()

if __name__ == "__main__":
    print("Testing Visualisation Builder...")
    gauge = viz.risk_gauge(78.5)
    print(f"Gauge: score={gauge['score']} color={gauge['color']} label={gauge['label']}")
    donut = viz.identity_donut({"Human": 850, "Machine": 320, "Robot": 77})
    print(f"Donut labels: {donut['labels']}")
    print("Visualisation Builder working correctly!")
