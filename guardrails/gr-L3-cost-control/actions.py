"""gr-L3-cost-control: Token and invocation budget enforcement."""
import time
import logging
from nemoguardrails.actions import action

logger = logging.getLogger("gr-L3-cost-control")

# In-memory budget tracking (use Redis/DynamoDB in production)
_budget_state = {}

DEFAULT_MAX_TOKENS = 100000
DEFAULT_MAX_INVOCATIONS = 50
DEFAULT_WINDOW_SECONDS = 3600
WARNING_THRESHOLD = 0.8


@action()
async def check_budget_limits(agent_id: str = "default") -> str:
    """Check budget. Returns 'pass', 'warning', or 'exceeded'."""
    now = time.time()

    if agent_id not in _budget_state:
        _budget_state[agent_id] = {
            "tokens_used": 0,
            "invocations": 0,
            "window_start": now,
            "max_tokens": DEFAULT_MAX_TOKENS,
            "max_invocations": DEFAULT_MAX_INVOCATIONS,
        }

    state = _budget_state[agent_id]

    # Reset window if expired
    if now - state["window_start"] > DEFAULT_WINDOW_SECONDS:
        state["tokens_used"] = 0
        state["invocations"] = 0
        state["window_start"] = now

    # Check invocation cap
    state["invocations"] += 1
    if state["invocations"] > state["max_invocations"]:
        logger.warning(f"COST_CONTROL: {agent_id} exceeded invocation cap")
        return "exceeded"

    # Check token budget
    token_ratio = state["tokens_used"] / state["max_tokens"]
    if token_ratio >= 1.0:
        logger.warning(f"COST_CONTROL: {agent_id} exceeded token budget")
        return "exceeded"

    if token_ratio >= WARNING_THRESHOLD:
        logger.info(f"COST_CONTROL: {agent_id} at {token_ratio*100:.0f}% of budget")
        return "warning"

    return "pass"
