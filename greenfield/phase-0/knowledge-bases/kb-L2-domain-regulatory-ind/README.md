# kb-L2-domain-regulatory

*A domain-KB slot, not a food-specific artifact:
`L1-vision-regulatory-feasibility-checker`'s prompt and spec reference this
id generically, so a different vertical can populate the same slot with its
own regulatory facts without touching the agent at all. This reference
deployment's slot is filled with food-domain content — see below.*

**Domain covered (this deployment):** **India** food production &
distribution — FSSAI registration and licensing tiers, hygiene and food
safety, labelling (allergens, veg/non-veg mark, Legal Metrology
declarations), cold chain and traceability, and the centre/state split
relevant to a distributor operating across multiple states.

> **Jurisdiction changed 2026-08-21.** This KB held UK/retained-EU food law
> until the deployment's target geography moved to India. Jurisdiction is
> part of this slot: one geography per KB. A deployment serving two
> geographies needs two KBs selected by the idea brief's `target_geography`
> — never one file with mixed rows, which would let the agent cite an Indian
> rule against a UK idea and still look internally consistent.

**Why it exists:** `L1-vision-regulatory-feasibility-checker` needs real
food-specific facts to classify constraints Green/Amber/Red and to cite a
specific regulation per constraint — generic knowledge isn't enough, and
the full technical regulatory corpus is far more than a vision-stage agent
needs. This is a condensed, purpose-specific cut: PM/feasibility
implications only, not field-level technical detail (that belongs in a
later-phase KB for design/construction agents, not here).

**Sources:** Food Safety and Standards Act, 2006; FSS (Licensing and
Registration of Food Businesses) Regulations, 2011 incl. Schedule 4; FSS
(Labelling and Display) Regulations, 2020; FSS (Food Products Standards and
Food Additives) Regulations, 2011; FSS (Food Recall Procedure) Regulations,
2017; FSS (Food Safety Auditing) Regulations, 2018; FSS (Approval of
Non-Specified Food) Regulations, 2017; FSS (Advertising and Claims)
Regulations, 2018; FSS (Import) Regulations, 2017; Legal Metrology
(Packaged Commodities) Rules, 2011; FoSTaC training scheme.

**Update frequency:** Quarterly — food regulation changes faster than most
domains. This KB is a starting point for a feasibility assessment, not a
substitute for current FSSAI notifications or legal review before an actual
licence application. **The INR turnover thresholds are revised periodically
and must be confirmed before they gate a real decision** — a stale threshold
silently puts a business in the wrong licence tier.

**Quality bar:** Every constraint bullet must cite a real, named regulation
or scheme. No constraint may be classified Red without also being checked
against `gr-L1-hallucination-check` for whether a mitigation genuinely
exists in this KB or elsewhere.

**Owner:** Food Domain Champion

**Consumers:** `L1-vision-regulatory-feasibility-checker`
