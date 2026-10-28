"""gr-L3-confidence-gate: Confidence threshold enforcement."""
import json
import logging
from nemoguardrails.actions import action

logger = logging.getLogger("gr-L3-confidence-gate")

BLOCK_THRESHOLD = 0.5
ESCALATE_THRESHOLD = 0.7


@action()
async def check_confidence_scores(output: str) -> str:
    """Check confidence scores. Returns 'pass', 'escalate', or 'block'."""
    if not output:
        return "block"

    try:
        data = json.loads(output) if isinstance(output, str) else output
        items = data.get("output", {}).get("items", [])

        if not items:
            return "pass"

        needs_escalation = False

        for i, item in enumerate(items):
            meta = item.get("metadata", {})
            confidence = meta.get("confidence")

            if confidence is None:
                logger.warning(f"CONFIDENCE_GATE: item[{i}] missing confidence score")
                return "block"

            try:
                conf_val = float(confidence)
            except (ValueError, TypeError):
                logger.warning(f"CONFIDENCE_GATE: item[{i}] invalid confidence: {confidence}")
                return "block"

            if conf_val < BLOCK_THRESHOLD:
                logger.warning(f"CONFIDENCE_GATE: item[{i}] confidence {conf_val} below block threshold")
                return "block"

            if conf_val < ESCALATE_THRESHOLD:
                needs_escalation = True
                logger.info(f"CONFIDENCE_GATE: item[{i}] confidence {conf_val} needs HITL review")

        return "escalate" if needs_escalation else "pass"

    except (json.JSONDecodeError, TypeError) as e:
        logger.error(f"CONFIDENCE_GATE: parse error: {e}")
        return "block"
