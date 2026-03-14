"""
FinGuard AI — Main Crew Orchestrator
======================================
The entry point for running FinGuard AI agents.
Run this file directly to test the full agentic pipeline.

Usage:
    python crew.py
"""

import os
from dotenv import load_dotenv
from crewai import Crew, Process

from agents import create_query_agent, create_fraud_agent, create_lineage_agent
from tasks import create_query_task, create_fraud_explanation_task, create_lineage_task

load_dotenv()

# Set OpenAI key for CrewAI
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")


def run_query(question: str) -> str:
    """Run a natural language query against the financial warehouse."""
    print(f"\n{'='*60}")
    print(f"FINGUARD AI — QUERY MODE")
    print(f"Question: {question}")
    print(f"{'='*60}\n")

    agent = create_query_agent()
    task  = create_query_task(agent, question)

    crew = Crew(
        agents=[agent],
        tasks=[task],
        process=Process.sequential,
        verbose=True,
    )
    result = crew.kickoff()
    return str(result)


def run_fraud_explanation(transaction_id: str) -> str:
    """Run a full fraud explanation for a specific transaction."""
    print(f"\n{'='*60}")
    print(f"FINGUARD AI — FRAUD EXPLANATION MODE")
    print(f"Transaction: {transaction_id}")
    print(f"{'='*60}\n")

    agent = create_fraud_agent()
    task  = create_fraud_explanation_task(agent, transaction_id)

    crew = Crew(
        agents=[agent],
        tasks=[task],
        process=Process.sequential,
        verbose=True,
    )
    result = crew.kickoff()
    return str(result)


def run_lineage_report(transaction_id: str) -> str:
    """Run a full data lineage audit report for a specific transaction."""
    print(f"\n{'='*60}")
    print(f"FINGUARD AI — LINEAGE REPORT MODE")
    print(f"Transaction: {transaction_id}")
    print(f"{'='*60}\n")

    agent = create_lineage_agent()
    task  = create_lineage_task(agent, transaction_id)

    crew = Crew(
        agents=[agent],
        tasks=[task],
        process=Process.sequential,
        verbose=True,
    )
    result = crew.kickoff()
    return str(result)


def get_sample_fraud_transaction() -> str:
    """Fetch a real fraud transaction ID from Snowflake to test with."""
    from tools.snowflake_tool import get_snowflake_connection
    conn   = get_snowflake_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT transaction_id
        FROM FINGUARD.STAGING.FCT_TRANSACTIONS
        WHERE is_fraud = TRUE
          AND rule_based_risk_score >= 0.4
        LIMIT 1
    """)
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row[0] if row else None


if __name__ == "__main__":
    print("\n" + "="*60)
    print("  FINGUARD AI — FINANCIAL INTELLIGENCE PLATFORM")
    print("  Powered by CrewAI + GPT-4o + Snowflake + dbt")
    print("="*60)

    # ── Test 1: Natural language query ────────────────────────────
    print("\n[TEST 1] Natural Language Query")
    result1 = run_query(
        "What are the top 5 merchant categories by total fraud amount? "
        "Include the fraud count and average transaction size."
    )
    print("\nRESULT:")
    print(result1)

    # ── Test 2: Fraud explanation ─────────────────────────────────
    print("\n[TEST 2] Fraud Explanation")
    txn_id = get_sample_fraud_transaction()
    if txn_id:
        result2 = run_fraud_explanation(txn_id)
        print("\nRESULT:")
        print(result2)
    else:
        print("No fraud transactions found.")

    # ── Test 3: Lineage report ────────────────────────────────────
    print("\n[TEST 3] Data Lineage Report")
    if txn_id:
        result3 = run_lineage_report(txn_id)
        print("\nRESULT:")
        print(result3)

    print("\n" + "="*60)
    print("  All tests complete. Check output above.")
    print("="*60)
