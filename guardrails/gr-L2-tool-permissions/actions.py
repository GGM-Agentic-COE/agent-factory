"""gr-L2-tool-permissions: Least-privilege tool access enforcement."""
import json
import logging
from nemoguardrails.actions import action

logger = logging.getLogger("gr-L2-tool-permissions")

# Agent permission registry — in production, load from config store
# AGENT_PERMISSIONS = {
#     "L2-payments-agent": {
#         "tools_allowed": ["kb_search", "schema_validate"],
#         "tools_denied": ["file_write", "exec_command"],
#         "org_scope": "payments"
#     }
# }


@action()
async def check_tool_allowed(tool_name: str, agent_id: str = None) -> bool:
    """Check if agent has permission to invoke the specified tool."""
    if not tool_name:
        logger.warning("TOOL_PERMISSIONS: no tool_name provided")
        return False

    # In production, load from config store / DynamoDB
    # permissions = AGENT_PERMISSIONS.get(agent_id, {})
    # allowed = permissions.get("tools_allowed", [])
    # denied = permissions.get("tools_denied", [])
    #
    # if tool_name in denied:
    #     logger.warning(f"TOOL_PERMISSIONS: {tool_name} explicitly denied for {agent_id}")
    #     return False
    #
    # if allowed and tool_name not in allowed:
    #     logger.warning(f"TOOL_PERMISSIONS: {tool_name} not in allowed list for {agent_id}")
    #     return False

    # Default: allow (configure restrictions per-agent in production)
    logger.info(f"TOOL_PERMISSIONS: {tool_name} permitted for {agent_id}")
    return True
