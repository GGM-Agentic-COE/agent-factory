"""gr-L1-injection-defence: Deterministic injection pattern detection."""
import re
import logging
from nemoguardrails.actions import action

logger = logging.getLogger("gr-L1-injection-defence")

INJECTION_PATTERNS = [
    r'(?i)ignore\s+(all\s+)?(previous|prior|above)\s+(instructions?|prompts?|rules?)',
    r'(?i)disregard\s+(all\s+)?(previous|prior|above)',
    r'(?i)you\s+are\s+now\s+',
    r'(?i)new\s+instructions?:',
    r'(?i)^system\s*:',
    r'(?i)forget\s+(everything|all|your\s+instructions)',
    r'(?i)override\s+(previous|system|your)',
    r'(?i)act\s+as\s+(if|though)\s+you\s+(have\s+)?no\s+restrictions',
    r'(?i)pretend\s+(you\s+are|to\s+be)\s+',
    r'(?i)reveal\s+(your|the)\s+(system\s+)?prompt',
    r'(?i)print\s+(your|the)\s+(system\s+)?(prompt|instructions)',
    r'(?i)\]\]\s*>\s*',  # XML/markup injection
    r'(?i)```\s*system',  # Fenced system block
]

BOUNDARY_MARKERS = [
    r'(?i)<\|im_start\|>',
    r'(?i)<\|im_end\|>',
    r'(?i)###\s*(system|assistant|user)\s*:',
    r'(?i)\[INST\]',
    r'(?i)\[/INST\]',
]


@action()
async def detect_injection_patterns(input: str) -> bool:
    """Return True if input is SAFE, False if injection detected."""
    if not input:
        return True

    text = input if isinstance(input, str) else str(input)

    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text):
            logger.warning(f"INJECTION_DEFENCE: pattern matched: {pattern}")
            return False

    for marker in BOUNDARY_MARKERS:
        if re.search(marker, text):
            logger.warning(f"INJECTION_DEFENCE: boundary marker detected: {marker}")
            return False

    return True
