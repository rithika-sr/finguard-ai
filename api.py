"""
FinGuard AI — FastAPI Backend
==============================
REST API that exposes the CrewAI agents as HTTP endpoints.
The Streamlit frontend calls this API — clean separation of concerns.

Endpoints:
  POST /query          — natural language question → SQL → answer
  POST /fraud/{txn_id} — fraud explanation report for a transaction
  POST /lineage/{txn_id} — data lineage audit trail
  GET  /metrics        — dashboard summary metrics
  GET  /transactions   — paginated transaction list with filters
  GET  /health         — health check
"""

import os
import sys
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import snowflake.connector
import pandas as pd
from dotenv import load_dotenv

# Add project root to path so we can import agents/tasks
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents import create_query_agent, create_fraud_agent, create_lineage_agent
from tasks import create_query_task, create_fraud_explanation_task, create_lineage_task
from crewai import Crew, Process

load_dotenv()

app = FastAPI(
    title="FinGuard AI API",
    description="Financial Intelligence Platform — AI-powered fraud detection with data governance",
    version="1.0.0",
)

# Allow Streamlit to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Snowflake helper ──────────────────────────────────────────────────────────
def get_conn():
    return snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema="STAGING",
    )


def run_query(sql: str) -> pd.DataFrame:
    conn   = get_conn()
    cursor = conn.cursor()
    cursor.execute(sql)
    cols = [d[0].lower() for d in cursor.description]
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return pd.DataFrame(rows, columns=cols)


# ── Request / Response models ─────────────────────────────────────────────────
class QueryRequest(BaseModel):
    question: str


class AgentResponse(BaseModel):
    success: bool
    result: str
    error: Optional[str] = None


# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok", "service": "FinGuard AI API"}


# ── POST /query ───────────────────────────────────────────────────────────────
@app.post("/query", response_model=AgentResponse)
def query_endpoint(body: QueryRequest):
    """Natural language query → SQL → formatted answer."""
    try:
        agent  = create_query_agent()
        task   = create_query_task(agent, body.question)
        crew   = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=False)
        result = crew.kickoff()
        return AgentResponse(success=True, result=str(result))
    except Exception as e:
        return AgentResponse(success=False, result="", error=str(e))


# ── POST /fraud/{transaction_id} ──────────────────────────────────────────────
@app.post("/fraud/{transaction_id}", response_model=AgentResponse)
def fraud_endpoint(transaction_id: str):
    """Full fraud explanation report for a transaction."""
    try:
        agent  = create_fraud_agent()
        task   = create_fraud_explanation_task(agent, transaction_id)
        crew   = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=False)
        result = crew.kickoff()
        return AgentResponse(success=True, result=str(result))
    except Exception as e:
        return AgentResponse(success=False, result="", error=str(e))


# ── POST /lineage/{transaction_id} ────────────────────────────────────────────
@app.post("/lineage/{transaction_id}", response_model=AgentResponse)
def lineage_endpoint(transaction_id: str):
    """Data lineage audit trail for a transaction."""
    try:
        agent  = create_lineage_agent()
        task   = create_lineage_task(agent, transaction_id)
        crew   = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=False)
        result = crew.kickoff()
        return AgentResponse(success=True, result=str(result))
    except Exception as e:
        return AgentResponse(success=False, result="", error=str(e))


# ── GET /metrics ──────────────────────────────────────────────────────────────
@app.get("/metrics")
def metrics_endpoint():
    """Summary metrics for the dashboard header cards."""
    try:
        df = run_query("""
            SELECT
                COUNT(*)                                          AS total_transactions,
                SUM(CASE WHEN is_fraud THEN 1 ELSE 0 END)        AS total_fraud,
                ROUND(AVG(CASE WHEN is_fraud THEN 1.0 ELSE 0 END) * 100, 2) AS fraud_rate_pct,
                ROUND(SUM(CASE WHEN is_fraud THEN amount ELSE 0 END), 2)    AS total_fraud_amount,
                ROUND(AVG(amount), 2)                             AS avg_transaction_amount,
                COUNT(DISTINCT user_id)                           AS unique_users,
                COUNT(DISTINCT merchant_id)                       AS unique_merchants
            FROM FINGUARD.STAGING.FCT_TRANSACTIONS
        """)
        return df.to_dict(orient="records")[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── GET /transactions ─────────────────────────────────────────────────────────
@app.get("/transactions")
def transactions_endpoint(
    limit:      int  = Query(50, le=200),
    fraud_only: bool = Query(False),
    min_risk:   float = Query(0.0),
):
    """Paginated transaction list for the dashboard table."""
    try:
        where_clauses = []
        if fraud_only:
            where_clauses.append("is_fraud = TRUE")
        if min_risk > 0:
            where_clauses.append(f"rule_based_risk_score >= {min_risk}")

        where = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

        df = run_query(f"""
            SELECT
                transaction_id,
                transaction_at,
                user_name,
                merchant_name,
                merchant_category,
                amount,
                transaction_country,
                user_home_country,
                is_fraud,
                fraud_reason,
                rule_based_risk_score,
                status,
                is_late_night,
                is_foreign_transaction,
                merchant_is_high_risk_category
            FROM FINGUARD.STAGING.FCT_TRANSACTIONS
            {where}
            ORDER BY rule_based_risk_score DESC, transaction_at DESC
            LIMIT {limit}
        """)
        return df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── GET /fraud-trends ─────────────────────────────────────────────────────────
@app.get("/fraud-trends")
def fraud_trends_endpoint():
    """Daily fraud count over time for the trend chart."""
    try:
        df = run_query("""
            SELECT
                transaction_date,
                COUNT(*)                                   AS total_txns,
                SUM(CASE WHEN is_fraud THEN 1 ELSE 0 END) AS fraud_txns,
                ROUND(SUM(CASE WHEN is_fraud THEN amount ELSE 0 END), 2) AS fraud_amount
            FROM FINGUARD.STAGING.FCT_TRANSACTIONS
            GROUP BY transaction_date
            ORDER BY transaction_date
        """)
        return df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── GET /fraud-by-category ────────────────────────────────────────────────────
@app.get("/fraud-by-category")
def fraud_by_category_endpoint():
    """Fraud breakdown by merchant category for the bar chart."""
    try:
        df = run_query("""
            SELECT
                merchant_category,
                COUNT(*)                                   AS total_txns,
                SUM(CASE WHEN is_fraud THEN 1 ELSE 0 END) AS fraud_count,
                ROUND(SUM(CASE WHEN is_fraud THEN amount ELSE 0 END), 2) AS fraud_amount,
                ROUND(AVG(CASE WHEN is_fraud THEN 1.0 ELSE 0 END) * 100, 2) AS fraud_rate_pct
            FROM FINGUARD.STAGING.FCT_TRANSACTIONS
            GROUP BY merchant_category
            ORDER BY fraud_amount DESC
            LIMIT 10
        """)
        return df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── GET /sample-fraud-id ──────────────────────────────────────────────────────
@app.get("/sample-fraud-id")
def sample_fraud_id():
    """Returns a sample fraud transaction ID for demo purposes."""
    try:
        df = run_query("""
            SELECT transaction_id
            FROM FINGUARD.STAGING.FCT_TRANSACTIONS
            WHERE is_fraud = TRUE AND rule_based_risk_score >= 0.4
            ORDER BY rule_based_risk_score DESC
            LIMIT 1
        """)
        return {"transaction_id": df.iloc[0]["transaction_id"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
