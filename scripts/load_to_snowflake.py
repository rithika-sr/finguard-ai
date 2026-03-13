"""
FinGuard AI — Snowflake Data Loader
=====================================
Loads the three CSVs from data/raw/ into Snowflake FINGUARD.RAW schema.
Creates tables with proper data types if they don't exist, then bulk-loads.

Run AFTER generate_data.py.
"""

import snowflake.connector
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

# ── Connect to Snowflake ──────────────────────────────────────────────────────
print("Connecting to Snowflake...")
conn = snowflake.connector.connect(
    account   = os.getenv("SNOWFLAKE_ACCOUNT"),
    user      = os.getenv("SNOWFLAKE_USER"),
    password  = os.getenv("SNOWFLAKE_PASSWORD"),
    warehouse = os.getenv("SNOWFLAKE_WAREHOUSE"),
    database  = os.getenv("SNOWFLAKE_DATABASE"),
    schema    = os.getenv("SNOWFLAKE_SCHEMA"),
)
cursor = conn.cursor()
print("  ✓ Connected successfully")

# ── Create tables ─────────────────────────────────────────────────────────────
print("Creating tables in FINGUARD.RAW...")

cursor.execute("""
CREATE TABLE IF NOT EXISTS FINGUARD.RAW.USERS (
    user_id        VARCHAR(36)   NOT NULL PRIMARY KEY,
    name           VARCHAR(100),
    email          VARCHAR(150),
    age            INTEGER,
    home_country   VARCHAR(10),
    account_type   VARCHAR(20),
    credit_score   INTEGER,
    created_at     TIMESTAMP_NTZ,
    is_high_risk   BOOLEAN
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS FINGUARD.RAW.MERCHANTS (
    merchant_id  VARCHAR(36)   NOT NULL PRIMARY KEY,
    name         VARCHAR(200),
    category     VARCHAR(50),
    country      VARCHAR(10),
    is_online    BOOLEAN,
    risk_score   FLOAT,
    created_at   TIMESTAMP_NTZ
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS FINGUARD.RAW.TRANSACTIONS (
    transaction_id      VARCHAR(36)   NOT NULL PRIMARY KEY,
    user_id             VARCHAR(36),
    merchant_id         VARCHAR(36),
    amount              FLOAT,
    currency            VARCHAR(5),
    transaction_type    VARCHAR(20),
    timestamp           TIMESTAMP_NTZ,
    transaction_country VARCHAR(10),
    device_type         VARCHAR(20),
    ip_address          VARCHAR(50),
    is_fraud            BOOLEAN,
    fraud_reason        VARCHAR(100),
    status              VARCHAR(20),
    created_at          TIMESTAMP_NTZ,
    updated_at          TIMESTAMP_NTZ
)
""")
print("  ✓ Tables created")

# ── Helper: load a CSV into a Snowflake table ─────────────────────────────────
def load_csv_to_snowflake(csv_path: str, table_name: str):
    print(f"Loading {csv_path} → FINGUARD.RAW.{table_name}...")
    df = pd.read_csv(csv_path)

    # Truncate table first so re-runs don't duplicate
    cursor.execute(f"TRUNCATE TABLE FINGUARD.RAW.{table_name}")

    # Write rows in batches of 5,000
    batch_size = 5000
    total      = len(df)
    cols       = ", ".join(df.columns)
    placeholders = ", ".join(["%s"] * len(df.columns))

    for start in range(0, total, batch_size):
        batch = df.iloc[start:start + batch_size]
        # Replace NaN with None so Snowflake stores NULL
        rows = [
            tuple(None if pd.isna(v) else v for v in row)
            for row in batch.itertuples(index=False, name=None)
        ]
        cursor.executemany(
            f"INSERT INTO FINGUARD.RAW.{table_name} ({cols}) VALUES ({placeholders})",
            rows
        )
        loaded = min(start + batch_size, total)
        print(f"  ... {loaded:,} / {total:,} rows", end="\r")

    print(f"  ✓ {total:,} rows loaded into {table_name}          ")

# ── Load all three files ──────────────────────────────────────────────────────
load_csv_to_snowflake("data/raw/users.csv",        "USERS")
load_csv_to_snowflake("data/raw/merchants.csv",    "MERCHANTS")
load_csv_to_snowflake("data/raw/transactions.csv", "TRANSACTIONS")

# ── Verify row counts ─────────────────────────────────────────────────────────
print("\nVerifying row counts in Snowflake...")
for table in ["USERS", "MERCHANTS", "TRANSACTIONS"]:
    cursor.execute(f"SELECT COUNT(*) FROM FINGUARD.RAW.{table}")
    count = cursor.fetchone()[0]
    print(f"  FINGUARD.RAW.{table}: {count:,} rows")

cursor.close()
conn.close()
print("\n✓ All data loaded. Snowflake connection closed.")
print("  Next step: set up dbt for data transformation!")