# L1-confluence-publisher

## Purpose

This is the exact split `agent-standards-best-practices.html`'s anti-pattern
calls out: *"The Vision Generator writes its output directly to a
Confluence page... this couples the agent to a platform."* Publishing is
pulled out into its own Utility agent so that swapping Confluence for
Notion touches this one agent, not every Core generator that happens to
produce a document — today `L1-vision-statement-generator`, later any
Phase 4 design-doc agent too.

## What does it do?

Accepts a document artifact from an upstream Core agent and:
- Publishes it to Confluence, verbatim — no summarizing, reformatting, or editing
- Creates a new page by default; only updates an existing page if `update: true`
  was explicitly passed — never overwrites by guessing intent from a similar title
- Reports whether the result was a create or an update

It holds zero domain logic — it doesn't judge, score, or alter what it's given.

## How does it work?

1. Ingests the artifact (name, format, content) and target space
2. If `target_page_id` is absent: creates a new page
3. If `target_page_id` is present: requires `update: true` explicitly, or refuses
4. Calls `tool-L1-confluence-create-page` and reports the actual result —
   never assumes success
5. Self-checks that content was published faithfully and no unintended
   overwrite occurred

## Input

- **Source:** agent_output (artifact) from any Core agent producing a document
- **Required:** `artifact`, `target_space`
- **Optional:** `target_page_id`, `update` (must be explicitly `true` to overwrite)

## Output

- **Type:** `publish_result`
- **Items:** `published_page` (url, space, title, published_at, action),
  `source_artifact_id` — see `output_schema.json`
- **Summary:** what was published, where, created vs. updated, tool outcome

## Composition

```
agents/L1-confluence-publisher/
├── spec.yaml
├── evaluation.md
├── output_schema.json
├── README.md
├── examples/
│   ├── input-01-create-new-page.json
│   ├── output-01-create-new-page.json
│   ├── input-02-refused-overwrite.json
│   └── output-02-refused-overwrite.json
└── golden/v1.0.0/
    ├── input-golden-01-harvestlink-vision.json
    ├── golden-01-harvestlink-vision.json
    ├── input-golden-02-explicit-update.json
    └── golden-02-explicit-update.json

prompts/L1-confluence-publisher/
└── instructions.md
```
