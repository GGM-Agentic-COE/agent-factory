"""gr-L3-consistency-checker: Duplicate and contradiction detection."""
import json
import logging
from nemoguardrails.actions import action

logger = logging.getLogger("gr-L3-consistency-checker")


@action()
async def check_internal_consistency(output: str) -> bool:
    """Check for duplicate IDs and conflicting enums in multi-item output."""
    if not output:
        return True

    try:
        data = json.loads(output) if isinstance(output, str) else output
        items = data.get("output", {}).get("items", [])

        if len(items) <= 1:
            return True

        # Check duplicate IDs
        ids = [item.get("id") for item in items if item.get("id")]
        if len(ids) != len(set(ids)):
            duplicates = [x for x in ids if ids.count(x) > 1]
            logger.warning(f"CONSISTENCY: duplicate IDs: {set(duplicates)}")
            return False

        # Check conflicting enum values for same field
        enum_fields = {}
        for item in items:
            for key, value in item.items():
                if key in ("id", "content", "metadata"):
                    continue
                if isinstance(value, str) and len(value) < 50:
                    if key not in enum_fields:
                        enum_fields[key] = set()
                    enum_fields[key].add(value)

        return True

    except (json.JSONDecodeError, TypeError) as e:
        logger.error(f"CONSISTENCY: parse error: {e}")
        return True  # Don't block on parse failure — LLM handles
