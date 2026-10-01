# HarvestLink — Wireframes · Cycle 1

**Feature Design Package** `C1-producer-registration` · `additive/wireframes.md`
Produced by `L1-design-ux-wireframe@1.0.0` · `exec-uxw-3b4c5d6f`

> **Additive.** Added to the Feature Design Package, never merged into a canonical document.

**Fidelity** low — layout, hierarchy and state, not visual design.
**Primary viewport** 360px. P-01 is a producer on a phone, often outdoors; desktop is the secondary layout, not the reference one.
**Accessibility baseline** WCAG 2.2 AA.
**Figma** not pushed. `tool-L1-figma-create-frame` is optional per the BOM row, and ASCII wireframes stay readable in a terminal, a diff and a PR review.

---

## WF-01 — Producer registration form

`TP-03` · producer-portal · `WU-F1.1-03` · covers `S-F1.1-a-AC1`, `AC2`, `AC3`

```text
┌─ HarvestLink ─────────────── [account] ┐
│                                        │
│  Register as a producer         1 of 1 │
│                                        │
│  Business name                         │
│  [____________________________]        │
│                                        │
│  Food Business Operator (FBO) number   │
│  [____________________________]        │
│  ⓘ Where do I find this?               │
│  ⚠ field-level error appears here      │
│                                        │
│  ┌────────────────────────────────┐    │
│  │ ☐  I confirm that I, not       │    │
│  │    HarvestLink, am the Food    │    │
│  │    Business Operator for what  │    │
│  │    I sell here.                │    │
│  │                                │    │
│  │    This is a legal declaration.│    │
│  └────────────────────────────────┘    │
│                                        │
│  [ Submit registration ]               │
│                                        │
│  Your details are saved as you type.   │
└────────────────────────────────────────┘
```

**Design notes**

- The attestation is boxed and set apart, with its consequence stated in plain words. UJ-01 step 4 warns it must not feel like boilerplate — a tick-box inline with business name would read as terms-and-conditions, and this one carries the facilitation-only regulatory position.
- **Not pre-ticked**, and no "select all" affordance. A pre-ticked legal declaration is not a declaration.
- "Where do I find this?" addresses UJ-01 step 3's abandonment risk directly. The producer without their FBO number to hand is the predicted drop-off, and the cheapest intervention is telling them where to look.
- The save-as-you-type line is the visible half of the resumption behaviour UJ-F02 says nothing specifies. Drawn because the journey needs it; flagged as WF-F03 because no acceptance criterion supports it.

**States**

| State | Covers | Behaviour |
| --- | --- | --- |
| empty | — | Submit enabled; validation on submit, not on blur — an outdoor user tabbing through fields should not be scolded mid-entry |
| field error | S-F1.1-a-AC2 | Error under the FBO field, names the expected format, entered value preserved. No record created |
| attestation missing | S-F1.1-a-AC3 | Client guard shown, but the screen assumes nothing about it. The server refuses regardless; the client guard is an affordance, not the control |
| submitted | S-F1.1-a-AC1 | Navigates to WF-02 |

---

## WF-02 — Registration status

`TP-04` · producer-portal · **no Work Unit** · covers `S-F1.1-a-AC4`, `S-F1.1-b-AC3`

```text
┌─ HarvestLink ─────────────── [account] ┐
│                                        │
│  Your registration                     │
│                                        │
│  ┌────────────────────────────────┐    │
│  │  ◐  Checking your FBO number   │    │
│  │                                │    │
│  │  We're confirming your Food    │    │
│  │  Business Operator registration│    │
│  │  with the competent authority. │    │
│  │                                │    │
│  │  Most checks finish within a   │    │
│  │  working day. We'll email you. │    │
│  └────────────────────────────────┘    │
│                                        │
│  What you can do now                   │
│  ✓ Add your business details           │
│  ✓ Draft listings (not published)      │
│  ✗ Publish listings — available once   │
│    your registration is confirmed      │
│                                        │
└────────────────────────────────────────┘
```

**Design notes**

- The blocked action is shown as blocked **with its reason**, not hidden. UJ-01 step 6 is explicit that a silently absent publish button generates the support contact this screen exists to prevent.
- "Most checks finish within a working day" is an expectation, not a commitment, and deliberately **not** a countdown or a progress bar. `S-F1.1-b-AC3` means a timeout and a slow answer are indistinguishable to this screen; a progress bar would assert knowledge the system does not have.
- The "what you can do now" list exists because UJ-01 step 5 identifies this as the point where the producer has finished their part and cannot act further. An empty waiting screen is read as failure.

**States**

| State | Covers | Behaviour |
| --- | --- | --- |
| pending | S-F1.1-a-AC4, S-F1.1-b-AC3 | The only state for both a slow lookup and a timed-out one |
| verified | S-F1.1-b-AC1 | Panel becomes confirmation; publish moves ✗ → ✓ |
| rejected | S-F1.1-b-AC2 | Panel states the reason returned by the register. Publish stays ✗ — see WF-F02 |

> **No Work Unit builds this screen.** Drawn anyway, because UJ-01 carries three steps here and a wireframe gap would hide the Work Unit gap. See WF-F01.

---

## WF-03 — Verification outcome email

`TP-05` · notifications-worker · `WU-F1.1-06` · covers `S-F1.1-b-AC2`

```text
┌────────────────────────────────────────┐
│ Subject: Your HarvestLink registration │
│                                        │
│ We couldn't confirm your FBO           │
│ registration.                          │
│                                        │
│ Reason: <reason returned by the        │
│          competent authority>          │
│                                        │
│ Your listings stay unpublished until   │
│ this is resolved.                      │
│                                        │
│ [ View your registration ]             │
└────────────────────────────────────────┘
```

**Design notes**

- Carries no FBO number, no business identifiers and no personal data beyond the addressee. An email is forwarded, quoted and archived outside the platform's control, and a registration number in a subject line is a disclosure nobody authorised.
- The reason is **passed through from the register**, not paraphrased. A rewritten regulatory reason is a new assertion about a legal status.

Same template serves the positive outcome. Drawn once.

---

## Coverage

| | |
| --- | --- |
| Touchpoints in the journey | 5 |
| Touchpoints wireframed | 3 |
| Acceptance criteria with a user-facing surface | 6 |
| Acceptance criteria surfaced | 6 |

**Not wireframed, deliberately**

- **TP-01 public landing** — exists already and is unchanged by this cycle. An unchanged screen placed in an additive folder reads as a change.
- **TP-02 external IdP** — owned by the identity provider, not by HarvestLink. Redrawing someone else's screen would assert a design this product does not control.

---

## Findings

### WF-F01 · MEDIUM — WF-02 is fully specified and has no Work Unit

The registration status screen carries three journey steps and two acceptance criteria, and nothing in `tasks.json` builds it. This is UJ-F01 reaching the wireframe stage unresolved — now with a concrete surface attached, and therefore a concrete size.

*Escalated, not absorbed.* The wireframe was drawn rather than omitted so the gap is visible as a missing builder rather than a missing screen.

### WF-F02 · MEDIUM — WF-02's rejected state has nowhere to go

The rejected panel says what the producer can do, and no acceptance criterion says what that is. `S-F1.1-b-AC2` ends at "notified with the reason". Whether a producer can correct an FBO number and resubmit, and whether that is a new registration or an amendment, is unspecified.

*A resubmit button was drawn and removed during authoring* — it would have implied a flow with no acceptance criteria, no Work Unit and no verifier behind it.

### WF-F03 · LOW — WF-01's save-as-you-type is drawn but unspecified

UJ-F02 notes the journey has no resumption path; the wireframe shows one, because a form the persona will abandon needs one. No acceptance criterion covers what is saved, for how long, or whether a partial registration with an unverified FBO number is a record at all — which is a data question (DAT-1.1 owns Producer) as much as a UX one.

*Drawn as a line of copy, flagged, and deliberately not detailed into behaviour.*

---

## Guardrails

**gr-L1-consistency-check — pass.** Screen states were checked against the acceptance criteria they claim. One correction during authoring: WF-02's pending panel originally showed a progress bar with an estimated completion time. That contradicts `S-F1.1-b-AC3` — the system cannot distinguish a slow lookup from a timed-out one, so a progress bar would display confidence it does not have. Replaced with a non-committal expectation.
