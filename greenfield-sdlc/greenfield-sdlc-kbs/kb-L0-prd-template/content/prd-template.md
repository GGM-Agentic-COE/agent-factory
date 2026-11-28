<!--
kb-L0-prd-template · content · prd-template.md
Layer: L0 (enterprise-wide, cross-phase — NOT domain-specific).
The literal document template L0-prd-composer fills to produce
{product_name}-prd.md. Headings, callouts, tables and the *shall* voice are
kept exactly; every {placeholder} is replaced; table rows repeat as needed.
Rules for filling each section live in the agent prompt, not here.
-->

# Product Requirements Document Template

Fill as `{product_name}-prd.md`. Keep headings, callouts, tables and the *shall* voice exactly; replace every `{placeholder}`; repeat table rows as needed.

# {product_name} Product Requirements
**{product_name} · Product Management** · Status: **Draft**
*Functional, non-functional, data and compliance requirements for the {product_name} {release names} releases*
## 1. Purpose and Scope
> **PURPOSE**
>
> {What this document sets out for {product_name}: **what the product must do, for whom, and in which release**, **how well it must do it**, **what data it collects and from where**, and **which regulatory obligations each requirement satisfies**. State that every requirement has a stable key and acceptance criteria so design, build and test trace back to it, and that it states what is required, not how it is built.}

> **KEY REQUIREMENTS ASSUMPTION**
>
> {The operating model the requirements are written for, why the first release must already meet every legal obligation, and what is added if the operating model is decided otherwise (cite the `OR-NN` or `OQ-NN` that holds it).}
### What this document covers
#### In scope
- {**Users, roles and key journeys.**} · {**Release plan** and scope boundaries.} · {**{N} functional requirements** with acceptance criteria.} · {**Non-functional, data and integration requirements.**} · {**Compliance mapping**, success metrics, risks and open questions.}
#### Not attempted here
- {**Solution design**: architecture, technology and data models.} · {**User-interface design** and wireframes.} · {**Quantitative metric targets**, if not yet set.} · {obligations pending a decision, citing its key}
> **READING THIS DOCUMENT**
>
> {One phrase per section stating what it holds.} Requirements are keyed `FR-` and `NFR-`; regulatory obligations `CON-`; metrics `NSM-` and `LI-`; risks `OR-`; open questions `OQ-` and `NQ-`.
---
## Document Control and Contents
*Identity, ownership and approval of this document, and how it is organised*
| Attribute | Value |
|---|---|
| **Document ID** | {document_code}-PRD-001 · version {n.n} |
| **Document type** | Product requirements |
| **Product** | {product_name} |
| **Owner** | Product Owner, {product_name} |
| **Approver** | *Human Name* |
| **Date of approval** | *Date* |
| **Approval comments** | *Comments* |
| **Source 1** | Functional requirements: `L0-requirements-elicitor-evaluator`, Date: *Insert Date* |
| **Source 2** | Non-functional requirements: `L0-nfr-classifier-evaluator`, Date: *Insert Date* |
| **Source 3** | {product_name}-vision.md, {optional_confluence_link or "link NA"}, Date: *Provided by Human* |
| **Change control** | A requirement is added, changed or withdrawn only with the owner's approval; its key is never reused |
| **Classification** | Internal |
### Approvals
| Role | Responsibility | Signature | Date |
|---|---|---|---|
| ***Human Name*** | Approver |   |   |
| **Product Owner** | Owner of the requirements |   |   |
| {reviewer roles; default Engineering Lead, Quality Engineering Lead, Legal and Compliance, Data Protection Officer where personal data is processed} | {responsibility} |   |   |
### How to read the tags
> **{release 1 tag}** {meaning}. **{release 2 tag}** {meaning}. **Proposed** a requirement or role added to close a gap; it needs the owner's agreement. **To be set** a target that has no agreed value yet. Priority is **High**, **Medium** or **Low** within its release.
### Contents
{Linked list of sections 1 to 12, Document Control and Contents, Appendix A and Appendix B}
---
## 2. Product Overview
*What {product_name} is, the problem it solves, and what the requirements must achieve*
> **THE PRODUCT**
>
> {One paragraph: what {product_name} does, from what inputs, and whom it serves with which need. Written last; nothing new introduced.}
### Problem
{The problem statement in {product_name}-vision.md's own terms.}
### Product goals
| Goal | Statement | Capability | Measured by |
|---|---|---|---|
| **G-{NN}** | {goal} | `CAP-{NN}` {capability} | {`NSM-NN`, `NFR-NN` or Section reference} |
> **WHAT THIS MEANS FOR THE REQUIREMENTS**
>
> {What the first release must contain, what later releases add, and what is never deferred.}
---
## 3. Users and Roles
*Who uses {product_name}, and what each role may see and do*
| Role | Who | Primary need | Channel |
|---|---|---|---|
| **{role}** | {who} | {need} | {channel, or "To be set" (`OQ-NN`)} |
{Note any roles or channels tagged **Proposed** and why.}
### Permissions
| Capability | {role 1} | {role 2} | {role n} |
|---|---|---|---|
| **{capability}** | {Own / All / Read / Yes / Propose / Approve / —} | {…} | {…} |
---
## 4. Release Plan and Scope
*What each release contains, and what {product_name} will not do*
```mermaid
{flowchart LR: one box per release aligned to the roadmap phases, each listing its FR ranges}
```
***FIGURE 1** · Release plan, aligned to the roadmap phases.*
#### {Release 1}
*{N} requirements*
{FR keys and ranges.}
{One or two lines on how this release is delivered and to whom.}
#### {Release 2}
*{N} requirements*
{FR keys and ranges.}
{One or two lines on what this release opens up.}
### Out of scope
| Item | Reason |
|---|---|
| **{item}** | {why excluded, citing "{product_name}-vision.md § {section}", roadmap phase, or `OR-NN` / `OQ-NN`} |
---
## 5. Key User Journeys
*The journeys the requirements must support end to end*
```mermaid
{flowchart LR: one lane per key journey; each step labelled with the FR keys that carry it}
```
***FIGURE 2** · Key user journeys and the requirements that carry each step.*
---
## 6. Functional Requirements
*What {product_name} shall do, each with its release, priority and acceptance criteria* · Keys: `FR`
{product_name} has {N} functional requirements: {n} in the {release 1} and {n} in the {release 2}. Priority is shown under each requirement.
| Key | Requirement | Release | Acceptance criteria |
|---|---|---|---|
| **FR-{NNN}** | **{Title.}** {statement, verbatim}<br>*Source:* {citation, verbatim}<br>{Priority} {**Proposed** when tagged} | **{release}** | • {criterion}<br>• {criterion} |
### Compound requirements split
| Source clause | Split into |
|---|---|
| {source clause, verbatim} | {FR keys} |
---
## 7. Non-Functional Requirements
*How well the product must perform, and the targets still to be set* · Keys: `NFR`
### Agreed requirements
| Key | Category | Requirement | Applies to | Release |
|---|---|---|---|---|
| **NFR-{NN}** | {category} | {boundary condition, verbatim} | `FR-{NNN}` | {release} |
### Targets to be set
| Key | Question | Applies to | Needed by |
|---|---|---|---|
| **NQ-{NN}** | {the TBD boundary condition, phrased as the question to answer} | `FR-{NNN}` | {design milestone or roadmap phase} |
---
## 8. Data and Integration Requirements
*The information {product_name} manages, where it comes from, and which personal data it holds*
```mermaid
{flowchart LR: data sources → records → outputs}
```
***FIGURE 3** · Data sources, records and outputs.*
### Business entities
| Entity | Meaning | Created by |
|---|---|---|
| **{entity}** | {meaning} | `FR-{NNN}` |
### Personal data inventory
| Data | Data principal | Purpose | Retention |
|---|---|---|---|
| **{data}** | {data principal} | {purpose} | {period, or **To be set** `OQ-NN`} |
{How records required by law relate to personal-data retention, where they conflict.}
---
## 9. Regulatory and Compliance Mapping
*Each obligation, and the requirements that satisfy it* · Keys: `CON`
| Key | Obligation | Satisfied by | Release | Note |
|---|---|---|---|---|
| **CON-{NN}** | {obligation} | {FR and NFR keys, or —} | {release, or —} | {note; conditional obligations cite the `OR-NN` that decides them} |
> **CONFIRMATION REQUIRED**
>
> {Which statutory limits and section references must be confirmed by legal counsel, and before which milestone.}
---
## 10. Success Metrics
*How the requirements produce the evidence that {product_name} works* · Keys: `NSM` · `LI`
| Key | Metric | Produced by | Target |
|---|---|---|---|
| **{NSM-NN / LI-NN}** | {metric, from {product_name}-vision.md} | {FR keys} | {target, or **To be set** with when} |
{Where each baseline comes from, and which metrics can only be baselined once the product runs.}
---
## 11. Assumptions, Dependencies and Risks
*What the requirements take for granted, rely on, and could be undermined by*
### Assumptions
| Key | Assumption | Underlies |
|---|---|---|
| **AS-{NN}** | {assumption} | {FR keys, or "program-level"} |
### Dependencies
| Key | Dependency | Needed for |
|---|---|---|
| **DP-{NN}** | {dependency} | {release} |
### Risks
| Key | Risk | Severity | Requirements affected | Response |
|---|---|---|---|---|
| **OR-{NN}** | {risk} | **{High / Amber / Low}** | {FR keys, or "Programme"} | {response} |
---
## 12. Open Questions and Approval
*What must still be decided, and what approval of this document means*
| Key | Question | Needed by |
|---|---|---|
| **OQ-{NN}** | {question, or **Coverage gap:** what is missing and why composing surfaced it} | {milestone} |
#### Requirement positions
- {one line per position the requirements take}
#### Approval of this document means
- {Release 1 scope (Section 4) is agreed for design.} · {Proposed requirements and roles are accepted, or explicitly rejected.} · {Targets marked *to be set* are owned and scheduled.} · {Legal confirmation (Section 9) is commissioned before build.}
> **BOTTOM-LINE POSITION**
>
> {What the first release must do and be from its first day, and what waits until it has proven itself.}
---
## Appendix A. Traceability Matrix
*Every functional requirement with its release, priority, quality attributes and obligations*
| FR | Release | Priority | Quality attributes | Obligations · metrics | Targets to be set |
|---|---|---|---|---|---|
| **FR-{NNN}** | {release} | {priority} | {NFR categories, or "None"} | {`CON-NN` · `NSM-NN` / `LI-NN`, or —} | {count of `NQ` rows for this FR, or 0} |
---
## Appendix B. Glossary
*Terms and abbreviations used in this document*
| Term | Meaning |
|---|---|
| **{term}** | {meaning, grounded in how {product_name}-vision.md or the requirements use it} |
