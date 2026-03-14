"""
FinGuard AI — Task Definitions
================================
Defines the tasks that agents execute.
Tasks are the actual work units — they combine an agent with
a specific goal, context, and expected output format.
"""

from crewai import Task
from crewai import Agent


def create_query_task(agent: Agent, question: str) -> Task:
    """Task: Answer a natural language question about financial data."""
    return Task(
        description=f"""
        Answer the following question about FinGuard's financial transaction data:

        QUESTION: {question}

        Instructions:
        1. Write a SQL query against FINGUARD.STAGING.FCT_TRANSACTIONS (or other staging tables if needed)
        2. Execute the query using the snowflake_query tool
        3. Interpret the results clearly
        4. If the question involves fraud, include the fraud rate and breakdown
        5. Always include the SQL you used so the analyst can verify it

        CRITICAL — Data conventions you MUST follow:
        - merchant_category values are always lowercase with underscores. Use EXACTLY:
          wire_transfer, gambling, crypto_exchange, grocery, restaurant,
          gas_station, online_retail, travel, entertainment, pharmacy,
          electronics, clothing, utilities, healthcare, education
        - transaction_type values: purchase, withdrawal, transfer, refund, payment
        - status values: completed, pending, failed
        - device_type values: mobile, web, atm, pos
        - country codes are 2-letter uppercase: US, CA, GB, NG, RU, CN, BR, DE, FR, AU, MX
        - is_fraud is a BOOLEAN — use: is_fraud = TRUE (not 'true' or 1)
        - All string comparisons must use exact lowercase values as listed above

        Format your response as:
        - ANSWER: [direct answer to the question]
        - SQL USED: [the query you ran]
        - DATA: [key numbers/findings]
        - INSIGHT: [one sentence of business context]
        """,
        agent=agent,
        expected_output=(
            "A clear answer to the question with supporting data, "
            "the SQL query used, and a brief business insight."
        ),
    )


def create_fraud_explanation_task(agent: Agent, transaction_id: str) -> Task:
    """Task: Explain why a specific transaction was flagged."""
    return Task(
        description=f"""
        Investigate and explain the fraud assessment for transaction ID: {transaction_id}

        Instructions:
        1. Query FINGUARD.STAGING.FCT_TRANSACTIONS for this transaction_id
        2. Retrieve ALL columns — especially the fraud signal columns:
           - is_fraud, fraud_reason
           - is_late_night, is_round_amount
           - is_foreign_transaction, is_high_value_late_night
           - merchant_is_high_risk_category, user_is_high_risk
           - rule_based_risk_score
           - transaction_country vs user_home_country
           - transaction_hour, amount, merchant_category
        3. Analyze which risk signals fired (are TRUE or elevated)
        4. Produce a structured fraud explanation report

        CRITICAL — Data conventions:
        - merchant_category is always lowercase with underscores (e.g. wire_transfer, not 'Wire Transfer')
        - is_fraud is BOOLEAN — TRUE means fraudulent
        - rule_based_risk_score is a float between 0.0 and 1.0
        - transaction_country and user_home_country are 2-letter uppercase country codes

        Format your response EXACTLY as:

        ══════════════════════════════════════════
        FINGUARD FRAUD ASSESSMENT REPORT
        ══════════════════════════════════════════
        Transaction ID : [id]
        Amount         : $[amount] [currency]
        Timestamp      : [transaction_at]
        Status         : [status]
        Merchant       : [merchant_name] ([merchant_category])
        User           : [user_name] (home: [user_home_country])
        Transaction in : [transaction_country]
        ──────────────────────────────────────────
        VERDICT: [FLAGGED / CLEARED]
        Risk Score: [rule_based_risk_score] / 1.0
        ──────────────────────────────────────────
        RISK SIGNALS DETECTED:
        [List each signal that fired with the actual data value]

        EXPLANATION:
        [2-3 sentences explaining why this transaction is suspicious or clean,
        written for a compliance officer — clear, specific, no jargon]

        RECOMMENDED ACTION:
        [One of: Auto-approve / Manual review / Block and investigate]
        ══════════════════════════════════════════
        """,
        agent=agent,
        expected_output=(
            "A complete structured fraud assessment report for the transaction, "
            "citing specific data points for each risk signal that fired."
        ),
    )


def create_lineage_task(agent: Agent, transaction_id: str) -> Task:
    """Task: Produce a data lineage and governance audit trail."""
    return Task(
        description=f"""
        Produce a complete data lineage audit trail for transaction ID: {transaction_id}

        Instructions:
        1. Query FINGUARD.STAGING.FCT_TRANSACTIONS to get full transaction details
        2. Also query FINGUARD.STAGING.STG_TRANSACTIONS for the staging-layer view
        3. Trace the complete data journey for this transaction

        CRITICAL — Data conventions:
        - merchant_category is always lowercase with underscores (e.g. wire_transfer)
        - is_fraud is BOOLEAN — use TRUE/FALSE
        - All string fields are lowercase unless noted otherwise

        Format your response EXACTLY as:

        ══════════════════════════════════════════
        FINGUARD DATA LINEAGE REPORT
        ══════════════════════════════════════════
        Transaction ID : [id]
        Report Type    : Data Governance Audit Trail
        ──────────────────────────────────────────
        LAYER 1 — RAW SOURCE
        Table  : FINGUARD.RAW.TRANSACTIONS
        Origin : Synthetic financial transaction generator (generate_data.py)
        Fields ingested: transaction_id, user_id, merchant_id, amount, currency,
                         transaction_type, timestamp, transaction_country,
                         device_type, ip_address, is_fraud, status

        LAYER 2 — STAGING TRANSFORMATION (dbt)
        Model  : FINGUARD.STAGING.STG_TRANSACTIONS
        Transformations applied:
          • Amount rounded to 2 decimal places
          • Currency uppercased and standardized
          • Timestamp cast to TIMESTAMP_NTZ
          • transaction_hour and transaction_date derived
          • is_late_night flag derived (hour >= 23 OR hour <= 4)
          • is_round_amount flag derived (amount MOD 100 = 0)
        Data tests passed: not_null(transaction_id), not_null(amount),
                           unique(transaction_id), accepted_values(status, transaction_type)

        LAYER 3 — MART ENRICHMENT (dbt)
        Model  : FINGUARD.STAGING.FCT_TRANSACTIONS
        Joins applied:
          • LEFT JOIN stg_users ON user_id (adds user context + credit tier)
          • LEFT JOIN stg_merchants ON merchant_id (adds merchant risk signals)
        Derived fields:
          • is_foreign_transaction (transaction_country != user_home_country)
          • is_high_value_late_night (amount > 800 AND is_late_night)
          • rule_based_risk_score (weighted sum of 6 risk signals)

        LAYER 4 — AI AGENT DECISION
        Agent  : FinGuard Fraud Detection Agent (CrewAI)
        Model  : GPT-4o-mini
        Input  : rule_based_risk_score + all fraud signal flags from fct_transactions
        Output : Fraud verdict + human-readable explanation

        ──────────────────────────────────────────
        GOVERNANCE SUMMARY
        Total transformations : 3 layers
        Data tests validated  : 23 automated tests
        Fields derived        : 8 computed columns
        Lineage tool          : dbt (docs available at localhost:8080)
        AI transparency       : Full audit trail preserved at every layer
        ══════════════════════════════════════════
        """,
        agent=agent,
        expected_output=(
            "A complete data lineage audit trail showing exactly how the transaction "
            "data was sourced, transformed, and used to make an AI decision."
        ),
    )