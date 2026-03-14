# 🛡️ FinGuard AI - Financial Intelligence Platform

> An AI-powered financial oversight platform that detects fraud, explains decisions, and provides full data lineage audit trails for every AI inference.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)
![Snowflake](https://img.shields.io/badge/Snowflake-Data_Warehouse-29B5E8?style=flat&logo=snowflake&logoColor=white)
![dbt](https://img.shields.io/badge/dbt-Data_Transformation-FF694B?style=flat&logo=dbt&logoColor=white)
![CrewAI](https://img.shields.io/badge/CrewAI-Agentic_AI-6366f1?style=flat)
![FastAPI](https://img.shields.io/badge/FastAPI-REST_API-009688?style=flat&logo=fastapi&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=flat&logo=streamlit&logoColor=white)

---

## 📌 What Is This?

FinGuard AI addresses one of the biggest challenges in enterprise AI adoption in 2026: **"Can I trust this decision?"**

A compliance analyst can ask plain-English questions like *"Why was transaction #TXN-4892 flagged?"* and receive:
- A structured fraud assessment report citing specific risk signals
- The exact SQL query the agent generated and ran
- A complete **data lineage audit trail** — from raw CSV ingestion through dbt transformations to the AI decision

This "Trust and Transparency" architecture is directly aligned with emerging AI governance frameworks (Basel III, GDPR, EU AI Act).

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Streamlit Dashboard                   │
│     Overview · Fraud Investigator · Lineage · Query      │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTP
┌──────────────────────▼──────────────────────────────────┐
│                   FastAPI Backend                        │
│   /metrics · /transactions · /fraud · /lineage · /query  │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│                  CrewAI Agents                           │
│    Query Agent · Fraud Agent · Lineage Agent             │
│              Powered by GPT-4o-mini                      │
└──────────────────────┬──────────────────────────────────┘
                       │ SQL
┌──────────────────────▼──────────────────────────────────┐
│              Snowflake Data Warehouse                    │
│                                                          │
│  RAW Schema          STAGING Schema                      │
│  ├── transactions    ├── stg_transactions  (dbt)         │
│  ├── users           ├── stg_users         (dbt)         │
│  └── merchants       ├── stg_merchants     (dbt)         │
│                      └── fct_transactions  (dbt mart)    │
└─────────────────────────────────────────────────────────┘
```
<img width="2596" height="1280" alt="Image" src="https://github.com/user-attachments/assets/308e8ccd-004f-4dd5-af4b-26eca2756f43" />

---

## ✨ Key Features

### 📊 Real-Time Dashboard
<img width="2704" height="1506" alt="Image" src="https://github.com/user-attachments/assets/934a947d-3600-48c8-a619-0d197860c94d" />
- 4 KPI cards: total transactions, fraud count, fraud exposure, avg transaction
- Fraud volume over time chart (daily trend)
- Fraud breakdown by merchant category
- Filterable high-risk transaction feed

### 🔍 Fraud Investigator
<img width="2700" height="1508" alt="Image" src="https://github.com/user-attachments/assets/e3654c68-398b-40d2-86f1-df069fbc874d" />
- Enter any transaction ID → AI generates a complete fraud assessment report
- Identifies which of 5 fraud patterns fired: late-night, foreign location, rapid succession, round amounts, high-risk merchant
- Weighted risk score (0.0–1.0) with recommended action: Auto-approve / Manual review / Block

### 🗄️ Data Lineage & Governance
<img width="2680" height="1242" alt="Image" src="https://github.com/user-attachments/assets/751ee5cb-7f78-42cf-8ea1-6d610667f947" />
- 4-layer pipeline visualization: Raw → Staging → Mart → AI Decision
- Complete audit trail for every transaction showing all transformations applied
- dbt lineage graph integration
- 23 automated data quality tests documented

### 💬 Natural Language Query
<img width="2700" height="1506" alt="Image" src="https://github.com/user-attachments/assets/5273992c-3457-4efc-a4d4-8198e91ea286" />
- Ask any question about the financial data in plain English
- Agent writes SQL, executes against Snowflake, interprets results
- Always returns the SQL used for full transparency

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Data Warehouse | Snowflake | Cloud-native data storage |
| Data Transformation | dbt | SQL models, lineage, tests |
| AI Agents | CrewAI + GPT-4o-mini | Agentic workflows |
| API Backend | FastAPI | REST endpoints |
| Dashboard | Streamlit | Interactive UI |
| Data Processing | Pandas + NumPy | Data manipulation |
| Visualization | Plotly | Charts |

---

## 📁 Project Structure

```
finguard-ai/
├── api.py                    # FastAPI backend (7 endpoints)
├── app.py                    # Streamlit dashboard (4 pages)
├── crew.py                   # CrewAI orchestrator
├── agents.py                 # 3 AI agent definitions
├── tasks.py                  # Agent task definitions
├── tools/
│   └── snowflake_tool.py     # Custom CrewAI tool for Snowflake
├── scripts/
│   ├── generate_data.py      # Synthetic data generator
│   └── load_to_snowflake.py  # Snowflake ingestion pipeline
├── dbt_project/
│   └── models/
│       ├── staging/
│       │   ├── stg_transactions.sql
│       │   ├── stg_users.sql
│       │   ├── stg_merchants.sql
│       │   └── schema.yml
│       └── mart/
│           └── fct_transactions.sql
├── .streamlit/
│   └── config.toml           # Light mode theme config
├── .env.example              # Environment variable template
├── requirements.txt
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Snowflake account (free trial at snowflake.com)
- OpenAI API key (platform.openai.com)

### 1. Clone the repo
```bash
git clone https://github.com/rithika-sr/finguard-ai.git
cd finguard-ai
```

### 2. Create virtual environment
```bash
python3 -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment
```bash
cp .env.example .env
# Edit .env with your Snowflake and OpenAI credentials
```

### 5. Set up Snowflake
Run this SQL in your Snowflake worksheet:
```sql
CREATE DATABASE IF NOT EXISTS FINGUARD;
CREATE SCHEMA IF NOT EXISTS FINGUARD.RAW;
CREATE SCHEMA IF NOT EXISTS FINGUARD.STAGING;
CREATE SCHEMA IF NOT EXISTS FINGUARD.MART;
```

### 6. Generate and load data
```bash
python scripts/generate_data.py       # Creates 50k synthetic transactions
python scripts/load_to_snowflake.py   # Loads into Snowflake RAW schema
```

### 7. Run dbt transformations
```bash
cd dbt_project
dbt run        # Builds all 4 models
dbt test       # Runs 23 data quality tests
cd ..
```

### 8. Launch the app
Open two terminals:

**Terminal 1 — API:**
```bash
uvicorn api:app --reload --port 8000
```

**Terminal 2 — Dashboard:**
```bash
streamlit run app.py
```

Open **http://localhost:8501** in your browser.

---

## 📊 Dataset

| Table | Rows | Description |
|---|---|---|
| `RAW.TRANSACTIONS` | 50,000 | Synthetic financial transactions |
| `RAW.USERS` | 2,000 | User profiles |
| `RAW.MERCHANTS` | 500 | Merchant data |

**Fraud patterns injected (3.9% fraud rate):**

| Pattern | Count | Description |
|---|---|---|
| Late night high-value | 510 | Transactions at 11pm–4am with amount > $800 |
| Foreign location mismatch | 490 | Transaction country ≠ user home country |
| Rapid succession | 353 | Same user, <60 seconds between transactions |
| Suspicious round amounts | 336 | Exact round numbers ($1000, $5000, etc.) |
| High-risk merchant | 271 | Wire transfers, gambling, crypto exchanges |

---

## 🔮 Future Roadmap

- [ ] ML model (Isolation Forest / XGBoost) to replace rule-based risk scoring
- [ ] Real-time Kafka streaming pipeline
- [ ] User authentication and role-based access
- [ ] Automated daily dbt runs via Airflow
- [ ] Export compliance reports as PDF
