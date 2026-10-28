"""gr-L1-nfr-spec-quality-gate: validates the RESULTANT
L1-requirements-nfr-classifier output (its own items, with the evaluator's
fixes_applied resolved in) against L1-requirements-nfr-classifier/output_schema.json
and its evaluation.md rubric (kb-L1-nfr-classification-taxonomy's six
categories, citation form, TBD/source consistency, ID sequencing). Fires at
L1-requirements-nfr-classifier-evaluator's post_execution.
"""
import json
import logging
import re
from nemoguardrails.actions import action

logger = logging.getLogger("gr-L1-nfr-spec-quality-gate")

VALID_CATEGORIES = {"Performance", "Security", "Scalability", "Availability", "Compliance", "Usability"}
TBD_PHRASE = "TBD — needs stakeholder input"
NO_CATEGORIES_PHRASE = "no nfr categories apply"

CITATION_PATTERNS = [
    re.compile(r"^requirements\.md § FR-\d{3}$"),
    re.compile(r"^vision\.md § .+$"),
    re.compile(r"^kb-L1-enterprise-security § ES\d+$"),
]


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


def _ids_sequential(entries, prefix, digits=3):
    ids = [e.get("id", "") for e in entries if re.match(rf"^{prefix}-\d{{{digits}}}$", e.get("id", ""))]
    nums = sorted(int(i.split("-")[1]) for i in ids)
    return nums == list(range(1, len(nums) + 1))


def _is_valid_citation_form(source: str) -> bool:
    return any(p.match(source) for p in CITATION_PATTERNS)


@action()
async def check_nfr_spec_quality_gate(output: str, generator_output: str = None) -> bool:
    """Return True if a quality-gate violation is found in the RESULTANT nfr_classifications output."""
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
    if "nfr_classifications" not in items:
        logger.warning("QUALITY-GATE: resultant output missing required field 'nfr_classifications'")
        return True

    classifications = items["nfr_classifications"]
    if not classifications:
        logger.warning("QUALITY-GATE: nfr_classifications[] is empty — at least one required")
        return True

    for c in classifications:
        cid = c.get("id", "")
        if not re.match(r"^FR-\d{3}$", cid):
            logger.warning(f"QUALITY-GATE: id '{cid}' malformed")
            return True
        if not c.get("title"):
            logger.warning(f"QUALITY-GATE: {cid} missing title")
            return True
        if "boundary_conditions" not in c or not isinstance(c["boundary_conditions"], list):
            logger.warning(f"QUALITY-GATE: {cid} missing boundary_conditions array")
            return True
        confidence = c.get("confidence")
        if confidence is None or not isinstance(confidence, (int, float)) or not (0.0 <= confidence <= 1.0):
            logger.warning(f"QUALITY-GATE: {cid} missing/invalid confidence")
            return True
        reasoning = c.get("reasoning", "")
        if not reasoning or len(reasoning) < 20:
            logger.warning(f"QUALITY-GATE: {cid} missing/short reasoning")
            return True

        bcs = c["boundary_conditions"]

        # empty boundary_conditions is valid ONLY with an explicit "No NFR categories apply" reasoning
        if not bcs and NO_CATEGORIES_PHRASE not in reasoning.lower():
            logger.warning(f"QUALITY-GATE: {cid} has empty boundary_conditions with no 'No NFR categories apply' reasoning")
            return True

        for bc in bcs:
            category = bc.get("category")
            condition = bc.get("boundary_condition", "")
            source = bc.get("source", "")

            # schema-compliance (per BoundaryCondition)
            if category not in VALID_CATEGORIES:
                logger.warning(f"QUALITY-GATE: {cid} boundary_condition has invalid/missing category '{category}'")
                return True
            if not condition or len(condition) < 5:
                logger.warning(f"QUALITY-GATE: {cid} boundary_condition text missing or too short")
                return True
            if not source:
                logger.warning(f"QUALITY-GATE: {cid} boundary_condition missing source")
                return True

            is_tbd = condition.endswith(TBD_PHRASE)

            # tbd-source-consistency — re-checked deterministically even though
            # output_schema.json already encodes this via allOf/if/then; the point
            # is to catch a case where the LLM didn't actually follow its own schema
            if is_tbd and source != "—":
                logger.warning(f"QUALITY-GATE: {cid} TBD boundary_condition has non-'—' source '{source}'")
                return True
            if not is_tbd and source == "—":
                logger.warning(f"QUALITY-GATE: {cid} non-TBD boundary_condition has bare '—' source")
                return True

            # citation-form-validity
            if not is_tbd and not _is_valid_citation_form(source):
                logger.warning(f"QUALITY-GATE: {cid} source '{source}' does not match any recognized citation form")
                return True

    # ids-sequential-no-gaps
    if not _ids_sequential(classifications, "FR", digits=3):
        logger.warning("QUALITY-GATE: FR ids not sequential / have gaps or duplicates")
        return True

    return False
