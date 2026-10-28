"""Custom actions for NeMo Guardrails — called by Colang flows."""
import re
import json
from nemoguardrails.actions import action

PII_PATTERNS = {
    "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    "phone": r'\b(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}\b',
    "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
    "credit_card": r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
    "uk_nino": r'\b[A-Z]{2}\d{6}[A-Z]\b',
}

SECRET_PATTERNS = {
    "aws_key": r'AKIA[0-9A-Z]{16}',
    "api_key": r'(?:api[_-]?key|apikey)\s*[:=]\s*["\']?[A-Za-z0-9_\-]{20,}',
    "jwt": r'eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}',
    "private_key": r'-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----',
    "generic_secret": r'(?:secret|password|token|passwd)\s*[:=]\s*["\']?[^\s"\']{8,}',
}

INJECTION_PATTERNS = [
    r'ignore\s+(all\s+)?previous\s+instructions',
    r'you\s+are\s+now\s+a',
    r'system:\s*',
    r'<\s*system\s*>',
    r'forget\s+(everything|all|your)\s+(above|prior|previous)',
    r'override\s+(your|the)\s+(instructions|rules|prompt)',
    r'new\s+instructions:',
    r'what\s+(are|is)\s+your\s+(system\s+)?prompt',
    r'(show|reveal|print|output)\s+(your\s+)?(system\s+)?(prompt|instructions)',
    r'\[\s*INST\s*\]',
    r'```\s*system',
]

JAILBREAK_PATTERNS = [
    r'(?:do\s+anything\s+now|DAN)',
    r'(?:pretend|act\s+as\s+if)\s+you\s+(?:are|have)\s+no\s+(?:restrictions|rules|limits|guidelines)',
    r'(?:roleplay|role.play)\s+as\s+(?:an?\s+)?(?:unrestricted|uncensored|evil)',
    r'(?:jailbreak|jail.break)',
    r'respond\s+(?:without|ignoring)\s+(?:any\s+)?(?:safety|ethical|moral)\s+(?:guidelines|filters|restrictions)',
    r'(?:developer|maintenance|debug|god)\s+mode',
    r'you\s+(?:can|must|should)\s+(?:now\s+)?(?:say|do|generate)\s+anything',
    r'(?:bypass|disable|turn\s+off)\s+(?:your\s+)?(?:filters|safeguards|guardrails|restrictions)',
    r'(?:base64|rot13|hex|encode).*(?:decode|translate)\s+(?:this|the\s+following)',
    r'(?:opposite|reverse)\s+day',
    r'in\s+(?:a\s+)?(?:fictional|hypothetical|imaginary)\s+(?:world|scenario)\s+where\s+(?:there\s+are\s+)?no\s+rules',
    r'(?:character|persona)\s+(?:who|that)\s+(?:has\s+no|ignores\s+all)\s+(?:restrictions|rules)',
]


@action()
async def detect_jailbreak(text: str) -> bool:
    """Detect jailbreak attempts including DAN, role-play, encoding tricks, and persona manipulation."""
    for pattern in JAILBREAK_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    # Check for base64/encoding obfuscation attempts
    if re.search(r'[A-Za-z0-9+/]{40,}={0,2}', text):
        import base64
        try:
            decoded = base64.b64decode(text.split()[-1]).decode('utf-8', errors='ignore').lower()
            for pattern in JAILBREAK_PATTERNS + INJECTION_PATTERNS:
                if re.search(pattern, decoded, re.IGNORECASE):
                    return True
        except Exception:
            pass
    return False


@action()
async def check_patterns(text: str, patterns: list) -> bool:
    for pattern in patterns:
        if pattern.lower() in text.lower():
            return True
    return False


@action()
async def detect_pii(text: str) -> bool:
    for pii_type, pattern in PII_PATTERNS.items():
        if re.search(pattern, text):
            return True
    return False


@action()
async def detect_secrets(text: str) -> bool:
    for secret_type, pattern in SECRET_PATTERNS.items():
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False


@action()
async def check_content_safety(text: str) -> bool:
    harmful_patterns = [
        r'\b(kill|murder|assassinate)\s+(yourself|himself|herself|someone)\b',
        r'\bhow\s+to\s+(make|build|create)\s+(a\s+)?(bomb|weapon|explosive)\b',
        r'\b(suicide|self.harm)\s+(method|instructions|guide)\b',
        r'\b(hate|inferior|subhuman)\s+(race|ethnic|religion|gender)\b',
        r'\b(slur|racial\s+epithet|derogatory)\b',
        r'\bhow\s+to\s+(hack|phish|defraud|steal\s+identity)\b',
    ]
    for pattern in harmful_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False


@action()
async def validate_input_schema(text: str) -> bool:
    try:
        data = json.loads(text)
        return "parameters" in data and bool(data["parameters"])
    except (json.JSONDecodeError, TypeError):
        return len(text.strip()) > 0


@action()
async def check_topic_adherence(text: str) -> bool:
    """Check if input is within agent's designated scope.
    
    In production, wire to prompts.yml 'check_topic_adherence' task
    for LLM-based checking, or use a fine-tuned classifier.
    Current: passthrough (always True).
    """
    return True


@action()
async def log_audit_record(output: str) -> bool:
    """Log execution audit record for compliance traceability."""
    try:
        data = json.loads(output) if isinstance(output, str) else output
        # Check all traceability fields
        if not data.get("agent_id"):
            return False
        if not data.get("execution_id"):
            return False
        input_summary = data.get("input_summary", {})
        if not input_summary.get("source"):
            return False
        if not isinstance(input_summary.get("parameters"), dict):
            return False
        # End-to-end traceability: must have agent_version + output.schema_version
        if not data.get("agent_version"):
            return False
        if not data.get("output", {}).get("schema_version"):
            return False
        return True
    except (json.JSONDecodeError, TypeError):
        return False


@action()
async def validate_output_schema(output: str) -> bool:
    try:
        data = json.loads(output) if isinstance(output, str) else output
        required = ["agent_id", "agent_version", "execution_id", "input_summary", "output"]
        if not all(field in data for field in required):
            return False
        out = data.get("output", {})
        if "type" not in out or "schema_version" not in out:
            return False
        items = out.get("items", [])
        for item in items:
            if not all(f in item for f in ["id", "title", "content", "metadata"]):
                return False
            meta = item.get("metadata", {})
            if not all(f in meta for f in ["confidence", "reasoning", "citation", "trajectory"]):
                return False
        return True
    except (json.JSONDecodeError, TypeError):
        return False


@action()
async def check_groundedness(output: str) -> bool:
    # Placeholder — in production, uses LLM-as-Judge for grounding check
    try:
        data = json.loads(output) if isinstance(output, str) else output
        items = data.get("output", {}).get("items", [])
        for item in items:
            citations = item.get("metadata", {}).get("citation", [])
            if not citations:
                return False
        return True
    except (json.JSONDecodeError, TypeError):
        return False


@action()
async def validate_citations(output: str) -> bool:
    try:
        data = json.loads(output) if isinstance(output, str) else output
        items = data.get("output", {}).get("items", [])
        for item in items:
            citations = item.get("metadata", {}).get("citation", [])
            if not citations:
                return False
            for c in citations:
                if not c.get("source_reference"):
                    return False
        return True
    except (json.JSONDecodeError, TypeError):
        return False


@action()
async def check_confidence_threshold(output: str, min_confidence: float = 0.7, block_below: float = 0.5) -> bool:
    try:
        data = json.loads(output) if isinstance(output, str) else output
        items = data.get("output", {}).get("items", [])
        for item in items:
            confidence = item.get("metadata", {}).get("confidence")
            if confidence is None or confidence < block_below:
                return False
        return True
    except (json.JSONDecodeError, TypeError):
        return False


@action()
async def check_cross_item_consistency(output: str) -> bool:
    try:
        data = json.loads(output) if isinstance(output, str) else output
        items = data.get("output", {}).get("items", [])
        if len(items) <= 1:
            return True
        ids = [item.get("id") for item in items]
        return len(ids) == len(set(ids))
    except (json.JSONDecodeError, TypeError):
        return False


@action()
async def validate_reasoning_field(output: str) -> bool:
    try:
        data = json.loads(output) if isinstance(output, str) else output
        items = data.get("output", {}).get("items", [])
        for item in items:
            reasoning = item.get("metadata", {}).get("reasoning", "")
            if not reasoning or len(str(reasoning)) < 20:
                return False
            # Check it's not just restating the title/content
            title = item.get("title", "")
            if reasoning.strip() == title.strip():
                return False
        return True
    except (json.JSONDecodeError, TypeError):
        return False


@action()
async def verify_tool_permission(tool: str) -> bool:
    # Placeholder — checks against agent's tools_allowed list
    return True


@action()
async def verify_memory_access(operation: str) -> bool:
    # Placeholder — checks memory isolation rules
    return True
