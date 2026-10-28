"""gr-L3-hallucination-detector: Fabrication pattern detection."""
import re
import json
import logging
from nemoguardrails.actions import action

logger = logging.getLogger("gr-L3-hallucination-detector")

FABRICATION_INDICATORS = [
    r'(?i)\b(according\s+to\s+(?:a\s+)?(?:recent\s+)?study)\b',
    r'(?i)\b(research\s+shows|studies\s+indicate|experts\s+say)\b',
    r'(?i)\b(approximately\s+\d+%\s+of)\b',
    r'https?://(?!kb-|source-)[a-z0-9.-]+\.(?:com|org|io)/[^\s"]+',  # URLs not from KB
]


@action()
async def detect_fabrication_patterns(output: str) -> bool:
    """Detect potential fabrication patterns. Return True if fabrication suspected."""
    if not output:
        return False

    content = output if isinstance(output, str) else str(output)

    try:
        data = json.loads(content)
        items = data.get("output", {}).get("items", [])

        for item in items:
            meta = item.get("metadata", {})
            reasoning = meta.get("reasoning", "")
            citations = meta.get("citation", [])

            # Item with strong claims but no citations
            body = json.dumps(item.get("content", ""))
            has_numbers = bool(re.search(r'\b\d{2,}%|\b\d{4,}\b', body))
            if has_numbers and not citations:
                logger.warning("HALLUCINATION: numeric claims without citations")
                return True

        return False
    except (json.JSONDecodeError, TypeError):
        # Non-JSON output — check for fabrication indicators
        for pattern in FABRICATION_INDICATORS:
            if re.search(pattern, content):
                logger.warning(f"HALLUCINATION: fabrication indicator: {pattern}")
                return True
        return False
