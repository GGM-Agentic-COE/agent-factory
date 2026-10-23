# kb-L1-regulatory-frameworks-index

**Domain covered:** None specific — a cross-domain index of which **Indian**
regulatory body governs which category of regulated activity, plus the
coverage-category sweep list every assessment must walk.

**Why it exists:** `L1-vision-regulatory-feasibility-checker` is a generic L1
agent, reused across every domain the CoE builds for. Before it can reason
about food, payments, healthcare, or anything else, it needs to know which
body's rules even apply. This KB is that first lookup — genuinely
domain-agnostic, so it stays at L1 rather than being duplicated into every
L2 domain KB.

> **Jurisdiction changed 2026-08-21: GB → IN.** Domain-agnostic is not the
> same as jurisdiction-agnostic. This index is reusable across every vertical
> but holds one country's regulators. A deployment serving a second geography
> needs a second index selected by the idea brief's `target_geography` —
> never merged rows, which would let a constraint cite the wrong country's
> regulator and still survive a plausibility check.

**Centre/state:** many Indian regimes bind at both levels — food licensing,
labour, factories, legal metrology, municipal trade licences, professional
tax. A constraint answered only at central level is incomplete, and the
checker prompt carries a matching edge case.

## Two sections

| Section | What it is |
|---|---|
| `#cross-domain-index` | Activity → the Indian body that governs it |
| `#coverage-categories` | The sweep list: every category is a constraint, or a declared not-applicable entry |

**Why the sweep list is here and not in a prompt (v2.0):** both the checker
and its evaluator read it — the checker to walk it, the evaluator to audit
that it was walked. Duplicating it into two prompts lets them drift, and the
failure mode is ugly: the evaluator fails the checker for missing a category
the checker was never told about. One file, one list, no drift.

**What deliberately stays out of this KB:** the *behaviour* when a rule
applies awkwardly — not yet in force, under an unresolved threshold,
extraterritorial, discharged through a third party's permission. Those live
in the checker's prompt. A KB states what is true; a prompt states what to
do about it. They also can't survive the micro-KB content rule (one line,
fifteen words, no explanations) without losing the instruction that is their
entire value.

**Sources:** Public regulator remit statements (FSSAI, Data Protection Board
of India/MeitY, CERT-In, RBI, SEBI, IRDAI, CCPA, CCI, ASCI, BIS, WPC/DoT,
TEC, TRAI, Legal Metrology, CDSCO, DGFASLI, EPFO, ESIC, CPCB, CERC, AERB,
DGFT, CBIC, CBDT, MCA, CGPDTM, DEPwD).

**Update frequency:** Quarterly, or on any regulator merger/rename/remit
change, when a new cross-cutting regulatory category emerges, or when the
deployment's target geography changes.

**Quality bar:** Every row must name a real, currently-operating Indian body.
No domain speculation — if a body isn't listed, the checker agent should
say so rather than guess. Removing a coverage category is a breaking change:
it silently narrows every assessment downstream. Note that several regimes
were phasing in when this was written (DPDP subordinate rules, the four
labour codes) — confirm a body's current remit before relying on it.

**Owner:** Agentic-AI CoE

**Consumers:** `L1-vision-regulatory-feasibility-checker` and
`L1-vision-regulatory-feasibility-checker-evaluator` (all domains)
