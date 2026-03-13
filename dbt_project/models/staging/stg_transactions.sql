-- staging/stg_transactions.sql
-- Cleans and standardizes raw transaction data.
-- This is the first transformation layer — no business logic yet,
-- just renaming, casting, and null handling.

WITH source AS (
    SELECT * FROM {{ source('raw', 'transactions') }}
),

cleaned AS (
    SELECT
        transaction_id,
        user_id,
        merchant_id,

        -- Standardize amount to 2 decimal places
        ROUND(amount, 2)                          AS amount,
        UPPER(currency)                           AS currency,

        -- Normalize transaction type to lowercase
        LOWER(transaction_type)                   AS transaction_type,

        -- Cast timestamp properly
        CAST(timestamp AS TIMESTAMP_NTZ)          AS transaction_at,

        UPPER(transaction_country)                AS transaction_country,
        LOWER(device_type)                        AS device_type,
        ip_address,

        -- Fraud fields (ground truth — only used for evaluation)
        CAST(is_fraud AS BOOLEAN)                 AS is_fraud,
        fraud_reason,

        LOWER(status)                             AS status,
        CAST(created_at AS TIMESTAMP_NTZ)         AS created_at,
        CAST(updated_at AS TIMESTAMP_NTZ)         AS updated_at,

        -- Derived time fields (useful for fraud pattern detection)
        EXTRACT(HOUR FROM CAST(timestamp AS TIMESTAMP_NTZ))        AS transaction_hour,
        EXTRACT(DOW  FROM CAST(timestamp AS TIMESTAMP_NTZ))        AS transaction_dow,
        DATE(CAST(timestamp AS TIMESTAMP_NTZ))                     AS transaction_date,

        -- Flag: is this a late-night transaction (11pm–4am)?
        CASE
            WHEN EXTRACT(HOUR FROM CAST(timestamp AS TIMESTAMP_NTZ)) >= 23
              OR EXTRACT(HOUR FROM CAST(timestamp AS TIMESTAMP_NTZ)) <= 4
            THEN TRUE ELSE FALSE
        END                                       AS is_late_night,

        -- Flag: is this a round-number amount?
        CASE
            WHEN MOD(amount, 100) = 0
            THEN TRUE ELSE FALSE
        END                                       AS is_round_amount

    FROM source
    WHERE transaction_id IS NOT NULL
      AND user_id        IS NOT NULL
      AND amount         > 0
)

SELECT * FROM cleaned
