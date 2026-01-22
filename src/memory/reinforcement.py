"""Reinforcement logic for RESPOND incident confidence boosting."""

import math

from src.utils.time_utils import utc_now_iso
from src.utils.logger import get_logger

_logger = get_logger("memory.reinforcement")


def compute_text_similarity(vec1: list[float], vec2: list[float]) -> float:
    """Compute cosine similarity between two vectors.
    
    Args:
        vec1: First embedding vector.
        vec2: Second embedding vector.
    
    Returns:
        Cosine similarity in range [-1, 1].
    """
    if len(vec1) != len(vec2):
        raise ValueError("Vectors must have same length")
    
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = math.sqrt(sum(a * a for a in vec1))
    norm2 = math.sqrt(sum(b * b for b in vec2))
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    return dot_product / (norm1 * norm2)


def reinforce_incident(
    incident_payload: dict,
    new_source_type: str,
    new_text: str,
    similarity: float,
) -> dict:
    """Apply reinforcement logic to incident payload.
    
    Args:
        incident_payload: Current incident payload.
        new_source_type: Source type of new evidence.
        new_text: Text content of new evidence.
        similarity: Cosine similarity between texts.
    
    Returns:
        Updated payload dict with reinforcement applied.
    """
    old_confidence = incident_payload.get("confidence_score", 0.5)
    evidence_chain = incident_payload.get("evidence_chain", [])
    reinforced_count = incident_payload.get("reinforced_count", 0)
    
    # Determine if evidence is accepted
    accepted = similarity >= 0.50
    
    # Compute new confidence
    if accepted:
        boost = min(0.15, similarity * 0.1)
        new_confidence = min(1.0, old_confidence + boost)
        reinforced_count += 1
        _logger.info(f"Reinforcement accepted: {old_confidence:.3f} -> {new_confidence:.3f}")
    else:
        new_confidence = old_confidence
        _logger.info(f"Reinforcement rejected: similarity {similarity:.3f} < 0.65")
    
    # Create evidence entry
    evidence_entry = {
        "source_type": new_source_type,
        "text": new_text,
        "similarity": round(similarity, 4),
        "timestamp": utc_now_iso(),
        "accepted": accepted,
    }
    evidence_chain.append(evidence_entry)
    
    # Return updated payload fields
    return {
        "confidence_score": new_confidence,
        "evidence_chain": evidence_chain,
        "reinforced_count": reinforced_count,
        "updated_at": utc_now_iso(),
        "_meta": {
            "old_confidence": old_confidence,
            "new_confidence": new_confidence,
            "accepted": accepted,
            "similarity": similarity,
        },
    }
