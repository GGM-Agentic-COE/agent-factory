"""gr-L1-secrets-protection: Deterministic secrets and credential detection."""
import re
import logging
from nemoguardrails.actions import action

logger = logging.getLogger("gr-L1-secrets-protection")

API_KEY_PATTERNS = [
    r'(?i)AKIA[0-9A-Z]{16}',  # AWS Access Key
    r'(?i)sk-[a-zA-Z0-9]{32,}',  # OpenAI key
    r'(?i)sk_live_[a-zA-Z0-9]{24,}',  # Stripe live key
    r'(?i)ghp_[a-zA-Z0-9]{36}',  # GitHub PAT
    r'(?i)xox[baprs]-[a-zA-Z0-9-]+',  # Slack token
    r'(?i)AIza[0-9A-Za-z_-]{35}',  # Google API key
]

CREDENTIAL_PATTERNS = [
    r'(?i)password\s*[:=]\s*["\']?[^\s"\']{8,}',
    r'(?i)secret\s*[:=]\s*["\']?[^\s"\']{8,}',
    r'(?i)token\s*[:=]\s*["\']?[^\s"\']{16,}',
    r'-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----',
    r'(?i)bearer\s+[a-zA-Z0-9._-]{20,}',
    r'(?i)eyJ[a-zA-Z0-9_-]+\.eyJ[a-zA-Z0-9_-]+',  # JWT
]

INTERNAL_URL_PATTERNS = [
    r'https?://[a-z0-9.-]+\.internal\.[a-z]+',
    r'https?://localhost:\d+',
    r'https?://127\.0\.0\.1:\d+',
    r'https?://10\.\d+\.\d+\.\d+',
    r'https?://192\.168\.\d+\.\d+',
    r'https?://172\.(1[6-9]|2\d|3[01])\.\d+\.\d+',
]


@action()
async def detect_secrets(text: str) -> bool:
    """Return True if secrets found, False if clean."""
    if not text:
        return False

    content = text if isinstance(text, str) else str(text)

    for pattern in API_KEY_PATTERNS:
        if re.search(pattern, content):
            logger.warning(f"SECRETS_PROTECTION: API key pattern matched")
            return True

    for pattern in CREDENTIAL_PATTERNS:
        if re.search(pattern, content):
            logger.warning(f"SECRETS_PROTECTION: credential pattern matched")
            return True

    for pattern in INTERNAL_URL_PATTERNS:
        if re.search(pattern, content):
            logger.warning(f"SECRETS_PROTECTION: internal URL detected")
            return True

    return False
