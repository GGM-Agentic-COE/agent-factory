<!--
kb-L1-enterprise-architecture · content · enterprise-architecture.md
Layer: L1 (enterprise-wide, cross-phase — NOT domain-specific). Illustrative
content for the reference scenario: Thornbury Foods Group, the fictional
parent enterprise building HarvestLink as a new digital product. Not a
real company; not a real product commitment. Grounds impact-assessment.md
and any later-phase design agent (HLD/LLD) that needs to know what
HarvestLink might touch, integrate with, or deliberately avoid touching.
Security & compliance standards live in kb-L1-enterprise-security — not
duplicated here.
-->

# Thornbury Foods Group — Enterprise Architecture

## EA1: Organisation Overview
- Thornbury Foods Group: UK food wholesale/distribution conglomerate, ~30 years operating
- Core business: traditional wholesale supply to foodservice (HORECA) via regional depots
- HarvestLink: new digital-first product unit, semi-autonomous, group-funded
- HarvestLink's mandate: producer/distributor marketplace + compliance tooling, NOT a replacement for core wholesale

## EA2: Technology Stack (Existing, Group-Wide)
| Component | Technology | Status | Notes |
|---|---|---|---|
| ERP | SAP ECC 6.0, on-prem | Migrating to S/4HANA (in flight) | Finance, invoicing, core ledger |
| Warehouse Management | Manhattan WMS | Stable | Depot/warehouse operations only |
| Supplier/Distributor Master Data | Supplier Master Data System (SMDS), custom .NET | Stable, no planned replacement | Existing producer/distributor records for the wholesale business |
| Compliance Document Store | SharePoint-based, manual upload | Legacy, no API | HACCP/allergen certs for wholesale suppliers — human-reviewed, not integrated |
| Employee Identity | Azure AD, group SSO | Stable | **Employees only** — no external-party support |
| Data Warehouse | Snowflake | Stable | Group-wide BI/reporting |
| Integration | Group ESB (MuleSoft) + emerging API Gateway (Kong) | API Gateway is new, mandatory for new digital products | New services must publish via Gateway, not point-to-point |

## EA3: Core Applications — Integration Relevance to HarvestLink
| System | What it holds | Does HarvestLink touch it? | Why / why not |
|---|---|---|---|
| SMDS | Existing wholesale supplier/distributor records | **Check only, read-only** | Onboarding (FR-001) should check for an existing SMDS record to avoid duplicate producer identity — but HarvestLink's own producer records live in its own service, not written back to SMDS |
| Group ERP (SAP) | Financial ledger, invoicing | **No integration, by design** | HarvestLink must never take title/possession of goods (vision.md § Regulatory Posture); any ERP posting would imply HarvestLink is a transacting party, undermining the facilitation-only structure |
| Compliance Document Store | Manually-uploaded wholesale supplier certs | **No integration** | No API exists (EA2); HarvestLink's traceability/allergen services (FR-003, FR-004) are built standalone, not as an extension of this legacy store — an explicit decision, not an oversight |
| Employee Identity (Azure AD) | Employee accounts only | **No integration** | HarvestLink's users (producers, distributors, buyers) are external parties; group SSO has no external-party tier (see kb-L1-enterprise-security) |
| Data Warehouse (Snowflake) | Group-wide aggregate reporting | **Outbound feed only** | HarvestLink's metrics-reporting-pipeline (FR-008/FR-009) feeds aggregate, non-PII metrics to the group DW per group reporting policy — one-way, no read dependency back |
| API Gateway (Kong) | New digital-product traffic | **Required** | Any HarvestLink service exposed beyond its own boundary must publish through the Gateway, not a direct point-to-point integration |

## EA4: Architecture Patterns & Principles
- New digital products: API-first, microservices — matches HarvestLink's own component breakdown (see dependency-graph.json)
- Cross-system integration: via Group ESB or API Gateway — never direct database-to-database
- New services: independently deployable, own datastore — no shared database with legacy systems
- Legacy systems (SMDS, Compliance Document Store): read-only integration where touched at all — never written to from a new digital product without Enterprise Architecture review (see EA10)

## EA5: Service Domains
| Domain | Owner | Includes |
|---|---|---|
| Finance & Ledger | Group Finance / Core IT | SAP ERP |
| Supply Chain & Warehouse | Core IT | WMS, SMDS |
| Customer & Sales | Core IT | Legacy wholesale CRM (not listed above — out of HarvestLink's touch surface entirely) |
| Compliance & Documentation | Core IT (legacy) | Compliance Document Store |
| Identity | Core IT | Azure AD (employees) |
| Producer Marketplace (NEW) | HarvestLink product unit | Onboarding, discovery, traceability, allergen, limits, routing, metrics — all HarvestLink's own components |

## EA6: Support Model & SLAs
| Tier | Systems | Uptime SLA | Support |
|---|---|---|---|
| Tier 1 (business-critical) | SAP ERP, WMS | 99.9% | 24/7, gold |
| Tier 2 (important) | SMDS, Azure AD, Data Warehouse | 99.5% | Business hours + on-call |
| Tier 3 (best-effort) | Compliance Document Store | No formal SLA | Business hours only |
| HarvestLink services | Own components | Set by HarvestLink product unit, not group default — see nfr-spec.md per component | New digital products define their own SLA tier; not automatically Tier 1 |

## EA7: Infrastructure Scale (Group-Wide, Illustrative)
- ~40 regional depots, ~1,200 SAP ERP transactions/hour at peak
- SMDS holds ~18,000 existing supplier/distributor records
- Compliance Document Store: ~9,000 documents, growing ~150/month, fully manual review

## EA8: Challenges & Technical Debt
- SAP ECC 6.0 approaching end of extended vendor support — S/4HANA migration is multi-year, in progress
- Compliance Document Store has no API — repeatedly flagged as technical debt, not yet funded for replacement
- Supplier identity is fragmented: SMDS (wholesale) and HarvestLink's own producer records are NOT reconciled — a known, accepted gap for the pilot phase, not yet a group-wide master-data initiative

## EA9: Roadmap (Group-Wide, Independent of HarvestLink's Own Roadmap)
- S/4HANA migration: continuing, no fixed group-wide completion date affecting HarvestLink
- API Gateway (Kong) rollout: mandatory for all new digital products from 2026 onward — HarvestLink is an early adopter
- Compliance Document Store replacement: identified need, not yet funded or scheduled

## EA10: Operating Model — Governance
- New service touching Tier 1 systems (SAP ERP, WMS): **mandatory Enterprise Architecture review before build**
- New service that is net-new, independently deployable, no Tier 1 touch (HarvestLink's current component set, per EA3): **product-unit autonomy, EA review optional but recommended**
- Any future HarvestLink component proposing to write to SMDS or Group ERP: **triggers mandatory EA review** — not covered by HarvestLink's current autonomy

---
*Last reviewed: 2026-08-07 · Review cadence: quarterly (technology stack and
integration boundaries change faster than organisational structure).*
