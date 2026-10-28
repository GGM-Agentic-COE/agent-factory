"""gr-L4-reasoning-validator: Reasoning quality validation."""
import json
import logging
from nemoguardrails.actions import action

logger = logging.getLogger("gr-L4-reasoning-validator")

MIN_REASONING_LENGTH = 20

GENERIC_FILLERS = [
    "this is the reasoning",
    "reasoning goes here",
    "n/a",
    "none",
    "see above",
]


@action()
async def validate_reasoning(output: str) -> bool:
    """Validate reasoning field quality on each item."""
    if not output:
        return False

    try:
        data = json.loads(output) if isinstance(output, str) else output
        items = data.get("output", {}).get("items", [])

        if not items:
            return True

        for i, item in enumerate(items):
            meta = item.get("metadata", {})
            reasoning = meta.get("reasoning")

            if not reasoning:
                logger.warning(f"REASONING_VALIDATOR: item[{i}] missing reasoning")
                return False

            if not isinstance(reasoning, str):
                reasoning = str(reasoning)

            if len(reasoning.strip()) < MIN_REASONING_LENGTH:
                logger.warning(f"REASONING_VALIDATOR: item[{i}] reasoning too short ({len(reasoning.strip())} chars)")
                return False

            if reasoning.strip().lower() in GENERIC_FILLERS:
                logger.warning(f"REASONING_VALIDATOR: item[{i}] generic filler reasoning")
                return False

        return True

    except (json.JSONDecodeError, TypeError) as e:
        logger.error(f"REASONING_VALIDATOR: parse error: {e}")
        return False
