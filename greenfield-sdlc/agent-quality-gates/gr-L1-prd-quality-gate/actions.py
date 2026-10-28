"""gr-L1-prd-quality-gate: validates the RESULTANT L1-requirements-prd-composer
output (its own items, with the evaluator's fixes_applied resolved in) against
L1-requirements-prd-composer/output_schema.json and its evaluation.md rubric.
Fires at L1-requirements-prd-composer-evaluator's post_execution. Gates what
actually flows to L1-planning-impact-assessor and L1-planning-dependency-mapper.
"""
import json
import logging
import re
from nemoguardrails.actions import action

logger = logging.getLogger("gr-L1-prd-quality-gate")

NFR_CATEGORIES = {"Performance", "Security", "Scalability", "Availability", "Compliance", "Usability"}
METRIC_KEY_MARKERS = ["metric", "kpi", "target"]


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


def _upstream_functional_requirements(original_input):
    """Return {fr_id: statement} from original_input.requirements_output, or None if unavailable."""
    req_output = (original_input or {}).get("requirements_output")
    if not isinstance(req_output, dict) or req_output.get("status") != "success":
        return None
    frs = req_output.get("content", {}).get("items", {}).get("functional_requirements", [])
    return {fr.get("id"): fr.get("statement") for fr in frs if fr.get("id")}


def _upstream_compound_splits(original_input):
    """Return requirements.md's own compound_splits[], or None if unavailable."""
    req_output = (original_input or {}).get("requirements_output")
    if not isinstance(req_output, dict) or req_output.get("status") != "success":
        return None
    return req_output.get("content", {}).get("items", {}).get("compound_splits", [])


def _upstream_nfr_map(original_input):
    """Return {fr_id: set of (category, boundary_condition)} from original_input.nfr_spec_output, or None."""
    nfr_output = (original_input or {}).get("nfr_spec_output")
    if not isinstance(nfr_output, dict) or nfr_output.get("status") != "success":
        return None
    classifications = nfr_output.get("content", {}).get("items", {}).get("nfr_classifications", [])
    out = {}
    for c in classifications:
        fr_id = c.get("id")
        if not fr_id:
            continue
        out[fr_id] = {
            (bc.get("category"), bc.get("boundary_condition"))
            for bc in c.get("boundary_conditions", [])
        }
    return out


def _upstream_tbds(original_input):
    """Return set of (fr_id, category) pairs from nfr_spec_output whose boundary_condition source is '—' (TBD)."""
    nfr_output = (original_input or {}).get("nfr_spec_output")
    if not isinstance(nfr_output, dict):
        return set()
    classifications = nfr_output.get("content", {}).get("items", {}).get("nfr_classifications", [])
    tbds = set()
    for c in classifications:
        fr_id = c.get("id")
        for bc in c.get("boundary_conditions", []):
            if bc.get("source") == "—":
                tbds.add((fr_id, bc.get("category")))
    return tbds


def _scan_for_metrics_field(node, path=""):
    """Return the offending key path if any dict key anywhere looks like a smuggled metrics field."""
    if isinstance(node, dict):
        for k, v in node.items():
            lk = k.lower()
            if any(marker in lk for marker in METRIC_KEY_MARKERS):
                return f"{path}.{k}" if path else k
            found = _scan_for_metrics_field(v, f"{path}.{k}" if path else k)
            if found:
                return found
    elif isinstance(node, list):
        for i, item in enumerate(node):
            found = _scan_for_metrics_field(item, f"{path}[{i}]")
            if found:
                return found
    return None


def _is_tagged(underlies_or_affects):
    if underlies_or_affects == "program-level":
        return True
    if isinstance(underlies_or_affects, list) and len(underlies_or_affects) >= 1:
        return all(isinstance(t, str) and re.match(r"^FR-\d{3}$", t) for t in underlies_or_affects)
    return False


@action()
async def check_prd_quality_gate(output: str, generator_output: str = None, original_input: str = None) -> bool:
    """Return True if a quality-gate violation is found in the RESULTANT prd-composer output."""
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

    # ---- schema-compliance ----
    required_top = ["executive_summary", "compound_splits", "assumptions", "constraints",
                     "risks", "requirements", "open_questions"]
    for field in required_top:
        if field not in items:
            logger.warning(f"QUALITY-GATE: resultant output missing required field '{field}'")
            return True

    exec_summary = items["executive_summary"]
    if (not isinstance(exec_summary, dict) or not exec_summary.get("summary")
            or len(exec_summary.get("summary", "")) > 150
            or exec_summary.get("confidence") is None
            or not exec_summary.get("reasoning") or len(exec_summary.get("reasoning", "")) < 20):
        logger.warning("QUALITY-GATE: executive_summary fails schema (summary/confidence/reasoning)")
        return True

    requirements = items["requirements"]
    if not requirements:
        logger.warning("QUALITY-GATE: requirements[] is empty — at least one required")
        return True

    fr_ids = set()
    for req in requirements:
        rid = req.get("id", "")
        if not re.match(r"^FR-\d{3}$", rid):
            logger.warning(f"QUALITY-GATE: requirement id '{rid}' malformed")
            return True
        fr_ids.add(rid)
        if not req.get("title") or not req.get("statement") or len(req.get("statement", "")) < 10:
            logger.warning(f"QUALITY-GATE: {rid} missing title/statement or statement too short")
            return True
        if not req.get("traces_to"):
            logger.warning(f"QUALITY-GATE: {rid} missing traces_to")
            return True
        if req.get("confidence") is None or not req.get("reasoning") or len(req.get("reasoning", "")) < 20:
            logger.warning(f"QUALITY-GATE: {rid} missing/short confidence or reasoning")
            return True
        if "nfrs" not in req or not isinstance(req["nfrs"], list):
            logger.warning(f"QUALITY-GATE: {rid} missing nfrs[] (may be an empty list, but must be present)")
            return True
        for nfr in req["nfrs"]:
            if (nfr.get("category") not in NFR_CATEGORIES or not nfr.get("boundary_condition")
                    or len(nfr.get("boundary_condition", "")) < 5 or not nfr.get("source")):
                logger.warning(f"QUALITY-GATE: {rid} has a malformed nfrs[] entry")
                return True

    for group_name in ["assumptions", "constraints", "risks"]:
        for point in items[group_name]:
            if (not point.get("short_title") or not point.get("summary")
                    or len(point.get("summary", "")) > 150
                    or point.get("confidence") is None
                    or not point.get("reasoning") or len(point.get("reasoning", "")) < 20):
                logger.warning(f"QUALITY-GATE: {group_name} entry '{point.get('short_title')}' fails schema")
                return True

            # assumption-constraint-risk-tagged (evaluation.md Quality Gate, line 8 —
            # re-derives output_schema.json's oneOf explicitly; never left untagged)
            if not _is_tagged(point.get("underlies_or_affects")):
                logger.warning(
                    f"QUALITY-GATE: {group_name} entry '{point.get('short_title')}' left untagged "
                    f"(underlies_or_affects={point.get('underlies_or_affects')!r})"
                )
                return True

    for oq in items["open_questions"]:
        if oq.get("type") not in ("tbd", "coverage_gap") or not oq.get("summary"):
            logger.warning("QUALITY-GATE: open_questions entry fails schema (type/summary)")
            return True
        if len(oq.get("summary", "")) > 200:
            logger.warning("QUALITY-GATE: open_questions entry summary over 200 chars")
            return True
        if oq["type"] == "tbd" and (
            not oq.get("fr_id") or not re.match(r"^FR-\d{3}$", oq.get("fr_id", ""))
            or oq.get("category") not in NFR_CATEGORIES
        ):
            logger.warning("QUALITY-GATE: open_questions 'tbd' entry missing/malformed fr_id or category")
            return True

    for split in items["compound_splits"]:
        summary = split.get("source_clause_summary", "")
        if not summary or len(summary) > 150:
            logger.warning("QUALITY-GATE: compound_splits entry missing/over-length source_clause_summary")
            return True
        split_into = split.get("split_into", [])
        if len(split_into) < 2 or not all(sid in fr_ids for sid in split_into):
            logger.warning("QUALITY-GATE: compound_splits entry has <2 split_into ids or references a missing FR")
            return True

    # ---- zero-drop-requirements (evaluation.md Quality Gate #1) ----
    orig = _parse(original_input) if original_input else None
    upstream_frs = _upstream_functional_requirements(orig)
    if upstream_frs is None:
        logger.warning("QUALITY-GATE: original_input.requirements_output not available — cannot verify zero-drop-requirements")
        return True

    upstream_ids = set(upstream_frs.keys())
    if fr_ids != upstream_ids:
        missing = upstream_ids - fr_ids
        invented = fr_ids - upstream_ids
        logger.warning(f"QUALITY-GATE: FR id set mismatch vs requirements.md — missing={missing} invented={invented}")
        return True

    for req in requirements:
        rid = req["id"]
        if req.get("statement") != upstream_frs.get(rid):
            logger.warning(f"QUALITY-GATE: {rid} statement does not match requirements.md verbatim")
            return True

    # ---- compound-splits-carried-forward (evaluation.md Quality Gate #3) ----
    upstream_splits = _upstream_compound_splits(orig)
    if upstream_splits is None:
        logger.warning("QUALITY-GATE: original_input.requirements_output not available — cannot verify compound_splits carry-forward")
        return True

    def _split_key(s):
        return (s.get("source_clause_summary"), tuple(s.get("split_into", [])))

    resultant_splits = {_split_key(s) for s in items["compound_splits"]}
    expected_splits = {_split_key(s) for s in upstream_splits}
    if resultant_splits != expected_splits:
        logger.warning("QUALITY-GATE: compound_splits not carried forward verbatim from requirements.md")
        return True

    # ---- zero-drop-nfrs (evaluation.md Quality Gate #2) ----
    upstream_nfrs = _upstream_nfr_map(orig)
    if upstream_nfrs is None:
        logger.warning("QUALITY-GATE: original_input.nfr_spec_output not available — cannot verify zero-drop-nfrs")
        return True

    for req in requirements:
        rid = req["id"]
        resultant_set = {(n.get("category"), n.get("boundary_condition")) for n in req.get("nfrs", [])}
        expected_set = upstream_nfrs.get(rid, set())
        if resultant_set != expected_set:
            logger.warning(
                f"QUALITY-GATE: {rid} nfrs[] does not match nfr-spec.md verbatim "
                f"(missing={expected_set - resultant_set}, extra={resultant_set - expected_set})"
            )
            return True

    # ---- no-success-metrics-field (evaluation.md Quality Gate #5) ----
    offending = _scan_for_metrics_field(items)
    if offending:
        logger.warning(f"QUALITY-GATE: success-metrics-looking field smuggled into resultant items: '{offending}'")
        return True

    # ---- open-questions-completeness (evaluation.md Quality Gate #6) ----
    upstream_tbds = _upstream_tbds(orig)
    resultant_tbds = {
        (oq.get("fr_id"), oq.get("category"))
        for oq in items["open_questions"] if oq.get("type") == "tbd"
    }
    missing_tbds = upstream_tbds - resultant_tbds
    if missing_tbds:
        logger.warning(f"QUALITY-GATE: open_questions missing TBD rollup for {missing_tbds}")
        return True

    return False
