# kb-L2-domain-market

*A domain-KB slot, not a food-specific artifact: `L1-vision-market-analyzer`'s
prompt and spec reference this id generically, so a different vertical can
populate the same slot with its own market facts without touching the
agent at all. This reference deployment's slot is filled with food-domain
content — see below.*

**Domain covered (this deployment):** UK food production & distribution
market structure —
distribution channel types, market player categories, industry trends, and
cost-structure norms.

**Why it exists:** `L1-vision-market-analyzer` needs a domain-grounded
starting scaffold before it issues live searches via
`tool-L1-web-search-competitor-scan`. This KB supplies the categories and
structural facts that don't change month to month (channel types, cost
drivers); the live search tool supplies whatever is current at execution
time. Neither replaces the other.

**Sources:** Public company/category knowledge (illustrative categories,
not a verified real-time competitor register) plus general UK food-industry
trend reporting (post-Brexit trade friction, traceability demand, plant-based
growth, COVID-era supply-chain resilience focus).

**Update frequency:** Monthly — market status ages faster than regulation.
Any named company should be treated as a category example, not a confirmed
current-market claim; re-verify via the live search tool before citing a
specific competitor as active in a real market-analysis output.

**Quality bar:** No bullet may assert a specific company's current strategy
or financials as fact — only well-known, public category/structure
information. Anything more specific belongs in the live search result, with
its own citation, not in this static KB.

**Owner:** Food Domain Champion

**Consumers:** `L1-vision-market-analyzer`
