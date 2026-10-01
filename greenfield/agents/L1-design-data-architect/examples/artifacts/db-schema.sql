-- ============================================================================
-- HarvestLink — identity-service physical schema
-- Cycle C1-producer-registration · produced by L1-design-data-architect@1.0.0
-- execution exec-datd-8a9b0c1e · run wf-hl-pi1-3c4d5e6f
--
-- This file holds the PHYSICAL schema. It is deliberately separate from
-- data-architecture.md, which records what is owned, how it is classified and
-- what access patterns must be satisfied — never tables, columns or indexes.
-- The index below satisfies a stated budget; it can change without the
-- architecture changing, which is exactly why it does not live there.
--
-- Constraints this schema is bound by:
--   DAT-1.1  Identity is the sole writer of Producer and FoodSafetyRegistration
--   DAT-1.b  No cross-context direct database access
--   DAT-3.2  FoodSafetyRegistration is Regulated Evidence, append-only,
--            6-year retention (ES3), approved PII region (ES9)
--   INT-4.3  Registration status read, p95 <= 250 ms
--   PLT-10   At-rest encryption via the managed key capability
-- ============================================================================

-- ----------------------------------------------------------------------------
-- producer
-- Classification: PII. Retention: UK GDPR erasure for the population not held
-- under the ES3 6-year compliance obligation — the two populations are distinct
-- and are handled distinctly.
-- ----------------------------------------------------------------------------
CREATE TABLE producer (
    id                  uuid         PRIMARY KEY,
    external_subject_id text         NOT NULL UNIQUE,   -- from the external IdP (ES1)
    business_name       text         NOT NULL,
    created_at          timestamptz  NOT NULL DEFAULT now(),
    updated_at          timestamptz  NOT NULL DEFAULT now()
);

COMMENT ON TABLE  producer IS 'Owned by the Identity bounded context (DAT-1.1). PII.';
COMMENT ON COLUMN producer.external_subject_id IS
    'Subject from the group-approved external IdP. Never an employee-directory principal (ES1).';

-- ----------------------------------------------------------------------------
-- food_safety_registration
-- Classification: Regulated Evidence. APPEND-ONLY.
--
-- A status change is a NEW ROW superseding the prior one. Rows are never
-- updated: a dispute asks what was true on the day of sale, and an overwritten
-- row cannot answer that question.
-- ----------------------------------------------------------------------------
CREATE TABLE food_safety_registration (
    id               uuid         PRIMARY KEY,
    producer_id      uuid         NOT NULL REFERENCES producer (id),
    fbo_number       text         NOT NULL,
    status           text         NOT NULL
                                  CHECK (status IN ('pending-verification','valid','rejected')),
    register_reason  text         NULL,     -- Regulated Evidence / Confidential (DATD-01)
    verified_on      date         NULL,
    supersedes_id    uuid         NULL REFERENCES food_safety_registration (id),
    appended_at      timestamptz  NOT NULL DEFAULT now()
);

COMMENT ON TABLE  food_safety_registration IS
    'Owned by the Identity bounded context (DAT-1.1). Regulated Evidence, append-only, '
    '6-year retention (ES3), approved PII region (ES9).';
COMMENT ON COLUMN food_safety_registration.register_reason IS
    'The competent authority rejection reason, stored verbatim so it can be passed '
    'through unparaphrased. Third-party supplied and unbounded in content, therefore '
    'classified Confidential defensively (DATD-01, DATD-F01). Never logged, never '
    'placed in an outbound notification body, never replicated.';
COMMENT ON COLUMN food_safety_registration.supersedes_id IS
    'The row this one replaces. NULL on the first row for a producer.';

-- ----------------------------------------------------------------------------
-- Index — satisfies INT-4.3's p95 <= 250 ms status read over an append-only
-- history. This is the whole of LLD-F01 that belongs in physical schema; the
-- projection half was declined and recorded as DAT-PEND-04.
-- ----------------------------------------------------------------------------
CREATE INDEX idx_fsr_producer_appended_desc
    ON food_safety_registration (producer_id, appended_at DESC);

-- ----------------------------------------------------------------------------
-- Append-only enforcement at the grant level.
--
-- The LLD enforces this a second time by exposing supersede() and no update()
-- on ProducerRepository. Two independent mechanisms, because a future ORM or
-- migration script would not know about the repository convention.
-- ----------------------------------------------------------------------------
GRANT SELECT, INSERT ON food_safety_registration TO identity_service_app;
-- deliberately NOT granted: UPDATE, DELETE
GRANT SELECT, INSERT, UPDATE ON producer TO identity_service_app;

-- ----------------------------------------------------------------------------
-- Isolation (DAT-1.b, PLT-3 access boundary, PRIN-03-C2 BLOCKING)
-- No other context's application role holds any grant in this schema, and no
-- foreign key crosses a schema boundary. Other contexts hold producer.id as an
-- identifier only and never join to it.
-- ----------------------------------------------------------------------------
REVOKE ALL ON ALL TABLES IN SCHEMA identity_schema FROM PUBLIC;

-- ----------------------------------------------------------------------------
-- Encryption (PLT-10, ES10)
-- At-rest encryption is provided by the managed relational capability using the
-- group managed key. No application-held keys, no key material in this file or
-- in any migration. Region: approved PII region (ES9); backups and DR copies
-- inherit it — a copy is not a new residency decision.
-- ----------------------------------------------------------------------------
