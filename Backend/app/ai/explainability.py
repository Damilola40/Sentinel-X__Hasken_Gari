"""
Module 4: Explainable AI (XAI Layer)
Translates risk model scores and features into plain-language explanations.
"""

from typing import List, Dict, Any

class XAIExplainer:
    def explain_lga_risk(self, lga_row: Dict[str, Any]) -> List[str]:
        """
        Generates human-readable contributing signals for an LGA risk assessment.
        """
        explanations = []
        
        # 1. Incident Velocity / Trend Signals
        change_rate = lga_row.get("change_rate", 1.0)
        if change_rate > 2.0:
            explanations.append(f"Recent 7-day incident frequency increased by {int((change_rate - 1)*100)}% over historical baseline.")
        elif change_rate > 1.2:
            explanations.append("Recent incident velocity shows a steady upward trend.")
            
        # 2. Severity Signals
        avg_sev = lga_row.get("avg_severity", 1.0)
        high_sev_ratio = lga_row.get("high_sev_ratio", 0.0)
        if high_sev_ratio > 0.4:
            explanations.append(f"High concentration of critical/high-severity reports ({int(high_sev_ratio*100)}% of total).")
        elif avg_sev > 2.5:
            explanations.append("Average incident severity in this area is elevated.")
            
        # 3. Anomaly Detection Signals
        if lga_row.get("is_anomaly", False):
            explanations.append("Isolation Forest flagged an unexpected statistical spike compared to historical LGA patterns.")
            
        # 4. Diversity of Threats
        category_diversity = lga_row.get("category_diversity", 1)
        if category_diversity >= 4:
            explanations.append(f"Multiple concurrent security threat types detected ({category_diversity} distinct categories).")
            
        if not explanations:
            explanations.append("Incident activity remains within normal historical baseline limits.")
            
        return explanations
