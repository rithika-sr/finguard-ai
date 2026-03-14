"""
FinGuard AI — Snowflake Query Tool
====================================
A reusable tool that CrewAI agents use to run SQL queries
against the FINGUARD Snowflake warehouse.
"""

import os
import snowflake.connector
import pandas as pd
from dotenv import load_dotenv
from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field

load_dotenv()


def get_snowflake_connection():
    """Create and return a Snowflake connection."""
    return snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema="STAGING",
    )


class SnowflakeQueryInput(BaseModel):
    """Input schema for the Snowflake query tool."""
    query: str = Field(description="The SQL query to execute against the FINGUARD Snowflake warehouse.")


class SnowflakeQueryTool(BaseTool):
    name: str = "snowflake_query"
    description: str = """
    Execute a SQL query against the FinGuard financial data warehouse.
    Use this to retrieve transaction data, fraud signals, user info, and merchant details.

    Available tables:
    - FINGUARD.STAGING.FCT_TRANSACTIONS — main analytics table with all fraud signals
      Key columns: transaction_id, user_id, merchant_id, amount, transaction_at,
      transaction_country, user_home_country, is_fraud, fraud_reason,
      is_late_night, is_round_amount, is_foreign_transaction,
      is_high_value_late_night, merchant_is_high_risk_category,
      rule_based_risk_score, merchant_category, user_name, merchant_name,
      credit_tier, merchant_risk_tier

    - FINGUARD.STAGING.STG_TRANSACTIONS — cleaned raw transactions
    - FINGUARD.STAGING.STG_USERS — cleaned user profiles
    - FINGUARD.STAGING.STG_MERCHANTS — cleaned merchant data

    Always use FINGUARD.STAGING as the schema prefix.
    Limit results to 100 rows unless asked for aggregations.
    """
    args_schema: Type[BaseModel] = SnowflakeQueryInput

    def _run(self, query: str) -> str:
        try:
            conn = get_snowflake_connection()
            cursor = conn.cursor()
            cursor.execute(query)
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            cursor.close()
            conn.close()

            if not rows:
                return "Query returned no results."

            df = pd.DataFrame(rows, columns=columns)
            return df.to_string(index=False, max_rows=50)

        except Exception as e:
            return f"Query failed: {str(e)}"
