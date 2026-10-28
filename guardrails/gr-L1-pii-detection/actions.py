"""gr-L1-pii-detection: Deterministic PII pattern detection."""
import re
import logging
from nemoguardrails.actions import action

logger = logging.getLogger("gr-L1-pii-detection")

PII_PATTERNS = {
    "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    "phone": r'\b(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}\b',
    "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
    "credit_card": r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
    "passport": r'\b[A-Z]{1,2}\d{6,9}\b',
    "address": r'\b\d{1,5}\s+[A-Z][a-z]+\s+(Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Boulevard|Blvd)\b',
}


@action()
async def detect_pii(text: str) -> bool:
    """Return True if PII is found, False if clean."""
    if not text:
        return False

    content = text if isinstance(text, str) else str(text)

    for pii_type, pattern in PII_PATTERNS.items():
        if re.search(pattern, content):
            logger.warning(f"PII_DETECTION: {pii_type} pattern found")
            return True

    return False
