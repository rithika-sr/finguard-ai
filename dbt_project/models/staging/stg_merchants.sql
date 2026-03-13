-- staging/stg_merchants.sql
-- Cleans and standardizes raw merchant data.

WITH source AS (
    SELECT * FROM {{ source('raw', 'merchants') }}
),

cleaned AS (
    SELECT
        merchant_id,
        INITCAP(name)                        AS merchant_name,
        LOWER(category)                      AS category,
        UPPER(country)                       AS merchant_country,
        CAST(is_online AS BOOLEAN)           AS is_online,
        ROUND(risk_score, 2)                 AS risk_score,

        -- Risk tier based on risk score
        CASE
            WHEN risk_score >= 0.75 THEN 'high'
            WHEN risk_score >= 0.40 THEN 'medium'
            ELSE 'low'
        END                                  AS risk_tier,

        -- Flag high-risk categories (key for fraud detection)
        CASE
            WHEN LOWER(category) IN ('gambling', 'crypto_exchange', 'wire_transfer')
            THEN TRUE ELSE FALSE
        END                                  AS is_high_risk_category,

        CAST(created_at AS TIMESTAMP_NTZ)    AS created_at

    FROM source
    WHERE merchant_id IS NOT NULL
)

SELECT * FROM cleaned
