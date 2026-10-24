# Product Vision: AI Credit Coach

**Product:** AI Credit Coach — an augmentation module within Lloyds' AI Financial Assistant  
**Author:** Prateek Sharma, Business Analyst  
**Date:** 5 May 2026  
**Version:** 1.1  
**Status:** Draft — for Product Owner & Stakeholder Review

---

## 1. Vision Statement

Transform Lloyds' AI Financial Assistant from a backward-looking spending narrator into a forward-looking financial coach that actively helps customers understand, monitor, and improve their credit health — and connects them to the right Lloyds products at the right time.

---

## 2. Problem Statement

### 2.1 Current State of the AI Financial Assistant

Lloyds Banking Group unveiled the UK's first multi-feature AI-powered financial assistant in November 2025, describing it as "a conversational tool that allows customers to request personalised spending insights" that "provides 24/7 personalised financial coaching and work as a financial companion" [1]. The assistant is built on Lloyds' generative AI and agentic framework, using generative AI for conversational interfaces and agentic AI to process requests and execute actions [1]. It retains prior inputs to "understand and respond to specific, hyper-personalised customer requests" [1].

In May 2026, Lloyds launched **Envoy**, an internal platform built with Google Cloud for building and deploying AI agents with built-in governance, monitoring, and risk controls [2]. Envoy provides standardised templates, an internal agent marketplace, and persistent memory across sessions [2]. The Credit Coach would be deployed as a new agent on this platform.

The Financial Assistant's planned expansion covers "the full suite of financial products offered by Lloyds in 2026 and beyond, from mortgages, to car finance, to protection needs" [1] — but notably excludes credit health and score management.

### 2.2 Capability Gaps

| Gap | Customer Impact |
|-----|----------------|
| No credit score visibility | Customers must use third-party apps (ClearScore, Credit Karma) to see their score |
| No credit improvement guidance | No actionable steps to improve borrowing power |
| No what-if simulation | Customers can't model the impact of financial decisions on their credit |
| No pre-approved offers | Generic product marketing instead of guaranteed personalised offers |
| No proactive credit alerts | Customers discover score drops after the fact |
| No cross-lender debt visibility | Incomplete picture of total indebtedness |

### 2.3 Competitive Context

Experian has already launched a credit score app within ChatGPT (March 2026) [3], demonstrating market appetite for AI-powered credit intelligence. ClearScore, Credit Karma (via TransUnion), and TotallyMoney provide free credit score access to millions of UK consumers [4]. If Lloyds doesn't act, customers will rely on third parties for credit intelligence — weakening Lloyds' position as the primary financial relationship.

---

## 3. Product Overview

The AI Credit Coach is a **new specialist agent** deployed via Lloyds' **Envoy platform** [2] within the existing agentic AI architecture. It is not a separate application — it plugs into the same orchestrator, uses the same conversational UI, and follows the same governance-first guardrails. Envoy's standardised templates, agent marketplace, and persistent memory capabilities [2] provide the infrastructure foundation.

### 3.1 Core Capabilities

| # | Capability | Description |
|---|-----------|-------------|
| 1 | **Credit Score Dashboard & Monitoring** | Real-time credit score from CRA partners (Experian/Equifax/TransUnion), score breakdown (what's helping/hurting), monthly change tracking with explanations |
| 2 | **Personalised Credit Improvement Action Plans** | AI-generated ranked actions based on the customer's specific credit profile, with estimated point impact and timelines. Progress tracking with milestones. |
| 3 | **Credit Score Simulator** | "What-if" engine: model scenarios (close a card, pay off overdraft, apply for mortgage) against CRA scoring algorithms to predict score impact |
| 4 | **Pre-Approved Offers Engine** | Matches customer's actual credit profile against Lloyds' lending products. Generates guaranteed (not indicative) offers presented at optimal moments. One-tap application with pre-filled data. |
| 5 | **Proactive Credit Health Alerts** | Forward-looking notifications: utilisation approaching thresholds, upcoming payment reminders with score impact context, score improvement celebrations with new product eligibility |

### 3.2 How It Augments the Existing Assistant

| Financial Assistant (Today) | + Credit Coach | Combined Value |
|-----------------------------|---------------|----------------|
| "You spent £450 on dining last month" | "Reducing dining by £150/month improves affordability by 12%" | Spending insight → actionable credit improvement |
| "Here are savings options" | "Saving £200/month for 3 months could improve your score by 20 points" | Savings guidance → credit-building strategy |
| Generic product information | "You're pre-approved for £12,000 at 8.9% APR" | Product awareness → guaranteed personalised offer |
| Reactive Q&A | "Your score dropped 15 points — utilisation went above 50%" | Answering questions → proactive monitoring |

---

## 4. Scope

### 4.1 In Scope

- Credit score retrieval and display (multi-bureau)
- Score factor analysis and plain-English explanations
- AI-generated improvement action plans with progress tracking
- What-if credit simulation engine
- Pre-approved offer matching and presentation
- Proactive alert generation and delivery
- Integration with existing Financial Assistant orchestrator
- Conversational interface (natural language queries about credit)
- Score history and trend visualisation
- Cross-lender debt visibility (via CRA data)

### 4.2 Out of Scope (v1)

- Debt consolidation execution (advice only, not transaction)
- Third-party product comparison (Lloyds products only)
- Credit report dispute filing (link to CRA only)
- Joint account / household credit view
- Business credit scoring
- Mortgage affordability calculator (planned for FA expansion separately)

---

## 5. Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                  Lloyds Mobile App                       │
│  ┌───────────────────────────────────────────────────┐  │
│  │           Unified Conversational UI                │  │
│  │  "How's my credit score?" → Credit Coach Agent    │  │
│  │  "What did I spend on food?" → Spending Agent     │  │
│  └───────────────────────────────────────────────────┘  │
│                          │                              │
│  ┌───────────────────────┼───────────────────────────┐  │
│  │          Agentic Orchestrator                      │  │
│  │  Routes requests to the right specialist agent     │  │
│  └───────────────────────┼───────────────────────────┘  │
│         ┌────────────────┼────────────────┐             │
│  ┌──────┴──┐      ┌──────┴──┐      ┌─────┴──────┐     │
│  │Spending │      │ Savings │      │  Credit    │     │
│  │ Agent   │      │  Agent  │      │  Coach     │     │
│  │(Current)│      │(Current)│      │  Agent     │     │
│  └────┬────┘      └────┬────┘      │  (NEW)     │     │
│       │                │           └─────┬──────┘     │
│  ┌────┴────────────────┴───┐      ┌─────┴──────┐     │
│  │   Lloyds Bank Data      │      │  CRA Data  │     │
│  │   (Transactions,        │      │  (Experian,│     │
│  │    Balances, Products)  │      │  Equifax,  │     │
│  └─────────────────────────┘      │  TU)       │     │
│                                    └────────────┘     │
└─────────────────────────────────────────────────────────┘
```

### 5.1 Technical Components

| Layer | Components |
|-------|-----------|
| **Frontend** | Credit Score Dashboard widget, Score Simulator UI, Action Plan tracker, Alert cards, Offer presentation cards — all within existing mobile app shell |
| **Backend APIs** | Credit Score Service, Simulation Engine, Action Plan Generator, Offer Matching Service, Alert Engine, CRA Integration Gateway |
| **Data Persistence** | Score history store, Action plan state, Customer credit preferences, Alert configuration, Offer audit trail, Consent records |
| **Integrations** | CRA APIs (Experian Connect, Equifax Data Services, TransUnion One), Lloyds Product Catalogue, Existing FA Orchestrator (via Envoy [2]), Push Notification Service |

**Platform note:** The Credit Coach agent will be published to Envoy's internal agent marketplace, enabling reuse across Lloyds Bank, Halifax, and Bank of Scotland brands [2].

---

## 6. Functional Requirements (High-Level)

### 6.1 Credit Score Dashboard & Monitoring

| ID | Requirement |
|----|-------------|
| FR-1.1 | System shall retrieve credit score from at least one CRA on customer opt-in |
| FR-1.2 | System shall display current score, score band, and month-on-month change |
| FR-1.3 | System shall display score factors (positive and negative) in plain English |
| FR-1.4 | System shall store score history for trend visualisation (minimum 24 months) |
| FR-1.5 | System shall refresh score at least monthly (configurable per CRA agreement) |
| FR-1.6 | System shall explain score changes with specific contributing factors |

### 6.2 Personalised Credit Improvement Action Plans

| ID | Requirement |
|----|-------------|
| FR-2.1 | System shall generate ranked improvement actions based on customer's credit profile |
| FR-2.2 | Each action shall include estimated point impact and estimated timeframe |
| FR-2.3 | System shall track action completion and update plan accordingly |
| FR-2.4 | System shall celebrate milestones (score thresholds reached, actions completed) |
| FR-2.5 | Plans shall update dynamically as the customer's profile changes |

### 6.3 Credit Score Simulator

| ID | Requirement |
|----|-------------|
| FR-3.1 | System shall support simulation of: paying down debt, closing accounts, opening new credit, missed payments, reducing utilisation |
| FR-3.2 | Simulations shall return estimated score impact and confidence level |
| FR-3.3 | System shall clearly label results as estimates, not guarantees |
| FR-3.4 | System shall allow natural language scenario input ("What if I pay off my overdraft?") |

### 6.4 Pre-Approved Offers Engine

| ID | Requirement |
|----|-------------|
| FR-4.1 | System shall match customer credit profile against Lloyds lending criteria |
| FR-4.2 | Offers presented shall be guaranteed (customer will not be declined if they apply) |
| FR-4.3 | System shall present offers at contextually appropriate moments |
| FR-4.4 | System shall support one-tap application with pre-filled customer data |
| FR-4.5 | System shall maintain full audit trail of offers presented and customer actions |

### 6.5 Proactive Credit Health Alerts

| ID | Requirement |
|----|-------------|
| FR-5.1 | System shall alert when credit utilisation approaches configurable thresholds |
| FR-5.2 | System shall alert for upcoming payments where a miss would impact credit score |
| FR-5.3 | System shall notify when score improvements unlock new product eligibility |
| FR-5.4 | Customer shall be able to configure alert preferences and opt out |

---

## 7. Non-Functional Requirements

| Category | Requirement |
|----------|-------------|
| **Performance** | Score retrieval < 3 seconds; Simulation results < 5 seconds |
| **Availability** | 99.9% uptime for dashboard; alerts delivered within 15 minutes of trigger |
| **Scalability** | Support 10M+ enrolled customers with daily score checks |
| **Security** | All CRA data encrypted at rest (AES-256) and in transit (TLS 1.3); data classified as Highly Confidential |
| **Data Retention** | Score history retained for 6 years (FCA record-keeping); consent records retained indefinitely |
| **Accessibility** | WCAG 2.1 AA compliant; screen reader compatible; colour-blind safe score visualisations |

---

## 8. Regulatory Requirements

The Product Manager must ensure compliance with the following when carving requirements:

### 8.1 FCA Consumer Duty (PS22/9 — in force since 31 July 2023)

The Consumer Duty established a new Principle 12: "A firm must act to deliver good outcomes for retail customers" [5]. It is supported by three cross-cutting rules [5][6]:

| Cross-Cutting Rule | Implication for Credit Coach |
|-----------|------------------------------|
| Act in good faith toward retail customers | Improvement plans must genuinely benefit the customer, not just drive lending revenue. Recommendations must be unbiased. |
| Avoid causing foreseeable harm to retail customers | Simulator must not encourage over-borrowing; pre-approved offers must include affordability warnings; must not present offers to customers showing signs of financial distress |
| Enable and support retail customers to pursue their financial objectives | Core purpose of the product — must demonstrate measurable customer outcomes through score improvement and better product access |

The Duty also requires four outcomes: products and services, price and value, consumer understanding, and consumer support [5]. The Credit Coach must demonstrate fair value versus free alternatives (ClearScore, Credit Karma) if any fee is charged.

### 8.2 FCA CONC (Consumer Credit Sourcebook)

| Section | Requirement | Citation |
|---------|-------------|----------|
| CONC 3 — Financial promotions | Pre-approved offers are financial promotions and must be clear, fair, and not misleading. Must include representative APR, representative example, and give equal prominence to risks. Note: FCA is consulting on CONC 3 updates in 2026 to align with Consumer Duty [7]. | FCA Handbook CONC 3 |
| CONC 5 — Creditworthiness | Pre-approved offers must be based on adequate creditworthiness assessment covering both credit risk (likelihood of default) and affordability (ability to repay without hardship) — not just credit score [8]. This is the section generating the most FCA enforcement action [9]. | FCA Handbook CONC 5.2A |
| CONC 7 — Arrears and default | Alerts must not pressure customers in financial difficulty; must signpost to free debt advice (StepChange, Citizens Advice). Credit Coach must detect vulnerability indicators. | FCA Handbook CONC 7 |

### 8.3 UK GDPR, Data Protection Act 2018 & Data (Use and Access) Act 2025

**Important:** The Data (Use and Access) Act 2025 (DUAA), which received Royal Assent on 19 June 2025, amends the UK GDPR's automated decision-making framework [10]. ICO guidance is under review. The PM must track ICO updates as provisions are brought into force.

| Requirement | Implementation | Source |
|-------------|---------------|--------|
| Lawful basis | Explicit consent for CRA data retrieval (not legitimate interest — too intrusive for external credit data) | UK GDPR Art. 6, Art. 9 |
| Purpose limitation | CRA data used only for credit coaching; not cross-sold to marketing without separate consent | UK GDPR Art. 5(1)(b) |
| Data minimisation | Retrieve only score and factors needed, not full credit report unless customer requests | UK GDPR Art. 5(1)(c) |
| Right to erasure | Customer can delete score history and opt out at any time; CRA data not retained beyond refresh cycle | UK GDPR Art. 17 |
| DPIA required | Mandatory Data Protection Impact Assessment before launch — large-scale profiling of financial data triggers DPIA requirement | UK GDPR Art. 35 |
| Automated decision-making | Pre-approved offers involve automated profiling with legal/significant effect (credit access). Under current Art. 22(1), must provide meaningful information about logic, significance, and consequences; must offer human review route [11]. DUAA 2025 introduces a risk-based framework distinguishing low and high-risk ADM [10] — credit decisions are likely high-risk. | UK GDPR Art. 22; DUAA 2025 Sch. 6 |
| Transparency | Must inform customers at point of data collection about automated processing, including profiling for credit purposes | UK GDPR Art. 13(2)(f) |

### 8.4 Consumer Credit Act 1974 (CCA)

**Note:** HM Treasury is consulting on CCA reform [12]. The PM should monitor legislative changes that may affect pre-contract requirements.

| Requirement | Implication | Source |
|-------------|-------------|--------|
| Pre-contract information | Pre-approved offers for regulated credit agreements must include adequate pre-contract explanations via the Standard European Consumer Credit Information form (SECCI) | CCA s.55; Consumer Credit (Disclosure of Information) Regulations 2010 |
| Cooling-off period | 14-day withdrawal right must be clearly communicated at point of offer acceptance. Customer can cancel without giving reason. | CCA s.66A; Consumer Contracts Regulations 2013 |
| Credit broking | If Credit Coach recommends third-party products in future, Lloyds would need credit broking permissions under CCA | CCA s.145 |
| Unfair relationships | The court can assess whether the credit relationship is unfair to the debtor — AI-driven offers must not create unfair terms | CCA s.140A-C |

### 8.5 BoE/PRA/FCA Joint Feedback on AI/ML (FS2/23, October 2023)

The Bank of England, PRA, and FCA published joint feedback statement FS2/23 in October 2023, summarising responses to DP5/22 on AI and Machine Learning in financial services [13]. While FS2/23 does not contain binding rules, it signals regulatory expectations:

| Theme | Application to Credit Coach |
|-----------|-------------|
| Explainability | Score factors and simulation logic must be explainable to customers in plain language. "Black box" models are not acceptable for customer-facing credit decisions. |
| Fairness & bias | Improvement plans and offers must not discriminate on protected characteristics (Equality Act 2010); regular bias audits required across demographic groups |
| Human oversight | Escalation path to human adviser for complex credit situations; human-in-the-loop for edge cases |
| Data quality | CRA data inputs must be validated; stale or incorrect data must not drive recommendations |
| Model governance | Simulation models require validation, ongoing monitoring, and model risk management framework (see 8.6) |
| Third-party dependencies | CRA model reliance must be assessed and documented as a third-party risk |

### 8.6 PRA SS1/23 — Model Risk Management Principles for Banks (in force 17 May 2024)

SS1/23 sets out five principles for model risk management [14]. It applies to firms with internal model approval, but Lloyds should adopt it as best practice for the Credit Coach's simulation and offer-matching models:

| Principle | Application |
|-----------|-------------|
| Model identification & classification | Credit simulation models and offer-matching algorithms must be inventoried and risk-classified |
| Governance | Board-level accountability via appropriate SMF holder; model risk committee oversight |
| Model development & implementation | Documentation, testing, performance monitoring for all scoring/simulation models |
| Model use & ongoing monitoring | Continuous performance tracking; drift detection on CRA score predictions |
| Risk mitigation & reporting | Independent validation before deployment; periodic revalidation; reporting to audit committee [14] |

The principles also specifically address "identifying and managing the risks associated with the use of artificial intelligence (AI) in modelling techniques such as machine learning (ML)" [14].

### 8.7 Equality Act 2010

The Credit Coach must not directly or indirectly discriminate in the provision of services based on protected characteristics (age, disability, gender reassignment, marriage/civil partnership, pregnancy/maternity, race, religion/belief, sex, sexual orientation). This is particularly relevant for:
- Action plan recommendations (must not assume financial behaviour based on demographics)
- Pre-approved offer criteria (must not use proxies for protected characteristics)
- Score simulation outputs (must be tested for disparate impact)

---

## 9. Data Architecture Considerations

### 9.1 CRA Score Context

Each UK CRA uses a different scoring scale [4]:
- **Experian:** 0–1,250 (excellent: 1,121–1,250; updated from 999 scale in late 2025)
- **Equifax:** 0–1,000 (excellent: 811–1,000)
- **TransUnion:** 0–710 (excellent: 628–710)

The Credit Coach must normalise these into a consistent customer-facing representation, or clearly label which bureau's score is displayed.

### 9.2 Data Domains

| Data Domain | Source | Classification | Consent Model |
|-------------|--------|---------------|---------------|
| Credit score & factors | CRA (Experian/Equifax/TU) | Highly Confidential | Explicit opt-in per CRA |
| Score history | Derived (stored internally) | Confidential | Covered by initial consent |
| Transaction data | Lloyds core banking | Confidential | Existing T&Cs (legitimate interest) |
| Action plan state | Generated internally | Internal | No additional consent needed |
| Pre-approved offers | Lloyds product engine | Internal | Existing marketing preferences apply |
| Alert preferences | Customer input | Personal | Customer-controlled |

**Key principle:** Lloyds transaction data and CRA data are kept in separate domains. They are combined only in the presentation/coaching layer, never co-mingled in storage.

---

## 10. Overlap Resolution with Existing Financial Assistant

| Overlap Area | Resolution |
|-------------|-----------|
| Spending insights | Complement — FA describes spending; Credit Coach connects spending to credit impact. Integrated as "deeper dive" |
| Savings guidance | Complement — FA is product-focused; Credit Coach is score-focused. FA recommends saving → Credit Coach shows credit benefit |
| Conversational interface | Credit Coach is a module within FA, not a separate chat. Orchestrator routes credit queries to Credit Coach agent |
| Competing recommendations | Unified recommendation engine weighs both perspectives. Credit health takes priority when score is below threshold |
| Offer timing | Credit Coach acts as pre-qualification gate — FA only shows products the customer actually qualifies for |

---

## 11. Success Metrics

| Metric | Target | Timeframe |
|--------|--------|-----------|
| Customer enrolment (opt-in to score monitoring) | 2M customers | 6 months post-launch |
| Score improvement | 60% of active users improve score within 6 months | Ongoing |
| Pre-approved offer conversion rate | 15%+ (vs 2-3% for cold marketing) | Steady state |
| Customer satisfaction (CSAT) | 4.5/5 for credit coaching interactions | Ongoing |
| Reduction in declined applications | 30% fewer declines from coached customers | 12 months |
| Third-party credit app usage reduction | 20% reduction in ClearScore/Credit Karma usage among enrolled customers | 12 months |

---

## 12. Phased Delivery Roadmap

| Phase | Scope | Timeline |
|-------|-------|----------|
| **Phase 1 — Monitor** | Credit score dashboard, score factors, monthly alerts, score history | 3 months |
| **Phase 2 — Coach** | Personalised action plans, progress tracking, milestone celebrations | +2 months |
| **Phase 3 — Simulate** | What-if engine, natural language scenario input | +2 months |
| **Phase 4 — Convert** | Pre-approved offers engine, one-tap application, offer audit trail | +3 months |
| **Phase 5 — Optimise** | Multi-bureau comparison, advanced alerts, cross-product recommendations | +3 months |

---

## 13. Key Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| CRA integration delays | Medium | High | Engage CRA partners early; start with single bureau, expand later |
| Regulatory challenge on automated offers | Medium | High | Early FCA engagement; conservative initial offer criteria; human review fallback |
| Customer distrust of AI credit advice | Medium | Medium | Transparent explanations; "how we calculated this" for every recommendation; human handoff |
| Model bias in improvement plans | Low | High | Regular bias audits; diverse training data; protected characteristic monitoring |
| Data breach of credit data | Low | Critical | Encryption at rest/transit; minimal data retention; separate data domain; penetration testing |
| Cannibalisation of existing lending marketing | Low | Medium | Measure incremental revenue; pre-approved offers should increase conversion, not replace marketing |

---

## 14. Dependencies

| Dependency | Owner | Status |
|-----------|-------|--------|
| CRA partnership agreement (Experian/Equifax/TU) | Commercial & Legal | To be initiated |
| Envoy platform access & agent template | AI Platform team | Available (launched May 2026 [2]) |
| Existing FA orchestrator API access | AI Platform team | Available |
| Lloyds product eligibility engine API | Lending Products | Exists, needs Credit Coach integration |
| Push notification infrastructure | Mobile Platform | Available |
| DPIA completion | Data Protection Office | Required before build |
| FCA regulatory review of offer mechanics | Compliance | Required before Phase 4 |
| ICO guidance on DUAA 2025 ADM provisions | Legal / DPO | Awaiting ICO final guidance [10] |

---

## 15. Stakeholders

| Role | Interest |
|------|----------|
| Product Owner | Owns backlog, prioritises features, defines acceptance criteria |
| AI Platform Team | Provides orchestrator integration, model hosting, guardrails |
| Lending Products | Defines offer criteria, product eligibility rules |
| Compliance & Legal | Regulatory sign-off, financial promotion approval |
| Data Protection Office | DPIA, consent mechanism design, data retention policies |
| CRA Partners | API access, data licensing, SLA agreements |
| Customer Experience | UI/UX design, accessibility, customer research |
| Risk | Model risk management, credit risk implications |

---

## 16. Next Steps

1. **Product Owner** to review this vision and confirm scope boundaries
2. **Compliance** to conduct initial regulatory feasibility assessment
3. **Architecture** to produce detailed technical design for Phase 1
4. **Commercial** to initiate CRA partnership discussions
5. **BA** to decompose Phase 1 into epics and user stories
6. **DPO** to begin DPIA process

---

*This document serves as the product introduction. It will be decomposed into epics, user stories, and technical specifications for implementation across frontend, backend API, and data persistence layers.*

---

## References

| # | Source | URL |
|---|--------|-----|
| [1] | FinTech Futures, "Lloyds Banking Group to launch AI financial assistant in 2026", 6 Nov 2025 | https://www.fintechfutures.com/ai-in-fintech/lloyds-banking-group-to-launch-ai-financial-assistant-in-2026 |
| [2] | Bobsguide, "Lloyds Unveils Envoy: Scaling Agentic AI with Governance at the Core", 5 May 2026 | https://www.bobsguide.com/lloyds-unveils-envoy-scaling-agentic-ai-with-governance-at-the-core/ |
| [3] | FinancialIT, "Experian and OpenAI Launch the UK's First Credit Score App in ChatGPT", 13 Mar 2026 | https://financialit.net/news/lending/experian-and-openai-launch-uks-first-credit-score-app-chatgpt |
| [4] | TransUnion UK, "Credit Score FAQ" / Debt Camel, "Best free ways to check your credit score" | https://www.transunion.co.uk/consumer/credit-score-faq |
| [5] | FCA, "PS22/9: A new Consumer Duty", 27 Jul 2022 | https://www.fca.org.uk/publications/policy-statements/ps22-9-new-consumer-duty |
| [6] | BCLP Law, "What will the disputes landscape look like for firms subject to the Consumer Duty?" | https://www.bclplaw.com/en-US/insights/shifting-sands-what-will-the-disputes-landscape-look-like-for-firms-subject-to-the-consumer-duty.html |
| [7] | LexisNexis, "The regulation of consumer credit advertisements" (FCA consulting on CONC 3, March 2026) | https://www.lexisnexis.co.uk/legal/guidance/the-regulation-of-consumer-credit-advertisements |
| [8] | MEMA Consultants, "Consumer Credit Affordability: FCA Expectations and Implementation" | https://memaconsultants.com/resources/explainers/consumer-credit-affordability |
| [9] | MEMA Consultants, "CONC: Consumer Credit Sourcebook Requirements for UK Firms" | https://memaconsultants.com/resources/explainers/conc-consumer-credit |
| [10] | ICO, "Data (Use and Access) Act 2025 — Summary of changes: Data protection" | https://ico.org.uk/about-the-ico/what-we-do/legislation-we-cover/data-use-and-access-act-2025/the-data-use-and-access-act-2025-duaa-summary-of-the-changes/data-protection/ |
| [11] | ICO, "What does the UK GDPR say about automated decision-making and profiling?" | https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/individual-rights/automated-decision-making-and-profiling/what-does-the-uk-gdpr-say-about-automated-decision-making-and-profiling/ |
| [12] | UK Parliament, House of Commons Library, "Consumer credit law reform" | https://commonslibrary.parliament.uk/research-briefings/cbp-10328/ |
| [13] | Bank of England, "FS2/23 – Artificial Intelligence and Machine Learning", 26 Oct 2023 | https://www.bankofengland.co.uk/prudential-regulation/publication/2023/october/artificial-intelligence-and-machine-learning |
| [14] | Bank of England, "PS6/23 – Model risk management principles for banks" (SS1/23 in force 17 May 2024) | https://bankofengland.co.uk/prudential-regulation/publication/2023/may/model-risk-management-principles-for-banks |

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 5 May 2026 | Prateek Sharma | Initial draft |
| 1.1 | 5 May 2026 | Prateek Sharma | Added citations, DUAA 2025 implications, Envoy platform context, Equality Act 2010, CRA score scales, corrected FS2/23 attribution |
