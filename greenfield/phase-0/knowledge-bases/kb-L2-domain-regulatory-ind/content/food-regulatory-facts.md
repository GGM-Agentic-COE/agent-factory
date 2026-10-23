# Food Production & Distribution — Regulatory Facts

## About this knowledge base

- KB: kb-L2-domain-regulatory-ind
- Layer: L2 — domain: food production & distribution
- Jurisdiction: India only (see #jurisdiction)
- Consumed by: L1-vision-regulatory-feasibility-checker and its evaluator
- Each fact is annotated with its target constraint category
- Content rules: max 1 line per bullet, max 15 words, no explanations, numbers not words
- VERIFY BEFORE RELIANCE: thresholds and turnover limits change often
- DPDP rules and labour codes were phasing in at the time of writing
- Confirm against current FSSAI notifications before this KB gates a real funding or build decision

## Jurisdiction

Section anchor: #jurisdiction

**Jurisdiction covered: India (ISO 3166-1 alpha-2: IN).**
Sub-national layers in scope: states and union territories, municipal bodies.
Every statute, regulator and threshold below is Indian. This KB covers no
other country — an idea targeting a different country cannot be assessed
from it, and no rule here may be translated onto one.

## Who Is a Food Business Operator

- Food business: manufacture, processing, packaging, storage, transport, distribution, import, sale or catering of food — FSS Act s.3(1)(n) (→ Constraint: Authorization)
- FBO: the person carrying on that food business; licensing duties attach to them — s.3(1)(o) (→ Constraint: Authorization)
- Transporter or storage provider handling food is an FBO, even without owning it (→ Constraint: Authorization)
- Marketplace facilitating food sale is an e-commerce FBO — needs its own FSSAI licence (→ Constraint: Authorization)
- Vendor supplying only software, data or advice, never handling food, is not an FBO (→ Constraint: Authorization · interpretation — confirm per operating model)
- Its FBO customers keep their own licences; vendor may carry derived record-keeping duties (→ Constraint: Traceability)

## Registration & Licensing
- Food Safety and Standards Act, 2006 is the governing statute (→ Constraint: Authorization)
- Every Food Business Operator (FBO) needs FSSAI registration or licence before trading (→ Constraint: Authorization)
- Basic Registration: annual turnover up to 12 lakh (→ Constraint: Authorization)
- State Licence: turnover above 12 lakh, up to 20 crore (→ Constraint: Authorization)
- Central Licence: turnover above 20 crore, importers, multi-state operations (→ Constraint: Authorization)
- Basis: FSS (Licensing and Registration of Food Businesses) Regulations, 2011 (→ Constraint: Authorization)
- FSSAI licence number must be displayed on premises and on labels (→ Constraint: Labelling)
- Municipal trade licence is a separate, additional state/local requirement (→ Constraint: Multi-jurisdiction risk)

## Food Hygiene & Safety
- Schedule 4 of the 2011 Licensing Regulations sets GMP/GHP by business type (→ Constraint: Hygiene)
- HACCP-based food safety plan required for Central Licence categories (→ Constraint: Hygiene)
- Food Safety Supervisor trained under FoSTaC mandatory for most licensed FBOs (→ Constraint: Hygiene)
- FSS (Food Recall Procedure) Regulations, 2017 require a documented recall plan (→ Constraint: Traceability)
- Annual food safety audit required for high-risk categories — FSS (Food Safety Auditing) Regs, 2018 (→ Constraint: Hygiene)

## Labelling
- FSS (Labelling and Display) Regulations, 2020 govern all pre-packaged food (→ Constraint: Labelling)
- Veg/non-veg symbol mandatory: green dot vegetarian, brown dot non-vegetarian (→ Constraint: Labelling)
- Allergen declaration mandatory — cereals containing gluten, crustaceans, eggs, fish, peanuts, soybeans, milk, tree nuts, added sulphites (→ Constraint: Labelling)
- Legal Metrology (Packaged Commodities) Rules, 2011: MRP, net quantity, importer details (→ Constraint: Labelling)
- Date marking: "best before" or "expiry"/"use by" per category (→ Constraint: Labelling)

## Distribution & Cold Chain
- FSS (Food Products Standards and Food Additives) Regulations, 2011 set product temperature standards (→ Constraint: Cold Chain)
- Chilled/refrigerated storage generally 0-4°C; frozen at -18°C or below (→ Constraint: Cold Chain)
- Schedule 4 Part V covers transportation hygiene and temperature control (→ Constraint: Cold Chain)
- Traceability: one-step-back, one-step-forward records required under the 2017 Recall Regulations (→ Constraint: Traceability)
- Temperature control applies in transport, not only in storage (→ Constraint: Cold Chain)
- FSSAI Food Safety and Standards (Import) Regulations, 2017 apply to imported consignments (→ Constraint: Authorization)

## Cross-Cutting
- FSS Act s.26 places primary liability on the FBO for food safety (→ Constraint: Liability)
- Penalties under FSS Act ss.48-67; unsafe food attracts criminal liability (→ Constraint: Liability)
- State Food Safety Commissioners enforce; central FSSAI sets standards (→ Constraint: Multi-jurisdiction risk)
- Multi-state operations need Central Licence plus state-level compliance (→ Constraint: Multi-jurisdiction risk)
- Novel food requires prior approval — FSS (Approval of Non-Specified Food) Regulations, 2017 (→ Constraint: New ingredients)
- Health and nutrition claims restricted — FSS (Advertising and Claims) Regulations, 2018 (→ Constraint: Advertising)
- E-commerce food sellers carry additional FSSAI duties, incl. licence display (→ Constraint: Authorization)

## Review

- Jurisdiction: India
- Last reviewed against FSSAI sources: 2026-08-21
- Last edited: 2026-10-05 — added "Who Is a Food Business Operator"; not yet reviewed against current FSSAI notifications
- Review cadence: quarterly — food regulation changes more often than most domains
- Verify against current FSSAI notifications before use in a real assessment, not this KB alone
- Turnover thresholds are in INR and revised periodically; treat figures as indicative
