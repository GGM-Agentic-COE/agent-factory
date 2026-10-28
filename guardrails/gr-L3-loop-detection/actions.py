"""gr-L3-loop-detection: Infinite loop and runaway execution detection."""
import time
import logging
from nemoguardrails.actions import action

logger = logging.getLogger("gr-L3-loop-detection")

# In-memory state (use Redis in production)
_loop_state = {}

DEFAULT_MAX_ITERATIONS = 10
DEFAULT_TIMEOUT_SECONDS = 300
DEFAULT_MAX_RECURSION = 5


@action()
async def detect_loops(agent_id: str = "default", action_name: str = None) -> str:
    """Detect loops. Returns 'ok', 'loop', 'timeout', or 'recursion'."""
    now = time.time()

    if agent_id not in _loop_state:
        _loop_state[agent_id] = {
            "start_time": now,
            "action_counts": {},
            "recursion_depth": 0,
        }

    state = _loop_state[agent_id]

    # Check timeout
    elapsed = now - state["start_time"]
    if elapsed > DEFAULT_TIMEOUT_SECONDS:
        logger.warning(f"LOOP_DETECTION: {agent_id} exceeded timeout ({elapsed:.0f}s)")
        return "timeout"

    # Check iteration count for same action
    if action_name:
        state["action_counts"][action_name] = state["action_counts"].get(action_name, 0) + 1
        count = state["action_counts"][action_name]
        if count > DEFAULT_MAX_ITERATIONS:
            logger.warning(f"LOOP_DETECTION: {agent_id} repeated {action_name} {count} times")
            return "loop"

    # Check recursion depth (tracked via call stack depth marker)
    if action_name and action_name.startswith("self_"):
        state["recursion_depth"] += 1
        if state["recursion_depth"] > DEFAULT_MAX_RECURSION:
            logger.warning(f"LOOP_DETECTION: {agent_id} recursion depth {state['recursion_depth']}")
            return "recursion"

    return "ok"
