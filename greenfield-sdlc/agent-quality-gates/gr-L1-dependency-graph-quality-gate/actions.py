"""gr-L1-dependency-graph-quality-gate: validates the RESULTANT
L1-planning-dependency-mapper output (its own items, with the evaluator's
fixes_applied resolved in) against L1-planning-dependency-mapper/
output_schema.json and its evaluation.md rubric. Fires at
L1-planning-dependency-mapper-evaluator's post_execution.

Unlike most other quality gates in this framework, the single most
important check here is NOT a schema/regex check — it is an INDEPENDENT
re-computation, in Python, of the DFS cycle check (Processing Rule 4) and
the longest-path critical_path (Processing Rule 6) over the resultant
nodes/edges, compared against what the resultant content claims. Neither
the generator's own cycle_check/critical_path fields nor the evaluator's
own re-derivation (scored, self-reported) are trusted at face value — a
reversed edge or an unverified cycle claim is schema-valid and still wrong
(see L1-planning-dependency-mapper-evaluator/golden/v1.0.0/
golden-02-edge-direction-bug.json).
"""
import json
import logging
import re
from nemoguardrails.actions import action

logger = logging.getLogger("gr-L1-dependency-graph-quality-gate")

NODE_ID_RE = re.compile(r"^[a-z0-9-]+$")
NODE_TYPES = {"component", "external-dependency"}
EDGE_TYPES = {"depends-on", "blocks", "integrates-with"}
BLOCKING_EDGE_TYPES = {"depends-on", "blocks"}
REQUIRED_TOP_FIELDS = [
    "product_name", "source_artifacts", "nodes", "edges",
    "cycle_check", "critical_path", "generated",
    "execution_id", "workflow_execution_id",
]


def _parse(x):
    if isinstance(x, dict):
        return x
    try:
        return json.loads(x)
    except (TypeError, ValueError):
        return None


# ---------------------------------------------------------------------------
# Resultant reconstruction: apply fixes_applied[].before -> after onto a
# deep copy of the generator's FULL output (envelope + content.items). Fixes
# in this domain are typically structural (a corrected edge object, a
# corrected critical_path.nodes ordering/rationale) rather than a single
# plain-string substitution, so this handles both the structural patterns
# this agent's own fixes actually take (see golden-02-edge-direction-bug)
# and falls back to generic string substitution for simpler fixes.
# ---------------------------------------------------------------------------

_EDGE_OBJ_RE = re.compile(
    r'\{\s*"from"\s*:\s*"[^"]*"\s*,\s*"to"\s*:\s*"[^"]*"\s*,\s*"type"\s*:\s*"[^"]*"\s*\}'
)
_CP_NODES_RE = re.compile(r'critical_path\.nodes\s*:\s*(\[[^\]]*\])')
_CP_RATIONALE_RE = re.compile(r'critical_path\.rationale\s*:\s*"([^"]*)"')


def _extract_edge_objs(text):
    objs = []
    for m in _EDGE_OBJ_RE.finditer(text or ""):
        try:
            objs.append(json.loads(m.group(0)))
        except (TypeError, ValueError):
            pass
    return objs


def _apply_edge_fix(doc, before, after):
    """If before/after each contain one or more {"from":.., "to":.., "type":..}
    edge-object fragments (in the same order), replace the matching edge(s)
    in doc's items.edges by structural equality."""
    before_edges = _extract_edge_objs(before)
    after_edges = _extract_edge_objs(after)
    if not before_edges or len(before_edges) != len(after_edges):
        return
    edges = doc.get("content", {}).get("items", {}).get("edges", [])
    for b_edge, a_edge in zip(before_edges, after_edges):
        for i, e in enumerate(edges):
            if (e.get("from") == b_edge.get("from")
                    and e.get("to") == b_edge.get("to")
                    and e.get("type") == b_edge.get("type")):
                edges[i] = a_edge
                break


def _apply_critical_path_fix(doc, after):
    """If after contains 'critical_path.nodes: [...]' and/or
    'critical_path.rationale: "..."' fragments, apply them directly."""
    items = doc.get("content", {}).get("items", {})
    cp = items.get("critical_path")
    if cp is None:
        return
    m = _CP_NODES_RE.search(after or "")
    if m:
        try:
            cp["nodes"] = json.loads(m.group(1))
        except (TypeError, ValueError):
            pass
    m = _CP_RATIONALE_RE.search(after or "")
    if m:
        cp["rationale"] = m.group(1)


def _apply_string_substitution(node, before, after):
    if isinstance(node, dict):
        for k, v in node.items():
            if isinstance(v, str):
                if before and after and before in v:
                    node[k] = v.replace(before, after)
            elif isinstance(v, (dict, list)):
                _apply_string_substitution(v, before, after)
    elif isinstance(node, list):
        for item in node:
            _apply_string_substitution(item, before, after)


def _apply_fixes(gen_doc, fixes_applied):
    """Reconstruct the RESULTANT generator_output: deep-copy gen_doc and
    resolve every fixes_applied[].before -> after into it (structural edge /
    critical_path patterns first, then generic string substitution as a
    fallback for simpler fixes)."""
    resultant = json.loads(json.dumps(gen_doc))
    for fx in fixes_applied or []:
        before, after = fx.get("before"), fx.get("after")
        if not before or not after:
            continue
        _apply_edge_fix(resultant, before, after)
        _apply_critical_path_fix(resultant, after)
        _apply_string_substitution(resultant, before, after)
    return resultant


# ---------------------------------------------------------------------------
# Output schema validation
# ---------------------------------------------------------------------------

def _check_schema_compliance(items):
    for field in REQUIRED_TOP_FIELDS:
        if field not in items:
            return True, f"resultant items missing required field '{field}'"

    nodes = items.get("nodes")
    if not isinstance(nodes, list) or not nodes:
        return True, "nodes[] missing or empty"

    seen_ids = set()
    for n in nodes:
        nid = n.get("id")
        if not nid or not NODE_ID_RE.match(nid):
            return True, f"node id '{nid}' is missing or not kebab-case (^[a-z0-9-]+$)"
        if nid in seen_ids:
            return True, f"duplicate node id '{nid}'"
        seen_ids.add(nid)
        if n.get("type") not in NODE_TYPES:
            return True, f"node '{nid}' has invalid/missing type '{n.get('type')}'"
        if not n.get("label"):
            return True, f"node '{nid}' missing label"

    edges = items.get("edges")
    if not isinstance(edges, list):
        return True, "edges[] missing"
    for e in edges:
        if not e.get("from") or not e.get("to") or e.get("type") not in EDGE_TYPES:
            return True, f"edge {e} missing from/to or has invalid type"

    cc = items.get("cycle_check", {})
    if not isinstance(cc, dict) or cc.get("status") not in ("PASS", "FAIL") or "cycles_found" not in cc:
        return True, "cycle_check malformed (must have status PASS|FAIL and cycles_found)"

    cp = items.get("critical_path", {})
    if not isinstance(cp, dict) or "nodes" not in cp or "rationale" not in cp:
        return True, "critical_path malformed (must have nodes and rationale)"

    return False, ""


def _check_edge_endpoints(items):
    node_ids = {n.get("id") for n in items.get("nodes", [])}
    for e in items.get("edges", []):
        if e.get("from") not in node_ids or e.get("to") not in node_ids:
            return True, f"edge {e} references a node id not present in nodes[]"
    return False, ""


# ---------------------------------------------------------------------------
# Independent DFS cycle check — mirrors Processing Rule 4 exactly:
# recursion-stack back-edge detection over EVERY node/edge.
# ---------------------------------------------------------------------------

def _independent_cycle_check(nodes, edges):
    node_ids = [n.get("id") for n in nodes if n.get("id")]
    adj = {nid: [] for nid in node_ids}
    for e in edges:
        f = e.get("from")
        if f in adj:
            adj[f].append(e.get("to"))

    WHITE, GRAY, BLACK = 0, 1, 2
    color = {nid: WHITE for nid in node_ids}
    stack = []
    cycles = []

    def dfs(u):
        color[u] = GRAY
        stack.append(u)
        for v in adj.get(u, []):
            if v not in color:
                continue  # dangling edge — caught separately by edge-endpoints-valid
            if color[v] == GRAY:
                idx = stack.index(v)
                cycles.append(stack[idx:] + [v])
            elif color[v] == WHITE:
                dfs(v)
        stack.pop()
        color[u] = BLACK

    for nid in node_ids:
        if color[nid] == WHITE:
            dfs(nid)

    status = "FAIL" if cycles else "PASS"
    return status, cycles


def _cycle_node_set(cycle):
    """Canonicalize a cycle (a node-id sequence, first==last) to the
    frozenset of distinct node ids involved — rotation/orientation of the
    same cycle should not be treated as a mismatch."""
    if len(cycle) > 1 and cycle[0] == cycle[-1]:
        return frozenset(cycle[:-1])
    return frozenset(cycle)


def _check_independent_cycle_recheck(items):
    computed_status, computed_cycles = _independent_cycle_check(items["nodes"], items["edges"])
    claimed_cc = items.get("cycle_check", {})
    claimed_status = claimed_cc.get("status")

    if computed_status != claimed_status:
        return True, computed_status, computed_cycles, (
            f"independent DFS computed cycle_check.status='{computed_status}' but resultant "
            f"content claims '{claimed_status}'"
        )

    if computed_status == "FAIL":
        computed_sets = {_cycle_node_set(c) for c in computed_cycles}
        claimed_sets = {_cycle_node_set(c) for c in claimed_cc.get("cycles_found", [])}
        if computed_sets != claimed_sets:
            return True, computed_status, computed_cycles, (
                f"independent DFS found cycle node-sets {computed_sets} which do not match "
                f"resultant cycles_found node-sets {claimed_sets}"
            )

    return False, computed_status, computed_cycles, ""


# ---------------------------------------------------------------------------
# Independent longest-path (critical path) computation — mirrors Processing
# Rule 6: depends-on/blocks edges only, from every root with no incoming
# blocking edge, collecting every chain tied at the maximum length.
# ---------------------------------------------------------------------------

def _independent_longest_path(nodes, edges):
    node_ids = [n.get("id") for n in nodes if n.get("id")]
    blocking = [e for e in edges if e.get("type") in BLOCKING_EDGE_TYPES]
    adj = {nid: [] for nid in node_ids}
    incoming = {nid: 0 for nid in node_ids}
    for e in blocking:
        f, t = e.get("from"), e.get("to")
        if f in adj:
            adj[f].append(t)
        if t in incoming:
            incoming[t] += 1

    roots = [nid for nid in node_ids if incoming.get(nid, 0) == 0]

    best = {"len": -1, "chains": []}

    def walk(node, path, visiting):
        extended = False
        for nxt in adj.get(node, []):
            if nxt in visiting:
                continue  # guard only — independent-cycle-recheck already gates a real cycle
            extended = True
            walk(nxt, path + [nxt], visiting | {nxt})
        if not extended:
            length = len(path) - 1
            if length > best["len"]:
                best["len"] = length
                best["chains"] = [path]
            elif length == best["len"]:
                best["chains"].append(path)

    for r in roots:
        walk(r, [r], {r})

    return best["len"], best["chains"]


def _check_independent_longest_path_recheck(items, best_len, best_chains):
    cp = items.get("critical_path", {}) or {}
    claimed_nodes = cp.get("nodes", []) or []
    blocking_edge_set = {
        (e.get("from"), e.get("to"))
        for e in items.get("edges", [])
        if e.get("type") in BLOCKING_EDGE_TYPES
    }

    if len(claimed_nodes) >= 2:
        for i in range(len(claimed_nodes) - 1):
            pair = (claimed_nodes[i], claimed_nodes[i + 1])
            if pair not in blocking_edge_set:
                return True, (
                    f"critical_path.nodes claims a hop {pair[0]} -> {pair[1]} that is not an "
                    f"actual depends-on/blocks edge"
                )

    claimed_len = max(len(claimed_nodes) - 1, 0)

    if claimed_len < best_len:
        return True, (
            f"critical_path.nodes claims length {claimed_len} but the independently-computed "
            f"longest blocking path is {best_len}"
        )
    if claimed_len > best_len:
        return True, (
            f"critical_path.nodes claims length {claimed_len}, longer than the independently-"
            f"computed longest blocking path {best_len} — not a valid walk"
        )

    if len(best_chains) > 1:
        rationale = cp.get("rationale", "") or ""
        matched_claimed = any(chain == claimed_nodes for chain in best_chains)
        if not matched_claimed:
            return True, (
                f"critical_path.nodes {claimed_nodes} does not match any of the "
                f"{len(best_chains)} independently-computed tied longest chains"
            )
        for chain in best_chains:
            if chain == claimed_nodes:
                continue
            missing = [nid for nid in chain if nid not in rationale]
            if missing:
                return True, (
                    f"genuine tie found ({len(best_chains)} chains at length {best_len}) but "
                    f"critical_path.rationale does not mention tied chain {chain} "
                    f"(missing node ids {missing})"
                )

    return False, ""


# ---------------------------------------------------------------------------
# Cycle-status escalation check — evaluation.md Quality Gate #8, zero
# tolerance: a real cycle must never ship as overall status "success".
# ---------------------------------------------------------------------------

def _check_cycle_status_escalation(resultant_status, computed_cycle_status):
    if computed_cycle_status == "FAIL" and resultant_status != "failed":
        return True, (
            f"independent DFS found a real cycle but resultant AgentOutput status is "
            f"'{resultant_status}', not 'failed' — a cyclic graph must never ship as success"
        )
    return False, ""


# ---------------------------------------------------------------------------
# FR coverage recheck — evaluation.md Quality Gate #5, set equality against
# original_input.prd_output.
# ---------------------------------------------------------------------------

def _check_fr_coverage(items, original_input):
    if not original_input:
        return False, ""  # nothing to check against — not this check's job to fail on missing plumbing

    prd = original_input.get("prd_output", {}) or {}
    reqs = prd.get("content", {}).get("items", {}).get("requirements", []) or []
    if not reqs:
        return False, ""

    full_fr_set = {r.get("id") for r in reqs if r.get("id")}
    covered = set()
    for n in items.get("nodes", []):
        for fr in n.get("source_requirement", []) or []:
            covered.add(fr)

    if covered != full_fr_set:
        missing = sorted(full_fr_set - covered)
        extra = sorted(covered - full_fr_set)
        parts = []
        if missing:
            parts.append(f"missing FRs not covered by any node: {missing}")
        if extra:
            parts.append(f"FRs referenced that don't exist in prd.md: {extra}")
        return True, "FR coverage mismatch — " + "; ".join(parts)

    return False, ""


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

@action()
async def check_dependency_graph_quality_gate(output: str, generator_output: str = None, original_input: str = None) -> bool:
    """Return True if a quality-gate violation is found in the RESULTANT
    dependency-graph output. Independently re-derives cycle_check and
    critical_path from the resultant nodes/edges rather than trusting either
    the generator's or the evaluator's claims — that independent
    re-derivation is the whole point of this guardrail."""
    evaluator_doc = _parse(output)
    gen_doc = _parse(generator_output)
    orig = _parse(original_input)

    if gen_doc is None:
        logger.warning("DEP-GRAPH-QUALITY-GATE: generator_output not available or not valid JSON")
        return True

    if gen_doc.get("status") == "failed":
        return False  # legitimate INSUFFICIENT_CONTEXT run — nothing to validate

    fixes_applied = []
    if evaluator_doc:
        fixes_applied = evaluator_doc.get("content", {}).get("items", {}).get("fixes_applied", [])

    resultant_doc = _apply_fixes(gen_doc, fixes_applied)
    resultant_status = resultant_doc.get("status")
    items = resultant_doc.get("content", {}).get("items", {})

    # --- Output schema validation ---
    bad, reason = _check_schema_compliance(items)
    if bad:
        logger.warning(f"DEP-GRAPH-QUALITY-GATE schema-compliance: {reason}")
        return True

    bad, reason = _check_edge_endpoints(items)
    if bad:
        logger.warning(f"DEP-GRAPH-QUALITY-GATE edge-endpoints-valid: {reason}")
        return True

    # --- Rubric adherence: independent recomputation (the core of this guardrail) ---
    bad, computed_status, computed_cycles, reason = _check_independent_cycle_recheck(items)
    if bad:
        logger.warning(f"DEP-GRAPH-QUALITY-GATE independent-cycle-recheck: {reason}")
        return True

    bad, reason = _check_cycle_status_escalation(resultant_status, computed_status)
    if bad:
        logger.warning(f"DEP-GRAPH-QUALITY-GATE cycle-status-escalation-check: {reason}")
        return True

    if computed_status == "PASS":
        best_len, best_chains = _independent_longest_path(items["nodes"], items["edges"])
        bad, reason = _check_independent_longest_path_recheck(items, best_len, best_chains)
        if bad:
            logger.warning(f"DEP-GRAPH-QUALITY-GATE independent-longest-path-recheck: {reason}")
            return True

    bad, reason = _check_fr_coverage(items, orig)
    if bad:
        logger.warning(f"DEP-GRAPH-QUALITY-GATE fr-coverage-recheck: {reason}")
        return True

    return False
