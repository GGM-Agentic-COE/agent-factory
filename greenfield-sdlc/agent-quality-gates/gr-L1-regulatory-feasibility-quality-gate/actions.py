"""gr-L1-regulatory-feasibility-quality-gate: validates the RESULTANT
L1-vision-regulatory-feasibility-checker output (its own items, with the
evaluator's fixes_applied resolved in) against
L1-vision-regulatory-feasibility-checker/output_schema.json and its
evaluation.md. Fires at L1-vision-regulatory-feasibility-checker-evaluator's
post_execution. Highest-stakes gate in Phase 0 — zero tolerance.
"""
import json
import logging
import re
from nemoguardrails.actions import action

logger = logging.getLogger("gr-L1-regulatory-feasibility-quality-gate")

GENERIC_REGULATION_PHRASES = ["applicable regulations", "relevant law", "relevant regulations", "comply with regulations"]


def _parse(x):
    if isinstance(x, dict):
        return x
    try:
        return json.loads(x)
    except (TypeError, ValueError):
        return None


def _apply_fixes(items, fixes_applied):
    resultant = json.loads(json.dumps(items))

    def _walk(node):
        if isinstance(node, dict):
            for k, v in node.items():
                if isinstance(v, str):
                    for fx in fixes_applied:
                        before, after = fx.get("before"), fx.get("after")
                        if before and after and before in v:
                            node[k] = v.replace(before, after)
                elif isinstance(v, (dict, list)):
                    _walk(v)
        elif isinstance(node, list):
            for item in node:
                _walk(item)

    _walk(resultant)
    return resultant


def _ids_sequential(entries, prefix):
    ids = [e.get("id", "") for e in entries if re.match(rf"^{prefix}-\d{{2}}$", e.get("id", ""))]
    nums = sorted(int(i.split("-")[1]) for i in ids)
    return nums == list(range(1, len(nums) + 1))


@action()
async def check_regulatory_feasibility_quality_gate(output: str, generator_output: str = None) -> bool:
    """Return True if a quality-gate violation is found in the RESULTANT regulatory-feasibility output."""
    evaluator_doc = _parse(output)
    gen_doc = _parse(generator_output)
    if gen_doc is None:
        logger.warning("QUALITY-GATE: generator_output not available or not valid JSON")
        return True

    gen_content = gen_doc.get("content", {})

    if gen_doc.get("status") == "failed":
        return False  # legitimate failure — nothing to validate

    fixes_applied = []
    if evaluator_doc:
        fixes_applied = evaluator_doc.get("content", {}).get("items", {}).get("fixes_applied", [])

    items = _apply_fixes(gen_content.get("items", {}), fixes_applied)

    # schema-compliance
    for field in ["constraints", "overall_status", "open_items"]:
        if field not in items:
            logger.warning(f"QUALITY-GATE: resultant output missing required field '{field}'")
            return True

    constraints = items["constraints"]
    if not constraints:
        logger.warning("QUALITY-GATE: constraints[] is empty — at least one required")
        return True

    for c in constraints:
        if not re.match(r"^CON-\d{2}$", c.get("id", "")):
            logger.warning(f"QUALITY-GATE: constraint id '{c.get('id')}' malformed")
            return True
        if c.get("status") not in ("Green", "Amber", "Red"):
            logger.warning(f"QUALITY-GATE: constraint {c.get('id')} has invalid status {c.get('status')!r}")
            return True
        rationale = c.get("rationale", "")
        if not rationale:
            logger.warning(f"QUALITY-GATE: constraint {c.get('id')} rationale missing")
            return True
        mitigation = c.get("mitigation")
        if not c.get("confidence") or not c.get("reasoning"):
            logger.warning(f"QUALITY-GATE: constraint {c.get('id')} missing confidence/reasoning")
            return True

        citation = c.get("citation", {})
        regulation = (citation.get("regulation") or "").strip()

        # citation-specificity
        if not citation.get("source_reference") or not regulation:
            logger.warning(f"QUALITY-GATE: constraint {c.get('id')} missing citation source_reference or regulation")
            return True
        if regulation.lower() in GENERIC_REGULATION_PHRASES:
            logger.warning(f"QUALITY-GATE: constraint {c.get('id')} citation.regulation is a generic phrase, not a specific regulation")
            return True

        # amber-red-mitigation-or-legal-review — THE zero-tolerance rule, re-checked on the RESULTANT content
        if c.get("status") in ("Amber", "Red"):
            has_mitigation = bool(mitigation) and mitigation.strip() != ""
            legal_review = bool(c.get("requires_legal_review"))
            if not has_mitigation and not legal_review:
                logger.warning(f"QUALITY-GATE: constraint {c.get('id')} is {c.get('status')} with no mitigation and requires_legal_review=false — ZERO TOLERANCE violation")
                return True

    if not _ids_sequential(constraints, "CON"):
        logger.warning("QUALITY-GATE: constraint ids not sequential / have gaps or duplicates")
        return True

    open_items = items["open_items"]
    for oi in open_items:
        if not re.match(r"^OI-\d{2}$", oi.get("id", "")) or not oi.get("description"):
            logger.warning(f"QUALITY-GATE: open_item {oi.get('id')} fails schema")
            return True
    if open_items and not _ids_sequential(open_items, "OI"):
        logger.warning("QUALITY-GATE: open_item ids not sequential / have gaps or duplicates")
        return True

    overall_status = items["overall_status"]
    if overall_status.get("status") not in ("Green", "Amber", "Red") or not overall_status.get("rationale"):
        logger.warning("QUALITY-GATE: overall_status fails schema")
        return True

    return False
