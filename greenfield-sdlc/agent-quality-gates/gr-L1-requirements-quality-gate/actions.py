"""gr-L1-requirements-quality-gate: validates the RESULTANT
L1-requirements-elicitor output (its own items, with the evaluator's
fixes_applied resolved in) against L1-requirements-elicitor/output_schema.json
and kb-L1-requirements-quality-standard's ISO/IEC/IEEE 29148 rubric. Fires
at L1-requirements-elicitor-evaluator's post_execution.
"""
import json
import logging
import re
from nemoguardrails.actions import action

logger = logging.getLogger("gr-L1-requirements-quality-gate")

VAGUE_TERMS = ["fast", "user-friendly", "appropriate", "secure", "robust", "intuitive"]


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


def _has_unqualified_vague_term(text: str) -> str:
    """Return the offending term if a vague term appears with no nearby number, else None."""
    lower = text.lower()
    for term in VAGUE_TERMS:
        for m in re.finditer(re.escape(term), lower):
            window = lower[m.end(): m.end() + 60]
            if not re.search(r"\d", window):
                return term
    return None


@action()
async def check_requirements_quality_gate(output: str, generator_output: str = None) -> bool:
    """Return True if a quality-gate violation is found in the RESULTANT requirements output."""
    evaluator_doc = _parse(output)
    gen_doc = _parse(generator_output)
    if gen_doc is None:
        logger.warning("QUALITY-GATE: generator_output not available or not valid JSON")
        return True

    gen_content = gen_doc.get("content", {})

    if gen_doc.get("status") == "failed":
        return False  # legitimate INSUFFICIENT_CONTEXT — nothing to validate

    fixes_applied = []
    if evaluator_doc:
        fixes_applied = evaluator_doc.get("content", {}).get("items", {}).get("fixes_applied", [])

    items = _apply_fixes(gen_content.get("items", {}), fixes_applied)

    # schema-compliance
    for field in ["functional_requirements", "compound_splits"]:
        if field not in items:
            logger.warning(f"QUALITY-GATE: resultant output missing required field '{field}'")
            return True

    frs = items["functional_requirements"]
    if not frs:
        logger.warning("QUALITY-GATE: functional_requirements[] is empty — at least one required")
        return True

    fr_ids = set()
    for fr in frs:
        if not re.match(r"^FR-\d{3}$", fr.get("id", "")):
            logger.warning(f"QUALITY-GATE: FR id '{fr.get('id')}' malformed")
            return True
        fr_ids.add(fr["id"])
        if not fr.get("title") or not fr.get("statement") or len(fr.get("statement", "")) < 10:
            logger.warning(f"QUALITY-GATE: {fr.get('id')} missing title/statement or statement too short")
            return True
        if not fr.get("traces_to"):
            logger.warning(f"QUALITY-GATE: {fr.get('id')} missing traces_to")
            return True
        if not fr.get("confidence") or not fr.get("reasoning") or len(fr.get("reasoning", "")) < 20:
            logger.warning(f"QUALITY-GATE: {fr.get('id')} missing/short confidence or reasoning")
            return True

        # unambiguous-vague-term-scan
        offending = _has_unqualified_vague_term(fr["statement"])
        if offending:
            logger.warning(f"QUALITY-GATE: {fr.get('id')} statement contains unqualified vague term '{offending}'")
            return True

    # ids-sequential-no-gaps
    nums = sorted(int(i.split("-")[1]) for i in fr_ids)
    if nums != list(range(1, len(nums) + 1)):
        logger.warning("QUALITY-GATE: FR ids not sequential / have gaps or duplicates")
        return True

    # compound-split-integrity
    for split in items["compound_splits"]:
        summary = split.get("source_clause_summary", "")
        if not summary or len(summary) > 150:
            logger.warning("QUALITY-GATE: compound_splits entry missing/over-length source_clause_summary")
            return True
        split_into = split.get("split_into", [])
        if len(split_into) < 2:
            logger.warning("QUALITY-GATE: compound_splits entry has fewer than 2 split_into ids")
            return True
        for sid in split_into:
            if sid not in fr_ids:
                logger.warning(f"QUALITY-GATE: compound_splits references {sid}, not present in functional_requirements")
                return True

    return False
