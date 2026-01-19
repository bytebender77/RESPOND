"""Action recommendation engine for RESPOND."""

from src.search import HybridSearcher
from src.utils.logger import get_logger

_logger = get_logger("recommendation.action")

# Keyword-based action rules
ACTION_RULES = {
    "fire": {"action_type": "DISPATCH_FIRE_BRIGADE", "base_priority": 4},
    "smoke": {"action_type": "DISPATCH_FIRE_BRIGADE", "base_priority": 4},
    "flood": {"action_type": "ISSUE_EVACUATION_ALERT", "base_priority": 4},
    "water": {"action_type": "ISSUE_EVACUATION_ALERT", "base_priority": 3},
    "collapse": {"action_type": "PRIORITIZE_HEAVY_EQUIPMENT", "base_priority": 4},
    "trapped": {"action_type": "DISPATCH_SEARCH_AND_RESCUE", "base_priority": 5},
    "earthquake": {"action_type": "DISPATCH_SEARCH_AND_RESCUE", "base_priority": 5},
    "explosion": {"action_type": "DISPATCH_FIRE_BRIGADE", "base_priority": 5},
}


class ActionRecommender:
    """Generates operational action recommendations based on incidents."""

    def __init__(self):
        self._searcher = HybridSearcher()

    def recommend_actions(
        self,
        query: str,
        limit: int = 5,
        zone_id: str | None = None,
    ) -> dict:
        """Generate action recommendations based on search results.
        
        Args:
            query: Search query text.
            limit: Max incidents to consider.
            zone_id: Optional zone filter.
        
        Returns:
            Dict with query, actions, and evidence_used.
        """
        # Fetch incidents
        incidents = self._searcher.search_incidents(
            query=query,
            limit=limit,
            zone_id=zone_id,
        )
        
        actions = []
        evidence_used = []
        seen_actions = {}  # action_type -> action dict
        
        for incident in incidents:
            payload = incident["payload"]
            evidence = incident["evidence"]
            incident_id = str(incident["id"])
            
            text = payload.get("text", "").lower()
            urgency = payload.get("urgency", "medium")
            status = payload.get("status", "pending")
            is_confirmed = evidence.get("is_multi_source_confirmed", False)
            
            # Track evidence used
            evidence_used.append({
                "id": incident_id,
                "text": payload.get("text", ""),
                "urgency": urgency,
                "status": status,
            })
            
            # Generate actions from keywords
            for keyword, rule in ACTION_RULES.items():
                if keyword in text:
                    action_type = rule["action_type"]
                    base_priority = rule["base_priority"]
                    
                    # Calculate priority
                    priority = base_priority
                    if urgency == "critical":
                        priority = min(5, priority + 1)
                    if is_confirmed:
                        priority = min(5, priority + 1)
                    
                    # Build reason
                    reason_parts = [f"Detected '{keyword}' in incident report"]
                    if urgency == "critical":
                        reason_parts.append("urgency is critical")
                    if is_confirmed:
                        reason_parts.append("multi-source confirmed")
                    if status == "pending":
                        reason_parts.append("awaiting response")
                    
                    reason = "; ".join(reason_parts)
                    
                    # Merge or create action
                    if action_type in seen_actions:
                        # Update if higher priority
                        existing = seen_actions[action_type]
                        if priority > existing["priority"]:
                            existing["priority"] = priority
                            existing["reason"] = reason
                        if incident_id not in existing["incident_ids"]:
                            existing["incident_ids"].append(incident_id)
                    else:
                        action = {
                            "action_type": action_type,
                            "priority": priority,
                            "reason": reason,
                            "incident_ids": [incident_id],
                        }
                        seen_actions[action_type] = action
                        actions.append(action)
            
            # Critical pending incidents get search and rescue
            if urgency == "critical" and status == "pending":
                action_type = "DISPATCH_SEARCH_AND_RESCUE"
                if action_type not in seen_actions:
                    priority = 5 if is_confirmed else 4
                    action = {
                        "action_type": action_type,
                        "priority": priority,
                        "reason": f"Critical pending incident in {payload.get('zone_id', 'unknown zone')}",
                        "incident_ids": [incident_id],
                    }
                    seen_actions[action_type] = action
                    actions.append(action)
                elif incident_id not in seen_actions[action_type]["incident_ids"]:
                    seen_actions[action_type]["incident_ids"].append(incident_id)
        
        # Sort by priority descending
        actions.sort(key=lambda x: x["priority"], reverse=True)
        
        _logger.info(f"Generated {len(actions)} actions for query '{query[:30]}...'")
        
        return {
            "query": query,
            "actions": actions,
            "evidence_used": evidence_used,
        }
