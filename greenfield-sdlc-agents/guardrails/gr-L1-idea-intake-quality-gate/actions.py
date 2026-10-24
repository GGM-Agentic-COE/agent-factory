"""gr-L1-idea-intake-quality-gate: validates the RESULTANT L1-vision-idea-intake
output (its own items, with the evaluator's fixes_applied resolved in) against
L1-vision-idea-intake/output_schema.json and L1-vision-idea-intake/evaluation.md.
Fires at L1-vision-idea-intake-evaluator's post_execution — evaluation concluded,
resultant content is what actually flows downstream.
"""
import json
import logging
import re
from nemoguardrails.actions import action

logger = logging.getLogger("gr-L1-idea-intake-quality-gate")

ID_PATTERNS = {"target_users": r"^TU-\d{2}$", "candidate_success_metrics": r"^SM-\d{2}$", "open_questions": r"^OQ-\d{2}$"}
PLACEHOLDER_MARKERS = ["tbd", "to be determined", "various users", "n/a", "placeholder", "lorem ipsum"]


def _parse(x):
    if isinstance(x, dict):
        return x
    try:
        return json.loads(x)
    except (TypeError, ValueError):
        return None


def _apply_fixes(items, fixes_applied):
    """Best-effort reconstruction of the resultant items: substitute every
    fixes_applied[].before -> after wherever the exact before-text is found
    as a string value anywhere in items (deep copy, non-mutating)."""
    resultant = json.loads(json.dumps(items))  # deep copy

    def _walk(node):
        if isinstance(node, dict):
            for k, v in node.items():
                if isinstance(v, str):
                    for fx in fixes_applied:
                        before, after = fx.get("before"), fx.get("after")
                        if before and after and before in v:
                            node[k] = v.replace(before, after)
                else:
                    _walk(v)
        elif isinstance(node, list):
            for item in node:
                _walk(item)

    _walk(resultant)
    return resultant


def _ids_sequential(entries, pattern):
    ids = [e.get("id", "") for e in entries if re.match(pattern, e.get("id", ""))]
    nums = sorted(int(i.split("-")[1]) for i in ids)
    return nums == list(range(1, len(nums) + 1))


@action()
async def check_idea_intake_quality_gate(output: str, generator_output: str = None) -> bool:
    """Return True if a quality-gate violation is found in the RESULTANT idea-intake output."""
    evaluator_doc = _parse(output)
    gen_doc = _parse(generator_output)
    if gen_doc is None:
        logger.warning("QUALITY-GATE: generator_output not available or not valid JSON — cannot validate resultant content")
        return True

    gen_content = gen_doc.get("content", {})

    # insufficient-context-integrity
    if gen_doc.get("status") == "failed":
        items = gen_content.get("items", {})
        non_empty = any(items.get(k) for k in ["problem_statement", "target_users", "value_proposition", "candidate_success_metrics", "open_questions"])
        if non_empty or "insufficient_context" not in (gen_content.get("execution_summary", "") or "").lower():
            logger.warning("QUALITY-GATE: status=failed but items non-empty or execution_summary doesn't state INSUFFICIENT_CONTEXT")
            return True
        return False  # a legitimate empty failure — nothing else to check

    fixes_applied = []
    if evaluator_doc:
        fixes_applied = evaluator_doc.get("content", {}).get("items", {}).get("fixes_applied", [])

    items = _apply_fixes(gen_content.get("items", {}), fixes_applied)

    # schema-compliance
    for field in ["problem_statement", "target_users", "value_proposition", "candidate_success_metrics", "open_questions"]:
        if field not in items:
            logger.warning(f"QUALITY-GATE: resultant output missing required field '{field}'")
            return True

    for key in ["problem_statement", "value_proposition"]:
        entry = items[key]
        statement = entry.get("statement", "")
        if not statement or not entry.get("confidence") or not entry.get("reasoning") or not entry.get("traced_to"):
            logger.warning(f"QUALITY-GATE: '{key}' fails schema (statement/confidence/reasoning/traced_to)")
            return True

    for tu in items.get("target_users", []):
        statement = tu.get("statement", "")
        if not re.match(ID_PATTERNS["target_users"], tu.get("id", "")) or not statement or not tu.get("confidence") or not tu.get("reasoning") or not tu.get("traced_to"):
            logger.warning(f"QUALITY-GATE: target_users entry {tu.get('id')} fails schema")
            return True

    for sm in items.get("candidate_success_metrics", []):
        if not re.match(ID_PATTERNS["candidate_success_metrics"], sm.get("id", "")) or sm.get("status") not in ("stated", "suggested") or not sm.get("metric") or not sm.get("reasoning"):
            logger.warning(f"QUALITY-GATE: success metric {sm.get('id')} fails schema")
            return True

    for oq in items.get("open_questions", []):
        if not re.match(ID_PATTERNS["open_questions"], oq.get("id", "")) or not oq.get("question") or not oq.get("reasoning"):
            logger.warning(f"QUALITY-GATE: open question {oq.get('id')} fails schema")
            return True

    # ids-sequential-no-gaps
    if items.get("target_users") and not _ids_sequential(items["target_users"], ID_PATTERNS["target_users"]):
        logger.warning("QUALITY-GATE: target_users ids not sequential / have gaps or duplicates")
        return True
    if items.get("candidate_success_metrics") and not _ids_sequential(items["candidate_success_metrics"], ID_PATTERNS["candidate_success_metrics"]):
        logger.warning("QUALITY-GATE: candidate_success_metrics ids not sequential / have gaps or duplicates")
        return True
    if items.get("open_questions") and not _ids_sequential(items["open_questions"], ID_PATTERNS["open_questions"]):
        logger.warning("QUALITY-GATE: open_questions ids not sequential / have gaps or duplicates")
        return True

    # no-placeholder-or-vague-filler (best-effort deterministic backstop; LLM covers nuance)
    all_text = json.dumps(items).lower()
    for marker in PLACEHOLDER_MARKERS:
        if marker in all_text:
            logger.warning(f"QUALITY-GATE: placeholder marker '{marker}' found in resultant content")
            return True

    return False
