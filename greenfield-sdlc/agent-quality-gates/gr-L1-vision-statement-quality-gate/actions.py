"""gr-L1-vision-statement-quality-gate: validates the RESULTANT
L1-vision-statement-generator output (its own items, with the evaluator's
fixes_applied resolved in) against L1-vision-statement-generator/output_schema.json
and its evaluation.md. Fires at L1-vision-statement-generator-evaluator's
post_execution. Last automated checkpoint before the Product Lead approval gate.
"""
import json
import logging
import re
from nemoguardrails.actions import action

logger = logging.getLogger("gr-L1-vision-statement-quality-gate")


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


def _find_all(obj, key):
    found = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == key:
                found.append(v)
            found.extend(_find_all(v, key))
    elif isinstance(obj, list):
        for item in obj:
            found.extend(_find_all(item, key))
    return found


@action()
async def check_vision_statement_quality_gate(output: str, generator_output: str = None, original_input: str = None) -> bool:
    """Return True if a quality-gate violation is found in the RESULTANT vision-statement output."""
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
    required = ["executive_summary", "problem_statement", "target_users", "value_proposition",
                "market_context", "regulatory_posture", "north_star_metrics", "roadmap", "open_risks"]
    for field in required:
        if field not in items:
            logger.warning(f"QUALITY-GATE: resultant output missing required field '{field}'")
            return True

    for key in ["executive_summary", "problem_statement", "target_users", "value_proposition", "market_context"]:
        entry = items[key]
        summary = entry.get("summary", "")
        if not summary or len(summary) > 150 or not entry.get("confidence") or not entry.get("reasoning"):
            logger.warning(f"QUALITY-GATE: '{key}' fails schema (summary/confidence/reasoning)")
            return True

    nsms = items["north_star_metrics"]
    for nsm in nsms:
        if not re.match(r"^NSM-\d{2}$", nsm.get("id", "")) or not nsm.get("metric") or not nsm.get("target") or not nsm.get("confidence") or not nsm.get("reasoning"):
            logger.warning(f"QUALITY-GATE: north_star_metric {nsm.get('id')} fails schema")
            return True
    if nsms and not _ids_sequential(nsms, "NSM"):
        logger.warning("QUALITY-GATE: north_star_metrics ids not sequential / have gaps or duplicates")
        return True

    roadmap = items["roadmap"]
    for r in roadmap:
        if not isinstance(r.get("phase_number"), int) or r["phase_number"] < 1 or not r.get("title") or not r.get("description_summary") or len(r["description_summary"]) > 150:
            logger.warning(f"QUALITY-GATE: roadmap phase {r.get('phase_number')} fails schema")
            return True
    phase_numbers = sorted(r["phase_number"] for r in roadmap)
    if phase_numbers != list(range(1, len(phase_numbers) + 1)):
        logger.warning("QUALITY-GATE: roadmap phase_numbers not sequential from 1")
        return True

    open_risks = items["open_risks"]
    for orisk in open_risks:
        if (not re.match(r"^OR-\d{2}$", orisk.get("id", "")) or not orisk.get("description_summary")
                or len(orisk["description_summary"]) > 150 or orisk.get("source") not in ("regulatory", "market")
                or not orisk.get("related_ids")):
            logger.warning(f"QUALITY-GATE: open_risk {orisk.get('id')} fails schema")
            return True
    if open_risks and not _ids_sequential(open_risks, "OR"):
        logger.warning("QUALITY-GATE: open_risks ids not sequential / have gaps or duplicates")
        return True

    regulatory_posture = items["regulatory_posture"]
    if "overall_status" not in regulatory_posture or "constraint_summaries" not in regulatory_posture:
        logger.warning("QUALITY-GATE: regulatory_posture missing overall_status or constraint_summaries")
        return True

    # reconciliation-coverage-complete — THE blocker, self-contained on this same output
    constraint_ids = {cs.get("constraint_id") for cs in regulatory_posture["constraint_summaries"] if cs.get("constraint_id")}
    covered_ids = set()
    for orisk in open_risks:
        for rid in orisk.get("related_ids", []):
            covered_ids.add(rid)
    uncovered = constraint_ids - covered_ids
    if uncovered:
        logger.warning(f"QUALITY-GATE: constraint_ids {uncovered} not covered by any open_risks.related_ids — reconciliation gap")
        return True

    # roadmap-phase1-addresses-worst-risk
    red_constraint_ids = {cs.get("constraint_id") for cs in regulatory_posture["constraint_summaries"] if cs.get("status") == "Red"}
    if red_constraint_ids:
        risk_ids_tracing_to_red = {orisk["id"] for orisk in open_risks if red_constraint_ids & set(orisk.get("related_ids", []))}
        phase1 = next((r for r in roadmap if r["phase_number"] == 1), None)
        if phase1 and risk_ids_tracing_to_red and phase1.get("resolves_risk") not in risk_ids_tracing_to_red:
            logger.warning(f"QUALITY-GATE: roadmap phase 1 does not resolve a Red-traced open risk ({risk_ids_tracing_to_red})")
            return True

    # no-publishing-tool-invoked (light deterministic text check)
    exec_summary = (gen_content.get("execution_summary", "") or "").lower()
    if "confluence" in exec_summary and ("invoked" in exec_summary or "published" in exec_summary or "created page" in exec_summary):
        logger.warning("QUALITY-GATE: execution_summary suggests a Confluence tool was invoked by this agent — not its job")
        return True

    # viability-score-honest (needs original_input)
    orig = _parse(original_input) if original_input else None
    if orig:
        orig_scores = _find_all(orig, "viability_score")
        if orig_scores:
            score_str = str(orig_scores[0])
            if score_str not in (gen_content.get("execution_summary", "") or ""):
                logger.warning(f"QUALITY-GATE: original viability_score={orig_scores[0]} not reported in execution_summary")
                return True

    return False
