---
name: guardrail-creator
description: Standard structure, patterns, and conventions for creating guardrails in the Agent Factory. Use this whenever asked to create, modify, or review a guardrail — apply this exact structure, naming, and implementation pattern.
trigger: When the user asks to create a guardrail, implement a guardrail, review guardrail code, or asks about guardrail patterns and standards.
---

# Guardrail Standards

## Naming Convention

```
gr-L{layer}-{function}
```

- `gr-` prefix always
- `L1` = Enterprise (all agents, non-overridable)
- `L2` = Domain/LOB (domain-specific agents)
- `L3` = Project/Initiative (project-specific)
- `L4` = Squad/Local (team-specific)
- `{function}` = kebab-case description of what it does

Examples:
- `gr-L1-pii-detection`
- `gr-L2-payments-compliance`
- `gr-L3-hallucination-detector`
- `gr-L4-reasoning-validator`
- `gr-L1-{core-agent-domain}-quality-gate` — see "Quality Gate Guardrail
  Pattern" below; required whenever a Core agent has a paired Evaluator agent

## Folder Structure

Every guardrail lives in its own folder under `/guardrails/` with this structure:

```
gr-L{n}-{name}/
├── config.yml              # NeMo Guardrails rail configuration
├── prompts.yml             # LLM evaluation prompts (self_check_input/output)
├── gr-L{n}-{name}.co      # LLM-only Colang flow (uses self_check)
├── {name}.co               # Python-hybrid Colang flow (calls actions.py)
├── actions.py              # Deterministic Python implementation
├── spec.yaml               # Guardrail specification
└── README.md               # Documentation with testing instructions
```

Two `.co` files provide two modes:
- **LLM-only** (`gr-L{n}-{name}.co`): Pure Colang, uses `execute self_check_input`/`self_check_output`. No Python dependency.
- **Python-hybrid** (`{name}.co`): Calls Python actions for regex/deterministic checks + LLM for semantic checks.

## spec.yaml Template

```yaml
spec_version: "1.0"
artifact_type: guardrail
metadata:
  name: gr-L{n}-{name}
  version: "1.0.0"
  layer: L{n}
  owner: {owner}
  implementation: colang

purpose:
  description: "{What this guardrail does in one sentence}"

triggers_on:
  - pre_execution    # input rail
  - post_execution   # output rail

on_fail: {block | retry_once | escalate_to_hitl | kill_execution | warn_and_continue}
applies_to: {all_agents | domain_agents | content_generator_agents | configured_agents}

rules:
  - name: {rule-name}
    description: "{What this rule checks}"
    action: {block | flag}
    severity: {critical | high | medium}

evaluation:
  false_positive_threshold: 0.05
```

## config.yml Template

```yaml
models:
  - type: main
    engine: openai
    model: gpt-4.1

rails:
  input:       # for pre_execution guardrails
    flows:
      - {flow name}
  output:      # for post_execution guardrails
    flows:
      - {flow name}
```

## prompts.yml Template

```yaml
prompts:
  - task: self_check_input    # for input rails
    content: |
      User input: {{ user_input }}

      {Numbered list of specific checks}

      Answer "yes" if {pass condition}. Answer "no" if {fail condition}.

  - task: self_check_output   # for output rails
    content: |
      Agent output: {{ bot_response }}

      {Numbered list of specific checks}

      Answer "yes" if {pass condition}. Answer "no" if {fail condition}.
```

### Prompt Rules
- Always use numbered lists for checks (1, 2, 3...)
- Be specific about what constitutes a pass vs fail
- Include edge cases in the prompt ("Note: X is acceptable, Y is not")
- Answer format must be "yes"/"no" (or "block"/"escalate"/"kill" for multi-outcome)
- Use `{{ user_input }}` for input rails, `{{ bot_response }}` for output rails

## LLM-Only .co Template (gr-L{n}-{name}.co)

```colang
# gr-L{n}-{name} — LLM-Driven Colang Implementation
# Layer: L{n} — {title}
# Validation: LLM self_check (pure Colang)
# Python actions preserved in actions.py for reference/hybrid mode

define flow {flow name}
  """LLM validates {description} rules."""
  $result = execute self_check_{input|output}

  if not $result
    bot block {guardrail name}
    stop

define bot block {guardrail name}
  "{Block message explaining what failed and why}"
```

### Flow Rules
- Flow names use spaces (Colang convention): `check output pii`, `check input injection`
- Use `execute self_check_input` for input rails, `execute self_check_output` for output rails
- `if not $result` — NeMo returns boolean
- Always `stop` after blocking
- Bot messages should be clear about what failed

## Python-Hybrid .co Template ({name}.co)

```colang
define flow {flow name}
  """Deterministic check via Python action."""
  $result = execute {action_name}(text=$user_message)  # or output=$bot_message

  if $result
    bot block {guardrail name}
    stop

  # Optional: also run LLM check for semantic analysis
  $llm_result = execute self_check_{input|output}

  if not $llm_result
    bot block {guardrail name}
    stop
```

## actions.py Template

```python
"""{guardrail name}: {description}"""
import re
import json
import logging
from nemoguardrails.actions import action

logger = logging.getLogger("{guardrail-name}")

@action()
async def {action_name}(text: str) -> bool:
    """Return True if violation detected, False if clean."""
    # Deterministic regex/logic checks
    patterns = [...]
    for pattern in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False
```

### Action Rules
- Always async (`async def`)
- Always decorated with `@action()`
- Return `bool` — True for detection (violation found), False for clean
- Use logging for observability (`logger.warning(...)`)
- Keep production integrations (DynamoDB, S3) commented

## README.md Template

```markdown
# gr-L{n}-{name}

**Layer:** L{n}
**Triggers on:** {pre_execution | post_execution | both}
**On fail:** {Block | Escalate | Kill | Warn}
**Implementation:** LLM-driven (Colang) — Python actions preserved for hybrid mode

## What does it do?

{Detailed explanation:}
- Why it exists
- What it catches (bullet list)
- When it fires (input/output/both) with clear explanation
- Why it matters (consequences of not having it)
- Scope notes if applicable

## How It Works

{ASCII flow diagram showing:}
- Entry point
- What's checked (numbered)
- Pass/fail outcomes
- What happens on each outcome

## File Structure

{Actual files with descriptions, noting the two .co modes}

## Testing

### Option 1: Prompt-Based Testing (LLM Judgement Only)
- Valid example (expected: "yes")
- Invalid example (expected: "no")

### Test Cases Matrix
| Test | Mutation | Expected |
|------|----------|----------|
| ... | ... | ... |

### Option 2: End-to-End Flow Testing (NeMo Guardrails SDK)
- Python code loading config and running pass/block scenarios

### Option 3: Python Unit Testing (standalone actions.py)
- Direct function calls
```

## Layering Rules

| Layer | Applies To | Overridable? | Examples |
|-------|-----------|--------------|----------|
| L1 Enterprise | ALL agents | ❌ Never | PII, injection, schema, secrets, content safety, audit |
| L2 Domain | Domain agents | ❌ Never (extends L1) | Compliance, policy, tool permissions, memory |
| L3 Project | Project agents | Can extend, not weaken | Hallucination, citations, confidence, consistency, cost, rate, loops |
| L4 Squad | Configured agents | Can extend, not weaken | Reasoning validator, custom format checks |

## Rail Types

| Type | When | Use For |
|------|------|---------|
| Input rail (`pre_execution`) | Before agent processes input | Injection, PII in input, validation, topic adherence, tool permissions |
| Output rail (`post_execution`) | After agent generates, before delivery | Schema, PII in output, secrets, hallucination, citations, confidence |
| Runtime rail | During execution | Loops, rate limits, cost control, memory safety |

## On-Fail Actions

| Action | Behaviour |
|--------|-----------|
| `block` | Stop delivery, return error message |
| `retry_once_then_escalate` | Retry generation once, escalate if still fails |
| `escalate_to_hitl` | Deliver to human review queue |
| `warn_and_continue` | Deliver output but log warning + alert ops |
| `kill_execution` | Terminate agent immediately |
| `throttle_then_block` | Slow down, block if persists |

## Cascade & Inheritance

Guardrails cascade downward — an L4 agent inherits ALL guardrails from L1 + L2 + L3 + L4:

```
L4 agent sees:
  └── L1 guardrails (enterprise — always applied, non-overridable)
  └── L2 guardrails (domain — if agent is in a domain)
  └── L3 guardrails (project — if agent is in a project)
  └── L4 guardrails (squad — agent's own squad rules)
```

Lower layers can ADD stricter guardrails but can NEVER weaken or remove inherited ones.

## Attaching Guardrails to an Agent

In the agent spec, guardrails are listed under `context.guardrails`:

```yaml
context:
  guardrails:
    - gr-L1-output-schema-validator   # L1 — auto-attached to all
    - gr-L1-pii-detection             # L1 — auto-attached to all
    - gr-L2-payments-compliance       # L2 — domain-specific
    - gr-L3-citation-validator        # L3 — project-specific
```

A quality gate guardrail (see "Quality Gate Guardrail Pattern" below) is
attached the same way, but ALWAYS on the Evaluator agent's spec, never the
paired Core generator's — even though what it validates is the generator's
resultant content.

L1 guardrails are auto-attached by the platform even if omitted from the spec.

## Execution Order

When multiple guardrails fire on the same rail (input or output), they execute in this order:

1. **L1 guardrails** (enterprise) — first, most critical
2. **L2 guardrails** (domain) — second
3. **L3 guardrails** (project) — third
4. **L4 guardrails** (squad) — last

Within the same layer, order follows the sequence in `config.yml` flows list. If any guardrail blocks, subsequent guardrails do NOT execute — fail fast.

## Logic Inversion (Important)

The two .co modes use **opposite boolean logic**:

| Mode | Function returns | Meaning | Block condition |
|------|-----------------|---------|-----------------|
| **LLM-only** | `self_check_input`/`output` returns `True` | Input/output is SAFE | `if not $result` → block |
| **Python-hybrid** | `detect_pii()`, `detect_injection()` returns `True` | Violation FOUND | `if $result` → block |

Always check which mode you're in before writing the `if` condition.

## Guardrails vs Evaluations

Guardrails and evaluations are different mechanisms:

| | Guardrails | Evaluations |
|---|---|---|
| When | Inline, real-time | Post-hoc, async |
| Action | Block/pass (binary) | Score (0.0–1.0) |
| Purpose | Prevent bad output delivery | Measure quality over time |
| Reference | `context.guardrails[]` in agent spec | `quality.evaluation_rubric` in agent spec |

See `quality-gates-vs-evaluation.md` for full comparison.

## Quality Gate Guardrail Pattern (Generator → Evaluator pairs)

**Whenever a Core agent has a paired Evaluator agent (the S6 pattern in
`agent-creator.md`), create exactly one quality gate guardrail for that
pair.** This is not optional decoration — a Generator→Evaluator pair
without one has no fast, binary check that a `fixed_and_approved` verdict
actually produced conformant content; it only has the evaluator's own
(scored, self-reported) word for it.

### The core principle — validate the RESULTANT content, not the evaluator's bookkeeping

The guardrail **fires** on the EVALUATOR's `post_execution` (evaluation has
concluded, so the resultant content is final) — but it **validates** the
paired CORE agent's resultant output, never the evaluator's own output
shape.

"Resultant output" = the core agent's original `items`, with the
evaluator's `fixes_applied[].before → after` substitutions resolved in.
Check that reconstructed content against:

1. **The CORE agent's own `output_schema.json`** — never the evaluator's
   shared envelope schema (`scores`/`overall_score`/`pass`/`findings`/
   `fixes_applied`/`final_decision`). If your rules reference any of those
   five fields structurally, you have built the wrong guardrail.
2. **The CORE agent's own `evaluation.md` rubric** — its Quality Gates and
   Reflection Checklist, translated into checkable binary gates.

**Why this distinction matters:** the evaluator's `fixed_and_approved` is a
*claim*. A fix that left a field over its length budget, resolved a
severity mismatch but forgot to clear `requires_legal_review`, or closed a
coverage gap by pointing at the wrong id would all still report as
"fixed" — the evaluator's own bookkeeping has no way to catch its own
mistake. This guardrail is the independent re-derivation that closes that
gap, checked directly against what actually ships to the next pipeline
step.

### Standard design process

1. **Inventory the core agent's `output_schema.json`**: required fields,
   ID patterns (`^CON-\d{2}$` etc.), length budgets (`maxLength`), enums,
   and any conditional rules (`allOf`/`if`/`then` — e.g. "Amber/Red
   requires a mitigation or a legal-review flag"). These become your
   **Output schema validation** rules.
2. **Inventory the core agent's `evaluation.md`**: its Quality Gates and
   Reflection Checklist. Mark which are BLOCKER/zero-tolerance (a false
   negative is a real risk, not a nuance) vs. advisory. These become your
   **Rubric adherence** rules — exactly two rule categories in `spec.yaml`,
   nothing else. (No third "evaluator meta-quality" category — that's the
   evaluator's own separate `evaluation.md`, never this guardrail's job.)
3. **Classify every rule as deterministic or semantic.** Structural checks
   (required fields present, ID sequencing, set-membership coverage
   checks, a conditional re-implemented in Python) go in `actions.py` and
   get `action: block`. Genuinely fuzzy judgment calls (does this reasoning
   read as generic vs. specific? does a claim actually appear elsewhere in
   the document?) stay LLM-only (`self_check_output` via `prompts.yml`) and
   typically get `action: flag`.
4. **Implement resultant-content reconstruction in `actions.py`** — a
   `_apply_fixes(items, fixes_applied)` helper that deep-copies the core
   agent's `items` and substitutes every `before → after` string match
   found anywhere in it, non-mutating. Validate the RECONSTRUCTED object,
   never the raw pre-fix `generator_output` directly (a fix that hasn't
   been applied to your check is a fix you can't see).
5. **Re-implement zero-tolerance conditionals explicitly**, even if the
   schema already encodes them (e.g. an `allOf`/`if`/`then` rule). Don't
   assume schema validation upstream already covered it — the whole point
   is to catch a case where a "fix" silently re-violates the rule.
6. **Wire it into the EVALUATOR's `spec.yaml`** under `context.guardrails`
   — never the generator's — with `applies_to: configured_agents` (never
   `all_agents`; this guardrail is scoped to exactly one evaluator).

### Naming

```
gr-L{n}-{core-agent-domain}-quality-gate
```

Use a short, recognizable stem for the core agent's output domain — it
doesn't need to be a verbatim copy of the agent's own name (`L1-vision-market-analyzer`
→ `gr-L1-market-analysis-quality-gate` is fine), but must stay obviously
traceable to which core agent it gates.

### Standard file conventions (extends the base guardrail folder structure above)

| Field | Standard value | Why |
|---|---|---|
| `triggers_on` | `[post_execution]` only | Nothing meaningful to gate before the evaluator runs |
| `on_fail` | `retry_once_then_escalate` | One retry gives the evaluator a chance to genuinely re-fix; escalate rather than block dead-end |
| `applies_to` | `configured_agents` | Scoped to exactly one evaluator's `context.guardrails`, never global |
| `rules` categories | Exactly two: "Output schema validation" and "Rubric adherence" | Keeps the guardrail honest about what it's checking — the core agent's contract, not the evaluator's |
| `evaluation.false_positive_threshold` | `0.05` default; `0.03` for a zero-tolerance / highest-stakes rubric | Mirror the core agent's own hallucination-tolerance tightness |
| `actions.py` signature | `async def check_{name}(output: str, generator_output: str = None, original_input: str = None) -> bool` | `output` = the evaluator's own output (source of `fixes_applied`); `generator_output` = the core agent's raw output (the thing being reconstructed and validated); `original_input` only when a rubric item needs something the core agent's own `items` doesn't carry (e.g. a score it received as an input parameter, not part of its own output) |
| A legitimate `status: "failed"` (INSUFFICIENT_CONTEXT) generator run | Return `False` (no violation) immediately, skip the rest of the checks | An honest failure has nothing to validate — don't invent schema violations against empty `items` |

### What this guardrail is NOT

- **Not** a re-score of faithfulness/hallucination/consistency/etc. — that
  scored judgment is the evaluator's own job, governed by the core agent's
  `evaluation.md` at runtime.
- **Not** a check on the evaluator's own `pass`/`final_decision`/`findings`
  bookkeeping. If you catch yourself writing a rule like "`pass` must equal
  `overall_score >= min_score`", stop — that validates the evaluator's
  envelope, not the core agent's content, and belongs nowhere in this
  pattern.
- **Not** a replacement for the workflow-level `qg-L{n}-{name}` score gate
  (e.g. a `viability_score` threshold) — that async, scored checkpoint
  still exists separately. This pattern is the fast, inline, binary gate
  layered underneath it, checking structural/rubric conformance rather
  than a quality score.

### Worked example — the zero-tolerance pattern

For a regulatory/compliance-style core agent whose `output_schema.json`
already encodes "every Amber/Red item needs a mitigation or a
legal-review flag" via `allOf`/`if`/`then`, re-derive that exact rule in
`actions.py` against the reconstructed resultant content:

```python
if c.get("status") in ("Amber", "Red"):
    has_mitigation = bool(c.get("mitigation_summary"))
    legal_review = bool(c.get("requires_legal_review"))
    if not has_mitigation and not legal_review:
        return True  # violation — zero tolerance, even post-fix
```

And for a synthesis agent whose rubric's BLOCKER is a coverage/reconciliation
check between two of its own output fields (no upstream lookup needed —
both fields live in the same resultant object):

```python
constraint_ids = {cs["constraint_id"] for cs in items["regulatory_posture"]["constraint_summaries"]}
covered_ids = {rid for risk in items["open_risks"] for rid in risk.get("related_ids", [])}
if constraint_ids - covered_ids:
    return True  # a constraint the evaluator's fix didn't actually cover
```
