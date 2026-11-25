# Test Scenario Writer – Best Practices KB

Used by: L0-test-scenario-writer (to write) and L0-testing-scenario-evaluator (to check).
This KB explains HOW to write good scenarios. The agent's instructions.md defines the inputs, steps, template and output.

---

## 1. What a Test Scenario Is
- A scenario says WHAT business behaviour must be tested. It does not say how.
- One scenario = one distinct behaviour stated in one Feature AC.
- Positive, negative, boundary and alternate paths belong to the Test Case Writer, not here.

---

## 2. Source Authority

| Source | May be used for | Must never be used for |
|---|---|---|
| Epic | Scope, business terms, actors, Feature grouping | Creating scenarios, expected results, filling AC gaps, SourceIssueId |
| Feature (description, dependencies, constraints, out of scope, risks, MVP fields) | Feature context, explicit relationships, wording boundaries | Creating scenarios or expected results |
| Feature AC | The ONLY source of expected behaviour | — |
| Test Strategy | Test Levels table, Functional acceptance levels, TP-04 | Behaviour |

**Conflict rule:** if any context disagrees with a Feature AC, the Feature AC wins.

---

## 3. Finding Valid Features
A child of the Epic is a Feature only if the returned Jira data clearly shows Feature identity, such as a Feature ID, Parent Epic, Feature description, ACs or equivalent metadata.

Ignore these:
- Items that only appear in `child_work_item_ids` or `children` with no Feature identity
- Existing Test Scenario Tasks and other generated artifacts
- Arbitrary, malformed or unrelated Tasks

---

## 4. Reading ACs
- Take ACs from the AC field, or from the description's ACCEPTANCE CRITERIA section if there's no AC field.
- Keep explicit AC IDs exactly as written (e.g. `AC-F-01.7-01`). If an AC has no ID, assign `AC-01`, `AC-02`… in source order.
- Never reorder, merge, split or reword an AC.
- `(SourceIssueId, acceptance_criteria_id)` is the unique AC reference, because AC IDs can repeat across Features.

---

## 5. How Many Scenarios
- Every AC with an observable outcome gets at least one scenario.
- Add another scenario for the same AC only when the AC states two or more distinct behaviours that one scenario can't describe accurately.
- If the AC states a rejection, error or prohibited action, write that as the scenario. Don't add a positive or negative counterpart unless the AC states it.
- An AC with no observable outcome gets no scenario.
- MVP class (Foundational or Incremental) does not change coverage.
- No near-duplicates: two scenarios must not test the same AC behaviour.

---

## 6. Choosing `testing_level` (TP-04)
Pick exactly one level, written exactly as in the Test Strategy's allowed Functional acceptance levels: the lowest level that can prove the behaviour.

| What the AC describes | Level |
|---|---|
| One business rule or one service behaviour | Lowest allowed level |
| An explicit hand-off across services, events, Features or systems | Integration level, if allowed |
| A user journey through a UI | End-to-end level, if allowed |
| Not enough information | Lowest allowed level |

- Explicit Feature dependencies can support the choice.
- Never choose Integration or End-to-end just because Features share an Epic, share a pillar, sit next to each other or sound related.

---

## 7. Choosing the Level Label
The level label is separate from `testing_level`. Never derive one from the other.

| Label | When |
|---|---|
| `level-feature` | The source issue type is Feature and the AC tests that Feature's own behaviour |
| `level-task` | The source issue type is Task |
| `level-api` | The source is a Feature AND the AC describes a hand-off between two named components (see Section 9) |

Reserved for other agents: `level-e2e`, `level-nfr`.

---

## 8. Writing Each Field

### Summary
Pattern: `[TS-XXX] Verify that [actor] can [action] to achieve [result]`
- Describe the AC's behaviour, nothing more.

### Pre-condition
- Only the system state stated in the AC.
- Add an actor role only if the AC, Feature or Epic states it.
- Never invent a precondition.

### Test Data
- Realistic mock values, enough to show the business case.
- Use placeholders: `[TRACE_RECORD_ID_003]`, `[REDACTED_EMAIL_ADDRESS_1]`, `{VALID_PASSWORD}`.
- No real PII, credentials or secrets. No new business rules hidden in the data.

### Navigable Path
- A business-level journey only.
- Use screen, app, workflow or actor names only if a source states them. Otherwise use generic business steps.
- No endpoints, HTTP methods, database tables or code components.

### Expected Result
- Only observable outcomes stated in the AC.
- Quote stated messages exactly.
- Never take expected results from Epic ACs, descriptions, dependencies, constraints, risks or MVP fields.

### Good vs Bad

| | Example |
|---|---|
| ✅ Good | Expected Result: "The record shows the supplier (one step back) and the buyer (one step forward)." — stated in the AC |
| ❌ Bad | Expected Result: "The record is returned within 2 seconds and is audit-logged." — not in the AC |
| ❌ Bad | Navigable Path: "Call GET /traceability/{id}" — technical detail |

---

## 9. API-Level Scenarios (`level-api`)

### When to use
Use `level-api` only when ALL of these are true:
1. The AC says one component sends, creates, updates or exposes data or an event.
2. Another component or external system receives or uses it.
3. Both components are named in the Feature, its ACs or the Test Strategy.
4. A system can check the result, not only a person looking at a screen.

### When NOT to use
- The AC only describes what a user sees → `level-feature`
- The hand-off is hinted at but a component isn't named → `level-feature`, and report that AC
- The Features share an Epic or sound related → not evidence

### Splitting one AC
If an AC describes both something a user sees and a hand-off, write two scenarios:
- one `level-feature` scenario for what the user sees
- one `level-api` scenario for the hand-off

### How to write it
- Keep it at business level, like every other scenario.
- Summary: `[TS-XXX] Verify that [provider component] [action] so that [consumer component] [result]`
- Add one extra description key, used for `level-api` only:
  `"Integration Point": "[provider] → [consumer]: [business data or event passed]"`
- Expected Result: what the receiving component holds or does after the hand-off, as stated in the AC.
- `SourceIssueId` stays the Feature key. The other labels don't change.

### Keep out (the Script Generator adds these later from the API spec)
Endpoints, URLs, HTTP methods, status codes, JSON field names, payloads, queues, tables, code names.

### Example (illustrative)

| | Integration Point |
|---|---|
| ✅ Good | "Trade Service → Traceability Service: finalised trade with supplier and buyer IDs" (both named in the AC) |
| ❌ Bad | "POST /trades → traceability_db.records" (technical) |
| ❌ Bad | "Trade Service → Reporting Service" (Reporting Service isn't named in any source) |

---

## 10. Common Mistakes
- Creating a scenario from the Epic, a description, a dependency or a risk
- Expanding one AC into positive and negative variants
- Treating every child item as a Feature
- Using the Epic key as `SourceIssueId`
- Choosing Integration or E2E because of Epic membership
- Putting technical API detail in any field
- Rewording an AC or making up messages, limits, roles or screens

---

## 11. Self-Check Before Writing to Blob Storage
- [ ] Every scenario traces to one `(SourceIssueId, acceptance_criteria_id)` pair
- [ ] Every observable AC has at least one scenario, with no near-duplicates
- [ ] Exactly one `testing_level`, chosen by TP-04
- [ ] All six labels are present, and `source-` matches the trace ID
- [ ] The level label follows Section 7, and every `level-api` scenario passes Section 9
- [ ] There's no invented or technical content in any field