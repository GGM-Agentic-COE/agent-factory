"""gr-L1-accessibility-standards: Deterministic accessibility checks."""
import re
import logging
from nemoguardrails.actions import action

logger = logging.getLogger("gr-L1-accessibility-standards")

ABLEIST_TERMS = [
    r'\bblind\s+spot\b', r'\bfalling\s+on\s+deaf\s+ears\b',
    r'\blame\b', r'\bcrippled?\b', r'\bdumb\b',
    r'\binsane\b', r'\bcrazy\b', r'\bmental\b(?!\s+model)',
    r'\bsuffering\s+from\b', r'\bconfined\s+to\s+a\s+wheelchair\b',
]

VAGUE_REFERENCES = [
    r'\bclick\s+here\b', r'\bsee\s+above\b', r'\bsee\s+below\b',
    r'\bthe\s+button\s+on\s+the\s+(left|right)\b',
    r'\bas\s+shown\s+in\s+the\s+image\b',
]

COLOUR_ONLY_PATTERNS = [
    r'\b(red|green|blue|yellow)\s+(items?|ones?|entries?)\s+(are|indicate|mean)\b',
    r'\bhighlighted\s+in\s+(red|green|blue|yellow)\b(?!.*\b(label|text|icon|marker)\b)',
]


@action()
async def check_accessibility(output: str) -> bool:
    """Return True if accessibility violation found, False if clean."""
    if not output:
        return False

    text = output if isinstance(output, str) else str(output)
    text_lower = text.lower()

    # Check for ableist/exclusionary language
    for pattern in ABLEIST_TERMS:
        if re.search(pattern, text_lower):
            logger.warning(f"ACCESSIBILITY: ableist term detected: {pattern}")
            return True

    # Check for vague directional references
    for pattern in VAGUE_REFERENCES:
        if re.search(pattern, text_lower):
            logger.warning(f"ACCESSIBILITY: vague reference detected: {pattern}")
            return True

    # Check for colour-only information
    for pattern in COLOUR_ONLY_PATTERNS:
        if re.search(pattern, text_lower):
            logger.warning(f"ACCESSIBILITY: colour-only meaning detected: {pattern}")
            return True

    # Check for images without alt text (HTML img tags)
    img_without_alt = re.findall(r'<img\b(?![^>]*\balt\s*=\s*"[^"]+")[^>]*>', text)
    if img_without_alt:
        logger.warning("ACCESSIBILITY: img tag without alt text (WCAG 1.1.1)")
        return True

    # HTML-specific checks (only if output contains HTML)
    if "<html" in text_lower or "<!doctype" in text_lower:
        # WCAG 3.1.1: lang attribute
        if "<html" in text_lower and not re.search(r'<html[^>]*\blang\s*=', text_lower):
            logger.warning("ACCESSIBILITY: HTML missing lang attribute (WCAG 3.1.1)")
            return True

        # WCAG 2.4.2: page title
        if "<head" in text_lower and not re.search(r'<title>[^<]+</title>', text_lower):
            logger.warning("ACCESSIBILITY: HTML missing meaningful title (WCAG 2.4.2)")
            return True

        # WCAG 3.3.2: form labels
        inputs_without_labels = re.findall(r'<input\b(?![^>]*\baria-label)[^>]*>', text)
        if inputs_without_labels:
            for inp in inputs_without_labels:
                inp_id = re.search(r'id\s*=\s*["\']([^"\']+)', inp)
                if inp_id and f'for="{inp_id.group(1)}"' not in text and f"for='{inp_id.group(1)}'" not in text:
                    logger.warning("ACCESSIBILITY: form input without label (WCAG 3.3.2)")
                    return True

        # WCAG 2.4.4: link purpose
        generic_links = re.findall(r'<a\b[^>]*>\s*(click here|here|link|read more)\s*</a>', text_lower)
        if generic_links:
            logger.warning("ACCESSIBILITY: generic link text (WCAG 2.4.4)")
            return True

    return False
