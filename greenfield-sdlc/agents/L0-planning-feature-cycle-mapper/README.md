# L1-planning-feature-cycle-mapper

## Purpose

Assigns each ranked feature to the 5-day cycle (or cycles) of one Program Increment (PI) it will be built in. It is the second agent in the agentic planning pipeline, at backlog level, and runs once per PI and again whenever the backlog changes. It enforces dependency order and cycle capacity without breaking rank. A feature too big for one cycle is split into two numbered stories, A and B, across two cycles; a feature that fits one cycle gets no stories.

## What does it do?

It accepts:
- The prioritized backlog from `L1-planning-backlog-prioritizer` (rank, effort, dependencies, epic-not-ready flags, optional tiers)
- The number of cycles in the PI (`cadence.pi_cycles`, including the reserved Cycle 0)

It produces `cycle_plan.json` with:
- **Feature assignments**, one per planned feature: cycle ID and number, end cycle ID and number, effort, `is_split`, and `stories` (numbered US-001… with part A/B, cycle and effort) or `[]`
- **Gaps** with questions for the RTE or Product Lead
- **Summary table** at the end (`summary_table`): one row per feature with rank, name, effort, cycle(s), split, stories, dependencies and MVP, plus a total row

## How does it work?

1. Validates inputs; fails with INSUFFICIENT_CONTEXT if the backlog is empty or `pi_cycles` is missing.
2. Leaves out features that are epic-not-ready, depend on an unplanned or unknown feature, or are larger than two cycles.
3. Places a feature that fits one cycle into the earliest cycle (C-01 onward) after its dependencies with capacity left; stories `[]`.
4. Splits a feature larger than one cycle into Story A (half the effort, rounded up) and Story B (the rest), placing B in a later cycle than A. If B cannot fit in the PI, the whole feature is left out, never Story A alone.
5. Numbers stories US-001, US-002 … across the PI and returns the assignments plus an execution summary.

## Input

- **Source:** agent output (`L1-planning-backlog-prioritizer`), direct input, or file upload (.json, .md)
- **Required:** `prioritized_backlog` — prioritizer AgentOutput
- **Required:** `cadence.pi_cycles` — total cycles including Cycle 0
- **Optional:** `cycle_capacity_effort` — effort per 5-day cycle (default 8)
- **Optional:** `mvp_feature_ids` — MVP scope for `is_mvp`; falls back to tier MVP/Foundational

## Output

- **Type:** `cycle_plan` (schema_version 3.1)
- **Items:** `feature_assignments`, `gaps` — features that cannot be planned are left out entirely
- **Metadata:** confidence, reasoning summary (≤ 150 chars) and citation on every assignment
- **Summary table:** markdown, last key in `content`
- **Summary:** counts, split decisions, reflection fixes, KBs, guardrails, gaps

Example assignment (split feature):

```json
{
  "feature_id": "F-03.3", "name": "Payout ledger and balance calculation", "rank": 3, "effort": 11,
  "cycle_id": "C-03", "cycle_number": 3, "end_cycle_id": "C-04", "end_cycle_number": 4,
  "is_split": true,
  "stories": [
    { "story_id": "US-001", "story_number": 1, "part": "A", "cycle_id": "C-03", "cycle_number": 3, "effort": 6, "depends_on_story_ids": [] },
    { "story_id": "US-002", "story_number": 2, "part": "B", "cycle_id": "C-04", "cycle_number": 4, "effort": 5, "depends_on_story_ids": ["US-001"] }
  ],
  "depends_on_feature_ids": ["F-03.1"], "is_mvp": true, "confidence": 0.8,
  "summary": "Rank 3 → split C-03–C-04: effort 11 > 8; after F-03.1; C-02 has no room, A slipped to C-03.",
  "citation": { "source_reference": "prioritized_backlog", "source_location": "prioritized_features[rank=3] F-03.3" }
}
```

A feature that fits one cycle has `"is_split": false`, `"stories": []` and `end_cycle_id` equal to `cycle_id`.

Example `summary_table` (rendered):

| Rank | Feature | Name | Effort | Cycle(s) | Split | Stories | Depends on | MVP |
|---|---|---|---|---|---|---|---|---|
| 1 | F-03.1 | Merchant onboarding and bank account verification | 5 | C-01 | No | — | — | Yes |
| 2 | F-03.2 | Payout scheduling (daily and weekly) | 3 | C-02 | No | — | F-03.1 | Yes |
| 3 | F-03.3 | Payout ledger and balance calculation | 11 | C-03 → C-04 | Yes | US-001 A (C-03, 6) · US-002 B (C-04, 5) | F-03.1 | Yes |
| 4 | F-03.4 | Bank file generation (ISO 20022 and NACHA) | 6 | C-05 | No | — | F-03.2, F-03.3 | Yes |
| 5 | F-03.5 | Payout status notifications | 2 | C-06 | No | — | F-03.4 | Yes |
| 6 | F-03.6 | Fee and FX deduction | 5 | C-06 | No | — | F-03.3 | No |
| 7 | F-03.7 | Reconciliation dashboard | 6 | C-07 | No | — | F-03.4 | No |
| | **Total** | 7 features | 38 | | 1 split | 2 stories | | |

## Changes in v3.1.0

- Added `content.summary_table`, a markdown table at the end of the output restating every assignment, with a total row.

## Changes in v3.0.0 (breaking)

- Output reduced to `feature_assignments` and `gaps`; features that cannot be planned are left out (no unplanned list).
- Added `cycle_number` / `end_cycle_number`; stories are numbered `US-001…` with `story_number`.
- Removed `pi`, `cycles`, `mvp_cut_line`, `integration_bands`, the `cycle-plan.md` artifact and `tool-L1-azure-blob-writer`; removed input `integration_band_size_cycles`.

## Composition

```
agents/L1-planning-feature-cycle-mapper/
├── spec.yaml
├── evaluation.md
├── output_schema.json
├── README.md
├── examples/
│   ├── input-01-kyc-onboarding.json
│   ├── output-01-kyc-onboarding.json
│   ├── input-02-empty-backlog.json
│   ├── output-02-empty-backlog.json
│   ├── input-03-loan-origination.json
│   └── output-03-loan-origination.json
└── golden/v3.1.0/
    ├── input-golden-01-merchant-payouts.json
    ├── golden-01-merchant-payouts.json
    ├── input-golden-02-missing-cadence.json
    └── golden-02-missing-cadence.json

prompts/L1-planning-feature-cycle-mapper/
└── instructions.md
```
