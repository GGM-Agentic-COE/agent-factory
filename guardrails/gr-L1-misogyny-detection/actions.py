"""gr-L1-misogyny-detection: Detects misogynistic and sexist content in agent output."""
import re
import json
import logging
from nemoguardrails.actions import action

logger = logging.getLogger("gr-L1-misogyny-detection")

CRITICAL_PATTERNS = [
    (r"\b(bitch|slut|whore|thot|bimbo|skank|tramp|harlot|wench|feminazi|femoid|foid)\b", "slur", "Derogatory gender-specific slur detected"),
    (r"\b(she'?s?\s+a|calling\s+her\s+a|dirty|stupid)\s+hoe\b", "slur", "Derogatory use of gendered slur in context"),
]

HIGH_PATTERNS = [
    (r"\b(women|girls|females|she)\s+(belong|should stay|are meant)\s+(in the|at home|in the kitchen)", "role_enforcement", "Prescriptive gender role: domestic confinement"),
    (r"\b(too emotional|too sensitive|too hysterical)\s+(to|for)\s+(lead|manage|decide|work|handle)", "competence_denial", "Emotional incompetence stereotype applied to gender"),
    (r"\bwom[ae]n\s+(can't|cannot|shouldn't|are(n't| not) (able|capable|smart enough))\b", "competence_denial", "Direct denial of competence based on gender"),
    (r"\bno place for (women|girls|ladies)\b", "competence_denial", "Gender-based exclusion from roles/spaces"),
    (r"\b(real wom[ae]n|proper lad(y|ies))\s+(should|must|need to|don't)\b", "role_enforcement", "Prescriptive enforcement of gender norms"),
    (r"\b(make me a sandwich|get back to the kitchen|know (her|your|their) place)\b", "role_enforcement", "Derogatory gender role enforcement"),
    (r"\b(all women are|women always)\s+(bad|weak|emotional|crazy|irrational|incompetent|useless|stupid)", "generalisation", "Negative sweeping generalisation based on gender"),
    (r"\btypical (woman|female)\b", "dismissal", "Dismissive gender generalisation"),
]

MEDIUM_PATTERNS = [
    (r"\b(man up|grow a pair)\b", "toxic_masculinity", "Toxic masculinity phrase used to demean"),
    (r"\b(like a girl|throw like a girl|run like a girl)\b", "diminishment", "Using femininity as insult or diminishment"),
    (r"\b(good|impressive|smart)\s+(for a|considering she'?s a)\s+(woman|girl|female)\b", "backhanded", "Backhanded compliment implying gender-based exception"),
    (r"\b(girls? (don'?t|shouldn'?t|can'?t)\s+(code|program|engineer|build))\b", "gatekeeping", "Gender-based gatekeeping of technical capability"),
]


def _scan_all(text):
    """Scan text against all pattern tiers. Returns list of all matches."""
    findings = []
    for patterns, severity in [(CRITICAL_PATTERNS, "critical"), (HIGH_PATTERNS, "high"), (MEDIUM_PATTERNS, "medium")]:
        for pattern, category, reason in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                findings.append({
                    "severity": severity,
                    "category": category,
                    "reason": reason,
                    "matched_text": match.group(0),
                })
    return findings


@action()
async def detect_misogyny_patterns(text: str) -> bool:
    """Return True if misogynistic patterns detected, False if clean."""
    if not text:
        return False
    findings = _scan_all(text)
    if findings:
        logger.warning("Misogyny detected: %s", json.dumps(findings[0]))
        return True
    return False


@action()
async def analyse_misogyny(text: str) -> str:
    """
    Analyse text for misogyny and return structured JSON result.
    Returns JSON string with detection status, findings, and verdict.
    """
    if not text:
        return json.dumps({
            "detected": False,
            "verdict": "accepted",
            "reason": "Empty input — nothing to evaluate",
            "findings": [],
            "severity": None,
        })

    findings = _scan_all(text)

    if findings:
        top = findings[0]
        return json.dumps({
            "detected": True,
            "verdict": "rejected",
            "reason": top["reason"],
            "severity": top["severity"],
            "category": top["category"],
            "matched_text": top["matched_text"],
            "findings": findings,
            "total_violations": len(findings),
        })

    return json.dumps({
        "detected": False,
        "verdict": "accepted",
        "reason": "No misogynistic patterns found in content",
        "findings": [],
        "severity": None,
    })
