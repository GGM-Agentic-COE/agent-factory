# Schreiber Foods Inc. — Jira Feature Decomposition Best Practices & Standard Operating Procedure (SOP)

**Document Owner:** Agile Program Management Office (PMO) / Enterprise Solutions Architecture
**Applies To:** All Product, Engineering, QA, and IT Delivery Teams
**Status:** Approved — Mandatory Standard
**Version:** 1.1 (adds §2.5 Foundational vs. Incremental MVP Classification)
**Related Source Document:** Schreiber Foods Jira Epic Best Practices & SOP (kb-epics-best-practices)

---

## 1. Purpose of a Schreiber Foods Feature

A Feature sits between an Epic and its Stories. Where an Epic answers **What/Why** at business altitude, a Feature answers:

- **What independently shippable slice** of the Epic's capability is this?
- **How much** functionality does it cover (scope boundary), without yet specifying **How** it is built.

> **Guiding Principle:** A Feature must be demoable and deliver standalone value to at least one stakeholder group, even if the rest of the Epic's pillars are not yet built. If a Feature cannot stand on its own, it is too small and belongs at the Story level; if it bundles multiple independently-shippable slices, it is too large and should be split.

A Feature must **never** contain Story-level detail: no acceptance test scripts, no UI wireframes, no API/data-schema design, no sprint assignment or story points. That detail belongs downstream in Stories, Tasks, and technical design docs.

---

## 2. Input Filtering Rules — What to Extract From the Epic

When decomposing an approved Epic into Features, the agent must pull only from the Epic's own structured fields — never re-read the original PRD directly for new content not already reflected in the Epic.

### 2.1 Macro Feature Pillar → One or More Features

- Each `macro_feature_pillars` entry in the Epic decomposes into **1–4 Features**.
- Test for correct altitude: a Feature title should be **4–8 words**, more concrete than the pillar phrase but still describing a functional capability slice, not an implementation step (e.g., pillar "Automated Intake Lot Capture" → Feature "Barcode Scan Intake Capture at Receiving Dock").
- If a pillar is already a single, independently-shippable slice, it becomes exactly **1 Feature**.
- Never create one Feature per Story-level task — if a candidate "Feature" cannot be demoed independently, merge it into a sibling Feature or defer it to the Story layer.

### 2.2 Feature Description & Acceptance Criteria

- Each Feature carries a **2–4 sentence description**: what the feature does, who uses it, and what capability slice of the parent pillar it covers.
- Each Feature carries **3–6 high-level acceptance criteria bullets** — outcome-level statements (may use Given/When/Then phrasing), never full test scripts, edge-case enumerations, or QA test-case IDs.
- Acceptance criteria must be traceable to the Epic's pillar text, out-of-scope, constraints, or risks — never invented from general domain knowledge.

### 2.3 Out of Scope & Constraints Inheritance

- A Feature inherits only the Epic's Out of Scope / Constraints items that are **directly relevant** to that Feature's slice — do not copy the entire Epic list onto every Feature.
- If none of the Epic's Out of Scope/Constraints apply to a given Feature, the Feature's own `out_of_scope`/`constraints` arrays may be empty.

### 2.4 Traceability (mandatory)

- Every Feature must carry `parent_epic_id`, `source_pillar` (verbatim pillar text), and a `prd_reference` inherited from the parent Epic (same `file`, `file_path`, `sections`).
- This preserves the full chain: PRD → Epic → Feature → (downstream) Story.

### 2.5 Foundational vs. Incremental (MVP) Classification — mandatory

*(Addendum — codifies how a senior Product Manager would sequence a pillar's Features into a walking-skeleton MVP followed by incremental value.)*

Every Feature must be classified as exactly one of:

- **Foundational** — the Feature is part of the minimum "walking skeleton" required to prove the Epic's core capability end-to-end for at least one real scenario. Remove it, and the Epic cannot be meaningfully demoed at all.
- **Incremental** — the Feature adds coverage, robustness, secondary use cases, reporting, or convenience on top of an already-functional foundation. Remove it, and the Epic's core capability still works, just with reduced scope/polish/edge-case handling.

**Foundational Classification Test:** Ask, *"If every Incremental Feature in this Epic were deferred to a later release, could this Feature alone (plus other Foundational Features) still let a user complete the Epic's primary end-to-end scenario at least once?"* If yes, it is Foundational. If it only improves, extends, monitors, or reports on a scenario that already works without it, it is Incremental.

Structural signals (use alongside the test above, never as a substitute for it):

- A Feature with **zero Features depending on it** and that only enhances an existing capability (dashboards, secondary alerting, audit/reporting views, convenience workflows) is usually **Incremental**.
- A Feature that **other Features list as a dependency** (i.e., appears in one or more sibling `dependencies` arrays) is usually **Foundational** — the pillar's later slices cannot function without it.
- The first, most upstream slice of a pillar (e.g., raw data capture before any downstream processing/reporting on that data) is typically **Foundational**.
- Manual-override, exception-handling, and audit-trail-only Features are typically **Incremental** unless a Critical-Compliance risk (kb-epics-best-practices §4) makes them launch-blocking — in that case classify as **Foundational** and say so in the rationale.

**Mandatory consistency rule:** A **Foundational** Feature must never list a dependency on an **Incremental** Feature — a walking skeleton cannot depend on scope that is allowed to slip to a later release. If this occurs, either the dependency is wrong or the classification is wrong; resolve the contradiction before publishing.

Every Feature must carry:
- `mvp_classification`: `"Foundational"` or `"Incremental"`.
- `mvp_rationale`: 1–2 sentences applying the Foundational Classification Test and/or structural signals above to this specific Feature — never a generic restatement of the definition.

---

## 3. Exclusion Rules — What Is Strictly Forbidden in a Feature

| Content | Why It's Forbidden | Correct Destination |
|---|---|---|
| Full test scripts / test case IDs | Execution-level detail, changes constantly, no strategic value at Feature altitude | Story-level acceptance criteria / test management tool |
| UI wireframes / mockups | Design-execution artifact | Story or design doc, linked not embedded |
| API contracts, data schemas, code-level design | Implementation detail | Technical design doc / Story |
| Sprint assignment, story points, delivery dates | Delivery-planning detail, not part of Feature definition | Sprint planning / Story fields |
| Content not traceable to the parent Epic's pillar, out-of-scope, constraints, or risks | Introduces ungrounded/hallucinated scope | Removed; flagged as a gap if genuinely needed |

---

## 4. Feature-to-Story Handoff Note (informational only)

Features are the seed for a downstream Story-generation process. Each Feature typically becomes 1 or more Stories, but this agent does **not** generate Stories — that decomposition is out of scope and handled by a separate downstream agent.

---

## 5. Writing & Formatting Standards

### 5.1 Feature ID Format

- `F-{epic-number}.{sequence}` — e.g., `F-01.1`, `F-01.2`, `F-02.1`. The epic number matches the parent `epic_id` (EP-01 → 01). Sequence is per-epic, starting at 1.

### 5.2 Naming Convention

- Feature titles: **4–8 words**, Title Case, concrete-but-not-technical.
- ✅ Good: "Barcode Scan Intake Capture at Receiving Dock", "SAP Batch Status Push to MES Dashboard"
- ❌ Avoid: "Implement REST endpoint for lot scan" (implementation-level), "Feature 1" (non-descriptive)

### 5.3 General Formatting Rules

- No paragraphs longer than 2 sentences in `description`.
- Acceptance criteria are bullets, not paragraphs.
- No nested bullets deeper than one level.
- No embedded diagrams, wireframes, or tables — link externally if truly necessary.

---

## 6. Quick-Reference Compliance Checklist

Before publishing any Feature set, confirm:

- [ ] Each pillar decomposed into 1–4 Features (never 1 Feature per Story-level task)
- [ ] Feature titles are 4–8 words, concrete capability slices, not implementation steps
- [ ] Each Feature has a 2–4 sentence description and 3–6 high-level acceptance criteria bullets
- [ ] No test scripts, UI wireframes, API/schema design, or sprint/story-point detail appears in any Feature
- [ ] Out of Scope/Constraints are inherited only where directly relevant, not blanket-copied
- [ ] Every Feature carries `parent_epic_id`, `source_pillar`, and a populated `prd_reference`
- [ ] Feature IDs follow `F-{epic-number}.{sequence}` and are sequential per epic
- [ ] No content appears that isn't traceable back to the parent Epic
- [ ] Every Feature carries `mvp_classification` (Foundational or Incremental) with a specific `mvp_rationale`, correctly applying the Foundational Classification Test (§2.5)
- [ ] No Foundational Feature depends on an Incremental Feature

---

*This SOP is maintained by the Schreiber Foods Agile PMO. Deviations require sign-off from the Enterprise Solutions Architecture team.*

## Revision History

| Version | Change | Note |
|---|---|---|
| 1.1 | Added §2.5 "Foundational vs. Incremental (MVP) Classification" and matching §6 checklist items | Codifies senior-PM-style walking-skeleton-first sequencing; mandates `mvp_classification`/`mvp_rationale` per Feature |
| 1.0 | Original Feature Decomposition SOP | Sections 1–6, modeled on kb-epics-best-practices v1.1 |
