"""gr-L2-memory-safety: Memory access control and poisoning prevention."""
import re
import json
import logging
from nemoguardrails.actions import action

logger = logging.getLogger("gr-L2-memory-safety")

INJECTION_PATTERNS = [
    r'(?i)ignore\s+previous',
    r'(?i)you\s+are\s+now',
    r'(?i)system\s*:',
    r'(?i)override\s+instructions',
]


@action()
async def validate_memory_operation(agent_id: str, operation: str) -> bool:
    """Validate memory operation safety."""
    if not operation:
        return True

    content = operation if isinstance(operation, str) else str(operation)

    try:
        data = json.loads(content)
    except (json.JSONDecodeError, TypeError):
        data = {"raw": content}

    # Check cross-agent isolation
    target_agent = data.get("target_agent_id", agent_id)
    if target_agent and target_agent != agent_id:
        shared = data.get("shared", False)
        if not shared:
            logger.warning(f"MEMORY_SAFETY: cross-agent access denied: {agent_id} → {target_agent}")
            return False

    # Check for poisoning patterns in write content
    write_content = data.get("content", data.get("raw", ""))
    if isinstance(write_content, str):
        for pattern in INJECTION_PATTERNS:
            if re.search(pattern, write_content):
                logger.warning(f"MEMORY_SAFETY: poisoning pattern detected in memory write")
                return False

    return True
