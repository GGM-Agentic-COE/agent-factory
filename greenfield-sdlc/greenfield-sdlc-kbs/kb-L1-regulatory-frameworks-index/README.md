# kb-L1-regulatory-frameworks-index

**Domain covered:** None specific — a cross-domain index of which UK
regulatory body governs which category of regulated activity.

**Why it exists:** `L1-vision-regulatory-feasibility-checker` is a generic L1
agent, reused across every domain the CoE builds for. Before it can reason
about food, payments, healthcare, or anything else, it needs to know which
body's rules even apply. This KB is that first lookup — genuinely
domain-agnostic, so it stays at L1 rather than being duplicated into every
L2 domain KB.

**Sources:** Public regulator remit statements (FCA, FSA, HSE, ICO, MHRA,
Ofcom, Ofgem, ONR, ASA, CMA, OPSS, Primary Authority Scheme).

**Update frequency:** Quarterly, or on any regulator merger/rename/remit
change.

**Quality bar:** Every row must name a real, currently-operating UK body.
No domain speculation — if a body isn't listed, the checker agent should
say so rather than guess.

**Owner:** Agentic-AI CoE

**Consumers:** `L1-vision-regulatory-feasibility-checker` (all domains)
