<!--
kb-L1-requirements-quality-standard · content · requirements-quality-standard.md
Layer: L1 (enterprise, domain-agnostic). Consumed by: L1-requirements-elicitor
(mechanical checks only, self-check) and L1-requirements-elicitor-evaluator
(full rubric, source of truth). Micro-KB content rules apply: max 1
line/bullet, max 15 words, no explanations, numbers not words. This KB
describes HOW to judge requirement quality, not WHAT a specific
requirement should say — it never asserts domain content. Two of the seven
characteristics below (Feasible, Correct) are judgment questions, not
mechanically checkable — this KB gives the QUESTION to ask, never a
verdict to assert without evidence.
-->

# Requirements Quality Standard (Cross-Domain)

Grounded in ISO/IEC/IEEE 29148 requirement quality characteristics and
RFC 2119 obligation keywords — not an invented house style.

## The Seven Characteristics (ISO/IEC/IEEE 29148)
- Unambiguous → single interpretation, no reader could read it two ways (→ Characteristic: Unambiguous)
- Complete → every upstream need has at least one covering requirement (→ Characteristic: Complete)
- Singular (atomic) → one requirement states exactly one capability (→ Characteristic: Singular)
- Feasible → achievable within known technical/organisational constraints (→ Characteristic: Feasible)
- Verifiable → a pass/fail test can be written against it (→ Characteristic: Verifiable)
- Correct → accurately reflects the actual stakeholder need, not a guess (→ Characteristic: Correct)
- Traceable → uniquely identified, linked to its source and to what implements it (→ Characteristic: Traceable)

## Unambiguous — Deterministic Vague-Term Scan
- Flag unqualified: "fast", "user-friendly", "appropriate", "secure", "robust", "intuitive" (→ Characteristic: Unambiguous)
- A flagged term is fine ONLY if immediately followed by a measurable qualifier (→ Characteristic: Unambiguous)
- Form: "fast" alone fails; "returns results within {{grounded number}}ms" passes (→ Characteristic: Unambiguous)
- "shall"/"should"/"may" are RFC 2119 obligation levels, not interchangeable synonyms (→ Characteristic: Unambiguous)

## Complete — Coverage Check (Set Membership, Not a Count)
- Every upstream section (Problem, Value Proposition, Regulatory Posture item, Roadmap phase) needs ≥1 covering FR (→ Characteristic: Complete)
- Checked by set membership — an upstream item present in NO requirement is a gap, not a rounding error (→ Characteristic: Complete)
- A requirement with no upstream trace is the opposite defect: ungrounded, not incomplete (→ Characteristic: Complete)
- Missing coverage is a genuine finding — do not silently invent a requirement to fill it (→ Characteristic: Complete)

## Singular — Compound-Clause Scan
- Flag any statement joining two independently testable capabilities with "and"/"or" (→ Characteristic: Singular)
- Test: could a system satisfy one half without the other? If yes, split it (→ Characteristic: Singular)
- A split requirement keeps its own id and its own trace to the same source clause (→ Characteristic: Singular)

## Verifiable — Testability Check
- Ask: could a tester write ONE pass/fail test directly from this sentence? (→ Characteristic: Verifiable)
- A requirement describing an internal implementation choice, not an observable behaviour, fails this (→ Characteristic: Verifiable)
- Verifiable does NOT require a number — "the system shall reject an unauthenticated request" is verifiable with no number at all (→ Characteristic: Verifiable)

## Consistent — Cross-Requirement Contradiction Check
- Compare every pair of requirements touching the same entity/state for contradiction (→ Characteristic: Consistent)
- A contradiction is a defect in ONE of the two, or a missing precondition distinguishing them (→ Characteristic: Consistent)
- Terminology must match across requirements — the same concept must not have two different names (→ Characteristic: Consistent)

## Feasible — Judgment Question, Not a Mechanical Check
- Ask: is this achievable within the constraints already stated (regulatory, architectural, timeline)? (→ Characteristic: Feasible)
- This KB does not supply a feasibility verdict — that requires domain/architecture knowledge this KB doesn't have (→ Characteristic: Feasible)
- An infeasibility finding must cite the SPECIFIC constraint it conflicts with, not a general doubt (→ Characteristic: Feasible)

## Correct — Judgment Question, Not a Mechanical Check
- Ask: does this requirement accurately restate the upstream need, or has it drifted? (→ Characteristic: Correct)
- Drift is common when a requirement over-specifies a SOLUTION the upstream source never asked for (→ Characteristic: Correct)
- A correct requirement's trace target, read literally, actually supports the stated capability (→ Characteristic: Correct)

## Glossary
- shall — mandatory (RFC 2119) (→ Glossary)
- should — recommended, not mandatory; a deviation needs a stated reason (→ Glossary)
- may — genuinely optional (→ Glossary)
- Atomic — states exactly one testable capability (→ Glossary)

---
*Last reviewed: 2026-08-08 · Review cadence: annually (this is a quality
METHOD, not a domain fact set — it changes far less frequently than a
domain/regulatory KB).*
