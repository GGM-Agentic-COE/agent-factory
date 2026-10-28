## Product: Omnichannel Loyalty Rewards

## Problem:
Repeat customer rate declined 18% year-over-year as competitors launched loyalty programs offering 5-10% effective discount rates. 67% of customers purchasing in both online and in-store channels are not recognized as the same individual, resulting in fragmented profiles and inability to reward cross-channel behavior. Store associates lack real-time visibility into customer lifetime value and loyalty status during in-person interactions.

## Users:
- Retail Customer (Member): Transparent points earning rules, easy redemption process, visibility of points balance and transaction history across all channels
- Store Associate: Real-time customer identification at POS, visibility of loyalty tier and lifetime value, ability to manually adjust points for service recovery
- Store Manager: Dashboard showing store-level loyalty enrollment rates, redemption patterns, and impact on sales metrics
- E-commerce Customer: Frictionless enrollment during checkout, automatic points crediting, mobile app integration for digital-first experience
- Loyalty Program Manager: Configuration tools for earning/redemption rules, tier thresholds, promotional campaigns; analytics on member behavior and program economics
- Customer Service Agent: Unified view of customer account, transaction history, points adjustments, ability to resolve disputes and process manual credits
- Marketing Manager: Segmentation tools based on loyalty behavior, campaign management for targeted offers, measurement of campaign impact on points activity
- Finance/Accounting: Points liability tracking, breakage analysis, reconciliation of points issued vs redeemed, financial reporting on program costs

## Capabilities:
- Enroll customers through multiple touchpoints: online checkout, mobile app, in-store POS, dedicated web portal
- Capture essential profile data: name, email, phone, postal code and establish unique member ID
- Perform real-time deduplication to prevent duplicate accounts
- Link existing purchase history using email/phone matching
- Verify identity via email/SMS OTP to prevent fraud
- Enable household linking to allow family members to pool points
- Support guest-to-member conversion flow for customers who initially checkout as guest
- Manage GDPR-compliant consent with granular opt-ins for marketing communications
- Calculate and credit points on qualifying purchases across all channels based on configurable earning rules
- Support base earn rate (1 point per £1 spent)
- Apply category multipliers (2x points on sale items)
- Apply tier bonuses (gold members earn 1.5x)
- Execute promotional campaigns (triple points weekend)
- Award non-transactional earning (points for app download, birthday bonus, referrals)
- Credit points in real-time for online purchases
- Credit points near-real-time for in-store purchases (within 4 hours, with path to real-time in Phase 2)
- Apply retroactive points crediting for purchases made before enrollment (trailing 90 days)
- Enforce points expiration policies with advance notification (points expire 24 months from earn date)
- Maintain audit trail of all points transactions for compliance and dispute resolution
- Redeem points for discount on current purchase (online or in-store)
- Apply statement credit to account
- Provide early access to sales
- Offer exclusive products
- Enable partner rewards (charity donations, gift cards)
- Support real-time redemption at online checkout (apply points as discount before payment)
- Enable in-store redemption via POS integration (associate-initiated or customer-scanned barcode)
- Provide mobile app redemption for digital rewards (coupons, early access codes)
- Display tiered rewards catalog with aspirational high-value rewards
- Support partial redemption (use points + cash for single transaction)
- Apply redemption restrictions (cannot redeem on sale items, minimum purchase thresholds)
- Manage rewards inventory to prevent over-redemption of limited-availability items
- Identify customers via loyalty card barcode scan
- Lookup customers by phone number
- Lookup customers by email
- Recognize customers via mobile app QR code
- Passively recognize via logged-in web session or app
- Provide store associate tools for customer lookup by phone, email, or name with disambiguation
- Generate mobile app QR code for fast in-store scanning
- Issue physical loyalty card (optional)
- Display real-time customer profile showing tier, points balance, recent activity, and lifetime value
- Provide privacy controls allowing customers to opt-out of in-store recognition while maintaining online benefits
- Calculate and promote membership tiers (Silver, Gold, Platinum) based on annual spend or points earned
- Apply automatic tier calculation and promotion based on rolling 12-month activity
- Provide tier retention grace period (3 months to re-qualify before demotion)
- Display tier status across all customer touchpoints (app, web, POS, email)
- Apply tier-specific earning multipliers and redemption options
- Communicate tier benefits catalog with clear value communication
- Execute tier challenge campaigns (\"Spend £200 more to reach Gold by month-end\")
- Display real-time program KPIs (enrollment rate, active members, points issued/redeemed, redemption rate)
- Perform member segmentation and cohort analysis (RFM scoring, tier distribution, channel preference)
- Measure campaign performance (promotional earn campaigns, targeted offers)
- Track financial reporting (points liability, breakage rate, cost per point, ROI by member segment)
- Generate predictive analytics (churn risk scoring, lifetime value prediction, next-best-action recommendations)
- Compare store-level performance (enrollment rates, redemption rates, impact on basket size)
- Provide A/B testing framework for program rule changes
- Orchestrate personalized communications across email, SMS, push notifications, and in-app messages
- Trigger event-driven messaging based on member actions (enrollment, tier promotion, points expiration approaching)
- Deliver segmented campaigns based on member attributes and behavior
- Orchestrate multi-channel communication with preference management
- Personalize messages with dynamic content (name, points balance, tier status, recommended actions)
- Measure communication effectiveness (open rates, click-through rates, conversion rates)
- Update customer email, phone, postal code via account settings
- Manage communication preferences
- Download CSV of all points transactions for personal records
- Configure earning rate, redemption rate, and expiration policy via admin UI
- Send automated welcome email upon enrollment with program overview, points balance, and link to terms
- Notify customers 60 days and 30 days before points expiration
- Provide web-based training module for store associates covering customer lookup, program overview, and common scenarios

## Quality Expectations:
- System uptime ≥99.5% during business hours
- Support 500 concurrent users (10x expected peak during launch)
- Credit points in real-time for online purchases
- Credit points within 4 hours for in-store purchases (MVP batch processing)
- Credit points within 24 hours for in-store purchases with SMS notification (MVP acceptable delay)
- Process phone number lookup at POS with immediate customer profile display
- Points liability reconciliation accurate within 1% variance
- Zero data breaches or GDPR compliance violations
- All customer data processing complies with UK GDPR
- Email/SMS OTP verification completes within 2 minutes
- Mobile app QR code generation instantaneous
- Transaction history displays last 10 transactions (MVP) with pagination for full history
- Store associate training completable within 15 minutes via video + 1-page quick reference
- Customer enrollment flow completable within 2 minutes
- Points redemption at checkout applies discount before payment processing
- Audit trail logs all points transactions with timestamp, amount, reason, and reference

## Constraints:
- Initial implementation budget capped at £450K capital expenditure
- £180K annual operating budget (hosting, support, ongoing development)
- Rewards liability reserve must be established at 85% of outstanding points value
- Customer data processing must comply with UK GDPR including lawful basis, data subject rights (access, erasure, portability), retention limits (active members + 2 years post-closure)
- If points redeemable for cash or cash-equivalent, program may fall under FCA financial promotions rules (CONC 3) requiring clear terms, representative examples, and fair treatment
- PSD2 Strong Customer Authentication required for account login and redemption transactions exceeding £30 value
- MVP launch required within 6 months to align with peak holiday shopping season (October launch target)
- Full vision features delivered in 3 phases over 18 months
- E-commerce platform: Shopify
- POS system: legacy proprietary system with limited API capabilities
- POS system API supports read-only customer lookup; write operations require batch file processing with 4-hour delay
- IT team consists of 4 developers with 60% allocated to BAU maintenance
- No existing customer data platform—customer records fragmented across 5 systems
- Store staff training must be completed within 2-week window
- Mobile app exists but not updated in 18 months; requires modernization to support loyalty features (6-week development effort)
- No real-time event streaming infrastructure—current architecture is batch-oriented with daily data synchronization
- Points expire 24 months from earn date (industry-standard policy)
- Minimum redemption 500 points (MVP)
- Redemption rate: 100 points = £1 discount
- Base earning rate: 1 point per £1 spent (MVP)
- Store associate phone number lookup adoption target: 60% of customers provide phone number when asked
- 10,000 customers enrolled within first 30 days of launch (MVP success criteria)
- 60% of enrolled customers earn points on at least one additional purchase within 90 days (MVP success criteria)
- 25% of enrolled customers redeem points at least once within 90 days (MVP success criteria)
- 50% of in-store transactions successfully identify customer as loyalty member (MVP success criteria)
- Store associate satisfaction score ≥7/10 on ease-of-use survey (MVP success criteria)

## Integrations:
- E-commerce Platform (Shopify): bi-directional integration for enrollment during checkout, real-time points earning on order completion, redemption as discount code, member profile display on account page, order history synchronization
- Point-of-Sale System (Legacy Proprietary): customer lookup API for member identification, batch file export for transaction data (4-hour delay), batch file import for points crediting, associate dashboard for member profile display
- Mobile Application (Native iOS/Android): embedded loyalty module showing points balance, transaction history, rewards catalog, QR code for in-store identification, push notification receiver for engagement campaigns
- Customer Data Platform (To Be Implemented): unified customer profile creation, cross-channel identity resolution, customer 360-degree view, segmentation engine for marketing campaigns
- Payment Gateway: transaction amount and payment method data for points calculation, fraud signal integration to prevent points abuse, refund event handling for points reversal
- Email Service Provider (ESP): transactional and promotional email delivery, template management, personalization engine, delivery/engagement metrics
- SMS Gateway: OTP delivery for identity verification, transactional SMS for points updates, promotional SMS for campaigns
- Customer Relationship Management (CRM): customer service agent access to loyalty profile, ticket creation for disputes, resolution workflow integration
- Business Intelligence Platform: data warehouse integration for historical reporting, dashboard embedding, predictive model deployment
- Fraud Detection System: real-time fraud scoring for enrollment and redemption transactions, velocity checks for abuse prevention, suspicious activity alerting

## Data Entities:
- Member Profile: member_id (unique), name, email, phone, postal_code, enrollment_date, tier_status, lifetime_value, consent_flags (PII: yes - name, email, phone, postal_code)
- Points Transaction: transaction_id, member_id, transaction_type (earn/redeem/expire/adjust), points_amount, transaction_date, expiration_date, order_reference, channel (online/in-store), reason_code (PII: no)
- Points Balance: member_id, current_balance, points_pending_expiration, next_expiration_date (PII: no)
- Order History: order_id, member_id, order_date, order_amount, channel, points_earned, points_redeemed (PII: no - linked via member_id)
- Tier Status: member_id, current_tier (Silver/Gold/Platinum), tier_start_date, tier_expiration_date, rolling_12_month_spend, points_to_next_tier (PII: no)
- Redemption Transaction: redemption_id, member_id, redemption_date, points_redeemed, reward_type, reward_value, order_reference (PII: no)
- Communication Preference: member_id, email_opt_in, sms_opt_in, push_opt_in, frequency_preference (PII: no - linked via member_id)
- Household Link: household_id, member_ids (array), pooled_points_balance (PII: no - linked via member_id)

## Success Metrics:
- Repeat purchase rate (90-day): current 34% → target 45% (12 months) | measured via percentage of customers making 2+ purchases within 90-day rolling window via unified customer ID
- Average customer lifetime value: current £340 → target £425 (12 months) | measured via total revenue per customer from enrollment through measurement date, segmented by member vs non-member cohorts
- Mobile app monthly active users: current 23,000 (23%) → target 35,000 (35%) (12 months) | measured via unique users opening app at least once per month via app analytics platform
- Program enrollment rate: current 0% → target 60% of transacting customers (12 months) | measured via percentage of customers who complete enrollment within 30 days of first purchase
- Cross-channel customer recognition rate: current 33% → target 85% (12 months) | measured via percentage of customers who purchase in both channels correctly linked to single customer profile
- In-store loyalty identification rate: current N/A → target 70% (12 months) | measured via percentage of in-store transactions where customer is identified as loyalty member at POS
- Points redemption rate (annual): current N/A → target 35% (12 months) | measured via percentage of points issued in trailing 12 months that are redeemed within same period
- Net Promoter Score (loyalty members): current N/A → target +40 (12 months) | measured via NPS survey administered to loyalty members quarterly
- Expected 15-20% increase in repeat purchase frequency within 12 months
- Expected 25% growth in mobile app active users
- Projected £2.4M incremental annual revenue from 15% increase in repeat purchase rate
- Program costs estimated at £680K annually
- ROI target: 3.5:1 return on investment
- Loyalty program members expected to spend 12-18% more annually than non-members
- Loyalty program members exhibit 2.5x higher retention rates
- Breakage assumption: 15% of points never redeemed (conservative vs industry average 20%)

## Risks:
- POS integration more complex than estimated, causing delays or requiring scope reduction (likelihood: high, impact: high)
- Low enrollment conversion rate (<40%) due to friction in checkout flow or unclear value proposition (likelihood: medium, impact: high)
- Customer confusion about points value and redemption process leads to support burden and dissatisfaction (likelihood: medium, impact: medium)
- Duplicate customer accounts created due to lack of robust identity resolution, fragmenting customer profiles (likelihood: high, impact: medium)
- Points liability higher than projected due to lower breakage rate (customers redeem more than expected) (likelihood: medium, impact: high)
- Store associate adoption low (<50%) due to training gaps, process friction, or lack of incentive (likelihood: medium, impact: high)
- Fraud and abuse (fake accounts, points manipulation, refund abuse) erodes program economics (likelihood: low, impact: high)
- Regulatory non-compliance (GDPR, FCA financial promotions) results in fines or enforcement action (likelihood: low, impact: critical)
- POS API limitations confirmed worse than expected, requiring deprioritization of real-time in-store features
- Mobile app more technically degraded than assessed, extending timeline or forcing MVP launch without app support
- Customer tolerance for 24-hour in-store points crediting delay lower than assumed, declining satisfaction and trust
- Data quality in existing systems worse than expected, causing duplicate accounts to proliferate
- Store associate training insufficient within 2-week window, undermining in-store experience
- Integration complexity underestimated, causing budget overruns and scope cuts

## MVP Boundary:

### In:
- Online enrollment during checkout with email, phone, postal code capture and OTP verification
- Automatic points crediting (1 point per £1 spent) on completed online orders
- Points balance and transaction history display on web account page and mobile app
- Points redemption at online checkout (100 points = £1 discount, minimum 500 points)
- Store associate phone number lookup to retrieve member profile (name, points balance, recent purchases)
- In-store transaction batch export with points credited within 24 hours and SMS notification
- Points expiration (24-month policy) with automated email notifications at 60 days and 30 days before expiration
- Basic member profile management (update email, phone, postal code, communication preferences)
- Welcome email automation upon enrollment with program overview and terms link
- Admin configuration panel to update earning rate, redemption rate, and expiration policy
- Transaction history export (CSV download for GDPR data portability)
- Store associate training portal with web-based training module
- GDPR compliance: lawful basis documentation, consent capture, data retention policy enforcement
- Audit trail logging all points transactions with timestamp, amount, reason, and reference
- Load testing for 500 concurrent users
- Security testing including penetration test and OWASP Top 10 vulnerability scan
- Points liability tracking in finance system with daily reconciliation report
- Rollback plan for critical failure scenarios

### Out:
- Tiered membership (Silver/Gold/Platinum) → Phase 2 (Month 7-12) - adds complexity to earning rules and communications
- Real-time in-store points crediting → Phase 2 (Month 7-12) - POS system API limitations require batch processing
- Mobile app QR code for in-store identification → Phase 2 (Month 7-12) - requires mobile app development and POS barcode scanner integration
- Retroactive points for pre-enrollment purchases → Phase 2 (Month 7-12) - requires historical transaction data cleanup and complex matching logic
- In-store redemption at POS → Phase 2 (Month 7-12) - POS system does not support real-time discount application
- Category-specific earning multipliers → Phase 3 (Month 13-18) - adds complexity to rules engine and customer communication
- Promotional campaigns (bonus points events) → Phase 3 (Month 13-18) - requires campaign management tools and scheduling logic
- Referral program (earn points for friend sign-ups) → Phase 3 (Month 13-18) - requires fraud prevention, attribution logic, and promotional mechanics
- Partner rewards (gift cards, charity donations) → Phase 4 (Month 19-24) - requires partner agreements, inventory management, and fulfillment workflows
- Household account linking → Phase 4 (Month 19-24) - complex identity resolution and privacy implications
- Predictive analytics and churn models → Phase 5 (Month 25-36) - requires 6-12 months of behavioral data to train models
- Advanced analytics dashboard with predictive models → Phase 3 (Month 13-18)
- A/B testing framework for program rule changes → Phase 3 (Month 13-18)
- Coalition loyalty with external partners → Phase 4 (Month 19-24)
- B2B loyalty extension → Phase 4 (Month 19-24)
- Gamification elements (challenges, badges, leaderboards) → Phase 3 (Month 13-18)
- AI-driven personalization and dynamic offer optimization → Phase 5 (Month 25-36)

## Open Questions:
- What is the target earning rate (points per £1 spent) that balances customer value perception with program economics, and should it vary by product category or customer segment? (Decision required by Week 6)
- Should points have cash-equivalent redemption value (100 points = £1 discount) or be restricted to specific rewards catalog, and what are the regulatory implications under FCA rules? (Decision required by Week 4)
- How should returns and refunds be handled—should points be reversed immediately, after return window closes, or with a delay, and how to prevent refund abuse? (Decision required by Week 8)
- What is the minimum viable mobile app experience—full loyalty module (balance, history, redemption) or just QR code for in-store identification, given 6-week development constraint? (Decision required by Week 4)
- Should MVP launch with single-tier program and add tiers in Phase 2, or launch with basic tiers (Silver/Gold) from day one to create aspiration? (Decision required by Week 6)
- How to prioritize store associate adoption—mandate phone number collection at every transaction, incentivize associates, or make it optional and risk low adoption? (Decision required by Week 10)
- What customer data from existing systems should be migrated into the loyalty platform, and what is the data quality threshold for migration vs starting fresh? (Decision required by Week 6)
- What is acceptable phone number lookup adoption rate at in-store checkout (assumption: 60%)?
- What is acceptable customer tolerance for in-store points crediting delay (assumption: 24 hours)?
- Is email and phone number sufficient for identity verification, or is government ID required?
- What velocity checks are needed to prevent fraud (max 3 accounts per phone/email/device)?
- What is the store associate training completion timeline and format (assumption: 15-minute video + 1-page quick reference within 2-week window)?
