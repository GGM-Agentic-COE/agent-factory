"""gr-L3-agent-rate-limit: Tool call and agent invocation rate limiting."""
import time
import logging
from nemoguardrails.actions import action

logger = logging.getLogger("gr-L3-agent-rate-limit")

# In-memory rate state (use Redis in production)
_rate_state = {}

DEFAULT_MAX_TOOL_CALLS = 20
DEFAULT_MAX_AGENT_CALLS = 5
DEFAULT_COOLDOWN_SECONDS = 2


@action()
async def check_rate_limits(agent_id: str = "default", tool_name: str = None) -> str:
    """Check rate limits. Returns 'pass', 'throttled', or 'blocked'."""
    now = time.time()

    if agent_id not in _rate_state:
        _rate_state[agent_id] = {
            "tool_calls": 0,
            "agent_calls": 0,
            "last_call_times": {},
        }

    state = _rate_state[agent_id]

    # Check max tool calls
    state["tool_calls"] += 1
    if state["tool_calls"] > DEFAULT_MAX_TOOL_CALLS:
        logger.warning(f"RATE_LIMIT: {agent_id} exceeded max tool calls ({DEFAULT_MAX_TOOL_CALLS})")
        return "blocked"

    # Check if this is a downstream agent call
    if tool_name and tool_name.startswith("invoke_agent"):
        state["agent_calls"] += 1
        if state["agent_calls"] > DEFAULT_MAX_AGENT_CALLS:
            logger.warning(f"RATE_LIMIT: {agent_id} exceeded max agent calls ({DEFAULT_MAX_AGENT_CALLS})")
            return "blocked"

    # Check cooldown for repeated same-tool calls
    if tool_name:
        last_time = state["last_call_times"].get(tool_name, 0)
        if now - last_time < DEFAULT_COOLDOWN_SECONDS:
            logger.info(f"RATE_LIMIT: {agent_id} cooldown active for {tool_name}")
            return "throttled"
        state["last_call_times"][tool_name] = now

    return "pass"
