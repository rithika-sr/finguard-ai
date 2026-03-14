"""
FinGuard AI — Streamlit Dashboard (Enterprise Redesign)
=========================================================
Enterprise fintech aesthetic: Stripe/Palantir inspired.
Light background, strong typography, spacious layout, real depth.

Run with: streamlit run app.py
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FinGuard AI — Financial Intelligence",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

API_BASE = "http://localhost:8000"

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Sans:wght@300;400;500&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #f7f8fa;
    color: #0f172a;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 2.5rem; max-width: 100%; }

[data-testid="stSidebar"] {
    background: #ffffff;
    border-right: 1px solid #e8eaf0;
}
.sidebar-logo {
    background: #0f172a;
    padding: 1.8rem 1.4rem 1.4rem;
    margin: -1rem -1rem 1.4rem;
}
.sidebar-logo-text {
    font-family: 'Syne', sans-serif;
    font-size: 1.35rem;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: -0.03em;
}
.sidebar-logo-accent { color: #3b82f6; }
.sidebar-logo-sub {
    font-size: 0.68rem;
    color: #64748b;
    font-family: 'DM Mono', monospace;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-top: 0.25rem;
}
.nav-label {
    font-size: 0.6rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.16em;
    color: #94a3b8;
    font-family: 'DM Mono', monospace;
    margin-bottom: 0.3rem;
}
.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 0.7rem;
    font-family: 'DM Mono', monospace;
}
.status-online  { background:#f0fdf4; color:#16a34a; border:1px solid #bbf7d0; }
.status-offline { background:#fef2f2; color:#dc2626; border:1px solid #fecaca; }
.status-dot { width:6px; height:6px; border-radius:50%; background:currentColor; display:inline-block; }
.stack-tag {
    display: inline-block;
    background: #f1f5f9;
    border: 1px solid #e2e8f0;
    color: #475569;
    font-size: 0.65rem;
    font-family: 'DM Mono', monospace;
    padding: 2px 7px;
    border-radius: 4px;
    margin: 2px 2px 0 0;
}
.page-eyebrow {
    font-size: 0.65rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.18em;
    color: #3b82f6;
    font-family: 'DM Mono', monospace;
    margin-bottom: 0.3rem;
}
.page-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.9rem;
    font-weight: 700;
    color: #0f172a;
    letter-spacing: -0.03em;
    line-height: 1.1;
    margin-bottom: 0.3rem;
}
.page-subtitle {
    font-size: 0.875rem;
    color: #64748b;
    margin-bottom: 2rem;
}
.kpi-card {
    background: #ffffff;
    border: 1px solid #e8eaf0;
    border-radius: 12px;
    padding: 1.4rem 1.6rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 4px 12px rgba(0,0,0,0.03);
}
.kpi-eyebrow {
    font-size: 0.65rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.14em;
    color: #94a3b8;
    font-family: 'DM Mono', monospace;
    margin-bottom: 0.6rem;
}
.kpi-value {
    font-family: 'Syne', sans-serif;
    font-size: 2.1rem;
    font-weight: 700;
    color: #0f172a;
    letter-spacing: -0.04em;
    line-height: 1;
    margin-bottom: 0.35rem;
}
.kpi-sub { font-size: 0.75rem; color: #94a3b8; font-family: 'DM Mono', monospace; }
.kpi-accent-blue  { border-top: 3px solid #3b82f6; }
.kpi-accent-red   { border-top: 3px solid #ef4444; }
.kpi-accent-amber { border-top: 3px solid #f59e0b; }
.kpi-accent-green { border-top: 3px solid #10b981; }
.kpi-value-red    { color: #ef4444 !important; }
.kpi-value-amber  { color: #f59e0b !important; }
.chart-card {
    background: #ffffff;
    border: 1px solid #e8eaf0;
    border-radius: 12px;
    padding: 1.4rem 1.6rem 0.5rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 4px 12px rgba(0,0,0,0.03);
}
.chart-title {
    font-family: 'Syne', sans-serif;
    font-size: 0.95rem;
    font-weight: 600;
    color: #0f172a;
    margin-bottom: 0.15rem;
}
.chart-sub { font-size: 0.72rem; color: #94a3b8; font-family: 'DM Mono', monospace; margin-bottom: 0.6rem; }
.section-header {
    font-family: 'Syne', sans-serif;
    font-size: 1.05rem;
    font-weight: 600;
    color: #0f172a;
    margin-bottom: 0.15rem;
}
.section-sub { font-size: 0.75rem; color: #94a3b8; font-family: 'DM Mono', monospace; margin-bottom: 1rem; }
.agent-card {
    background: #ffffff;
    border: 1px solid #e8eaf0;
    border-radius: 12px;
    padding: 1.6rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.agent-output {
    font-family: 'DM Mono', monospace;
    font-size: 0.8rem;
    line-height: 1.8;
    color: #334155;
    white-space: pre-wrap;
    max-height: 520px;
    overflow-y: auto;
    background: #f8fafc;
    border: 1px solid #e8eaf0;
    border-radius: 8px;
    padding: 1.2rem 1.4rem;
    margin-top: 0.8rem;
}
.stTextInput input, .stTextArea textarea {
    background: #ffffff !important;
    border: 1.5px solid #e2e8f0 !important;
    border-radius: 8px !important;
    color: #0f172a !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.85rem !important;
}
.stButton > button {
    background: #0f172a !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.85rem !important;
    padding: 0.55rem 1.4rem !important;
}
.stButton > button:hover { background: #1e293b !important; }
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    background: transparent;
    border-bottom: 2px solid #e8eaf0;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.82rem;
    font-weight: 500;
    color: #64748b;
    padding: 0.7rem 1.4rem;
    border-bottom: 2px solid transparent;
    margin-bottom: -2px;
}
.stTabs [aria-selected="true"] {
    color: #0f172a !important;
    border-bottom-color: #0f172a !important;
    background: transparent !important;
}
.pipeline-card {
    background: #ffffff;
    border: 1px solid #e8eaf0;
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    min-height: 160px;
}
.pipeline-layer-num {
    font-size: 0.6rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.18em;
    font-family: 'DM Mono', monospace;
    margin-bottom: 0.4rem;
}
.pipeline-title {
    font-family: 'Syne', sans-serif;
    font-size: 0.9rem;
    font-weight: 700;
    color: #0f172a;
    margin-bottom: 0.3rem;
}
.pipeline-subtitle { font-size:0.7rem; font-family:'DM Mono',monospace; color:#64748b; margin-bottom:0.5rem; }
.pipeline-desc { font-size: 0.75rem; color: #475569; line-height: 1.5; }
[data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; border: 1px solid #e8eaf0; }
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────
def api_get(endpoint):
    try:
        r = requests.get(f"{API_BASE}{endpoint}", timeout=30)
        r.raise_for_status()
        return r.json(), None
    except Exception as e:
        return None, str(e)

def api_post(endpoint, body=None):
    try:
        r = requests.post(f"{API_BASE}{endpoint}", json=body, timeout=120)
        r.raise_for_status()
        return r.json(), None
    except Exception as e:
        return None, str(e)


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
        <div class="sidebar-logo-text">Fin<span class="sidebar-logo-accent">Guard</span> AI</div>
        <div class="sidebar-logo-sub">Financial Intelligence Platform</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="nav-label">Menu</div>', unsafe_allow_html=True)
    page = st.radio("", [
        "📊  Overview",
        "🔍  Fraud Investigator",
        "🗄️  Data Lineage",
        "💬  AI Query",
    ], label_visibility="collapsed")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="nav-label">System Status</div>', unsafe_allow_html=True)
    health, _ = api_get("/health")
    if health:
        st.markdown('<div class="status-pill status-online"><span class="status-dot"></span> API Online</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-pill status-offline"><span class="status-dot"></span> API Offline</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="nav-label">Tech Stack</div>', unsafe_allow_html=True)
    st.markdown("""<div>
        <span class="stack-tag">Snowflake</span><span class="stack-tag">dbt</span>
        <span class="stack-tag">CrewAI</span><span class="stack-tag">GPT-4o-mini</span>
        <span class="stack-tag">FastAPI</span><span class="stack-tag">Streamlit</span>
    </div>""", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div style="font-size:0.65rem;color:#cbd5e1;font-family:DM Mono,monospace;">v1.0.0 · Built by Rithika</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
if page == "📊  Overview":
    st.markdown("""
    <div class="page-eyebrow">Dashboard</div>
    <div class="page-title">Transaction Overview</div>
    <div class="page-subtitle">Real-time fraud monitoring and risk intelligence across all financial transactions.</div>
    """, unsafe_allow_html=True)

    metrics, err = api_get("/metrics")
    if not metrics:
        st.error(f"⚠️ API unavailable. Run: `uvicorn api:app --reload` · Error: {err}")
        st.stop()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class="kpi-card kpi-accent-blue">
            <div class="kpi-eyebrow">Total Transactions</div>
            <div class="kpi-value">{int(metrics['total_transactions']):,}</div>
            <div class="kpi-sub">All time · 1 year window</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="kpi-card kpi-accent-red">
            <div class="kpi-eyebrow">Fraud Detected</div>
            <div class="kpi-value kpi-value-red">{int(metrics['total_fraud']):,}</div>
            <div class="kpi-sub">{metrics['fraud_rate_pct']}% fraud rate</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="kpi-card kpi-accent-amber">
            <div class="kpi-eyebrow">Fraud Exposure</div>
            <div class="kpi-value kpi-value-amber">${float(metrics['total_fraud_amount']):,.0f}</div>
            <div class="kpi-sub">Total at-risk value</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class="kpi-card kpi-accent-green">
            <div class="kpi-eyebrow">Avg Transaction</div>
            <div class="kpi-value">${float(metrics['avg_transaction_amount']):,.0f}</div>
            <div class="kpi-sub">{int(metrics['unique_users']):,} users · {int(metrics['unique_merchants']):,} merchants</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_l, col_r = st.columns([3, 2], gap="large")
    with col_l:
        st.markdown("""<div class="chart-card">
            <div class="chart-title">Fraud Volume Over Time</div>
            <div class="chart-sub">Daily transaction count vs. flagged fraud events</div>
        </div>""", unsafe_allow_html=True)
        trends, _ = api_get("/fraud-trends")
        if trends:
            df_t = pd.DataFrame(trends)
            df_t["transaction_date"] = pd.to_datetime(df_t["transaction_date"])
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_t["transaction_date"], y=df_t["total_txns"], name="All transactions",
                line=dict(color="#cbd5e1", width=1.5),
                fill="tozeroy", fillcolor="rgba(203,213,225,0.15)"))
            fig.add_trace(go.Scatter(
                x=df_t["transaction_date"], y=df_t["fraud_txns"], name="Fraud flagged",
                line=dict(color="#ef4444", width=2),
                fill="tozeroy", fillcolor="rgba(239,68,68,0.08)"))
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="DM Mono", color="#94a3b8", size=11),
                legend=dict(bgcolor="rgba(0,0,0,0)", orientation="h",
                            yanchor="bottom", y=1.02, xanchor="right", x=1),
                xaxis=dict(gridcolor="#f1f5f9", showline=False, zeroline=False),
                yaxis=dict(gridcolor="#f1f5f9", showline=False, zeroline=False),
                margin=dict(l=0, r=0, t=30, b=0), height=300,
            )
            st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.markdown("""<div class="chart-card">
            <div class="chart-title">Fraud by Category</div>
            <div class="chart-sub">Flagged amount by merchant type</div>
        </div>""", unsafe_allow_html=True)
        cats, _ = api_get("/fraud-by-category")
        if cats:
            df_c = pd.DataFrame(cats).head(8).sort_values("fraud_amount")
            high_risk = ["wire_transfer", "gambling", "crypto_exchange"]
            colors = ["#fee2e2" if c in high_risk else "#dbeafe" for c in df_c["merchant_category"]]
            line_colors = ["#fca5a5" if c in high_risk else "#93c5fd" for c in df_c["merchant_category"]]
            fig2 = go.Figure(go.Bar(
                x=df_c["fraud_amount"], y=df_c["merchant_category"],
                orientation="h", marker_color=colors,
                marker_line_color=line_colors, marker_line_width=1,
                text=df_c["fraud_count"].apply(lambda x: f"{int(x)}"),
                textposition="inside",
                textfont=dict(size=10, family="DM Mono", color="#334155"),
            ))
            fig2.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="DM Mono", color="#94a3b8", size=10),
                xaxis=dict(gridcolor="#f1f5f9", showline=False, zeroline=False),
                yaxis=dict(showline=False),
                margin=dict(l=0, r=0, t=30, b=0), height=300, showlegend=False,
            )
            st.plotly_chart(fig2, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div class="section-header">High-Risk Transaction Feed</div>
    <div class="section-sub">Sorted by risk score descending</div>
    """, unsafe_allow_html=True)

    f1, f2, f3 = st.columns([1, 2, 1])
    with f1:
        fraud_only = st.checkbox("Fraud flagged only", value=True)
    with f2:
        min_risk = st.slider("Minimum risk score", 0.0, 1.0, 0.25, 0.05)
    with f3:
        limit = st.selectbox("Rows", [25, 50, 100], index=1)

    txns, _ = api_get(f"/transactions?fraud_only={str(fraud_only).lower()}&min_risk={min_risk}&limit={limit}")
    if txns:
        df_txns = pd.DataFrame(txns)
        df_txns["Status"] = df_txns["is_fraud"].apply(lambda x: "🔴 Fraud" if x else "🟢 Clear")
        df_txns["Risk"]   = df_txns["rule_based_risk_score"].apply(lambda x: f"{float(x):.2f}")
        df_txns["Amount"] = df_txns["amount"].apply(lambda x: f"${float(x):,.2f}")
        df_txns["Time"]   = pd.to_datetime(df_txns["transaction_at"]).dt.strftime("%b %d, %H:%M")
        st.dataframe(
            df_txns[["Time","user_name","merchant_name","merchant_category",
                     "Amount","transaction_country","Status","Risk","fraud_reason"]].rename(columns={
                "user_name":"User","merchant_name":"Merchant","merchant_category":"Category",
                "transaction_country":"Country","fraud_reason":"Fraud Signal",
            }),
            use_container_width=True, height=400,
        )


# ══════════════════════════════════════════════════════════════════════════════
# FRAUD INVESTIGATOR
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🔍  Fraud Investigator":
    st.markdown("""
    <div class="page-eyebrow">AI Agent</div>
    <div class="page-title">Fraud Investigator</div>
    <div class="page-subtitle">Enter any transaction ID to receive a complete AI-generated fraud assessment with risk signal breakdown and recommended action.</div>
    """, unsafe_allow_html=True)

    sample, _ = api_get("/sample-fraud-id")
    sample_id  = sample["transaction_id"] if sample else ""

    col1, col2 = st.columns([4, 1], gap="medium")
    with col1:
        txn_id = st.text_input("Transaction ID", value=sample_id, placeholder="Paste any transaction UUID...")
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("↻ New Sample"):
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["  Fraud Assessment  ", "  Data Lineage Audit  "])

    with tab1:
        if st.button("Run Fraud Analysis →", key="fraud_btn"):
            if not txn_id.strip():
                st.warning("Please enter a transaction ID.")
            else:
                with st.spinner("Fraud agent analyzing transaction signals..."):
                    result, err = api_post(f"/fraud/{txn_id.strip()}")
                if result and result["success"]:
                    st.markdown('<div class="agent-card"><div class="chart-title">Assessment Report</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="agent-output">{result["result"]}</div></div>', unsafe_allow_html=True)
                else:
                    st.error(f"Agent error: {err or (result or {}).get('error','Unknown')}")

    with tab2:
        if st.button("Run Lineage Audit →", key="lineage_btn"):
            if not txn_id.strip():
                st.warning("Please enter a transaction ID.")
            else:
                with st.spinner("Tracing data from source to AI decision..."):
                    result, err = api_post(f"/lineage/{txn_id.strip()}")
                if result and result["success"]:
                    st.markdown('<div class="agent-card"><div class="chart-title">Lineage Audit Trail</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="agent-output">{result["result"]}</div></div>', unsafe_allow_html=True)
                else:
                    st.error(f"Agent error: {err or (result or {}).get('error','Unknown')}")


# ══════════════════════════════════════════════════════════════════════════════
# DATA LINEAGE
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🗄️  Data Lineage":
    st.markdown("""
    <div class="page-eyebrow">Governance</div>
    <div class="page-title">Data Lineage & Governance</div>
    <div class="page-subtitle">Full audit trail from raw data source through dbt transformations to every AI decision. Built for regulatory transparency.</div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-header">Data Pipeline</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">4-layer transformation from raw ingestion to AI inference</div>', unsafe_allow_html=True)

    pipeline = [
        ("Layer 01", "Raw Ingestion",  "FINGUARD.RAW",      "CSV → Snowflake via Python. 52,500 rows, 3 tables.",          "#eff6ff", "#3b82f6"),
        ("Layer 02", "dbt Staging",    "STG_TRANSACTIONS",  "Type casting, normalization, 6 derived fraud signal flags.",   "#f0fdf4", "#10b981"),
        ("Layer 03", "dbt Mart",       "FCT_TRANSACTIONS",  "3-way join enrichment. rule_based_risk_score computed.",       "#fffbeb", "#f59e0b"),
        ("Layer 04", "AI Decision",    "CrewAI Agents",     "3 agents: Query · Fraud · Lineage. GPT-4o-mini powered.",      "#fdf4ff", "#a855f7"),
    ]
    cols = st.columns(4, gap="medium")
    for col, (num, title, subtitle, desc, bg, accent) in zip(cols, pipeline):
        with col:
            st.markdown(f"""<div class="pipeline-card" style="border-top:3px solid {accent}; background:{bg};">
                <div class="pipeline-layer-num" style="color:{accent};">{num}</div>
                <div class="pipeline-title">{title}</div>
                <div class="pipeline-subtitle">{subtitle}</div>
                <div class="pipeline-desc">{desc}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">Data Quality</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Automated dbt tests run on every model</div>', unsafe_allow_html=True)

    quality = [
        ("Tests Passing", "23 / 23", "100% pass rate",     "#f0fdf4", "#10b981"),
        ("Models Built",  "4",       "3 staging + 1 mart", "#eff6ff", "#3b82f6"),
        ("Derived Fields","8",       "fraud signal cols",  "#fffbeb", "#f59e0b"),
        ("Sources",       "3",       "RAW schema tables",  "#fdf4ff", "#a855f7"),
    ]
    qcols = st.columns(4)
    for col, (label, val, sub, bg, accent) in zip(qcols, quality):
        with col:
            st.markdown(f"""<div class="kpi-card" style="background:{bg}; border-top:3px solid {accent};">
                <div class="kpi-eyebrow">{label}</div>
                <div class="kpi-value" style="font-size:1.6rem;">{val}</div>
                <div class="kpi-sub">{sub}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">Fraud Signal Definitions</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">How each risk signal is computed in fct_transactions</div>', unsafe_allow_html=True)

    signals = [
        ("is_late_night",            "HOUR >= 23 OR HOUR <= 4",                              "0.20"),
        ("is_round_amount",          "amount MOD 100 = 0",                                   "0.15"),
        ("is_foreign_transaction",   "transaction_country != user_home_country",              "0.25"),
        ("is_high_value_late_night", "amount > 800 AND is_late_night",                       "0.20 (combo)"),
        ("merchant_is_high_risk",    "category IN (gambling, crypto_exchange, wire_transfer)","0.20"),
        ("user_is_high_risk",        "user profile flagged at ingestion",                    "0.10"),
    ]
    st.dataframe(pd.DataFrame(signals, columns=["Signal","SQL Logic","Risk Weight"]),
                 use_container_width=True, hide_index=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""<div class="agent-card">
        <div class="chart-title">View Interactive Lineage Graph</div>
        <div class="chart-sub" style="margin-top:0.3rem;">Generated by dbt docs</div>
        <div style="margin-top:0.8rem;font-size:0.82rem;color:#475569;font-family:DM Mono,monospace;line-height:2;">
            Run in terminal: <code style="background:#f1f5f9;padding:2px 8px;border-radius:4px;color:#0f172a;">cd dbt_project && dbt docs serve</code><br>
            Then open <span style="color:#3b82f6;font-weight:500;">localhost:8080</span> → click the blue circle icon (bottom right).
        </div>
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# AI QUERY
# ══════════════════════════════════════════════════════════════════════════════
elif page == "💬  AI Query":
    st.markdown("""
    <div class="page-eyebrow">AI Agent</div>
    <div class="page-title">Natural Language Query</div>
    <div class="page-subtitle">Ask any question about your financial data in plain English. The agent writes SQL, queries Snowflake, and interprets the results.</div>
    """, unsafe_allow_html=True)

    examples = [
        "Top 5 merchant categories by total fraud amount?",
        "What is the fraud rate by device type?",
        "Which users have the most flagged transactions?",
        "Average transaction amount for foreign mismatches?",
        "How does fraud volume vary by hour of day?",
    ]

    st.markdown('<div class="section-header">Quick Queries</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Click any to populate the input below</div>', unsafe_allow_html=True)

    cols = st.columns(len(examples))
    selected = None
    for i, (col, ex) in enumerate(zip(cols, examples)):
        with col:
            if st.button(f"Q{i+1}", help=ex, key=f"ex_{i}"):
                selected = ex

    st.markdown("<br>", unsafe_allow_html=True)
    question = st.text_area("Your question", value=selected or "",
                            placeholder="e.g. What percentage of wire transfer transactions are fraudulent?",
                            height=90)

    col_btn, col_note = st.columns([1, 4])
    with col_btn:
        ask = st.button("Ask FinGuard AI →")
    with col_note:
        st.markdown('<div style="font-size:0.72rem;color:#94a3b8;font-family:DM Mono,monospace;padding-top:0.7rem;">Powered by CrewAI + GPT-4o-mini + Snowflake</div>', unsafe_allow_html=True)

    if ask:
        if not question.strip():
            st.warning("Please enter a question.")
        else:
            with st.spinner("Query agent thinking..."):
                result, err = api_post("/query", {"question": question.strip()})
            if result and result["success"]:
                st.markdown('<div class="agent-card"><div class="chart-title">Agent Response</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="agent-output">{result["result"]}</div></div>', unsafe_allow_html=True)
            else:
                st.error(f"Agent error: {err or (result or {}).get('error','Unknown')}")