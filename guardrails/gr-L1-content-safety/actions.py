"""gr-L1-content-safety: Deterministic content safety checks."""
import re
import json
import logging
from nemoguardrails.actions import action

logger = logging.getLogger("gr-L1-content-safety")

# Severity: CRITICAL — violence/harm instructions
CRITICAL_PATTERNS = [
    (r"(?i)\b(kill\s+(yourself|themselves|himself|herself)|commit\s+suicide)\b", "self_harm", "Self-harm or suicide instruction detected"),
    (r"(?i)\b(how\s+to\s+(make|build|create)\s+(a\s+)?(bomb|weapon|explosive|gun))\b", "weapons", "Weapons/explosive manufacturing instructions"),
    (r"(?i)\b(instructions\s+for\s+(making|creating)\s+(drugs|weapons|poison|meth))\b", "illegal_activity", "Illegal manufacturing instructions"),
    (r"(?i)\b(how\s+to\s+(hack|ddos|phish|crack)\s+)", "illegal_activity", "Hacking/cybercrime instructions"),
]

# Severity: CRITICAL — hate speech (slurs only; contextual bias handled elsewhere)
HATE_SPEECH_PATTERNS = [
    (r"(?i)\b(n[i1]gg[ae]r|f[a@]gg?[o0]t|k[i1]ke|sp[i1]c|ch[i1]nk|w[e3]tb[a@]ck|r[e3]t[a@]rd)\b", "hate_speech", "Hate speech slur detected"),
]

# Severity: MEDIUM — profanity (threshold-based, excludes gendered slurs handled by misogyny guardrail)
PROFANITY_PATTERN = re.compile(r"(?i)\b(fuck|shit|damn|ass|bastard|crap)\b")
PROFANITY_THRESHOLD = 3


def _scan_patterns(text, patterns, severity):
    """Scan text against pattern list. Returns (matched, details)."""
    for pattern, category, reason in patterns:
        match = re.search(pattern, text)
        if match:
            return True, {"severity": severity, "category": category, "reason": reason, "matched_text": match.group(0)}
    return False, None


@action()
async def check_content_safety(text: str) -> bool:
    """Return True if UNSAFE content found, False if safe."""
    if not text:
        return False

    # Critical: violence/harm
    found, details = _scan_patterns(text, CRITICAL_PATTERNS, "critical")
    if found:
        logger.warning("CRITICAL content safety | category=%s | text='%s'", details["category"], details["matched_text"])
        return True

    # Critical: hate speech
    found, details = _scan_patterns(text, HATE_SPEECH_PATTERNS, "critical")
    if found:
        logger.warning("CRITICAL content safety | category=%s | text='%s'", details["category"], details["matched_text"])
        return True

    # Medium: excessive profanity
    profanity_count = len(PROFANITY_PATTERN.findall(text))
    if profanity_count >= PROFANITY_THRESHOLD:
        logger.warning("MEDIUM content safety | category=profanity | count=%d", profanity_count)
        return True

    return False


@action()
async def analyse_content_safety(text: str) -> str:
    """Return structured JSON analysis of content safety."""
    if not text:
        return json.dumps({"detected": False, "verdict": "accepted", "reason": "Empty input", "findings": [], "severity": None})

    findings = []

    for patterns, severity in [(CRITICAL_PATTERNS, "critical"), (HATE_SPEECH_PATTERNS, "critical")]:
        for pattern, category, reason in patterns:
            match = re.search(pattern, text)
            if match:
                findings.append({"severity": severity, "category": category, "reason": reason, "matched_text": match.group(0)})

    profanity_count = len(PROFANITY_PATTERN.findall(text))
    if profanity_count >= PROFANITY_THRESHOLD:
        findings.append({"severity": "medium", "category": "profanity", "reason": f"Excessive profanity ({profanity_count} instances)", "matched_text": None})

    if findings:
        top = findings[0]
        return json.dumps({"detected": True, "verdict": "rejected", "reason": top["reason"], "severity": top["severity"], "category": top["category"], "findings": findings, "total_violations": len(findings)})

    return json.dumps({"detected": False, "verdict": "accepted", "reason": "No unsafe content found", "findings": [], "severity": None})
