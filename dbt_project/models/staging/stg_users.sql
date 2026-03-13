-- staging/stg_users.sql
-- Cleans and standardizes raw user data.

WITH source AS (
    SELECT * FROM {{ source('raw', 'users') }}
),

cleaned AS (
    SELECT
        user_id,
        INITCAP(name)                        AS full_name,
        LOWER(email)                         AS email,
        age,
        UPPER(home_country)                  AS home_country,
        LOWER(account_type)                  AS account_type,
        credit_score,

        -- Credit score tier (useful feature for fraud models)
        CASE
            WHEN credit_score >= 750 THEN 'excellent'
            WHEN credit_score >= 700 THEN 'good'
            WHEN credit_score >= 650 THEN 'fair'
            ELSE 'poor'
        END                                  AS credit_tier,

        CAST(is_high_risk AS BOOLEAN)        AS is_high_risk,
        CAST(created_at AS TIMESTAMP_NTZ)    AS created_at

    FROM source
    WHERE user_id IS NOT NULL
      AND email   IS NOT NULL
)

SELECT * FROM cleaned
