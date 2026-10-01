# L1-design-platform-architect

> **Status: built (foundational invocation).** `spec.yaml`,
> `output_schema.json`, `evaluation.md` and
> `prompts/L1-design-platform-architect/instructions.md` exist. `examples/`
> and `golden/v1.0.0/` are **not** built — see open item 4. The conditional
> delta invocation (BOM Phase 4) is a separate build. Read this file before
> changing any of the built files.

## Purpose

BOM **Phase 2.25 — Platform & Data Foundation (Cycle 0)**, marked `NEW`.
Owns the platform viewpoint `PLT-*`: runtime topology, environment model,
CI/CD pipeline and supply chain, observability and SLOs, secrets and workload
identity, network, resilience and DR.

## Why a separate phase, and not a section of the first feature's HLD

Platform is **~80% front-loaded**. A feature cycle's platform delta is empty
most of the time and occasionally very large — a completely different shape
from application architecture, which changes roughly in proportion to
features delivered. A document topology that makes platform a subsection of a
per-feature HLD cannot represent that shape.

The practical consequence, if this phase does not exist: the first real
feature cycle absorbs the platform work, takes three times its estimate, and
forces every platform decision under delivery pressure. Every estimate after
it is then calibrated against a corrupted number.

## `PLT-6` is the point

The distinguishing output is not the runtime diagram — it is **`PLT-6`, the
capability register**: a table of what the platform can currently support.
It turns *"did we think about platform?"* from a judgement call into a
**lookup `L1-planning-impact-assessor` performs mechanically** on every
future feature.

Three design consequences follow, and all three are enforced in the schema
rather than left to the prompt's good intentions:

1. **`NOT PRESENT` rows are mandatory, not optional.** A capability absent
   from the register cannot be looked up. To the impact assessor, an absent
   row is indistinguishable from an oversight.
2. **`AVAILABLE` is a claim about provisioning, not about intent.** It means
   technically provisioned and consumable — *not* "we know which product we
   might use". A wrongly-`AVAILABLE` row is the most damaging error this
   agent can make, because it makes a feature's platform delta **disappear
   from its estimate** while looking entirely correct. The prompt's rule is
   "when in doubt, `NOT PRESENT`".
3. **Naming a product obliges a lifecycle check.** `Capability` requires
   `realization` *and* `lifecycle_check` whenever status is `AVAILABLE` or
   `PENDING`, so `PRIN-07` cannot be skipped by simply not mentioning it.

## The `PRIN-07` trap this agent is most likely to fall into

`binding-principles.template.json`'s own worked example resolves `PRIN-07`
(prefer approved platforms) as `applicability: NOT_APPLICABLE` — because the
FSA names no technology, so there is nothing there for the principle to bind.

This document **does** name technologies. It is, with the data architecture,
the first artifact in the pipeline permitted to, and therefore the first that
can violate `PRIN-07`. Reading `NOT_APPLICABLE` as "ignore me" without also
reading `resolved_scope` ("Binds the Platform and Data viewpoint documents,
not the FSA") would skip the principle precisely where it bites.

`kb-L1-enterprise-architecture` `BP8` carries a standing note about exactly
this; the prompt, the spec's `binding_principles_json` description and
`evaluation.md` all point at it.

## What it reads

| Input | Source | Required? | Why |
|---|---|---|---|
| `foundational-solution-architecture.md` | `L1-design-foundational-architect`, via blob | **Yes** | `APP-1` contexts (the deployability obligation), `APP-2` map, `CON-*`, `REQ-PLT-*`, `SEC-*`, § 4 `PRIN` rows. Context-less `APP-1` is `INSUFFICIENT_CONTEXT` |
| `nfr-spec.md` | `L1-requirements-nfr-classifier`, via blob | **Yes** | Availability, Performance and Scalability boundary conditions — the **only** admissible source for an availability target, RTO, RPO or capacity figure |
| `data-architecture.md` | `L1-design-data-architect`, via blob | No | `DAT-4` planes and `DAT-3.3` encryption requirement become capabilities this viewpoint realises |
| `integration-architecture.md` | `L1-design-integration-architect`, via blob | No | `INT-2` styles imply event infrastructure; `INT-8` implies correlation propagation |
| `binding-principles.json` | per-product resolution, via blob | No | Read per `BP11`, with `BP8`'s note |

The two required inputs match the BOM row exactly (`Agent:
foundational-solution-architecture.md from foundational-architect;
nfr_classifications items from nfr-classifier`).

### The ordering awkwardness, stated rather than hidden

The BOM's Phase 2.25 chain order is **`platform → data → integration`**. The
HarvestLink reference platform document, however, lists *both* Data
Architecture and Integration Architecture among its inputs — which the chain
order cannot satisfy on a first pass.

The resolution here: both siblings are **optional enriching inputs**. On a
first pass both are usually absent, capability demands come from `REQ-PLT-*`
alone, and the prompt requires recording that the capability set must be
**re-checked before Cycle 0 closes**. On a re-run or a second pass they are
present and their demands are realised directly. The gap is therefore visible
at the human gate rather than discovered when `PLT-6` turns out to be missing
the event bus the integration architecture assumed.

This is worth revisiting when `L1-design-foundational-architect` lands: if
the FSA's `REQ-PLT-*` demands are complete enough, the first pass loses
nothing and the note becomes unnecessary.

## Output — four artifact kinds, one of which is a handoff

| Artifact | Notes |
|---|---|
| `platform-architecture.md` | `PLT-1`..`PLT-19`, including the `PLT-6` register |
| `hld-{platform-component}.md` / `lld-{platform-component}.md` | **Platform** components only — a gateway configuration, a shared observability stack, a pipeline. Application-service HLDs belong to Phase 4's per-component design agents; one written here would be a second, drifting source |
| `iac-{capability}.tf` | The architecture's provisioning intent. The platform repository holds the implementation of record |

All four go to **blob storage**, per the build instruction.

### "IaC committed" — satisfied in two steps, not one

The BOM row's output column says `IaC committed`, and its tools column lists
`tool-L1-github-upload-file`, `tool-L1-github-create-branch` and
`tool-L1-confluence-create-page`. Those are **write/publish tools**, and per
the `agent-creator` Core/Utility split they belong to a Utility agent rather
than to a generator — coupling this agent's derivation logic to one
repository host is exactly what that split exists to prevent.

So: **this agent writes the manifests to blob; `github-orchestrator` commits
what it wrote.** The prompt explicitly forbids claiming the commit happened
here, because an agent that reports a commit it did not make is worse than
one that reports nothing. The blob writer is the repo's standing exception to
the Core/Utility rule — `L1-vision-statement-generator` uses it the same way.

If the commit must happen inside this agent, that is a deliberate departure
from the Core/Utility split and should be recorded as such rather than
arrived at by adding a tool.

## `PLT-19` and why the gate is boolean

`PLT-19` states exactly six proofs — build, deploy, run, observe, emit event,
consume event — and the schema pins the array to `minItems: 6, maxItems: 6`.
Platform readiness is **proven**, not scored. The BOM's `QG: cycle-0-exit` is
a boolean gate for the same reason: a scalar cannot express "the pipeline
half works", and five of six is not 83% ready, it is not ready.

The `supported` flag is the architecture's claim that its capability set
makes each proof *achievable* — not that the proof has been run. The Platform
Lead executes and signs it at the human gate. A `false` is honest and useful:
it names exactly what blocks Cycle 0 exit.

## Prompt length — a flagged, deliberate overage

`instructions.md` is ~470 lines against the skill's ≤150-line budget — the
longest of the three viewpoint architects, because `PLT` has 19 sections and
this agent emits three artifact kinds rather than one. Same justification as
its siblings: no template KB exists, the section structure **is** the
contract (`L1-planning-impact-assessor` looks for `PLT-6` by name), and
Processing Rules were kept free of restatements of the template's inline
guidance. The shared-template-KB extraction is the honest lever if the budget
must be met.

## Composition

```
greenfield/agents/L1-design-platform-architect/
├── spec.yaml
├── output_schema.json
├── evaluation.md
└── README.md                  # this file

greenfield/prompts/L1-design-platform-architect/
└── instructions.md            # embedded platform-architecture.md template (S4)
```

## Two invocations — only one is built here

| Invocation | BOM phase | Fires when | Reads | Emits | Built? |
|---|---|---|---|---|---|
| **Foundational** | 2.25, once per project | Always | FSA + `nfr-spec.md` | `platform-architecture.md` v1.0, platform HLD/LLDs, IaC | **Yes** |
| **Delta (conditional)** | 4, per cycle | **Only on a `PLT-6` `NOT PRESENT` hit** — which is most cycles' no | `impact-assessment.md` capability-gap list, **current `platform-architecture.md`** | `platform-architecture.delta.json` incl. `PLT-6` status updates, new platform-component HLD/LLDs | No |

The conditional firing is `PLT-6` paying for itself: the impact assessor's
mechanical lookup is what decides whether this agent runs at all in a given
cycle. `PLT-18` defines the delta contract it will consume.

## Open items

1. **`gr-L1-consistency-check` and `gr-L1-secret-scanner` are not built.**
   Both are named on the BOM row and referenced in `spec.yaml`. The repo has
   `gr-L3-consistency-checker`, not an L1 build — the same naming mismatch
   `L1-design-api-spec`'s README already flags. `gr-L1-secret-scanner` is
   load-bearing **here specifically**: this is the agent that emits IaC
   manifests, which is where a committed credential actually gets introduced.
   Guardrails were out of scope for this build.
2. **`gr-L1-architecture-conformance` is not built.** It is the real consumer
   of `PLT-16`.
3. **`tool-L1-github-upload-file` / `tool-L1-github-create-branch` are not
   attached**, by the Core/Utility reasoning above. If "IaC committed" must
   be literal within this agent, that is a deliberate architectural
   departure, not a missing tool.
4. **`examples/` and `golden/v1.0.0/` are not built.** The edge case is
   already specified in the prompt: an FSA with no `APP-1` bounded contexts →
   `INSUFFICIENT_CONTEXT`.
5. **No `L1-design-foundational-architect` exists yet.** See the matching item
   in the sibling READMEs — all three are built against the FSA's *specified*
   section vocabulary and need re-checking together if it ships differently.
6. **`L1-arch-baseline-generator` (the fourth Phase 2.25 agent) is not
   built.** It reads all four architecture documents and emits
   `application-baseline.md` v0.1 and `component-inventory.json`. Out of
   scope for this build, but it is the consumer that closes the phase.
7. **Not wired into `L1-WF-greenfield-idea-to-pr.yaml`.** No Phase 2.25 stage
   exists yet; wiring all four agents is one change, not three. Note the
   cross-phase ordering constraint the workflow must preserve:
   `L1-testing-env-provisioner` in Phase 2.5 cannot provision environments
   until the platform exists, which is why 2.25 precedes 2.5.
