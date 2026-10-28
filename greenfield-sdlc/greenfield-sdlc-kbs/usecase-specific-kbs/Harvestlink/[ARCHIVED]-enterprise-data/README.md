# enterprise-data/

Raw external data exports for Thornbury Foods Group — **not** knowledge
bases, and deliberately kept separate from `knowledge-bases/`.

## Why this is a separate category from `knowledge-bases/`

`knowledge-bases/kb-L1-enterprise-architecture` is curated *knowledge*: WHY
things are the way they are, architecture principles, integration
reasoning, governance rules. It's written prose+tables, reviewed quarterly,
attached to an agent's `context.knowledge_bases`, and chunked/embedded for
retrieval — the standard KB pattern in this framework
(`knowledge-base-creator.md`).

The files here are *data*: a raw, timestamped export from Thornbury's own
systems (illustrative ServiceNow-style Service Catalog and CMDB), exactly
as `L1-planning-impact-assessor`'s BOM row has always described its input:
`"External: service catalog / CMDB export (e.g. Backstage, ServiceNow)"`
— an external system export, not an agent-factory-governed artifact. It
has no `spec.yaml` (no chunking/embedding model applies to it), no review
cadence in the KB sense — it's a snapshot as-of its `exported_at`
timestamp, refreshed by re-running the export, not by editing prose.

Same underlying estate, two complementary technical views (plus the KB's
narrative view, for a third angle):

| File | Grain | Answers |
|---|---|---|
| `thornbury-service-catalog.json` | Service (business/technical capability) | "Does something like this already exist? Who owns it?" — avoid duplicate build, find the right escalation path |
| `thornbury-cmdb-export.json` | Configuration Item (individual technical asset) + relationships | "What specific technical touchpoint exists, and what does it currently integrate with?" |
| `knowledge-bases/kb-L1-enterprise-architecture` | Narrative | "Why does HarvestLink touch or not touch this, and what's the governance rule?" |

## Provenance

Illustrative content for this reference scenario — not a real
organisation's actual estate. If this framework is deployed against a real
enterprise, these files are replaced by an actual export from that
organisation's ServiceNow/Backstage/equivalent — the shape (services with
tier/owner, CIs with type/criticality/relationships) is the reusable part.

## Consumers

`L1-planning-impact-assessor` (primary — both files); `L1-planning-dependency-mapper`
(CMDB relationships, as a cross-check against its own computed graph).

## Refresh cadence

Re-export on demand before a new impact assessment — this is a snapshot,
not a maintained document. A stale export (e.g. missing a newly
decommissioned CI) is a data-quality risk `impact-assessor` cannot itself
detect; `exported_at` should be checked against the assessment date before
trusting it as current.
