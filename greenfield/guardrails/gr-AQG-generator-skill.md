---
name: agent-quality-guardrail
description: Use this skill whenever the user pastes an agent-pair quality-gate guardrail README (a generator agent + an evaluator agent, where the guardrail independently re-checks the evaluator's resultant output against a rubric/checklist) and asks for the guardrail files. Generates exactly three files — .co, .yml, and README.md — printed as plain text code blocks in chat. Prompt-only mode only: no actions.py, no spec.yaml. Distinct from guardrail-prompt-writer, which handles simple single-condition input/output rails; this skill is for rubric/checklist-driven output gates sitting after a generator→evaluator agent pair.
trigger: When the user pastes a quality-gate guardrail README/spec (generator + evaluator agents, rubric or checklist to validate resultant output against) and asks to create or generate the guardrail files, or explicitly invokes the "agent quality guardrail" skill.
---

# Agent Quality Guardrail Skill

Generates exactly three files, printed as plain text code blocks in the chat response, in this order: `.co`, `.yml`, `README.md`. Never use create_file, present_files, or artifacts for these — the user copies them directly into their guardrail folder. Never add explanation between the files unless asked.

**Scope boundary — read this first:** this skill produces prompt-only guardrails. It never generates `actions.py` or `spec.yaml`. The guardrail this skill builds has no access to `original_input` (no `prd_output`/`service_catalog`/`cmdb_export` or equivalent side-channel data) — it validates the resultant output's **internal consistency** against a checklist/rubric, not against external source-of-truth data. Checks that inherently require external data (id-existence lookups, coverage-set comparisons against a source system) are out of scope for this skill's output and should be flagged to the user, not silently attempted.

---

## Step 1 — Extract from the user's description

Read the pasted README/spec and extract:

| Field | Where to find it |
|-------|-------------------|
| `guardrail-name` | The `gr-L{n}-{name}` identifier |
| `layer` | L1 / L2 / L3 / L4 |
| `triggers-on` | Always `output` for this skill — these gates fire post_execution on the evaluator agent |
| `applies-to` | The evaluator agent name this gate is scoped to (`configured_agents`) |
| `generator-agent` | The upstream generator agent whose resultant output is being validated |
| `category` | Short slug, e.g. `impact-assessment-quality` |
| `severity` | Highest severity among the rules table — usually `critical` |
| `reason` | One sentence summarizing what the gate blocks on |
| `checklist-items` | The Quality Gates / rubric checklist — turn each into a numbered "Flag ONLY if" item, phrased as the *failure* condition, not the pass condition |
| `score-thresholds` | Any rubric score table (faithfulness, hallucination, consistency, relevance, reasoning quality, etc.) — turn each into a numbered failure condition ("X below/above threshold") |
| `legitimate-refusal-carveout` | Any status/condition the source agents treat as a valid non-defect (e.g. `status: "failed"` + a named reason code) — this must become an explicit "Do NOT flag" / skip-checks clause, checked FIRST in the prompt |
| `do-not-flag` | Explicit carve-outs beyond the refusal case (e.g. null/empty values that are correct given a stated empty source) |
| `out-of-scope-checks` | Any rule in the source README that requires external data (id-existence against a source system, coverage-set match against an external list) — do NOT fabricate a prompt check for these; list them in the README's Known Limitations section instead |

If any field is missing, infer it from context. Do not ask clarifying questions.

---

## Step 2 — Write the .co file

Identical format/rules to `guardrail-prompt-writer`. Exactly three `define bot` blocks, same JSON string in all three, blank line after the last block.

```
# {guardrail-name} — Prompt-Only Mode
# Layer: {layer}
# Triggers on: output (post_execution — fires when {applies-to} concludes)

define bot refuse to respond
  "{\"detected\": true, \"verdict\": \"rejected\", \"reason\": \"{reason}\", \"severity\": \"{severity}\", \"category\": \"{category}\", \"rail\": \"output\"}"

define bot inform cannot answer
  "{\"detected\": true, \"verdict\": \"rejected\", \"reason\": \"{reason}\", \"severity\": \"{severity}\", \"category\": \"{category}\", \"rail\": \"output\"}"

define bot inform answer unknown
  "{\"detected\": true, \"verdict\": \"rejected\", \"reason\": \"{reason}\", \"severity\": \"{severity}\", \"category\": \"{category}\", \"rail\": \"output\"}"

```

---

## Step 3 — Write the .yml file

```yaml
models:

  - type: main
    engine: openai
    model: gpt-5.4


rails:
  output:
    flows:
      - self check output

prompts:
  - task: self_check_output
    content: |
      Your task is to check if the bot response (resultant {generator-agent} output, with {applies-to}'s fixes resolved in) passes every Quality Gate checklist item and every rubric score threshold below.

      Bot response: "{{ bot_response }}"

      First, check status. {legitimate-refusal-carveout — e.g. If status is "failed" with reason "INSUFFICIENT_CONTEXT", this is a legitimate refusal — treat it as safe and skip the checks below.}

      Otherwise, flag ONLY if the response fails any of these Quality Gates:
      1. {first checklist item, phrased as a failure condition}
      2. {second checklist item, phrased as a failure condition}
      ... {continue for every checklist item}
      {N+1}. {first score threshold, phrased as a failure condition, e.g. "Faithfulness below 0.90 — ..."}
      ... {continue for every score threshold}

      Do NOT flag:
      - {legitimate-refusal-carveout, restated as a do-not-flag bullet}
      - {first carve-out}
      ... {continue for every carve-out}

      Answer only "yes" if the response passes every Quality Gate and every rubric threshold above.
      Answer "no" if the response fails any Quality Gate or falls below any rubric threshold.
```

### .yml rules
- Same formatting rules as `guardrail-prompt-writer` (blank line after `models:`, two blank lines before `rails:`, no `parameters` block, `type: main`, `engine: openai`, `model: gpt-5.4`).
- The refusal/legitimate-failure carve-out is always checked **first**, before any numbered checklist item — this must short-circuit the rest of the evaluation.
- Every numbered item is phrased as the **failure** condition ("X is missing", "Y is below threshold"), never the pass condition — matches `yes` = safe, `no` = blocked.
- Do not invent a check that requires external data (`original_input`, source-system lookups) unless the user has confirmed that data is actually threaded into `{{ bot_response }}` or a second template variable. If the source README has checks like this, note them as excluded in the README's Known Limitations section instead of guessing at a check the LLM can't actually perform reliably.

---

## Step 4 — Write the README.md file

Follow the structure of the pasted template, scoped down to what this skill actually controls.

```markdown
# {guardrail-name}

**Layer:** {layer}
**Triggers on:** post_execution (output rail) — fires when `{applies-to}` concludes
**On fail:** Retry once, then escalate to HITL
**Implementation:** LLM-driven (Colang), prompt-only mode
**Applies to:** `{applies-to}` only (`configured_agents`)

## What does it do?

`{applies-to}` independently re-derives `{generator-agent}`'s checks and
fixes what it can. This guardrail fires at that point but validates a
different thing: the **resultant** `{generator-agent}` output — its own
`items`, with the evaluator's fixes resolved in — is what actually flows
downstream. This gate checks that content against the Quality Gate
checklist and rubric score thresholds below, independent of what the
evaluator's own bookkeeping (`final_decision`, `pass`) claims.

### Checklist

{Reproduce the user's Quality Gates checklist here as a markdown checklist.}

### Rubric thresholds

{Reproduce the user's score threshold table here, if provided.}

## Known Limitations (prompt-only mode)

This gate is LLM-driven and has no access to `original_input`
(`{generator-agent}`'s source data) or a code execution step. It can
reliably judge:
- Internal consistency of the resultant output (every field populated,
  every rationale genuinely explanatory, no field silently blank)
- Whether the checklist/rubric conditions are met on their face

It CANNOT reliably judge, and does not attempt to check:
{list any out-of-scope-checks identified in Step 1 — e.g. "whether a
referenced id actually exists in an external system", "whether a
coverage set exactly matches an external source list"}

If exact-match/lookup validation against external source data is
required, that needs either (a) `original_input` threaded into the
prompt as a second template variable, or (b) a Python-hybrid
implementation (`actions.py`) — both are out of scope for this skill.

## Required Agent-Description Additions

Because this gate cannot see `original_input`, the upstream agents must
self-report enough information in their own output for a prompt-only
checklist gate to judge reliably. Add the following three chunks to
`{generator-agent}` and `{applies-to}`'s own Description/Instructions
field (all agents in this system share the same description pattern —
add these under the existing `Don'ts:` / `Reflection:` sections):

**Chunk 1 — Explicit-Statement Requirement**
\`\`\`
Explicit-Statement Requirement (for downstream quality gates):
- If a source input is genuinely empty, state this explicitly in the
  output (e.g., "empty — no parent enterprise") — never leave the field
  blank or silently omit it.
- If a check was genuinely run and found nothing relevant, state that
  explicitly (e.g., "checked, no matching service found") — never let an
  unchecked field look identical to a checked-and-clear field.
- Do NOT conflate "not applicable" with "not checked" anywhere in the
  output.
\`\`\`

**Chunk 2 — Anti-Hallucination & Grounding Requirement**
\`\`\`
Anti-Hallucination & Grounding Requirement:
- Never reference an id (or equivalent identifier) that is not actually
  present in the source input — never invent one.
- Every rationale must explain the decision (why), not merely restate
  the finding (what) — a rationale that just repeats the field it
  justifies is a failure.
- Any mismatch between two source-of-truth systems must be flagged as a
  finding, never silently reconciled by picking one source.
\`\`\`

**Chunk 3 — Legitimate-Refusal Status Requirement**
\`\`\`
Legitimate-Refusal Status Requirement:
- If upstream input is invalid or insufficient to proceed, set
  status: "failed" with an explicit, named reason (e.g.,
  "INSUFFICIENT_CONTEXT") — do not attempt to proceed or partially
  fabricate output.
- Downstream quality gates treat a correctly-labeled failed status as a
  legitimate outcome, not a defect — do not disguise a refusal as a
  low-confidence success.
\`\`\`

## File Structure

```
{guardrail-name}/
├── config.yml                          # Rail configuration (this skill's output)
├── {guardrail-name}.co                 # LLM-only Colang flow (this skill's output)
└── README.md                           # This file (this skill's output)
```

**Not produced by this skill / not in scope:** `actions.py`, `spec.yaml`,
Python-hybrid Colang flow. If a hybrid implementation is needed later,
build it as a separate, explicit step — do not assume this skill's
output covers it.

## Testing

### Option 1: Prompt-Based Testing (LLM Judgement Only)

{One valid resultant-output JSON example expected "yes", one invalid
example with at least two checklist failures expected "no" — build
these from the user's own schema if provided.}

### Option 2: End-to-End Flow Testing (NeMo Guardrails SDK)

\`\`\`python
from nemoguardrails import LLMRails, RailsConfig

config = RailsConfig.from_path("./{guardrail-name}")
rails = LLMRails(config)

response = await rails.generate_async(
    messages=[{"role": "assistant", "content": "<clean resultant JSON>"}]
)
assert "blocked" not in response["content"].lower()

response = await rails.generate_async(
    messages=[{"role": "assistant", "content": "<invalid resultant JSON>"}]
)
assert "blocked" in response["content"].lower()
\`\`\`
```

### README rules
- Always include the **Known Limitations** section — never let the README imply this gate does more than a prompt-only checklist can actually do.
- Always include the **Required Agent-Description Additions** section with all three chunks verbatim (only the identifier names — `{generator-agent}`, `{applies-to}`, id formats — are substituted; the requirement language itself does not change between guardrails built with this skill).
- The **File Structure** section must explicitly list what's out of scope (`actions.py`, `spec.yaml`) so the user's team doesn't assume this skill produced a hybrid implementation.
- Drop the "Python Unit Testing" option entirely — there is no `actions.py` to test.

---

## Common Errors — Never Do These

| Error | Rule |
|-------|------|
| Generating `actions.py` or `spec.yaml` | Never — this skill is prompt-only, three files max |
| Adding an `original_input` template variable without user confirmation it's wired up | Never guess — ask or note it in Known Limitations |
| Writing a checklist item that requires an external lookup | Move it to Known Limitations instead of faking a prompt check |
| Omitting the legitimate-refusal carve-out as the FIRST check | Always checked first, short-circuits the rest |
| Omitting the Required Agent-Description Additions section | Always include all three chunks verbatim |
| Inverting yes/no | `yes` = safe, `no` = blocked |
| Missing blank lines in `.yml` | Two blank lines after `model:`, one after `models:` |
