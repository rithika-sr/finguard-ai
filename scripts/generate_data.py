"""
FinGuard AI — Synthetic Data Generator
=======================================
Generates realistic financial transaction data with hidden fraud patterns.
Outputs three CSV files into data/raw/:
  - transactions.csv  (~50,000 rows)
  - users.csv         (~2,000 rows)
  - merchants.csv     (~500 rows)

Fraud patterns baked in (ground truth):
  1. Late night high-value transactions (11pm–4am, amount > $800)
  2. Rapid successive transactions (same user, <60 seconds apart)
  3. Foreign location mismatch (user home country != transaction country)
  4. Unusual merchant category for user profile
  5. Round number amounts ($1000, $5000 exactly) — common in money laundering
"""

import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import random
import os
import uuid

fake = Faker()
Faker.seed(42)
np.random.seed(42)
random.seed(42)

# ── Config ──────────────────────────────────────────────────────────────────
NUM_USERS        = 2000
NUM_MERCHANTS    = 500
NUM_TRANSACTIONS = 50000
FRAUD_RATE       = 0.04   # 4% fraud — realistic for financial datasets
OUTPUT_DIR       = "data/raw"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Reference data ───────────────────────────────────────────────────────────
COUNTRIES = ["US", "US", "US", "US", "CA", "GB", "DE", "FR", "AU", "MX", "BR", "NG", "RU", "CN"]
MERCHANT_CATEGORIES = [
    "grocery", "restaurant", "gas_station", "online_retail", "travel",
    "entertainment", "pharmacy", "electronics", "clothing", "utilities",
    "healthcare", "education", "gambling", "crypto_exchange", "wire_transfer"
]
# Higher-risk categories (used in fraud pattern 4)
HIGH_RISK_CATEGORIES = {"gambling", "crypto_exchange", "wire_transfer"}

TRANSACTION_TYPES = ["purchase", "withdrawal", "transfer", "refund", "payment"]

# ── 1. Generate Users ─────────────────────────────────────────────────────────
print("Generating users...")
users = []
for _ in range(NUM_USERS):
    home_country = random.choices(
        ["US", "CA", "GB", "DE", "AU"],
        weights=[70, 10, 8, 6, 6]
    )[0]
    users.append({
        "user_id":        str(uuid.uuid4()),
        "name":           fake.name(),
        "email":          fake.email(),
        "age":            random.randint(18, 75),
        "home_country":   home_country,
        "account_type":   random.choices(["personal", "business"], weights=[80, 20])[0],
        "credit_score":   random.randint(300, 850),
        "created_at":     fake.date_time_between(start_date="-5y", end_date="-6m"),
        "is_high_risk":   random.random() < 0.05  # 5% flagged as high-risk profiles
    })

users_df = pd.DataFrame(users)
users_df.to_csv(f"{OUTPUT_DIR}/users.csv", index=False)
print(f"  ✓ {len(users_df)} users written to {OUTPUT_DIR}/users.csv")

# ── 2. Generate Merchants ─────────────────────────────────────────────────────
print("Generating merchants...")
merchants = []
for _ in range(NUM_MERCHANTS):
    category = random.choice(MERCHANT_CATEGORIES)
    merchants.append({
        "merchant_id":   str(uuid.uuid4()),
        "name":          fake.company(),
        "category":      category,
        "country":       random.choices(COUNTRIES, weights=[40,4,4,4,4,4,4,4,4,4,4,4,4,4])[0],
        "is_online":     random.random() < 0.35,
        "risk_score":    round(random.uniform(0.1, 1.0), 2),
        "created_at":    fake.date_time_between(start_date="-8y", end_date="-1y"),
    })

merchants_df = pd.DataFrame(merchants)
merchants_df.to_csv(f"{OUTPUT_DIR}/merchants.csv", index=False)
print(f"  ✓ {len(merchants_df)} merchants written to {OUTPUT_DIR}/merchants.csv")

# ── 3. Generate Transactions ──────────────────────────────────────────────────
print("Generating transactions (this may take a moment)...")

user_ids     = users_df["user_id"].tolist()
user_country = dict(zip(users_df["user_id"], users_df["home_country"]))
merchant_ids = merchants_df["merchant_id"].tolist()
merch_cat    = dict(zip(merchants_df["merchant_id"], merchants_df["category"]))
merch_country= dict(zip(merchants_df["merchant_id"], merchants_df["country"]))

transactions = []
# Track last transaction time per user for rapid-succession fraud
last_txn_time = {}

start_date = datetime.now() - timedelta(days=365)

for i in range(NUM_TRANSACTIONS):
    user_id     = random.choice(user_ids)
    merchant_id = random.choice(merchant_ids)
    txn_type    = random.choices(
        TRANSACTION_TYPES,
        weights=[55, 15, 15, 10, 5]
    )[0]

    # Base transaction timestamp — spread over the last year
    timestamp = start_date + timedelta(
        seconds=random.randint(0, 365 * 24 * 3600)
    )

    # Base amount — log-normal so most are small, few are large
    amount = round(np.random.lognormal(mean=4.5, sigma=1.2), 2)
    amount = max(1.0, min(amount, 50000.0))

    txn_country = merch_country[merchant_id]
    is_fraud    = False
    fraud_reason = None

    # ── Inject fraud patterns ──────────────────────────────────────────────
    roll = random.random()

    if roll < FRAUD_RATE:
        fraud_type = random.choices(
            ["late_night", "rapid_succession", "foreign_mismatch", "round_amount", "high_risk_merchant"],
            weights=[25, 20, 25, 15, 15]
        )[0]

        if fraud_type == "late_night":
            # Force timestamp to 11pm–4am
            fraud_hour = random.choice([23, 0, 1, 2, 3, 4])
            timestamp  = timestamp.replace(hour=fraud_hour, minute=random.randint(0,59))
            amount     = round(random.uniform(800, 8000), 2)
            fraud_reason = "late_night_high_value"
            is_fraud   = True

        elif fraud_type == "rapid_succession":
            # Force timestamp to be within 45 seconds of last transaction
            if user_id in last_txn_time:
                timestamp = last_txn_time[user_id] + timedelta(seconds=random.randint(5, 45))
                fraud_reason = "rapid_succession"
                is_fraud = True

        elif fraud_type == "foreign_mismatch":
            # Force transaction country to differ from user's home
            foreign_countries = [c for c in ["NG", "RU", "CN", "BR"] if c != user_country[user_id]]
            txn_country  = random.choice(foreign_countries)
            amount       = round(random.uniform(500, 5000), 2)
            fraud_reason = "foreign_location_mismatch"
            is_fraud     = True

        elif fraud_type == "round_amount":
            # Exact round numbers — money laundering signal
            amount       = random.choice([500, 1000, 2000, 5000, 10000])
            fraud_reason = "suspicious_round_amount"
            is_fraud     = True

        elif fraud_type == "high_risk_merchant":
            # Force merchant category to high-risk
            high_risk_merchants = merchants_df[
                merchants_df["category"].isin(HIGH_RISK_CATEGORIES)
            ]["merchant_id"].tolist()
            if high_risk_merchants:
                merchant_id  = random.choice(high_risk_merchants)
                amount       = round(random.uniform(200, 3000), 2)
                fraud_reason = "high_risk_merchant_category"
                is_fraud     = True

    last_txn_time[user_id] = timestamp

    transactions.append({
        "transaction_id":   str(uuid.uuid4()),
        "user_id":          user_id,
        "merchant_id":      merchant_id,
        "amount":           amount,
        "currency":         "USD",
        "transaction_type": txn_type,
        "timestamp":        timestamp,
        "transaction_country": txn_country,
        "device_type":      random.choices(["mobile", "web", "atm", "pos"], weights=[40,30,10,20])[0],
        "ip_address":       fake.ipv4(),
        "is_fraud":         is_fraud,          # ground truth label
        "fraud_reason":     fraud_reason,      # only set if fraud (for evaluation)
        "status":           random.choices(["completed", "pending", "failed"], weights=[90,7,3])[0],
        "created_at":       timestamp,
        "updated_at":       timestamp + timedelta(seconds=random.randint(1, 300)),
    })

transactions_df = pd.DataFrame(transactions)
transactions_df.to_csv(f"{OUTPUT_DIR}/transactions.csv", index=False)

# ── Summary ───────────────────────────────────────────────────────────────────
fraud_count = transactions_df["is_fraud"].sum()
print(f"  ✓ {len(transactions_df)} transactions written to {OUTPUT_DIR}/transactions.csv")
print()
print("=" * 50)
print("DATA GENERATION SUMMARY")
print("=" * 50)
print(f"  Users:           {len(users_df):,}")
print(f"  Merchants:       {len(merchants_df):,}")
print(f"  Transactions:    {len(transactions_df):,}")
print(f"  Fraud txns:      {fraud_count:,} ({fraud_count/len(transactions_df)*100:.1f}%)")
print()
print("Fraud breakdown:")
print(transactions_df[transactions_df["is_fraud"]]["fraud_reason"].value_counts().to_string())
print("=" * 50)
print("✓ All files written to data/raw/")
print("  Next step: run load_to_snowflake.py")