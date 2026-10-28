---
name: knowledge-base-creator
description: Standard structure, patterns, and conventions for creating knowledge bases in the Agent Factory. Use this whenever asked to create a new KB — apply this exact structure, naming, content format, and spec pattern.
trigger: When the user asks to create a knowledge base, KB, domain knowledge, standards document, or scaffold reference that agents will consume at runtime.
---

# Knowledge Base Creator Skill

## Naming Convention

```
kb-L{layer}-{scope}
```

- `kb-` prefix always
- `L1` = Enterprise standards (technology, architecture, coding, testing, agent platform standards)
- `L2` = Domain/LOB (domain-specific business rules, regulations, terminology)
- `L3` = Project/Initiative (project baselines, ADRs, API contracts)
- `L4` = Squad/Local (team conventions, repo structure)
- `{scope}` = kebab-case description of what the KB covers

**Reference:** See `01-agent-development-naming-standard.html` for the full naming guide.

Patterns per layer:
- L1: `kb-L1-{scope}`
- L2: `kb-L2-{domain}-{scope}`
- L3: `kb-L3-{project}-{scope}`
- L4: `kb-L4-{squad}-{scope}`

Examples:
- `kb-L1-golang-api-standards`
- `kb-L1-enterprise-architecture`
- `kb-L2-payments-domain-model`
- `kb-L2-early-childhood-education-domain`
- `kb-L3-kyc-api-contracts`
- `kb-L3-application-baseline`
- `kb-L4-squad-alpha-conventions`

## Folder Structure

```
knowledge-bases/{kb-name}/
├── spec.yaml                       # KB specification (purpose, consumers, visibility)
├── README.md                       # What the KB covers, how to use it, who it's for
└── content/
    └── {kb-name}.md                # KB content (structured markdown)
```

Optional:
- `content/{kb-name}.pdf` — PDF version for reference/print
- Multiple `.md` files for very large KBs (split by section)

## README.md Template

```markdown
# {kb-name}

## Purpose

{What this KB provides and why it exists}

## Who uses it?

{List of agents/roles that consume this KB at runtime}

## What does it cover?

{Bullet list of sections/topics covered}

## How to use

- Attached automatically to agents listed in spec.yaml consumers
- Agents ground their output in this KB's rules and data
- Sections are retrieved independently (chunked by section header)

## Maintenance

- Owner: {owner}
- Review cadence: {quarterly/monthly}
- Last reviewed: {date}
- To update: edit content/{kb-name}.md, bump version in spec.yaml and header
```

## spec.yaml Template

```yaml
spec_version: "1.0"
artifact_type: knowledge_base
metadata:
  name: {kb-name}
  version: "1.0.0"
  layer: L{n}
  owner: {owner}
  last_reviewed: "{date}"
  review_cadence: quarterly

purpose:
  description: "{What this KB provides in one sentence}"

content:
  format: markdown
  documents:
    - path: content/{kb-name}.md
      sections: [{section-1}, {section-2}, ...]

  total_tokens_estimate: {estimate}
  chunking: by-section
  embedding_model: text-embedding-3-small

consumers:
  agents:
    - {agent-1}
    - {agent-2}
  usage: "{How agents use this KB}"

visibility:
  accessible_by: [L{n}, L{n+1}, ...]
  rule: "{Who can access and why}"
```

## Content Format (Markdown)

### Header (mandatory)

```markdown
# {Title} — Knowledge Base
### {kb-name} v{version}
### {One sentence describing what this KB is for and who must follow it}

---
```

### Section Pattern

```markdown
## {CODE}{NUMBER}: {Section Title}

### {Subsection}
- Prescriptive rules using MUST/MUST NOT/SHOULD language
- Tables for structured data
- Code blocks for patterns/examples
- Clear validation criteria

---
```

### Section Numbering by KB Type

| KB Type | Section Prefix | Example |
|---------|---------------|---------|
| Quality Standards | B1, B2, B3... | B1: Grounding Enforcement |
| Coding Standards | CS1, CS2... or GO1, GO2... | GO1: Technology Stack |
| Domain Knowledge | PD1, PD2... or EC1, EC2... | EC1: Childcare Lifecycle |
| Enterprise Architecture | EA1, EA2... | EA1: Technology Stack |
| Evaluation Standards | E1, E2... | E1: Epic Rules |
| Scaffold | SCAFFOLD1, SCAFFOLD2... | SCAFFOLD1: Makefile |

## Content Types & What They Must Include

### Technology Standards KB (L1)
1. Technology stack table (component, technology, version, notes)
2. Project/solution structure (directory tree)
3. Naming conventions table
4. Code patterns with full examples (handler, service, repository)
5. Error handling pattern
6. Testing standards (with table-driven test example)
7. Configuration pattern (environment-based)
8. Security standards
9. Observability (logging, tracing, metrics)

### Scaffold KB (L1)
1. Makefile
2. Dockerfile (multi-stage)
3. Main entry point (full code)
4. Configuration struct
5. Error/response helpers
6. Module/dependency list
7. Linter configuration
8. Database migration template

### Domain KB (L2)
1. Domain lifecycle (customer journey + operator/business journey)
2. Key entities & data model (tables with field/type/validation/regulatory basis)
3. Regulatory framework (regulations, requirements, system impact)
4. Financial/fee structure (if applicable)
5. Business rules (enrolment, calculation, notification rules)
6. Integration landscape (external + internal systems)
7. User personas (with counts, needs, pain points)
8. State machine / workflow (if the domain has states)
9. Terminology glossary
10. Compliance rules (what system MUST enforce)

### Enterprise Architecture KB (L1)
1. Organisation overview
2. Technology stack (full table)
3. Core application details (users, stats, SLAs)
4. Architecture patterns
5. Service domains
6. Support model & SLAs
7. Quality standards
8. Security & compliance
9. Infrastructure scale
10. Challenges & technical debt
11. Future roadmap
12. Operating model

### Evaluation KB (per agent)
1. Quality gates (checklist: `- [ ]` format, not verbose tables)
2. Scores table (Evaluator | ≥ threshold | What it checks)
3. Reflection checklist (checkboxes only)
4. Reflection process (single line: Generate → Check → Fix → Deliver)
5. Total ≤ 50 lines — no verbose rubric descriptions or writing rules (those belong in prompt Don'ts)

## Key Rules

1. **Prescriptive language** — Use MUST/MUST NOT/SHOULD for rules agents must follow. Not "consider" or "you might want to".
2. **Tables over prose** — Structured data in tables, not paragraphs. Agents parse tables more reliably.
3. **Code examples are complete** — Show full working patterns, not fragments. Agent will copy the pattern.
4. **Section independence** — Each section should be understandable on its own (chunked retrieval may return one section).
5. **Regulatory references** — Always cite the specific regulation/act/section (not just "comply with regulations").
6. **Version in header** — KB version in the markdown header, updated when content changes.
7. **No stale data** — Review cadence in spec. Content must reflect current state.
8. **Domain language** — Use the terminology the domain uses. Include a glossary section for non-obvious terms.
9. **Validation rules explicit** — For data models, include type, format, constraints, and regulatory basis per field.
10. **Token estimate in spec** — Helps agents/platforms manage context window budget.

## Token Optimisation for Knowledge Bases

### Target Budgets
| KB Type | Target Tokens | Rationale |
|---------|--------------|-----------|
| Evaluation KB | ≤ 500 | Checklist only — no prose |
| Template KB | ≤ 1,200 | Structural headings — consider embedding in prompt (S4) |
| Domain KB (condensed) | ≤ 8,000 | PM implications + journeys + glossary — for vision/inception agents |
| Domain KB (full) | ≤ 25,000 | Full field-level detail — for LLD/code agents |
| Enterprise Architecture KB | ≤ 15,000 | System landscape, patterns, standards |

### Create Condensed Variants (S3)
For domain KBs consumed by inception-phase agents (vision, requirements, epics):
- **Keep:** PM implications, user journeys (full), state machines (full), glossary, section headings
- **Remove:** Field-level data models, validation regex, implementation guidance, regulatory full-text
- **Naming — do NOT bake the tier into the KB's own id/name.** If only one
  tier exists (the common case — most domains only ever need the
  inception-phase cut), it IS the KB: `kb-L2-{domain}`, no suffix. A KB's
  name should describe what domain it covers, not how big it currently is.
- If a full/detailed variant is later added alongside it for later-phase
  agents (LLD/code), the FULL one gets the distinguishing suffix instead
  — `kb-L2-{domain}-full` or `kb-L2-{domain}-detailed` — since the
  condensed cut stays the default most agents consume. Never `-slim`,
  `-lite`, `-mini`, or similar on the default/primary variant.
- Spec should list both variants with consumer mapping when both exist

### When to Embed in Prompt (S4)
If KB is ≤ 3,000 tokens AND is structural (headings + placeholder guidance):
- Embed directly in the agent prompt as "Output Document Structure"
- Eliminates a separate KB load entirely
- Applicable to: template KBs, small evaluation KBs

### Two-Phase Consumption (S5)
When a KB > 2,000 words is attached:
- Agent Phase 1: extract only relevant facts into internal brief
- Agent Phase 2: generate from brief (KB no longer needed in active attention)
- Prevents "lost in the middle" problem with large KBs

### Measuring Token Size
- Rule of thumb: 1 token ≈ 4 characters of English text
- Add `total_tokens_estimate` to spec.yaml (chars / 4)
- Red flag: if KB > 50% of target model's context window, slimming is mandatory

## Layering & Visibility

| Layer | Scope | Owned By | Accessible By |
|-------|-------|----------|---------------|
| L1 | Enterprise (any domain, platform standards) | Agentic-AI CoE | All layers |
| L2 | Domain-specific | Domain AI Champion | L2, L3, L4 |
| L3 | Project-specific | Project Lead | L3, L4 |
| L4 | Squad-specific | Squad | L4 only |

An L4 agent sees: L1 + L2 + L3 + L4 KBs (all layers at or above).

## Quality Checklist Before Publishing

- [ ] Header includes KB name, version, and one-sentence purpose
- [ ] All sections have numbered codes (GO1, EC1, EA1, etc.)
- [ ] Tables used for structured data (not buried in prose)
- [ ] Code examples are complete and copy-pasteable
- [ ] Regulatory references cite specific acts/sections
- [ ] Terminology glossary included for domain KBs
- [ ] spec.yaml has consumers, visibility, and token estimate
- [ ] Content validates against what agents actually need (not just what humans read)
- [ ] No placeholder or TODO content — every section is complete
- [ ] Tested: can an agent ground a decision using only this KB?
