"""gr-L1-impact-assessment-quality-gate: validates the RESULTANT
L1-planning-impact-assessor output (its own items, with the evaluator's
fixes_applied resolved in) against L1-planning-impact-assessor/output_schema.json
and its evaluation.md rubric. Fires at
L1-planning-impact-assessor-evaluator's post_execution.

Unlike the Phase 0 sibling gates, several rules here need the ORIGINAL
input (prd_output.content.items.requirements[], service_catalog.services[],
cmdb_export.configuration_items[]) — full-fr-coverage, capability-check-
not-vacuous, and ci-id-validity are coverage/anti-hallucination checks
against source data the generator's own items do not themselves carry.
"""
import json
import logging
import re
from nemoguardrails.actions import action

logger = logging.getLogger("gr-L1-impact-assessment-quality-gate")

BLAST_RADIUS_VALUES = {"Low", "Medium", "High"}

FR_ID_RE = re.compile(r"^FR-\d{3}$")
CI_ID_RE = re.compile(r"^CI-[A-Z]+-\d{3}$")
SVC_ID_RE = re.compile(r"^SVC-[A-Z]+-\d{3}$")


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


@action()
async def check_impact_assessment_quality_gate(output: str, generator_output: str = None, original_input: str = None) -> bool:
    """Return True if a quality-gate violation is found in the RESULTANT impact-assessment output."""
    evaluator_doc = _parse(output)
    gen_doc = _parse(generator_output)
    orig_doc = _parse(original_input) or {}

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

    # ------------------------------------------------------------------
    # schema-compliance
    # ------------------------------------------------------------------
    for field in ["capability_check", "existing_system_impact", "components", "external_dependencies"]:
        if field not in items:
            logger.warning(f"QUALITY-GATE: resultant output missing required field '{field}'")
            return True

    cap = items["capability_check"]
    for f in ["summary", "matched_service_id", "is_duplicate", "rationale"]:
        if f not in cap:
            logger.warning(f"QUALITY-GATE: capability_check missing required field '{f}'")
            return True
    if not cap.get("summary") or len(cap.get("summary", "")) < 20:
        logger.warning("QUALITY-GATE: capability_check.summary missing or under 20 chars")
        return True
    if not cap.get("rationale") or len(cap.get("rationale", "")) < 20:
        logger.warning("QUALITY-GATE: capability_check.rationale missing or under 20 chars")
        return True
    matched = cap.get("matched_service_id")
    if matched is not None and not SVC_ID_RE.match(matched):
        logger.warning(f"QUALITY-GATE: capability_check.matched_service_id '{matched}' malformed")
        return True
    if not isinstance(cap.get("is_duplicate"), bool):
        logger.warning("QUALITY-GATE: capability_check.is_duplicate is not a boolean")
        return True

    esi_list = items["existing_system_impact"]
    for esi in esi_list:
        for f in ["ci_id", "system_name", "touched", "how_or_why_not", "related_components"]:
            if f not in esi:
                logger.warning(f"QUALITY-GATE: existing_system_impact entry missing '{f}'")
                return True
        if not CI_ID_RE.match(esi.get("ci_id", "")):
            logger.warning(f"QUALITY-GATE: existing_system_impact ci_id '{esi.get('ci_id')}' malformed")
            return True
        if not isinstance(esi.get("touched"), bool):
            logger.warning(f"QUALITY-GATE: existing_system_impact {esi.get('ci_id')} touched is not a boolean")
            return True
        if not esi.get("how_or_why_not") or len(esi.get("how_or_why_not", "")) < 10:
            logger.warning(f"QUALITY-GATE: existing_system_impact {esi.get('ci_id')} how_or_why_not missing or under 10 chars")
            return True

    components = items["components"]
    if not components:
        logger.warning("QUALITY-GATE: components[] is empty — at least one required")
        return True
    for c in components:
        for f in ["requirement_id", "component_name", "is_new", "blast_radius", "rationale"]:
            if f not in c:
                logger.warning(f"QUALITY-GATE: components entry missing '{f}'")
                return True
        if not FR_ID_RE.match(c.get("requirement_id", "")):
            logger.warning(f"QUALITY-GATE: components requirement_id '{c.get('requirement_id')}' malformed")
            return True
        if not isinstance(c.get("is_new"), bool):
            logger.warning(f"QUALITY-GATE: component {c.get('requirement_id')} is_new is not a boolean")
            return True
        if not c.get("rationale") or len(c.get("rationale", "")) < 10:
            logger.warning(f"QUALITY-GATE: component {c.get('requirement_id')} rationale missing or under 10 chars")
            return True

    ext_deps = items["external_dependencies"]
    for ed in ext_deps:
        for f in ["name", "description", "related_components", "newly_surfaced"]:
            if f not in ed:
                logger.warning(f"QUALITY-GATE: external_dependencies entry missing '{f}'")
                return True
        if not ed.get("description") or len(ed.get("description", "")) < 20:
            logger.warning(f"QUALITY-GATE: external_dependency '{ed.get('name')}' description missing or under 20 chars")
            return True
        if not isinstance(ed.get("newly_surfaced"), bool):
            logger.warning(f"QUALITY-GATE: external_dependency '{ed.get('name')}' newly_surfaced is not a boolean")
            return True

    # ------------------------------------------------------------------
    # blast-radius-enum-validity
    # ------------------------------------------------------------------
    for c in components:
        if c.get("blast_radius") not in BLAST_RADIUS_VALUES:
            logger.warning(f"QUALITY-GATE: component {c.get('requirement_id')} has invalid blast_radius '{c.get('blast_radius')}'")
            return True

    # ------------------------------------------------------------------
    # Pull original_input sources (prd_output, service_catalog, cmdb_export)
    # ------------------------------------------------------------------
    prd_output = orig_doc.get("prd_output", {}) or {}
    service_catalog = orig_doc.get("service_catalog", {}) or {}
    cmdb_export = orig_doc.get("cmdb_export", {}) or {}

    services = service_catalog.get("services", []) or []
    cis = cmdb_export.get("configuration_items", []) or []
    catalog_empty = len(services) == 0
    cmdb_empty = len(cis) == 0
    service_ids = {s.get("service_id") for s in services if s.get("service_id")}
    ci_ids = {c.get("ci_id") for c in cis if c.get("ci_id")}

    # ------------------------------------------------------------------
    # capability-check-not-vacuous
    # ------------------------------------------------------------------
    if not catalog_empty:
        if matched is None:
            logger.warning("QUALITY-GATE: capability_check.matched_service_id is null despite a non-empty service_catalog — vacuous check")
            return True
        if matched not in service_ids:
            logger.warning(f"QUALITY-GATE: capability_check.matched_service_id '{matched}' not present in service_catalog — vacuous/invented")
            return True
    else:
        if matched is not None and matched not in service_ids:
            logger.warning(f"QUALITY-GATE: capability_check.matched_service_id '{matched}' invented — service_catalog is genuinely empty")
            return True

    # ------------------------------------------------------------------
    # no-vacuous-empty-check
    # ------------------------------------------------------------------
    if not catalog_empty and not cmdb_empty and len(esi_list) == 0:
        logger.warning("QUALITY-GATE: existing_system_impact[] is empty despite a non-empty service_catalog/cmdb_export — nothing was checked")
        return True

    # ------------------------------------------------------------------
    # ci-id-validity (skipped entirely if cmdb_export is genuinely empty)
    # ------------------------------------------------------------------
    if not cmdb_empty:
        for esi in esi_list:
            if esi.get("ci_id") not in ci_ids:
                logger.warning(f"QUALITY-GATE: existing_system_impact references ci_id '{esi.get('ci_id')}' not present in cmdb_export")
                return True

    # ------------------------------------------------------------------
    # full-fr-coverage
    # ------------------------------------------------------------------
    prd_items = prd_output.get("content", {}).get("items", {}) if isinstance(prd_output, dict) else {}
    prd_requirements = prd_items.get("requirements", []) if isinstance(prd_items, dict) else []
    fr_ids_in_prd = {r.get("id") for r in prd_requirements if r.get("id")}

    component_fr_ids = {c.get("requirement_id") for c in components if c.get("requirement_id")}

    if fr_ids_in_prd:
        missing = fr_ids_in_prd - component_fr_ids
        if missing:
            logger.warning(f"QUALITY-GATE: FR(s) {sorted(missing)} in prd.md have no component — coverage gap")
            return True
        invented = component_fr_ids - fr_ids_in_prd
        if invented:
            logger.warning(f"QUALITY-GATE: component(s) reference FR id(s) {sorted(invented)} not present in prd_output")
            return True

    return False
