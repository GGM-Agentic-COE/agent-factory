"""gr-L1-market-analysis-quality-gate: validates the RESULTANT
L1-vision-market-analyzer output (its own items, with the evaluator's
fixes_applied resolved in) against L1-vision-market-analyzer/output_schema.json
and L1-vision-market-analyzer/evaluation.md. Fires at
L1-vision-market-analyzer-evaluator's post_execution.
"""
import json
import logging
import re
from nemoguardrails.actions import action

logger = logging.getLogger("gr-L1-market-analysis-quality-gate")

SWOT_QUADRANTS = {"strengths": "ST", "weaknesses": "WK", "opportunities": "OP", "threats": "TH"}
DIRECTION_ENUM = {"growing", "declining", "stable", "emerging"}
PRICING_MODEL_ENUM = {"commission", "subscription", "listing_fee", "transaction_fee", "other"}


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
                else:
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
async def check_market_analysis_quality_gate(output: str, generator_output: str = None) -> bool:
    """Return True if a quality-gate violation is found in the RESULTANT market-analysis output."""
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
    for field in ["competitor_matrix", "swot", "market_sizing", "industry_trends", "customer_insights", "pricing_benchmarks", "data_sufficiency"]:
        if field not in items:
            logger.warning(f"QUALITY-GATE: resultant output missing required field '{field}'")
            return True

    def _citation_incomplete(entry, label):
        citation = entry.get("citation", {})
        if not citation.get("source_reference") or not citation.get("retrieved_date"):
            logger.warning(f"QUALITY-GATE: {label} missing source_reference or retrieved_date — citation incomplete")
            return True
        return False

    competitors = items["competitor_matrix"]
    for c in competitors:
        if not re.match(r"^CM-\d{2}$", c.get("id", "")):
            logger.warning(f"QUALITY-GATE: competitor id '{c.get('id')}' malformed")
            return True
        for f in ["positioning", "strengths", "weaknesses"]:
            v = c.get(f, "")
            if not v:
                logger.warning(f"QUALITY-GATE: competitor {c.get('id')}.{f} missing")
                return True
        if not c.get("confidence") or not c.get("reasoning"):
            logger.warning(f"QUALITY-GATE: competitor {c.get('id')} missing confidence/reasoning")
            return True

        # citation-completeness-100pct — the primary rubric check for this agent
        if _citation_incomplete(c, f"competitor {c.get('id')}"):
            return True

    # market_sizing — a single tam/sam/som structured estimate, not a list; every
    # sub-estimate still requires its own citation, even a low-confidence
    # gap-flagging one (citing what was consulted and came up empty)
    market_sizing = items["market_sizing"]
    for sub in ("tam", "sam", "som"):
        estimate = market_sizing.get(sub)
        if not estimate:
            logger.warning(f"QUALITY-GATE: market_sizing.{sub} missing")
            return True
        if not estimate.get("value") or not estimate.get("basis"):
            logger.warning(f"QUALITY-GATE: market_sizing.{sub} missing value/basis")
            return True
        if not estimate.get("confidence") or not estimate.get("reasoning"):
            logger.warning(f"QUALITY-GATE: market_sizing.{sub} missing confidence/reasoning")
            return True
        if _citation_incomplete(estimate, f"market_sizing.{sub}"):
            return True

    industry_trends = items["industry_trends"]
    for t in industry_trends:
        if not re.match(r"^TR-\d{2}$", t.get("id", "")):
            logger.warning(f"QUALITY-GATE: industry_trends id '{t.get('id')}' malformed")
            return True
        if not t.get("statement") or not t.get("confidence") or not t.get("reasoning"):
            logger.warning(f"QUALITY-GATE: industry_trends {t.get('id')} fails schema")
            return True
        if t.get("direction") not in DIRECTION_ENUM:
            logger.warning(f"QUALITY-GATE: industry_trends {t.get('id')} has invalid direction '{t.get('direction')}'")
            return True
        if _citation_incomplete(t, f"industry_trends {t.get('id')}"):
            return True
    if industry_trends and not _ids_sequential(industry_trends, "TR"):
        logger.warning("QUALITY-GATE: industry_trends ids not sequential / have gaps or duplicates")
        return True

    customer_insights = items["customer_insights"]
    for ci in customer_insights:
        if not re.match(r"^CI-\d{2}$", ci.get("id", "")):
            logger.warning(f"QUALITY-GATE: customer_insights id '{ci.get('id')}' malformed")
            return True
        if not ci.get("insight") or not ci.get("segment") or not ci.get("confidence") or not ci.get("reasoning"):
            logger.warning(f"QUALITY-GATE: customer_insights {ci.get('id')} fails schema")
            return True
        if _citation_incomplete(ci, f"customer_insights {ci.get('id')}"):
            return True
    if customer_insights and not _ids_sequential(customer_insights, "CI"):
        logger.warning("QUALITY-GATE: customer_insights ids not sequential / have gaps or duplicates")
        return True

    pricing_benchmarks = items["pricing_benchmarks"]
    for pb in pricing_benchmarks:
        if not re.match(r"^PB-\d{2}$", pb.get("id", "")):
            logger.warning(f"QUALITY-GATE: pricing_benchmarks id '{pb.get('id')}' malformed")
            return True
        if not pb.get("subject") or not pb.get("price_point") or not pb.get("confidence") or not pb.get("reasoning"):
            logger.warning(f"QUALITY-GATE: pricing_benchmarks {pb.get('id')} fails schema")
            return True
        if pb.get("model") not in PRICING_MODEL_ENUM:
            logger.warning(f"QUALITY-GATE: pricing_benchmarks {pb.get('id')} has invalid model '{pb.get('model')}'")
            return True
        if _citation_incomplete(pb, f"pricing_benchmarks {pb.get('id')}"):
            return True
    if pricing_benchmarks and not _ids_sequential(pricing_benchmarks, "PB"):
        logger.warning("QUALITY-GATE: pricing_benchmarks ids not sequential / have gaps or duplicates")
        return True

    swot = items["swot"]
    for quadrant, prefix in SWOT_QUADRANTS.items():
        entries = swot.get(quadrant, [])
        for e in entries:
            if not re.match(rf"^{prefix}-\d{{2}}$", e.get("id", "")):
                logger.warning(f"QUALITY-GATE: {quadrant} id '{e.get('id')}' malformed")
                return True
            statement = e.get("statement", "")
            if not statement or not e.get("confidence") or not e.get("reasoning"):
                logger.warning(f"QUALITY-GATE: {quadrant} entry {e.get('id')} fails schema")
                return True
        if entries and not _ids_sequential(entries, prefix):
            logger.warning(f"QUALITY-GATE: {quadrant} ids not sequential / have gaps or duplicates")
            return True

    if competitors and not _ids_sequential(competitors, "CM"):
        logger.warning("QUALITY-GATE: competitor_matrix ids not sequential / have gaps or duplicates")
        return True

    data_suff = items["data_sufficiency"]
    if data_suff.get("status") not in ("sufficient", "insufficient") or not data_suff.get("rationale"):
        logger.warning("QUALITY-GATE: data_sufficiency fails schema")
        return True

    return False
