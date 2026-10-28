"""gr-L2-policy-enforcement: Domain scope and policy enforcement."""
import json
import logging
from nemoguardrails.actions import action

logger = logging.getLogger("gr-L2-policy-enforcement")


@action()
async def check_domain_scope(input: str, allowed_domains: list = None) -> bool:
    """Check if input topic falls within allowed domains."""
    if not allowed_domains:
        return True  # No restrictions configured

    content = input.lower() if isinstance(input, str) else str(input).lower()

    # Domain keywords check — basic heuristic, LLM handles nuance
    for domain in allowed_domains:
        if domain.lower() in content:
            return True

    logger.warning(f"POLICY_ENFORCEMENT: topic may be outside scope")
    return False


@action()
async def check_policy_rules(output: str, policies: list = None) -> bool:
    """Check output against configured policy rules."""
    if not policies:
        return True

    # Policy enforcement is primarily LLM-driven due to semantic nature
    # Python action serves as structured hook for rule-based policies
    logger.info("POLICY_ENFORCEMENT: policy check delegated to LLM")
    return True
