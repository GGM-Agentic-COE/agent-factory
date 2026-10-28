# Vision Document: Omnichannel Loyalty Rewards

## Executive Summary

Omnichannel Loyalty Rewards is a customer retention platform that enables customers to earn and redeem points across online and in-store purchase channels. The program addresses declining repeat purchase rates driven by competitive loyalty offerings in the retail market. By unifying customer identity and transaction data across channels, the platform will enable store staff to recognize high-value customers at point-of-sale and provide differentiated service, while driving mobile app adoption through exclusive digital benefits. Expected outcomes include 15-20% increase in repeat purchase frequency within 12 months and 25% growth in mobile app active users.

## Business Context

### Problem Statement

Current repeat customer rate has declined 18% year-over-year as competitors have launched loyalty programs offering 5-10% effective discount rates through points redemption. Customer purchase data shows online and in-store systems operate in silos—67% of customers who purchase in both channels are not recognized as the same individual, resulting in fragmented customer profiles and inability to reward cross-channel behavior. Store associates lack real-time visibility into customer lifetime value and loyalty status during in-person interactions, missing opportunities to provide differentiated service to high-value segments. Mobile app engagement remains at 23% of total customer base despite representing the highest lifetime value cohort (2.3x average order value).

### Business Drivers

Market analysis indicates loyalty program members spend 12-18% more annually than non-members and exhibit 2.5x higher retention rates. Competitive pressure is acute—four of five primary competitors launched or enhanced loyalty programs in the past 18 months. Customer research shows 72% of respondents would increase purchase frequency if a points-based rewards program were available. The business case projects £2.4M incremental annual revenue from a 15% increase in repeat purchase rate, with program costs (technology, operations, rewards liability) estimated at £680K annually, yielding a 3.5:1 return on investment. Regulatory environment requires compliance with UK GDPR for customer data processing, FCA financial promotions rules (CONC 3) if points have monetary value, and PSD2 Strong Customer Authentication for account access and redemption transactions.

### Target Users and Stakeholders

| User Type | Description | Primary Need |
|-----------|-------------|--------------|
| Retail Customer (Member) | Individual who enrolls in loyalty program and earns/redeems points through purchases | Transparent points earning rules, easy redemption process, visibility of points balance and transaction history across all channels |
| Store Associate | Front-line staff processing in-store transactions and assisting customers | Real-time customer identification at POS, visibility of loyalty tier and lifetime value, ability to manually adjust points for service recovery |
| Store Manager | Manages store operations and staff performance | Dashboard showing store-level loyalty enrollment rates, redemption patterns, and impact on sales metrics |
| E-commerce Customer | Online shopper who may or may not also shop in-store | Frictionless enrollment during checkout, automatic points crediting, mobile app integration for digital-first experience |
| Loyalty Program Manager | Business owner responsible for program design, performance, and ROI | Configuration tools for earning/redemption rules, tier thresholds, promotional campaigns; analytics on member behavior and program economics |
| Customer Service Agent | Handles inquiries, disputes, and account issues across phone, email, and chat channels | Unified view of customer account, transaction history, points adjustments, ability to resolve disputes and process manual credits |
| Marketing Manager | Drives customer acquisition, engagement, and retention campaigns | Segmentation tools based on loyalty behavior, campaign management for targeted offers, measurement of campaign impact on points activity |
| Finance/Accounting | Manages rewards liability, revenue recognition, and financial reporting | Points liability tracking, breakage analysis, reconciliation of points issued vs redeemed, financial reporting on program costs |

### Business Constraints

**Budget**: Initial implementation budget capped at £450K capital expenditure (technology platform, integration, testing) with £180K annual operating budget (hosting, support, ongoing development). Rewards liability reserve must be established at 85% of outstanding points value based on historical breakage assumptions from comparable programs.

**Regulatory**: Customer data processing must comply with UK GDPR including lawful basis (legitimate interest for program operation, consent for marketing), data subject rights (access, erasure, portability), and retention limits (active members + 2 years post-closure). If points are redeemable for cash or cash-equivalent, program may fall under FCA financial promotions rules requiring clear terms, representative examples, and fair treatment. PSD2 Strong Customer Authentication required for account login and redemption transactions exceeding £30 value.

**Timeline**: MVP launch required within 6 months to align with peak holiday shopping season (October launch target). Full vision features to be delivered in 3 phases over 18 months.

**Organizational**: Online and in-store systems currently operate on separate technology stacks (e-commerce platform: Shopify; POS system: legacy proprietary system with limited API capabilities). IT team consists of 4 developers with limited availability (60% allocated to BAU maintenance). No existing customer data platform—customer records fragmented across 5 systems. Store staff training must be completed within 2-week window to minimize disruption.

**Technical**: POS system API supports read-only customer lookup but write operations (points crediting) require batch file processing with 4-hour delay. Mobile app exists but has not been updated in 18 months; requires modernization to support loyalty features. No real-time event streaming infrastructure—current architecture is batch-oriented with daily data synchronization.

### Success Metrics

| Metric | Current State | Target State (12 months) | Measurement Method |
|--------|---------------|--------------------------|-------------------|
| Repeat purchase rate (90-day) | 34% | 45% | Percentage of customers making 2+ purchases within 90-day rolling window, measured via unified customer ID across channels |
| Average customer lifetime value | £340 | £425 | Total revenue per customer from enrollment through measurement date, segmented by member vs non-member cohorts |
| Mobile app monthly active users | 23,000 (23% of customer base) | 35,000 (35% of customer base) | Unique users opening app at least once per month, measured via app analytics platform |
| Program enrollment rate | 0% (no program exists) | 60% of transacting customers | Percentage of customers who complete enrollment within 30 days of first purchase |
| Cross-channel customer recognition rate | 33% (estimated via email matching) | 85% | Percentage of customers who purchase in both online and in-store channels correctly linked to single customer profile |
| In-store loyalty identification rate | N/A | 70% | Percentage of in-store transactions where customer is identified as loyalty member at POS (via card scan, phone lookup, or app) |
| Points redemption rate (annual) | N/A | 35% | Percentage of points issued in trailing 12 months that are redeemed within same period (indicates engagement and perceived value) |
| Net Promoter Score (loyalty members) | N/A | +40 | NPS survey administered to loyalty members quarterly, measuring likelihood to recommend program |

## Full Scope Vision

### Product Vision Statement

Omnichannel Loyalty Rewards will become the primary driver of customer retention and lifetime value growth by creating a unified, friction-free rewards experience that recognizes and rewards every customer interaction—whether shopping online, in-store, or via mobile app. The platform will transform store associates into customer advocates armed with real-time insights, enable marketing to deliver hyper-personalized offers based on true cross-channel behavior, and provide customers with transparent, flexible redemption options that enhance rather than complicate their shopping experience. By treating loyalty data as a strategic asset and the program as a continuous dialogue rather than a transactional mechanism, we will shift customer perception from \"where can I get the best deal today\" to \"this brand knows me and values my business.\"

### Feature Areas

#### Member Enrollment and Identity Management

Customers can enroll in the loyalty program through multiple touchpoints: during online checkout, via mobile app, at in-store POS, or through a dedicated web portal. Enrollment captures essential profile data (name, email, phone, postal code) and establishes a unique member ID. The system performs real-time deduplication to prevent duplicate accounts and links existing purchase history where possible.

**Key capabilities:**
- Multi-channel enrollment with progressive profiling (capture minimum data upfront, enrich over time)
- Identity verification via email/SMS OTP to prevent fraud
- Automatic linking of pre-enrollment purchase history using email/phone matching
- Household linking to allow family members to pool points (optional feature)
- Guest-to-member conversion flow for customers who initially checkout as guest
- GDPR-compliant consent management with granular opt-ins for marketing communications

**User value:** Customers can join instantly without disrupting their purchase journey, and immediately see value through recognition of past purchases. Reduced friction increases enrollment conversion rates.

#### Points Earning Engine

Customers earn points on qualifying purchases across all channels based on configurable earning rules. The engine supports multiple earning mechanisms: base earn rate (e.g., 1 point per £1 spent), category multipliers (e.g., 2x points on sale items), tier bonuses (e.g., gold members earn 1.5x), promotional campaigns (e.g., triple points weekend), and non-transactional earning (e.g., points for app download, birthday bonus, referrals).

**Key capabilities:**
- Real-time points calculation and crediting for online purchases
- Near-real-time crediting for in-store purchases (within 4 hours given POS constraints, with path to real-time in Phase 2)
- Configurable earning rules engine with support for complex logic (spend thresholds, product categories, customer segments, time-based promotions)
- Retroactive points crediting for purchases made before enrollment (trailing 90 days)
- Points expiration policies with advance notification (e.g., points expire 24 months from earn date)
- Audit trail of all points transactions for compliance and dispute resolution

**User value:** Customers understand exactly how they earn points and see immediate credit, building trust and encouraging repeat purchases. Flexible rules enable marketing to drive specific behaviors.

#### Points Redemption and Rewards Catalog

Members can redeem points for rewards through multiple mechanisms: discount on current purchase (online or in-store), statement credit applied to account, early access to sales, exclusive products, or partner rewards (e.g., charity donations, gift cards). The rewards catalog is dynamically configured with redemption thresholds and availability rules.

**Key capabilities:**
- Real-time redemption at online checkout (apply points as discount before payment)
- In-store redemption via POS integration (associate-initiated or customer-scanned barcode)
- Mobile app redemption for digital rewards (coupons, early access codes)
- Tiered rewards catalog with aspirational high-value rewards to drive engagement
- Partial redemption support (use points + cash for single transaction)
- Redemption restrictions (e.g., cannot redeem on sale items, minimum purchase thresholds)
- Rewards inventory management to prevent over-redemption of limited-availability items

**User value:** Customers have flexibility in how they use points, with clear value proposition (e.g., 100 points = £1 discount). Aspirational rewards create emotional connection beyond transactional discounts.

#### Omnichannel Customer Recognition

The platform provides multiple methods for customers to identify themselves across channels, with system automatically linking all activity to their unified profile. Recognition methods include: loyalty card barcode scan, phone number lookup, email lookup, mobile app QR code, and passive recognition via logged-in web session or app.

**Key capabilities:**
- Store associate tools for customer lookup by phone, email, or name (with disambiguation for common names)
- Mobile app QR code generation for fast in-store scanning
- Physical loyalty card issuance (optional, for customers who prefer card)
- Automatic recognition for logged-in online sessions
- Fallback mechanisms when primary identification fails (e.g., manual points crediting via receipt upload)
- Real-time customer profile display showing tier, points balance, recent activity, and lifetime value
- Privacy controls allowing customers to opt-out of in-store recognition while maintaining online benefits

**User value:** Customers are recognized regardless of how they shop, eliminating frustration of \"I have an account but can't access it.\" Store associates can provide personalized service based on customer history.

#### Tiered Membership Levels

The program includes multiple membership tiers (e.g., Silver, Gold, Platinum) with qualification thresholds based on annual spend or points earned. Higher tiers unlock incremental benefits such as accelerated earning rates, exclusive redemption options, free shipping, priority customer service, and early access to sales.

**Key capabilities:**
- Automatic tier calculation and promotion based on rolling 12-month activity
- Tier retention grace period (e.g., 3 months to re-qualify before demotion)
- Tier status display across all customer touchpoints (app, web, POS, email)
- Tier-specific earning multipliers and redemption options
- Tier benefits catalog with clear value communication
- Tier challenge campaigns (e.g., \"Spend £200 more to reach Gold by month-end\")

**User value:** Tiers create aspirational goals and reward best customers with meaningful benefits, driving increased spend to reach next tier. Status recognition provides emotional value beyond points.

#### Loyalty Analytics and Insights Dashboard

Business users access a comprehensive analytics platform showing program performance, member behavior, and financial metrics. Dashboards support multiple user personas (executive summary, program manager deep-dive, store manager local view, finance liability tracking).

**Key capabilities:**
- Real-time program KPIs (enrollment rate, active members, points issued/redeemed, redemption rate)
- Member segmentation and cohort analysis (RFM scoring, tier distribution, channel preference)
- Campaign performance measurement (promotional earn campaigns, targeted offers)
- Financial reporting (points liability, breakage rate, cost per point, ROI by member segment)
- Predictive analytics (churn risk scoring, lifetime value prediction, next-best-action recommendations)
- Store-level performance comparison (enrollment rates, redemption rates, impact on basket size)
- A/B testing framework for program rule changes

**User value:** Business users can optimize program economics, identify high-value segments, and make data-driven decisions on rule changes and promotional investments.

#### Customer Communication and Engagement

The platform orchestrates personalized communications across email, SMS, push notifications, and in-app messages based on member behavior and lifecycle stage. Communication types include: welcome series, points balance updates, tier status changes, expiration warnings, promotional offers, and re-engagement campaigns.

**Key capabilities:**
- Event-driven messaging triggered by member actions (enrollment, tier promotion, points expiration approaching)
- Segmented campaign delivery based on member attributes and behavior
- Multi-channel orchestration with preference management (customer controls channel and frequency)
- Regulatory compliance for marketing communications (GDPR consent, opt-out mechanisms, FCA financial promotions rules)
- Message personalization with dynamic content (name, points balance, tier status, recommended actions)
- Communication effectiveness measurement (open rates, click-through rates, conversion rates)

**User value:** Customers receive relevant, timely information that helps them maximize program value without feeling spammed. Clear communication builds trust and engagement.

### Integration Points

**E-commerce Platform (Shopify)**: Bi-directional integration for enrollment during checkout, real-time points earning on order completion, redemption as discount code, member profile display on account page, and order history synchronization.

**Point-of-Sale System (Legacy Proprietary)**: Customer lookup API for member identification, batch file export for transaction data (4-hour delay), batch file import for points crediting, and associate dashboard for member profile display.

**Mobile Application (Native iOS/Android)**: Embedded loyalty module showing points balance, transaction history, rewards catalog, QR code for in-store identification, and push notification receiver for engagement campaigns.

**Customer Data Platform (To Be Implemented)**: Unified customer profile creation, cross-channel identity resolution, customer 360-degree view, and segmentation engine for marketing campaigns.

**Payment Gateway**: Transaction amount and payment method data for points calculation, fraud signal integration to prevent points abuse, and refund event handling for points reversal.

**Email Service Provider (ESP)**: Transactional and promotional email delivery, template management, personalization engine, and delivery/engagement metrics.

**SMS Gateway**: OTP delivery for identity verification, transactional SMS for points updates, and promotional SMS for campaigns.

**Customer Relationship Management (CRM)**: Customer service agent access to loyalty profile, ticket creation for disputes, and resolution workflow integration.

**Business Intelligence Platform**: Data warehouse integration for historical reporting, dashboard embedding, and predictive model deployment.

**Fraud Detection System**: Real-time fraud scoring for enrollment and redemption transactions, velocity checks for abuse prevention, and suspicious activity alerting.

### User Journeys (Full Vision)

#### Journey 1: New Customer Enrollment and First Reward (Online)

1. Customer browses website and adds items to cart (not logged in, first-time visitor)
2. At checkout, prominent banner displays: \"Join Loyalty Rewards and earn 200 points on this order (worth £2)\"
3. Customer clicks \"Join Now\" and modal appears requesting email, phone, and postal code
4. Customer enters details and checks consent boxes (program terms, marketing opt-in optional)
5. System sends OTP to email and phone for verification
6. Customer enters OTP and enrollment completes
7. System automatically searches past 90 days for orders matching email/phone and links 2 previous orders worth 350 points
8. Checkout page updates showing \"You've earned 550 points total! (350 from past orders + 200 from this order)\"
9. Customer completes purchase and receives welcome email with points balance and tier status (Silver)
10. Customer downloads mobile app (prompted in welcome email) and logs in to see full transaction history

**Outcome:** Customer is enrolled, sees immediate value from retroactive points, and is engaged with mobile app—all within a single session.

#### Journey 2: In-Store VIP Recognition and Redemption

1. Gold-tier member enters store and approaches checkout with £150 of merchandise
2. Store associate scans first item and POS prompts: \"Ask customer for loyalty identification\"
3. Customer opens mobile app and displays QR code
4. Associate scans QR code and POS displays: \"Welcome back, Sarah! Gold Member | 2,450 points | Lifetime value: £1,840\"
5. Associate greets customer by name and mentions Gold status: \"Thanks for being a Gold member, Sarah\"
6. POS calculates points to be earned: 225 points (150 base + 75 Gold bonus at 1.5x rate)
7. Associate mentions: \"You'll earn 225 points on this purchase, bringing you to 2,675 points—enough for £25 off your next purchase\"
8. Customer asks: \"Can I use points today?\" Associate confirms: \"Absolutely! You can redeem 2,000 points for £20 off this purchase\"
9. Customer agrees, associate applies redemption, final total is £130
10. Customer receives SMS receipt showing transaction, points redeemed, points earned, and new balance (675 points)
11. Three days later, customer receives email: \"You're only £50 away from Platinum status—enjoy free shipping and early sale access!\"

**Outcome:** Customer feels recognized and valued, receives personalized service, and is motivated to reach next tier through clear progress communication.

### Scalability and Growth

**Geographic Expansion**: Platform designed to support multi-region deployment with localized currency, language, and regulatory compliance (GDPR, local consumer protection laws). Points earning/redemption rules configurable per region.

**Partner Ecosystem**: Architecture supports coalition loyalty model where partner merchants can issue and accept points, expanding earning/redemption opportunities beyond owned channels. Partner API enables third-party integration.

**Product Line Expansion**: As business launches new product categories or sub-brands, loyalty program can support category-specific earning multipliers, exclusive rewards, and cross-category engagement campaigns.

**B2B Loyalty Extension**: Platform can be extended to support trade/wholesale customer loyalty with different earning mechanics (volume-based, contract compliance), redemption options (invoice credits, exclusive inventory access), and account hierarchies.

**Subscription Integration**: Future subscription services (e.g., premium membership, auto-replenishment) can leverage loyalty data for targeting and offer points as subscription benefits.

**Gamification Layer**: Advanced engagement features such as challenges, badges, leaderboards, and social sharing can be added to drive non-transactional engagement and community building.

**AI-Driven Personalization**: Machine learning models can optimize next-best-action recommendations, personalized earning multipliers, churn prevention interventions, and dynamic reward suggestions based on individual preferences.

### Long-Term Roadmap

| Phase | Focus | Timeframe |
|-------|-------|-----------|
| Phase 1 (MVP) | Core enrollment, earning, redemption; online and in-store basic integration; manual store associate tools | Months 1-6 |
| Phase 2 (Omnichannel) | Real-time POS integration, mobile app QR code, tiered membership, customer-facing dashboards, automated communications | Months 7-12 |
| Phase 3 (Optimization) | Advanced analytics, predictive models, A/B testing framework, partner integrations, gamification elements | Months 13-18 |
| Phase 4 (Ecosystem) | Coalition loyalty with external partners, B2B extension, subscription integration, API marketplace | Months 19-24 |
| Phase 5 (Intelligence) | AI-driven personalization, dynamic pricing integration, real-time offer optimization, voice/conversational interfaces | Months 25-36 |

## MVP Scope

### MVP Objective

Launch a functional loyalty program within 6 months that enables customers to enroll, earn points on purchases (online and in-store), view their points balance, and redeem points for discounts, while providing store associates with basic customer identification capabilities—validating core value proposition and establishing foundation for omnichannel expansion.

### MVP Success Criteria

- [ ] 10,000 customers enrolled within first 30 days of launch
- [ ] 60% of enrolled customers earn points on at least one additional purchase within 90 days (repeat purchase validation)
- [ ] 25% of enrolled customers redeem points at least once within 90 days (engagement validation)
- [ ] 50% of in-store transactions successfully identify customer as loyalty member when customer presents phone number (recognition validation)
- [ ] Store associate satisfaction score ≥7/10 on ease-of-use survey (operational feasibility validation)
- [ ] Zero data breaches or GDPR compliance violations (regulatory compliance validation)
- [ ] Points liability reconciliation accurate within 1% variance (financial control validation)
- [ ] System uptime ≥99.5% during business hours (reliability validation)

### Features In Scope (MVP)

| Feature | Description | Priority | Rationale |
|---------|-------------|----------|-----------|
| Online enrollment during checkout | Customer can join loyalty program during checkout flow by providing email, phone, postal code; OTP verification required | P0 | Primary enrollment channel; captures customers at moment of purchase intent |
| Points earning on online purchases | Automatic points crediting (1 point per £1 spent) when order completes; visible in confirmation email and account page | P0 | Core value proposition; must demonstrate immediate value to drive adoption |
| Points earning on in-store purchases (batch) | Store transactions exported nightly, points credited within 24 hours; customer receives SMS notification | P0 | Enables omnichannel earning despite POS limitations; acceptable delay for MVP |
| Phone number lookup at POS | Store associate can enter customer phone number to retrieve member profile (name, points balance, recent purchases) | P0 | Minimum viable recognition; enables personalized service without requiring new hardware |
| Points balance display (web and app) | Customer can view current points balance, transaction history (last 10 transactions), and points expiration date on account page and mobile app | P0 | Transparency builds trust; customers must be able to verify points are being credited |
| Points redemption at online checkout | Customer can apply points as discount (100 points = £1) during checkout; minimum redemption 500 points | P0 | Core value proposition; must enable customers to realize value from points earned |
| Basic member profile management | Customer can update email, phone, postal code, and communication preferences via account settings | P1 | Required for GDPR compliance (data accuracy, preference management) |
| Welcome email automation | Automated email sent upon enrollment with program overview, points balance, and link to terms | P1 | Sets expectations and provides reference for program rules |
| Points expiration (24-month policy) | Points expire 24 months from earn date; customer notified 60 days and 30 days before expiration | P1 | Manages liability and creates urgency; industry-standard policy |
| Store associate training portal | Web-based training module covering customer lookup, program overview, and common scenarios | P1 | Ensures consistent customer experience and reduces support burden |
| Admin configuration panel | Program manager can update earning rate, redemption rate, and expiration policy via admin UI | P2 | Enables business flexibility without engineering changes; not required for launch but valuable for iteration |
| Transaction history export | Customer can download CSV of all points transactions for personal records | P2 | GDPR data portability requirement; low usage expected but legally required |

### Features Explicitly Out of Scope

| Feature | Reason for Deferral | Target Phase |
|---------|---------------------|--------------|
| Tiered membership (Silver/Gold/Platinum) | Adds complexity to earning rules, communications, and customer understanding; requires historical data to set meaningful thresholds | Phase 2 (Month 7-12) |
| Real-time in-store points crediting | POS system API limitations require batch processing; real-time requires POS upgrade or middleware investment beyond MVP budget | Phase 2 (Month 7-12) |
| Mobile app QR code for in-store identification | Requires mobile app development (4-6 weeks) and POS barcode scanner integration; phone lookup sufficient for MVP | Phase 2 (Month 7-12) |
| Retroactive points for pre-enrollment purchases | Requires historical transaction data cleanup and complex matching logic; high error risk; defer until core flows proven | Phase 2 (Month 7-12) |
| In-store redemption at POS | POS system does not support real-time discount application; requires significant integration work; customers can redeem online in MVP | Phase 2 (Month 7-12) |
| Category-specific earning multipliers | Adds complexity to rules engine and customer communication; base earn rate sufficient to validate demand | Phase 3 (Month 13-18) |
| Promotional campaigns (bonus points events) | Requires campaign management tools and scheduling logic; focus MVP on always-on base program | Phase 3 (Month 13-18) |
| Referral program (earn points for friend sign-ups) | Requires fraud prevention, attribution logic, and promotional mechanics; defer until member base established | Phase 3 (Month 13-18) |
| Partner rewards (gift cards, charity donations) | Requires partner agreements, inventory management, and fulfillment workflows; discount redemption sufficient for MVP | Phase 4 (Month 19-24) |
| Household account linking | Complex identity resolution and privacy implications; low demand signal in research | Phase 4 (Month 19-24) |
| Predictive analytics and churn models | Requires 6-12 months of behavioral data to train models; no data exists pre-launch | Phase 5 (Month 25-36) |

### MVP User Journeys

#### MVP Journey 1: Online Enrollment and First Redemption

1. Customer adds £80 of items to cart and proceeds to checkout
2. Enrollment banner displays: \"Join Loyalty Rewards and earn 80 points on this order\"
3. Customer clicks \"Join Now,\" enters email and phone, receives OTP via email
4. Customer enters OTP, enrollment completes, checkout shows \"You've earned 80 points!\"
5. Customer completes purchase and receives confirmation email with points balance
6. Two weeks later, customer returns to site, adds £60 of items to cart
7. At checkout, customer is logged in and sees: \"You have 140 points (£1.40 value). Redeem now?\"
8. Customer clicks \"Redeem 100 points\" and sees discount applied: subtotal £60, discount -£1, total £59
9. Customer completes purchase and receives email: \"You redeemed 100 points and earned 60 new points. New balance: 100 points\"

**Limitations vs Full Vision:** No retroactive points from past purchases. No tier status or accelerated earning. No in-store redemption option.

#### MVP Journey 2: In-Store Recognition (Phone Lookup)

1. Customer brings £120 of merchandise to checkout
2. Store associate scans items and asks: \"Are you a loyalty member? I can look you up by phone number\"
3. Customer provides phone number (07700 900123)
4. Associate enters phone into POS lookup tool, system displays: \"Jane Smith | 340 points | Member since: 15 Sept 2024\"
5. Associate greets customer by name: \"Thanks for being a member, Jane\"
6. Associate completes transaction and informs: \"You'll earn 120 points on this purchase, credited within 24 hours\"
7. Customer receives SMS next morning: \"Your purchase of £120 earned 120 points. New balance: 460 points\"

**Limitations vs Full Vision:** No real-time points crediting. No tier status display. No in-store redemption. Associate must manually enter phone number (no QR code scan).

### MVP Constraints and Assumptions

**Constraint:** POS system API is read-only for customer lookup; points crediting requires batch file processing with 4-24 hour delay.  
**Risk if wrong:** If delay exceeds 24 hours regularly, customer trust erodes and in-store value proposition weakens. Mitigation: SMS notification when points credited provides closure; monitor batch job SLA daily.

**Constraint:** Mobile app has not been updated in 18 months and requires 6-week modernization effort before loyalty features can be added.  
**Risk if wrong:** If app is more technically degraded than assessed, timeline extends or MVP must launch without app support. Mitigation: Conduct technical assessment in Week 1; if app cannot be ready, defer app features to Phase 2 and focus on web experience.

**Assumption:** 60% of customers will provide phone number at in-store checkout when asked by associate.  
**Risk if wrong:** If adoption is lower (e.g., 30%), in-store recognition fails and value proposition weakens. Mitigation: Train associates on value-based ask (\"I can look up your points balance\"); monitor adoption weekly and adjust training if needed.

**Assumption:** Customers will tolerate 24-hour delay for in-store points crediting in MVP.  
**Risk if wrong:** If customers expect immediate crediting and complain, satisfaction and trust decline. Mitigation: Set clear expectations at enrollment (\"In-store points credited within 24 hours\"); monitor customer service tickets for complaints.

**Assumption:** Email and phone number are sufficient for identity verification; no government ID required.  
**Risk if wrong:** If fraud is high (fake accounts, points abuse), program economics deteriorate. Mitigation: Implement velocity checks (max 3 accounts per phone/email); monitor for suspicious patterns; add stricter verification in Phase 2 if needed.

**Constraint:** No existing customer data platform; customer profiles fragmented across 5 systems.  
**Risk if wrong:** If data quality is worse than expected, duplicate accounts proliferate and customer experience suffers. Mitigation: Implement fuzzy matching on email/phone during enrollment; manual deduplication process for first 90 days; prioritize CDP implementation in Phase 2.

**Assumption:** Store associates can be trained on phone lookup process within 2-week window without disrupting operations.  
**Risk if wrong:** If training is insufficient, associates don't ask for phone numbers or make errors, undermining in-store experience. Mitigation: Develop 15-minute video training + 1-page quick reference guide; conduct train-the-trainer sessions with store managers; provide support hotline for first 30 days.

**Constraint:** £450K capital budget must cover platform implementation, integrations, and testing.  
**Risk if wrong:** If integration complexity is underestimated (especially POS), budget overruns and scope must be cut. Mitigation: Prioritize online experience if budget pressured; defer in-store features to Phase 2; negotiate fixed-price contracts with integration vendors.

### MVP Definition of Done

- [ ] Customer can enroll via online checkout with email/phone/postal code capture and OTP verification
- [ ] Customer automatically earns 1 point per £1 spent on completed online orders
- [ ] Customer can view points balance and transaction history on web account page and mobile app
- [ ] Customer can redeem points (100 points = £1 discount, minimum 500 points) at online checkout
- [ ] Store associate can look up customer by phone number and view name, points balance, and member since date
- [ ] In-store transactions are exported nightly and points credited within 24 hours with SMS notification to customer
- [ ] Points expire 24 months from earn date with automated email notifications at 60 days and 30 days before expiration
- [ ] Customer can update profile information (email, phone, postal code) and communication preferences
- [ ] Welcome email sent automatically upon enrollment with program overview and terms link
- [ ] Admin user can update earning rate, redemption rate, and expiration policy via configuration panel
- [ ] All customer data processing complies with UK GDPR (lawful basis documented, consent captured, data retention policy enforced)
- [ ] System logs all points transactions with timestamp, amount, reason, and reference for audit trail
- [ ] Load testing completed for 500 concurrent users (10x expected peak during launch)
- [ ] Security testing completed including penetration test and OWASP Top 10 vulnerability scan
- [ ] Store associate training materials published and train-the-trainer sessions completed for all store managers
- [ ] Customer-facing terms and conditions reviewed by legal and published
- [ ] Points liability tracking implemented in finance system with daily reconciliation report
- [ ] Rollback plan documented and tested for critical failure scenarios

## Risks and Dependencies

### Key Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| POS integration more complex than estimated, causing delays or requiring scope reduction | High | High | Conduct technical discovery with POS vendor in Week 1; if API limitations confirmed, deprioritize real-time in-store features and focus on batch processing; allocate 20% contingency buffer in integration timeline |
| Low enrollment conversion rate (<40%) due to friction in checkout flow or unclear value proposition | Medium | High | A/B test enrollment messaging and placement during beta; offer enrollment incentive (e.g., 200 bonus points); simplify data capture to email + phone only; monitor conversion funnel daily post-launch |
| Customer confusion about points value and redemption process leads to support burden and dissatisfaction | Medium | Medium | Develop clear value communication (100 points = £1) displayed consistently across all touchpoints; create FAQ page and chatbot for common questions; monitor customer service ticket volume and content for first 60 days |
| Duplicate customer accounts created due to lack of robust identity resolution, fragmenting customer profiles | High | Medium | Implement fuzzy matching on email and phone during enrollment; manual deduplication process for first 90 days; prioritize customer data platform implementation in Phase 2; provide customer self-service merge tool |
| Points liability higher than projected due to lower breakage rate (customers redeem more than expected) | Medium | High | Set conservative breakage assumption (15% vs industry average 20%); establish liability reserve at 85% of outstanding points; monitor redemption rate weekly; adjust earning rate if liability exceeds threshold |
| Store associate adoption low (<50%) due to training gaps, process friction, or lack of incentive | Medium | High | Tie store-level loyalty enrollment and recognition metrics to manager performance reviews; provide associate incentives (e.g., recognition, small bonuses) for high adoption; simplify lookup to single phone number field; conduct refresher training at 30 days |
| Fraud and abuse (fake accounts, points manipulation, refund abuse) erodes program economics | Low | High | Implement velocity checks (max 3 accounts per email/phone/device); flag suspicious patterns (high refund rate, rapid redemption); manual review queue for high-value redemptions; integrate fraud scoring in Phase 2 |
| Regulatory non-compliance (GDPR, FCA financial promotions) results in fines or enforcement action | Low | Critical | Conduct legal review of program terms, data processing, and marketing communications before launch; document lawful basis for data processing; implement consent management and data subject rights workflows; annual compliance audit |

### External Dependencies

**POS Vendor (Legacy System Provider)**: API documentation and test environment access required by Week 2; batch file format specification required by Week 3; production API credentials required by Week 16. **Owner:** IT Director. **Status:** Initial contact made; awaiting response on API capabilities.

**E-commerce Platform (Shopify)**: App development approval and API rate limit increase required by Week 8; production app review and approval required by Week 20. **Owner:** E-commerce Manager. **Status:** Shopify Partner account established; initial app scaffolding complete.

**Mobile App Development Agency**: Statement of work for loyalty module signed by Week 4; development complete by Week 18; app store submission by Week 22. **Owner:** Product Manager. **Status:** RFP issued; vendor selection in progress.

**Email Service Provider (ESP)**: Transactional email template development and testing by Week 12; production sending domain authentication by Week 16. **Owner:** Marketing Manager. **Status:** ESP contract in place; technical integration not yet started.

**SMS Gateway Provider**: Contract negotiation and setup by Week 8; production API credentials by Week 16; compliance review for promotional SMS by Week 12. **Owner:** IT Director. **Status:** Vendor not yet selected; procurement process initiated.

**Legal/Compliance Team**: Program terms and conditions review by Week 10; GDPR data processing assessment by Week 8; FCA financial promotions review by Week 12. **Owner:** General Counsel. **Status:** Initial briefing scheduled for Week 2.

**Finance Team**: Points liability accounting treatment determined by Week 6; chart of accounts updated by Week 12; reconciliation process designed by Week 14. **Owner:** CFO. **Status:** Finance stakeholder identified; kickoff meeting pending.

**Customer Service Team**: Training materials reviewed by Week 16; support ticket categories configured by Week 18; staffing plan for launch week by Week 20. **Owner:** Customer Service Director. **Status:** Stakeholder engaged; awaiting detailed requirements.

### Open Questions

**Q1:** What is the target earning rate (points per £1 spent) that balances customer value perception with program economics, and should it vary by product category or customer segment?  
**Action:** Finance to model program economics at 1 point, 1.5 points, and 2 points per £1 scenarios with 15%, 20%, and 25% breakage assumptions; Marketing to conduct customer research on perceived value thresholds; Decision required by Week 6 to finalize MVP configuration.

**Q2:** Should points have cash-equivalent redemption value (e.g., 100 points = £1 discount) or be restricted to specific rewards catalog, and what are the regulatory implications of each approach under FCA rules?  
**Action:** Legal to assess FCA financial promotions applicability for cash-equivalent vs catalog-only redemption; Finance to model liability and breakage differences; Decision required by Week 4 to inform technical design.

**Q3:** How should we handle returns and refunds—should points be reversed immediately, after return window closes, or with a delay, and how do we prevent refund abuse?  
**Action:** Finance to define policy balancing customer experience with fraud risk; Technical team to design points reversal workflow with audit trail; Customer Service to provide input on common return scenarios; Decision required by Week 8 to implement in MVP.

**Q4:** What is the minimum viable mobile app experience—should MVP include full loyalty module (balance, history, redemption) or just QR code for in-store identification, given 6-week development constraint?  
**Action:** Product Manager to assess app development agency capacity and timeline; prioritize features based on customer research (which features drive app downloads); Decision required by Week 4 to finalize mobile app scope and timeline.

**Q5:** Should we launch with a single-tier program and add tiers in Phase 2, or launch with basic tiers (e.g., Silver/Gold) from day one to create aspiration, accepting additional complexity?  
**Action:** Marketing to model tier threshold scenarios based on customer spend distribution; assess communication complexity and customer understanding; Product to assess technical complexity; Decision required by Week 6 to finalize MVP scope.

**Q6:** How do we prioritize store associate adoption—should we mandate phone number collection at every transaction, incentivize associates, or make it optional and risk low adoption?  
**Action:** Store Operations to pilot phone number collection at 3 test stores for 2 weeks; measure adoption rate, customer response, and associate feedback; Decision required by Week 10 to finalize training and rollout approach.

**Q7:** What customer data from existing systems should be migrated into the loyalty platform, and what is the data quality threshold for migration vs starting fresh?  
**Action:** IT to assess data quality in existing systems (email accuracy, phone number format, duplicate rate); Data team to define matching rules and deduplication logic; Decision required by Week 6 to finalize migration scope and timeline.
