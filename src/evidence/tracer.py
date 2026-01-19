"""Evidence tracer for RESPOND search results."""

from src.utils.logger import get_logger

_logger = get_logger("evidence.tracer")


def extract_evidence(payload: dict) -> dict:
    """Extract structured evidence from incident payload.
    
    Args:
        payload: Incident payload from Qdrant.
    
    Returns:
        Structured evidence object with all supporting information.
    """
    # Primary evidence from original report
    primary = {
        "primary_text": payload.get("text", ""),
        "primary_source": payload.get("source_type", "unknown"),
        "timestamp": payload.get("timestamp"),
        "location": payload.get("location"),
        "confidence_score": payload.get("confidence_score", 0.5),
        "status": payload.get("status", "pending"),
        "urgency": payload.get("urgency", "medium"),
        "zone_id": payload.get("zone_id", "unknown"),
    }
    
    # Evidence chain from reinforcement
    evidence_chain = payload.get("evidence_chain", [])
    
    # Count accepted evidence
    accepted_count = sum(1 for e in evidence_chain if e.get("accepted", False))
    
    # Build evidence summary
    evidence = {
        **primary,
        "evidence_count": len(evidence_chain),
        "accepted_evidence_count": accepted_count,
        "is_multi_source_confirmed": accepted_count >= 1,
        "evidence_chain": evidence_chain,
    }
    
    return evidence
