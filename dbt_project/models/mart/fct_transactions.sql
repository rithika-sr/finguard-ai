-- mart/fct_transactions.sql
-- The main analytics table. Joins transactions with user and merchant context.
-- This is what the AI agent will query to answer questions and explain decisions.

WITH transactions AS (
    SELECT * FROM {{ ref('stg_transactions') }}
),

users AS (
    SELECT * FROM {{ ref('stg_users') }}
),

merchants AS (
    SELECT * FROM {{ ref('stg_merchants') }}
),

joined AS (
    SELECT
        -- Transaction core
        t.transaction_id,
        t.transaction_at,
        t.transaction_date,
        t.transaction_hour,
        t.transaction_dow,
        t.amount,
        t.currency,
        t.transaction_type,
        t.transaction_country,
        t.device_type,
        t.ip_address,
        t.status,

        -- Fraud ground truth
        t.is_fraud,
        t.fraud_reason,

        -- Derived flags
        t.is_late_night,
        t.is_round_amount,

        -- User context
        t.user_id,
        u.full_name                                     AS user_name,
        u.email                                         AS user_email,
        u.age                                           AS user_age,
        u.home_country                                  AS user_home_country,
        u.account_type,
        u.credit_score,
        u.credit_tier,
        u.is_high_risk                                  AS user_is_high_risk,

        -- Merchant context
        t.merchant_id,
        m.merchant_name,
        m.category                                      AS merchant_category,
        m.merchant_country,
        m.is_online                                     AS merchant_is_online,
        m.risk_score                                    AS merchant_risk_score,
        m.risk_tier                                     AS merchant_risk_tier,
        m.is_high_risk_category                         AS merchant_is_high_risk_category,

        -- Composite fraud risk signals (used by the AI agent for explanation)
        CASE
            WHEN t.transaction_country != u.home_country
            THEN TRUE ELSE FALSE
        END                                             AS is_foreign_transaction,

        CASE
            WHEN t.amount > 800 AND t.is_late_night
            THEN TRUE ELSE FALSE
        END                                             AS is_high_value_late_night,

        -- Overall risk score (simple weighted sum — will be enhanced in Phase 3)
        ROUND(
            (CASE WHEN t.is_late_night            THEN 0.20 ELSE 0 END) +
            (CASE WHEN t.is_round_amount          THEN 0.15 ELSE 0 END) +
            (CASE WHEN t.transaction_country != u.home_country THEN 0.25 ELSE 0 END) +
            (CASE WHEN m.is_high_risk_category    THEN 0.20 ELSE 0 END) +
            (CASE WHEN u.is_high_risk             THEN 0.10 ELSE 0 END) +
            (CASE WHEN t.amount > 5000            THEN 0.10 ELSE 0 END),
        2)                                              AS rule_based_risk_score

    FROM transactions t
    LEFT JOIN users     u ON t.user_id     = u.user_id
    LEFT JOIN merchants m ON t.merchant_id = m.merchant_id
)

SELECT * FROM joined
