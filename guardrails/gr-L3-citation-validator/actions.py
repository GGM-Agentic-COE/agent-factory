"""gr-L3-citation-validator: Citation presence and resolvability checks."""
import json
import re
import logging
from nemoguardrails.actions import action

logger = logging.getLogger("gr-L3-citation-validator")

VALID_SOURCE_PREFIXES = ["kb-", "source-", "doc-", "ref-"]


@action()
async def validate_citations(output: str) -> bool:
    """Validate every item has at least one resolvable citation."""
    if not output:
        return False

    try:
        data = json.loads(output) if isinstance(output, str) else output
        items = data.get("output", {}).get("items", [])

        if not items:
            return True  # No items to validate

        for i, item in enumerate(items):
            meta = item.get("metadata", {})
            citations = meta.get("citation", [])

            if not citations:
                logger.warning(f"CITATION_VALIDATOR: item[{i}] has no citations")
                return False

            if not isinstance(citations, list):
                citations = [citations]

            for citation in citations:
                source_ref = citation.get("source_reference", "") if isinstance(citation, dict) else str(citation)
                if not source_ref:
                    logger.warning(f"CITATION_VALIDATOR: item[{i}] has empty source_reference")
                    return False

        return True
    except (json.JSONDecodeError, TypeError) as e:
        logger.error(f"CITATION_VALIDATOR: parse error: {e}")
        return False
