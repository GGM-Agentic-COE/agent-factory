# kb-L2-domain-regulatory

*A domain-KB slot, not a food-specific artifact:
`L1-vision-regulatory-feasibility-checker`'s prompt and spec reference this
id generically, so a different vertical can populate the same slot with its
own regulatory facts without touching the agent at all. This reference
deployment's slot is filled with food-domain content — see below.*

**Domain covered (this deployment):** UK food production & distribution —
registration and
licensing, hygiene and food safety, allergen labelling, cold chain and
traceability, and cross-jurisdiction mechanisms relevant to a distributor
operating across multiple local authority areas.

**Why it exists:** `L1-vision-regulatory-feasibility-checker` needs real
food-specific facts to classify constraints Green/Amber/Red and to cite a
specific regulation per constraint — generic knowledge isn't enough, and
the full technical regulatory corpus is far more than a vision-stage agent
needs. This is a condensed, purpose-specific cut: PM/feasibility
implications only, not field-level technical detail (that belongs in a
later-phase KB for design/construction agents, not here).

**Sources:** Food Safety Act 1990; Regulation (EC) 852/2004 (retained UK
law); Food Information Regulations 2014 / EU FIC Regulation 1169/2011; Food
Information (Amendment) (England) Regulations 2019 ("Natasha's Law"); Food
Safety and Hygiene (England) Regulations 2013; Regulation (EC) 178/2002;
Regulation (EU) 2015/2283; Weights and Measures Act 1985; FSA Food Hygiene
Rating Scheme guidance; Primary Authority Scheme (BRDO).

**Update frequency:** Quarterly — food regulation changes faster than most
domains. This KB is a starting point for a feasibility assessment, not a
substitute for current FSA/FSS guidance or legal review before an actual
authorization application.

**Quality bar:** Every constraint bullet must cite a real, named regulation
or scheme. No constraint may be classified Red without also being checked
against `gr-L1-hallucination-check` for whether a mitigation genuinely
exists in this KB or elsewhere.

**Owner:** Food Domain Champion

**Consumers:** `L1-vision-regulatory-feasibility-checker`
