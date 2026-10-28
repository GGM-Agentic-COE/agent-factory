"""gr-L2-payments-compliance: Payments regulatory reference validation."""
import re
import logging
from nemoguardrails.actions import action

logger = logging.getLogger("gr-L2-payments-compliance")

VALID_REGULATIONS = [
    "PSD2", "PSD3", "SCA", "PCI-DSS", "PCI DSS",
    "EMD2", "AMLD", "GDPR", "FCA", "PSR",
    "Wire Transfer Regulation", "Interchange Fee Regulation",
]

VALID_PSD2_ARTICLES = {
    "Article 97": "SCA requirements",
    "Article 98": "RTS on SCA",
    "Article 4": "Definitions",
    "Article 64": "Notification",
    "Article 74": "Liability",
}

PAYMENTS_TERMINOLOGY = [
    "PSP", "PISP", "AISP", "ASPSP", "acquirer", "issuer",
    "scheme", "interchange", "merchant", "cardholder",
    "card-not-present", "CNP", "3DS", "3D Secure",
]


@action()
async def validate_payments_references(output: str) -> bool:
    """Validate regulatory references in payments output."""
    if not output:
        return True

    content = output if isinstance(output, str) else str(output)

    # Check for regulation-like references that don't match known list
    reg_refs = re.findall(r'\b([A-Z]{2,5}\d?)\s+Article\s+(\d+)', content)
    for reg, article in reg_refs:
        if reg == "PSD2" and f"Article {article}" not in VALID_PSD2_ARTICLES:
            logger.warning(f"PAYMENTS_COMPLIANCE: invalid PSD2 article reference: Article {article}")
            return False

    # Check for SCA requirement in CNP contexts
    if re.search(r'(?i)\b(card.not.present|CNP|e-commerce\s+payment)', content):
        if not re.search(r'(?i)\b(SCA|strong\s+customer\s+authentication|3DS|3D\s+Secure)', content):
            logger.warning("PAYMENTS_COMPLIANCE: CNP transaction without SCA reference")
            return False

    return True
