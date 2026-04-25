import os
import json
import numpy as np
import altair as alt
import streamlit as st
from dotenv import load_dotenv
from google import genai
import pandas as pd
import duckdb
from datetime import datetime

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

st.set_page_config(
    page_title="MSME Underwriter | Institutional Release",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"Get Help": None, "Report a bug": None, "About": None}
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
:root {
    --bg: #f0ede6;
    --surface: #ffffff;
    --surface-2: #f8fafc;
    --text: #1f2937;
    --muted: #64748b;
    --border: #dbe2ea;
    --primary: #0f766e;
    --approve-bg: #ecfdf3;
    --approve-fg: #166534;
    --approve-bd: #22c55e;
    --refer-bg: #fffbeb;
    --refer-fg: #92400e;
    --refer-bd: #f59e0b;
    --decline-bg: #fef2f2;
    --decline-fg: #991b1b;
    --decline-bd: #ef4444;
}
@media (prefers-color-scheme: dark) {
    :root {
        --bg: #171614;
        --surface: #1c1b19;
        --surface-2: #23211f;
        --text: #e5e7eb;
        --muted: #a1a1aa;
        --border: #3a3a3a;
        --primary: #4f98a3;
        --approve-bg: #16261d;
        --approve-fg: #86efac;
        --approve-bd: #22c55e;
        --refer-bg: #2a2415;
        --refer-fg: #fbbf24;
        --refer-bd: #f59e0b;
        --decline-bg: #2a1818;
        --decline-fg: #fca5a5;
        --decline-bd: #ef4444;
    }
}
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
/* ── Sidebar collapse button: hide broken Material Icons text, inject chevron ── */
[data-testid="stSidebarCollapseButton"] span,
[data-testid="stSidebarCollapsedControl"] span {
    font-size: 0 !important;
    color: transparent !important;
}
[data-testid="stSidebarCollapseButton"] span::after,
[data-testid="stSidebarCollapsedControl"] span::after {
    content: '❮';
    font-size: 15px !important;
    color: var(--muted) !important;
    font-family: Arial, sans-serif !important;
}
.stApp { background: var(--bg); color: var(--text); }
.hero-card {
    background: var(--surface);
    border: 1px solid var(--border);
    padding: 18px;
    border-radius: 14px;
    box-shadow: 0 1px 2px rgba(0,0,0,0.04);
    height: 100%;
}
.hero-label {
    color: var(--muted) !important;
    font-size: 0.72rem;
    font-weight: 800;
    text-transform: uppercase;
    margin-bottom: 6px;
    display: flex;
    justify-content: space-between;
    letter-spacing: 0.04em;
}
.hero-value { color: var(--text) !important; font-size: 1.55rem; font-weight: 800; line-height: 1.1; }
.hero-subtext { color: var(--muted) !important; font-size: 0.82rem; margin-top: 8px; line-height: 1.35; }
.entity-strip {
    background: #eef1f6;
    border: 1px solid #c5cfde;
    border-radius: 14px;
    padding: 14px 18px;
    margin-bottom: 16px;
}
@media (prefers-color-scheme: dark) {
    .entity-strip { background: #1a1e28 !important; border-color: #2a3248 !important; }
}
.entity-name { color: var(--text) !important; font-weight: 800; font-size: 1.15rem; margin-bottom: 8px; }
.entity-meta { color: var(--muted) !important; font-size: 0.88rem; display: flex; gap: 18px; flex-wrap: wrap; }
.status-box { padding: 22px 24px; border-radius: 14px; margin-bottom: 18px; border-left: 10px solid; }
.approve { background: var(--approve-bg); color: var(--approve-fg); border-color: var(--approve-bd); }
.refer   { background: var(--refer-bg);   color: var(--refer-fg);   border-color: var(--refer-bd); }
.decline { background: var(--decline-bg); color: var(--decline-fg); border-color: var(--decline-bd); }
.waterfall-table { width: 100%; font-size: 0.88rem; border-collapse: collapse; }
.waterfall-table td { padding: 10px 0; border-bottom: 1px solid var(--border); color: var(--text); }
.policy-table { width: 100%; border-radius: 10px; overflow: hidden; border: 1px solid var(--border); font-size: 0.86rem; }
.policy-table th { background: var(--surface-2); padding: 12px; text-align: left; color: var(--muted); border-bottom: 1px solid var(--border); }
.policy-table td { padding: 12px; border-bottom: 1px solid var(--border); color: var(--text); }
.metric-badge { display: inline-block; margin-top: 10px; padding: 4px 8px; border-radius: 999px; font-size: 0.72rem; font-weight: 700; letter-spacing: 0.02em; }
.metric-good  { background: #dcfce7; color: #166534; }
.metric-watch { background: #fef3c7; color: #92400e; }
.metric-bad   { background: #fee2e2; color: #991b1b; }
.tooltip-icon {
    position: relative; cursor: pointer;
    color: var(--muted); font-size: 1rem;
}
.tooltip-icon:focus { outline: none; }
.tooltip-text {
    display: none;
    position: absolute;
    bottom: 130%;
    left: 50%;
    transform: translateX(-50%);
    background: #1f2937;
    color: #fff;
    font-size: 0.74rem;
    font-weight: 400;
    text-transform: none;
    letter-spacing: normal;
    padding: 7px 10px;
    border-radius: 8px;
    width: 210px;
    z-index: 9999;
    line-height: 1.45;
    white-space: normal;
    pointer-events: none;
    box-shadow: 0 4px 12px rgba(0,0,0,0.18);
}
.tooltip-icon:hover .tooltip-text,
.tooltip-icon:focus .tooltip-text { display: block; }
.caption-box { background: var(--surface-2); border: 1px solid var(--border); padding: 12px 14px; border-radius: 10px; color: var(--text); font-size: 0.9rem; line-height: 1.45; }
.section-kicker { color: var(--muted); text-transform: uppercase; letter-spacing: .08em; font-size: 0.72rem; font-weight: 800; margin-bottom: 8px; }
.insight-box { background: var(--surface-2); border-left: 4px solid var(--primary); border-radius: 0 8px 8px 0; padding: 10px 14px; margin: 12px 0 16px 0; color: var(--muted); font-size: 0.86rem; font-style: italic; }
.gate-pass { color: #166534; font-weight: 700; }
.gate-warn { color: #92400e; font-weight: 700; }
.gate-fail { color: #991b1b; font-weight: 700; }
.brand-sidebar { padding: 0.3rem 0; margin-bottom: 0.3rem; }
.brand-title { color: var(--text) !important; font-size: 1.1rem; font-weight: 800; line-height: 1.2; margin-bottom: 0.35rem; }
.sidebar-link { display: inline-flex; align-items: center; gap: 5px; color: #0a66c2 !important; font-size: 0.82rem; font-weight: 700; text-decoration: none; margin-top: 4px; }
.sidebar-link:hover { text-decoration: underline; }
.linkedin-icon { width: 16px; height: 16px; border-radius: 4px; display: inline-flex; align-items: center; justify-content: center; background: #0a66c2; color: white; font-size: 11px; font-weight: 800; line-height: 1; }
.page-title-card {
    background: linear-gradient(135deg, #0f2744, #1a3a5c);
    border: 1px solid #1e4070;
    border-radius: 16px;
    padding: 18px 20px;
    margin: 8px 0 18px 0;
    box-shadow: 0 4px 16px rgba(15,39,68,0.18);
}
.page-title-main { color: #ffffff; font-size: 1.95rem; font-weight: 800; line-height: 1.1; margin: 0 0 6px 0; }
.page-title-sub  { color: #a0b8d0; font-size: 0.93rem; line-height: 1.45; margin: 0; }
.landing-wrap {
    background: linear-gradient(180deg, color-mix(in srgb, var(--surface) 94%, #e7f0ff 6%), var(--surface));
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 20px 24px 18px 24px;
    box-shadow: 0 8px 24px rgba(15,23,42,0.04);
}
.landing-kicker { color: var(--primary); text-transform: uppercase; letter-spacing: 0.08em; font-size: 0.76rem; font-weight: 800; margin-bottom: 10px; }
.landing-title  { color: var(--text); font-size: 1.9rem; font-weight: 800; line-height: 1.1; margin: 0 0 8px 0; }
.landing-copy   { color: var(--muted); font-size: 0.95rem; line-height: 1.55; max-width: 760px; margin: 0 0 10px 0; }
.persona-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; margin: 12px 0 14px 0; }
.persona-card { background: var(--surface-2); border: 1px solid var(--border); border-radius: 14px; padding: 13px 14px; }
.persona-title { color: var(--text); font-size: 0.98rem; font-weight: 800; margin-bottom: 8px; }
.persona-desc  { color: var(--muted); font-size: 0.88rem; line-height: 1.5; }
.persona-tag   { display: inline-block; margin-top: 10px; padding: 5px 9px; border-radius: 999px; font-size: 0.72rem; font-weight: 800; }
.tag-approve { background: var(--approve-bg); color: var(--approve-fg); }
.tag-refer   { background: var(--refer-bg);   color: var(--refer-fg); }
.tag-decline { background: var(--decline-bg); color: var(--decline-fg); }
.landing-steps {
    display: flex; flex-direction: column; gap: 8px; margin-top: 12px; padding: 12px 14px;
    background: linear-gradient(135deg, color-mix(in srgb, var(--primary) 6%, var(--surface)), var(--surface-2));
    border: 1.5px solid color-mix(in srgb, var(--primary) 30%, var(--border));
    border-radius: 10px;
}
.landing-step { display: flex; align-items: flex-start; gap: 10px; color: var(--muted); font-size: 0.88rem; line-height: 1.45; }
.landing-step b { color: var(--primary); }
.step-num { min-width: 20px; height: 20px; background: var(--primary); color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.7rem; font-weight: 800; flex-shrink: 0; margin-top: 1px; }
.section-divider { display: flex; align-items: center; gap: 12px; margin: 20px 0 14px 0; }
.section-band { margin-left: -2rem; margin-right: -2rem; padding: 20px 2rem 16px 2rem; margin-bottom: 0; }
.section-band-1 { background: #ffffff !important; border-left: 4px solid #0f766e; }
.section-band-2 { background: #f0f4f8 !important; border-left: 4px solid #3b82f6; }
.section-band-3 { background: #f0faf6 !important; border-left: 4px solid #10b981; }
.section-band-4 { background: #fdf8f0 !important; border-left: 4px solid #f59e0b; }
@media (prefers-color-scheme: dark) {
    .section-band-1 { background: #1c2020 !important; border-color: #0f766e; }
    .section-band-2 { background: #1a1e28 !important; border-color: #3b82f6; }
    .section-band-3 { background: #182420 !important; border-color: #10b981; }
    .section-band-4 { background: #242018 !important; border-color: #f59e0b; }
}
.section-divider-line  { flex: 1; height: 1px; background: var(--border); }
.section-divider-label { color: var(--muted); font-size: 0.82rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.1em; white-space: nowrap; background: var(--bg); padding: 0 4px; }
.credit-footer { margin-top: 26px; padding: 14px 0 6px 0; border-top: 1px solid var(--border); text-align: center; color: var(--muted); font-size: 0.9rem; }
.credit-footer a { color: #0a66c2 !important; font-weight: 700; text-decoration: none; }
.credit-footer a:hover { text-decoration: underline; }
.override-help { color: var(--muted); font-size: 0.76rem; line-height: 1.35; margin-top: -4px; margin-bottom: 2px; padding: 0 2px; }
.cta-highlight {
    background: linear-gradient(135deg, color-mix(in srgb, var(--primary) 8%, var(--surface)), var(--surface-2));
    border: 1.5px solid color-mix(in srgb, var(--primary) 30%, var(--border));
    border-radius: 10px; padding: 8px 10px; margin-top: 4px;
}
.cta-highlight .cta-label { color: var(--primary); font-size: 0.68rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.07em; margin-bottom: 3px; }

/* AI Memo star banner */
.memo-star-banner {
    background: linear-gradient(135deg, #0f2744 0%, #1a4a6e 100%);
    border-radius: 14px; padding: 18px 22px; margin-bottom: 18px;
    display: flex; align-items: center; gap: 16px;
}
.memo-star-icon  { font-size: 2rem; flex-shrink: 0; }
.memo-star-title { color: #ffffff; font-size: 1.05rem; font-weight: 800; margin-bottom: 4px; }
.memo-star-sub   { color: #a0c4e0; font-size: 0.85rem; line-height: 1.4; }

/* Sidebar inline step labels */
.sidebar-step-label {
    display: inline-flex; align-items: center; gap: 6px;
    font-size: 0.78rem; font-weight: 700; color: var(--muted);
    margin-bottom: 3px;
}
.sidebar-step-num {
    min-width: 18px; height: 18px; background: var(--primary); color: white;
    border-radius: 50%; display: inline-flex; align-items: center; justify-content: center;
    font-size: 0.62rem; font-weight: 800; flex-shrink: 0;
}

.block-container { padding-top: 0.8rem !important; padding-bottom: 1rem !important; }
.block-container::before {
    content: '';
    display: block;
    height: 3px;
    background: linear-gradient(90deg, #0f2744, #0f766e);
    margin: -0.8rem -1rem 1rem -1rem;
}
section[data-testid="stSidebar"] > div { padding-top: 0 !important; padding-bottom: 0 !important; }
section[data-testid="stSidebar"] > div > div { padding-top: 0 !important; padding-bottom: 0 !important; }
div[data-testid="stSidebarContent"] { padding-top: 1rem !important; padding-bottom: 1rem !important; background: #eef1f7 !important; }
section[data-testid="stSidebar"] .stMarkdown    { margin-bottom: 0.25rem !important; }
section[data-testid="stSidebar"] .stNumberInput { margin-bottom: 0.1rem !important; }
section[data-testid="stSidebar"] .stSelectbox   { margin-bottom: 0.1rem !important; }
section[data-testid="stSidebar"] hr { margin: 0.5rem 0 !important; }
section[data-testid="stSidebar"] .stButton { margin-top: 0.1rem !important; }
section[data-testid="stSidebar"] * { font-family: 'Inter', sans-serif !important; }
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stNumberInput label {
    font-size: 0.8rem !important; font-weight: 600 !important; color: var(--muted) !important;
    text-transform: uppercase !important; letter-spacing: 0.05em !important; margin-bottom: 4px !important;
}
section[data-testid="stSidebar"] input,
section[data-testid="stSidebar"] select,
section[data-testid="stSidebar"] div[data-baseweb="select"] {
    font-size: 0.88rem !important; font-weight: 500 !important; color: var(--text) !important;
}
section[data-testid="stSidebar"] .stButton button {
    font-size: 0.9rem !important; font-weight: 800 !important;
    background: var(--primary) !important; color: #ffffff !important;
    border: none !important; border-radius: 8px !important;
    padding: 0.5rem 1rem !important; letter-spacing: 0.02em !important;
    box-shadow: 0 2px 8px rgba(15,118,110,0.25) !important;
}
section[data-testid="stSidebar"] .stButton button:hover {
    background: #0a5c55 !important; box-shadow: 0 4px 12px rgba(15,118,110,0.35) !important;
}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    font-size: 0.88rem !important; font-weight: 800 !important; color: var(--text) !important;
    margin: 0 0 0.3rem 0 !important; padding: 0 !important; border: none !important;
    background: none !important; letter-spacing: 0 !important; text-transform: none !important;
}
div[data-testid="stDecoration"]  { display: none !important; }
div[data-testid="stStatusWidget"] { display: none !important; }
#MainMenu { visibility: hidden !important; }
footer { visibility: hidden; }
@media (max-width: 980px) {
    .persona-grid { grid-template-columns: 1fr; }
    .landing-title { font-size: 1.7rem; }
    .page-title-main { font-size: 1.55rem; }
}

/* ── Generate AI Credit Memo button: shimmer sweep ── */
@keyframes memo-shimmer {
    0%   { left: -80%; }
    100% { left: 130%; }
}
div[data-testid="stTabs"] div[data-testid="stVerticalBlock"] .stButton button[kind="primary"],
div[data-testid="stTabs"] div[data-testid="stHorizontalBlock"] .stButton button[kind="primary"] {
    position: relative;
    overflow: hidden;
}
div[data-testid="stTabs"] div[data-testid="stVerticalBlock"] .stButton button[kind="primary"]::after,
div[data-testid="stTabs"] div[data-testid="stHorizontalBlock"] .stButton button[kind="primary"]::after {
    content: '';
    position: absolute;
    top: 0;
    left: -80%;
    width: 55%;
    height: 100%;
    background: linear-gradient(
        120deg,
        transparent 20%,
        rgba(255, 255, 255, 0.45) 50%,
        transparent 80%
    );
    animation: memo-shimmer 2.4s ease-in-out infinite;
    pointer-events: none;
}
</style>
""", unsafe_allow_html=True)


TOOLTIPS = {
    "HHI": "Concentration Risk: scores above 0.40 indicate dangerous dependency on a narrow set of buyers.",
    "CRR": "Retention: percentage of customers from Month 1 who returned in Month 3.",
    "DSCR": "Serviceability: ability to cover the new EMI with current surplus cash flow.",
    "DIV": "Integrity: percentage gap between bank credits and GST declarations.",
    "CV": "Volatility: predictability of cash flow. Scores above 0.60 suggest erratic revenue.",
    "GAP": "Operational silence: the longest period in days without a business credit."
}

PERSONA_INSIGHTS = {
    "Prime Retailer (Alpha)": {
        "truth_table": "All four gates pass cleanly — this is the benchmark for a well-structured MSME credit proposal.",
        "triangulation": "Bank credits and GST declarations are within 2–3% of each other across all three months — strong financial hygiene.",
        "velocity": "Consistent daily inflows with weekend spikes — pattern of a live retail operation with stable footfall."
    },
    "GST-Divergent Unit": {
        "truth_table": "Integrity Gate triggers a 50% haircut — the wide gap between bank credits and GST declarations is the primary disqualifier.",
        "triangulation": "Bank credits are roughly half the GST declared — a classic sign of revenue inflation or parallel cash routing outside the banking channel.",
        "velocity": "Lumpy inflows with long gaps — large RTGS credits followed by immediate outflows; inconsistent with genuine retail behavior."
    },
    "Distressed Trader": {
        "truth_table": "Survival Gate fails on DSCR and Stability Gate fires on repeated bounces — two independent and sufficient grounds for decline.",
        "triangulation": "Bank and GST figures broadly match but at a low absolute level — the problem here is volume and liquidity, not reporting integrity.",
        "velocity": "Low-amplitude, irregular inflows — cash generation is thin and unpredictable throughout the quarter, with no recovery pattern."
    }
}

PERSONA_CONFIG = {
    "Prime Retailer (Alpha)": {
        "file_name": "prime_retailer_aa.json",
        "gst": [
            {"month": "January", "sales": 1145000},
            {"month": "February", "sales": 1130000},
            {"month": "March", "sales": 1165000}
        ],
        "p_emi": 10000,
        "default_req": 1500000,
    },
    "GST-Divergent Unit": {
        "file_name": "gst_divergent_aa.json",
        "gst": [
            {"month": "January", "sales": 1450000},
            {"month": "February", "sales": 1420000},
            {"month": "March", "sales": 1480000}
        ],
        "p_emi": 15000,
        "default_req": 2000000,
    },
    "Distressed Trader": {
        "file_name": "distressed_trader_aa.json",
        "gst": [
            {"month": "January", "sales": 135000},
            {"month": "February", "sales": 132000},
            {"month": "March", "sales": 138000}
        ],
        "p_emi": 25000,
        "default_req": 400000,
    }
}


def fetch_sourced_persona(choice):
    cfg = PERSONA_CONFIG.get(choice)
    if not cfg:
        return pd.DataFrame(), [], 0, {}
    with open(cfg["file_name"], "r") as f:
        aa_payload = json.load(f)
    account = aa_payload.get("Account", {})
    profile = account.get("Profile", {}).get("Holders", {}).get("Holder", [{}])[0]
    summary = account.get("Summary", {})
    entity = {
        "name": profile.get("name", choice),
        "pan": profile.get("pan", "NA"),
        "branch": summary.get("branch", "NA"),
        "facility": summary.get("facility", "NA"),
        "ifsc": summary.get("ifscCode", "NA"),
        "account_type": summary.get("type", "NA"),
        "current_balance": float(summary.get("currentBalance", 0) or 0),
        "masked_acc": account.get("maskedAccNumber", "NA")
    }
    parsed_txns = []
    for t in account["Transactions"]["Transaction"]:
        amt = float(t["amount"])
        if t["type"] == "DEBIT":
            amt = -amt
        date_obj = datetime.strptime(t["valueDate"], "%Y-%m-%d")
        month_str = date_obj.strftime("%B")
        narration = t["narration"]
        parts = narration.split("-")
        derived_payee = parts[-1] if len(parts) > 1 else narration
        parsed_txns.append({
            "date": t["valueDate"],
            "month": month_str,
            "payee_id": derived_payee,
            "amount": amt,
            "description": narration
        })
    return pd.DataFrame(parsed_txns), cfg["gst"], cfg["p_emi"], entity


def metric_signal(metric, value):
    if metric == "HHI":
        if value <= 0.15: return "Diversified inflow base", "metric-good"
        if value <= 0.40: return "Moderate concentration", "metric-watch"
        return "Single-buyer dependency risk", "metric-bad"
    if metric == "CRR":
        if value >= 0.60: return "Sticky customer base", "metric-good"
        if value >= 0.35: return "Retention needs monitoring", "metric-watch"
        return "Weak repeat behavior", "metric-bad"
    if metric == "DSCR":
        if value >= 1.20: return "Comfortable debt cover", "metric-good"
        if value >= 0.80: return "Borderline serviceability", "metric-watch"
        return "Insufficient repayment cover", "metric-bad"
    if metric == "DIV":
        abs_v = abs(value)
        if abs_v <= 10: return "Bank and GST broadly aligned", "metric-good"
        if abs_v <= 15: return "Minor reporting mismatch", "metric-watch"
        return "Integrity haircut zone", "metric-bad"
    if metric == "CV":
        if value <= 0.25: return "Stable inflow pattern", "metric-good"
        if value <= 0.60: return "Variable but manageable", "metric-watch"
        return "Erratic cash-flow behavior", "metric-bad"
    if metric == "GAP":
        if value <= 3: return "Continuous operating activity", "metric-good"
        if value <= 7: return "Some inactivity pockets", "metric-watch"
        return "Long silence in cash generation", "metric-bad"
    return "Review required", "metric-watch"


def render_metric_card(title, tooltip, display_value, signal_text, signal_class, benchmark_text):
    return f"""
    <div class='hero-card'>
        <div class='hero-label'>{title} <span class='tooltip-icon' tabindex='0'>ⓘ<span class='tooltip-text'>{tooltip}</span></span></div>
        <div class='hero-value'>{display_value}</div>
        <div class='hero-subtext'>{benchmark_text}</div>
        <span class='metric-badge {signal_class}'>{signal_text}</span>
    </div>
    """


def gate_signal(passed, warn=False):
    if passed: return "<span class='gate-pass'>PASS</span>"
    elif warn:  return "<span class='gate-warn'>WARN</span>"
    else:       return "<span class='gate-fail'>FAIL</span>"


def render_creator_footer():
    st.markdown(
        """<div class='credit-footer'>
            Crafted by <a href='https://www.linkedin.com/in/omeshksingh/' target='_blank'>
            <span class='linkedin-icon'>in</span> Omesh Kumar Singh</a>
        </div>""",
        unsafe_allow_html=True,
    )


# ── SIDEBAR ── clean, no extra step-block, step numbers embedded in labels
with st.sidebar:
    st.markdown(
        """<div class='brand-sidebar'>
            <div class='brand-title'>MSME Agentic Underwriter</div>
            <a class='sidebar-link' href='https://www.linkedin.com/in/omeshksingh/' target='_blank'>
                <span class='linkedin-icon'>in</span> Omesh Kumar Singh
            </a>
        </div>""",
        unsafe_allow_html=True,
    )
    st.markdown("<hr>", unsafe_allow_html=True)

    # Step numbers embedded directly in widget labels — no extra block
    st.markdown(
        "<div class='sidebar-step-label'><span class='sidebar-step-num'>1</span> Select persona</div>",
        unsafe_allow_html=True
    )
    persona_choice = st.selectbox(
        "Select Sourced Persona",
        ["Select...", "Prime Retailer (Alpha)", "GST-Divergent Unit", "Distressed Trader"],
        label_visibility="collapsed"
    )

    st.markdown(
        "<div class='sidebar-step-label'><span class='sidebar-step-num'>2</span> Adjust loan request</div>",
        unsafe_allow_html=True
    )
    dynamic_req = PERSONA_CONFIG.get(persona_choice, {}).get("default_req", 1000000)
    loan_req_input = st.number_input(
        "Override Loan Request (₹)", value=dynamic_req, step=100000,
        label_visibility="collapsed"
    )
    st.markdown(
        "<div class='override-help'>Borrower's requested credit limit.</div>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<div class='sidebar-step-label'><span class='sidebar-step-num'>3</span> Run the engine</div>",
        unsafe_allow_html=True
    )
    if st.button("▶ Execute Audit", use_container_width=True, type="primary") and persona_choice != "Select...":
        df, gst, p_emi, entity = fetch_sourced_persona(persona_choice)
        st.session_state.update({
            "df_txns": df,
            "gst_logs": gst,
            "p_emi": p_emi,
            "req": loan_req_input,
            "biz_name": persona_choice,
            "entity": entity,
            "ai_memo": None
        })


# ── MAIN PANEL ──
if "df_txns" not in st.session_state:
    # LANDING PAGE
    st.markdown(
        """<div class='landing-wrap'>
            <div class='landing-kicker'>Institutional Credit Intelligence · AA-Native</div>
            <div class='landing-title'>MSME Agentic Underwriter</div>
            <div class='landing-copy'>
                Bank-statement analytics meets policy-gate automation. Pick a persona on the left,
                run the audit, and explore the full decisioning stack — from raw transactions to
                an AI-generated credit memo.
            </div>
        </div>""",
        unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        """<div class='persona-grid'>
            <div class='persona-card'>
                <div class='persona-title'>🏪 Prime Retailer (Alpha)</div>
                <div class='persona-desc'>Clean AA data. All four policy gates pass. Benchmark for a well-structured MSME proposal.</div>
                <span class='persona-tag tag-approve'>APPROVE</span>
            </div>
            <div class='persona-card'>
                <div class='persona-title'>📊 GST-Divergent Unit</div>
                <div class='persona-desc'>Bank credits diverge sharply from GST declarations. Integrity haircut triggers on audit.</div>
                <span class='persona-tag tag-refer'>REFER</span>
            </div>
            <div class='persona-card'>
                <div class='persona-title'>⚠️ Distressed Trader</div>
                <div class='persona-desc'>Repeated bounces and weak DSCR. Two independent decline triggers fire simultaneously.</div>
                <span class='persona-tag tag-decline'>DECLINE</span>
            </div>
        </div>""",
        unsafe_allow_html=True
    )

    # Steps on landing — numbered clearly
    st.markdown(
        """<div class='landing-steps'>
            <div class='landing-step'><div class='step-num'>1</div><div><b>Select a persona</b> in the left panel — each represents a distinct borrower archetype</div></div>
            <div class='landing-step'><div class='step-num'>2</div><div><b>Override the loan request</b> if you want to stress-test a different exposure level</div></div>
            <div class='landing-step'><div class='step-num'>3</div><div><b>Execute Audit</b> — DuckDB analytics, GST triangulation and policy gates run instantly</div></div>
            <div class='landing-step'><div class='step-num'>4</div><div><b>Explore tabs</b> below the verdict — especially ✨ AI Credit Memo for narrative synthesis</div></div>
        </div>""",
        unsafe_allow_html=True
    )

    render_creator_footer()

else:
    df_txns = st.session_state["df_txns"]

    sql_query = """
    SELECT
        (SELECT MAX(gap) FROM (SELECT CAST(date AS DATE) - LAG(CAST(date AS DATE)) OVER (ORDER BY CAST(date AS DATE)) as gap FROM df_txns WHERE amount > 0)) as max_gap,
        (SELECT CAST(COUNT(DISTINCT m3.payee_id) AS FLOAT) / NULLIF(COUNT(DISTINCT m1.payee_id), 0)
         FROM (SELECT payee_id FROM df_txns WHERE month='January' AND amount > 0) m1
         LEFT JOIN (SELECT payee_id FROM df_txns WHERE month='March' AND amount > 0) m3 ON m1.payee_id = m3.payee_id) as crr,
        (SELECT SUM(share*share) FROM (SELECT (SUM(amount) / (SELECT SUM(amount) FROM df_txns WHERE amount > 0)) as share FROM df_txns WHERE amount > 0 GROUP BY payee_id)) as hhi,
        (SELECT AVG(turn) FROM (SELECT SUM(amount) as turn FROM df_txns WHERE amount > 0 GROUP BY month)) as v_turnover,
        (SELECT COUNT(*) FROM df_txns WHERE description LIKE '%CHQ RTN%') as total_b,
        (SELECT STDDEV(daily_tot)/NULLIF(AVG(daily_tot), 0) FROM (SELECT CAST(date AS DATE), SUM(amount) as daily_tot FROM df_txns WHERE amount > 0 GROUP BY CAST(date AS DATE))) as cv_val
    """
    max_gap, crr, hhi, v_turnover, total_b, avg_cv = duckdb.sql(sql_query).fetchone()

    crr    = crr    or 0
    hhi    = hhi    or 0
    avg_cv = avg_cv or 0
    max_gap = max_gap or 0

    gst_df  = pd.DataFrame(st.session_state["gst_logs"])
    avg_gst = gst_df["sales"].mean()
    gst_variance = ((v_turnover / avg_gst) - 1) * 100 if avg_gst else 0

    integrity_haircut    = 0.5 if abs(gst_variance) > 15 else 1.0
    limit_turnover       = (v_turnover * 0.85) * integrity_haircut
    limit_serviceability = max(((v_turnover * 0.12) - st.session_state["p_emi"]) * 36, 0)
    limit_policy         = v_turnover * 0.40 if total_b > 0 else v_turnover * 1.0
    final_limit          = max(min(limit_turnover, limit_serviceability, limit_policy), 0)
    risk_score           = min((hhi * 30) + (total_b * 15) + (max(max_gap - 7, 0) * 4) + (avg_cv * 15), 100)

    dscr_ratio       = limit_serviceability / max(st.session_state["req"], 1)
    limit_vs_req_pct = (final_limit / max(st.session_state["req"], 1)) * 100
    proposed_emi    = st.session_state.req / 36
    monthly_surplus = max(v_turnover - st.session_state.p_emi, 0)
    true_dscr       = monthly_surplus / max(proposed_emi, 1)
    if true_dscr < 1.0 or total_b > 1:  # FIX: aligned with gate formula
        verdict, status_class = "DECLINE", "decline"
    elif risk_score < 45 and final_limit > (st.session_state["req"] * 0.5):
        verdict, status_class = "APPROVE", "approve"
    else:
        verdict, status_class = "REFER", "refer"

    gate_dscr_pass   = dscr_ratio >= 0.1
    gate_div_pass    = abs(gst_variance) <= 15
    gate_bounce_pass = total_b <= 1  # FIX: Stability Gate triggers only if bounces > 1
    gate_yield_pass  = limit_vs_req_pct >= 50

    gate_dscr_val   = f"{dscr_ratio:.2f}x"
    gate_div_val    = f"{gst_variance:.1f}%"
    gate_bounce_val = f"{int(total_b)} bounces"
    gate_yield_val  = f"{limit_vs_req_pct:.0f}% covered"

    entity   = st.session_state.get("entity", {})
    biz_name = st.session_state["biz_name"]
    insights = PERSONA_INSIGHTS.get(biz_name, {"truth_table": "", "triangulation": "", "velocity": ""})

    # Entity strip
    st.markdown("<div class='section-kicker'>Institutional account profile</div>", unsafe_allow_html=True)
    st.markdown(
        f"""<div class='entity-strip'>
            <div class='entity-name'>{entity.get("name", biz_name)}</div>
            <div class='entity-meta'>
                <span><b>PAN:</b> {entity.get("pan","NA")}</span>
                <span><b>Branch:</b> {entity.get("branch","NA")}</span>
                <span><b>Facility:</b> {entity.get("facility","NA")}</span>
                <span><b>A/c Type:</b> {entity.get("account_type","NA")}</span>
                <span><b>IFSC:</b> {entity.get("ifsc","NA")}</span>
                <span><b>Masked A/c:</b> {entity.get("masked_acc","NA")}</span>
            </div>
        </div>""",
        unsafe_allow_html=True
    )

    # Page title — navy gradient (kept from previous version)
    st.markdown(
        f"""<div class='page-title-card'>
            <div class='page-title-main'>🛡️ Underwriting Terminal: {biz_name}</div>
            <p class='page-title-sub'>Decisioning summary built from verified bank inflows, GST triangulation, behavioural risk metrics, and institutional policy gates.</p>
        </div>""",
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns([1.55, 1])
    with c1:
        st.markdown(
            f"""<div class='status-box {status_class}'>
                <h2 style='margin:0 0 8px 0;'>📢 {verdict}</h2>
                <p style='margin:0; font-size:0.98rem;'>Risk Score: <b>{risk_score:.1f}/100</b> | Integrity Variance: <b>{gst_variance:.1f}%</b> | Requested: <b>₹{int(st.session_state["req"]):,}</b></p>
            </div>""",
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"""<div class='hero-card' style='background:#f5f0e8 !important; border-color:#d4c9b4 !important;'>
                <div class='hero-label'>LIMIT DISCOVERY (MIN-CAP)</div>
                <table class='waterfall-table'>
                    <tr><td>Turnover Capacity</td><td style='text-align:right;'>₹{int(limit_turnover):,}</td></tr>
                    <tr><td>Serviceability (DSCR)</td><td style='text-align:right;'>₹{int(limit_serviceability):,}</td></tr>
                    <tr><td>Policy Floor (Bounces)</td><td style='text-align:right;'>₹{int(limit_policy):,}</td></tr>
                    <tr style='background:var(--surface-2);'><td style='font-weight:800;'>FINAL RECOMMENDED</td><td style='font-weight:800; text-align:right;'>₹{int(final_limit):,}</td></tr>
                </table>
            </div>""",
            unsafe_allow_html=True,
        )

    # Behavioural Risk Metrics
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-band section-band-2'>", unsafe_allow_html=True)
    st.markdown("""<div class='section-divider'>
        <div class='section-divider-line'></div>
        <div class='section-divider-label'>Behavioural Risk Metrics</div>
        <div class='section-divider-line'></div>
    </div>""", unsafe_allow_html=True)

    r1 = st.columns(3)
    sig_text, sig_class = metric_signal("HHI", hhi)
    r1[0].markdown(render_metric_card("HHI (CONCENTRATION)", TOOLTIPS["HHI"], f"{hhi:.2f}", sig_text, sig_class, "Benchmark: ≤0.15 healthy, >0.40 high dependency"), unsafe_allow_html=True)
    sig_text, sig_class = metric_signal("CRR", crr)
    r1[1].markdown(render_metric_card("CRR (RETENTION)", TOOLTIPS["CRR"], f"{crr*100:.1f}%", sig_text, sig_class, "Benchmark: ≥60% sticky customer franchise"), unsafe_allow_html=True)
    sig_text, sig_class = metric_signal("DSCR", dscr_ratio)
    r1[2].markdown(render_metric_card("MODIFIED DSCR", TOOLTIPS["DSCR"], f"{dscr_ratio:.2f}x", sig_text, sig_class, "Benchmark: ≥1.2x comfortable repayment cover"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    r2 = st.columns(3)
    sig_text, sig_class = metric_signal("DIV", gst_variance)
    r2[0].markdown(render_metric_card("REPORTING DIVERGENCE", TOOLTIPS["DIV"], f"{gst_variance:.1f}%", sig_text, sig_class, "Benchmark: beyond ±15% triggers haircut"), unsafe_allow_html=True)
    sig_text, sig_class = metric_signal("CV", avg_cv)
    r2[1].markdown(render_metric_card("VOLATILITY (CV)", TOOLTIPS["CV"], f"{avg_cv:.2f}", sig_text, sig_class, "Benchmark: ≤0.25 stable, >0.60 erratic"), unsafe_allow_html=True)
    sig_text, sig_class = metric_signal("GAP", max_gap)
    r2[2].markdown(render_metric_card("MAX ACTIVITY GAP", TOOLTIPS["GAP"], f"{int(max_gap)} Days", sig_text, sig_class, "Benchmark: >7 days indicates operating silence"), unsafe_allow_html=True)

    # Commercial Structuring
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-band section-band-3'>", unsafe_allow_html=True)
    st.markdown("""<div class='section-divider'>
        <div class='section-divider-line'></div>
        <div class='section-divider-label'>Commercial Structuring & Yield Optimisation</div>
        <div class='section-divider-line'></div>
    </div>""", unsafe_allow_html=True)

    if verdict == "APPROVE":
        roi    = 14.5 + (risk_score * 0.1)
        pf     = 1.5 if hhi < 0.2 else 2.5
        tenure = "24 Months (Term)" if avg_cv > 0.4 else "12 Months (Revolving OD)"
    elif verdict == "REFER":
        roi    = 18.0 + (risk_score * 0.1)
        pf     = 3.0
        tenure = "12 Months (Strict Term)"
    else:
        roi    = 0.0
        pf     = 0.0
        tenure = "N/A"

    com_col, chart_col = st.columns([1, 1.8])
    with com_col:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"<div class='hero-card' style='margin-bottom:15px; background:#edf4f0 !important; border-color:#b8d4c4 !important;'><div class='hero-label'>RISK-ADJUSTED ROI</div><div class='hero-value'>{roi:.2f}%</div><div class='hero-subtext'>Base price plus risk-score load.</div></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='hero-card' style='margin-bottom:15px; background:#edf4f0 !important; border-color:#b8d4c4 !important;'><div class='hero-label'>PROCESSING FEE</div><div class='hero-value'>{pf:.1f}%</div><div class='hero-subtext'>Higher concentration pushes fee upward.</div></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='hero-card' style='background:#edf4f0 !important; border-color:#b8d4c4 !important;'><div class='hero-label'>OPTIMAL FACILITY</div><div class='hero-value' style='font-size:1.08rem;'>{tenure}</div><div class='hero-subtext'>Volatility steers OD versus term structure.</div></div>", unsafe_allow_html=True)

    with chart_col:
        if final_limit > 0:
            max_x    = max(st.session_state["req"], final_limit) + 400000
            x_values = np.linspace(100000, max_x, 100)
            y_values = []
            for x in x_values:
                if x <= final_limit:
                    expected_yield = x * 0.06
                else:
                    max_profit    = final_limit * 0.06
                    overage_ratio = (x - final_limit) / final_limit
                    risk_penalty  = max_profit * (overage_ratio ** 2) * 5
                    expected_yield = max_profit - risk_penalty
                y_values.append(max(expected_yield, -200000))

            curve_df = pd.DataFrame({"Exposure": x_values, "Yield": y_values})
            area_chart = alt.Chart(curve_df).mark_area(
                line={"color": "#3b82f6"},
                color=alt.Gradient(
                    gradient="linear",
                    stops=[alt.GradientStop(color="#60a5fa", offset=0), alt.GradientStop(color="#ffffff", offset=1)],
                    x1=1, x2=1, y1=1, y2=0,
                ),
                opacity=0.8,
            ).encode(
                x=alt.X("Exposure:Q", title="Loan Exposure (₹)", axis=alt.Axis(format="~s", labelExpr="datum.value / 100000 + 'L'")),
                y=alt.Y("Yield:Q", title="Projected Net Yield (₹)", axis=alt.Axis(format="~s")),
                tooltip=[
                    alt.Tooltip("Exposure:Q", format=",.0f", title="Exposure (₹)"),
                    alt.Tooltip("Yield:Q",    format=",.0f", title="Yield (₹)"),
                ],
            )
            req_df   = pd.DataFrame({"Requested": [st.session_state["req"]]})
            req_rule = alt.Chart(req_df).mark_rule(color="#ef4444", strokeDash=[5,5], strokeWidth=2).encode(x="Requested:Q")
            opt_df   = pd.DataFrame({"Optimum": [final_limit]})
            opt_rule = alt.Chart(opt_df).mark_rule(color="#10b981", strokeDash=[5,5], strokeWidth=2).encode(x="Optimum:Q")
            st.altair_chart(area_chart + req_rule + opt_rule, use_container_width=True)
            st.markdown(
                f"""<div class='caption-box'>
                    💡 <b>RAROC interpretation:</b> Green line = optimal exposure <b>₹{int(final_limit):,}</b> · Red line = borrower request <b>₹{int(st.session_state["req"]):,}</b>.
                    Lending beyond the green line erodes net yield non-linearly.
                </div>""",
                unsafe_allow_html=True,
            )
        else:
            st.warning("No viable yield curve. Risk of default approaches 100%.")

    # Analysis tabs
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-band section-band-4'>", unsafe_allow_html=True)
    st.markdown("""<div class='section-divider'>
        <div class='section-divider-line'></div>
        <div class='section-divider-label'>Analysis, Audit & Policy</div>
        <div class='section-divider-line'></div>
    </div>""", unsafe_allow_html=True)

    tab_memo, tab_audit, tab_guide = st.tabs([
        "✨ AI Credit Memo  ← Star Feature",
        "📊 Underwriting Audit Trail",
        "📖 Policy & Formula Guide"
    ])

    # ── TAB 1: AI CREDIT MEMO ──
    with tab_memo:
        st.markdown(
            """<div class='memo-star-banner'>
                <div class='memo-star-icon'>🧠</div>
                <div>
                    <div class='memo-star-title'>Agentic Credit Memo · Gemini-Powered</div>
                    <div class='memo-star-sub'>Generates a structured institutional narrative — Archetype · Tensions · Character · Mitigants · Final Verdict.<br>
                    Synthesises all six behavioural metrics into language a credit committee can act on.</div>
                </div>
            </div>""",
            unsafe_allow_html=True
        )
        if st.session_state.get("ai_memo") is None:
            if not api_key:
                st.info("ℹ️ Add GEMINI_API_KEY to your .env file to enable the AI memo. All other tabs are fully functional without it.")
            else:
                if st.button("✨ Generate AI Credit Memo", type="primary"):
                    prompt = (
                        f"You are a Senior Credit Officer writing an internal memo for the credit committee. "
                        f"Borrower: {biz_name}. "
                        f"Data: Verified Turnover ₹{v_turnover:,.0f}, GST Variance {gst_variance:.1f}%, "
                        f"Bounces {int(total_b)}, HHI {hhi:.2f}, CV {avg_cv:.2f}, Max Gap {int(max_gap)} days. "
                        f"Verdict: {verdict}. "
                        f"Write EXACTLY in this format with NO paragraphs — use bullet points inside each section:\n\n"
                        f"**BORROWER:** {biz_name}\n"
                        f"**VERDICT:** {verdict}\n\n"
                        f"**1. ARCHETYPE** (2 lines max — what type of borrower is this?)\n\n"
                        f"**2. KEY TENSIONS** (exactly 3 bullets — top risks, one line each)\n\n"
                        f"**3. CHARACTER SIGNALS** (exactly 3 bullets — positive behavioural indicators)\n\n"
                        f"**4. MITIGANTS & CONDITIONS** (2-3 bullets — what would change the view or conditions to impose)\n\n"
                        f"**5. FINAL RECOMMENDATION** (2 lines max — verdict rationale + suggested next action)\n\n"
                        f"Rules: No subject line. No email format. No invented numbers. Total output under 300 words. Be clinical and direct."
                    )
                    with st.spinner("Synthesizing Institutional Analysis..."):
                        try:
                            client_ai = genai.Client(api_key=api_key)
                            memo_text = None
                            for model_id in ["gemini-2.5-flash", "gemini-2.0-flash"]:
                                try:
                                    res = client_ai.models.generate_content(model=model_id, contents=prompt)
                                    memo_text = res.text
                                    break
                                except Exception:
                                    continue
                            if memo_text:
                                st.session_state["ai_memo"] = memo_text
                                st.rerun()
                            else:
                                st.warning("AI memo unavailable — Gemini quota reached. Try again shortly.")
                        except Exception as e:
                            st.error(f"API connection failed: {e}")
        else:
            st.markdown(st.session_state["ai_memo"])
            if st.button("↩ Regenerate Memo"):
                st.session_state["ai_memo"] = None
                st.rerun()

    # ── TAB 2: UNDERWRITING AUDIT TRAIL ──
    with tab_audit:
        st.markdown("### ⚖️ Decision Truth Table")
        if insights["truth_table"]:
            st.markdown(f"<div class='insight-box'>🔍 {insights['truth_table']}</div>", unsafe_allow_html=True)
        st.markdown(f"""<table class='policy-table'>
            <tr><th>Gate</th><th>Metric</th><th>Trigger</th><th>Institutional Result</th><th>This Applicant</th></tr>
            <tr>
                <td><b>Survival Gate</b></td><td>DSCR</td><td>&lt; 1.0</td><td><b>AUTO-DECLINE</b></td>
                <td>{gate_signal(gate_dscr_pass)} {gate_dscr_val}</td>
            </tr>
            <tr>
                <td><b>Integrity Gate</b></td><td>GST Divergence</td><td>&gt; 15%</td><td><b>50% HAIRCUT</b></td>
                <td>{gate_signal(gate_div_pass)} {gate_div_val}</td>
            </tr>
            <tr>
                <td><b>Stability Gate</b></td><td>Bounce Count</td><td>&gt; 1</td><td><b>AUTO-DECLINE</b></td>
                <td>{gate_signal(gate_bounce_pass)} {gate_bounce_val}</td>
            </tr>
            <tr>
                <td><b>Yield Gate</b></td><td>Limit vs Request</td><td>&lt; 50%</td><td><b>REFER</b></td>
                <td>{gate_signal(gate_yield_pass)} {gate_yield_val}</td>
            </tr>
        </table>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 📐 GST Triangulation")
        if insights["triangulation"]:
            st.markdown(f"<div class='insight-box'>🔍 {insights['triangulation']}</div>", unsafe_allow_html=True)
        gst_display = gst_df.copy()
        gst_display["sales"] = gst_display["sales"].apply(lambda x: f"₹{x:,.0f}")
        monthly_credits = df_txns[df_txns["amount"] > 0].groupby("month")["amount"].sum()
        month_order = [row["month"] for row in st.session_state.gst_logs]
        gst_display["Bank Credits (₹)"] = [f"₹{monthly_credits.get(m, 0):,.0f}" for m in month_order]
        gst_display.columns = ["Month", "GST Declared (₹)", "Bank Credits (₹)"]
        st.dataframe(gst_display, use_container_width=True, hide_index=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 🔄 Cash-Flow Velocity")
        if insights["velocity"]:
            st.markdown(f"<div class='insight-box'>🔍 {insights['velocity']}</div>", unsafe_allow_html=True)
        credits_df = df_txns[df_txns["amount"] > 0].copy()
        credits_df["date"] = pd.to_datetime(credits_df["date"])
        daily = credits_df.groupby("date")["amount"].sum().reset_index()
        velocity_chart = alt.Chart(daily).mark_bar(color="#0f766e", opacity=0.75).encode(
            x=alt.X("date:T", title="Date"),
            y=alt.Y("amount:Q", title="Daily Credits (₹)", axis=alt.Axis(format="~s")),
            tooltip=[alt.Tooltip("date:T", title="Date"), alt.Tooltip("amount:Q", format=",.0f", title="Credits (₹)")]
        ).properties(height=200)
        st.altair_chart(velocity_chart, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 🧾 Transaction Ledger")
        ledger = df_txns[["date", "month", "description", "amount"]].copy()
        ledger["amount"] = ledger["amount"].apply(lambda x: f"₹{x:,.0f}")
        st.dataframe(ledger, use_container_width=True, hide_index=True)

    # ── TAB 3: POLICY & FORMULA GUIDE (original narrative restored + table added) ──
    with tab_guide:
        st.markdown("### 📖 How the Underwriting Engine Works")
        st.markdown("""
The engine processes three months of Account Aggregator (AA) bank-statement data through a sequential decisioning stack.
Each layer has a distinct purpose — no single metric alone determines the outcome.

---

**Step 1 — Inflow Extraction & Cleaning**

Raw transactions are filtered to credits only. Debits are excluded from turnover calculations but retained
in the ledger for pattern analysis. The narration field is parsed to derive a `payee_id` — a proxy
for customer identity — which powers the concentration and retention metrics.

**Step 2 — Six Behavioural Metrics**

| Metric | What it measures | Healthy range |
|--------|-----------------|---------------|
| **HHI** (Herfindahl Index) | Inflow concentration across payees | ≤ 0.15 |
| **CRR** (Customer Retention Rate) | % of Jan payees who returned in Mar | ≥ 60% |
| **Modified DSCR** | Limit serviceability ÷ requested amount | ≥ 1.0x |
| **GST Variance** | Gap between bank credits and GST filings | Within ±15% |
| **CV** (Coefficient of Variation) | Volatility of daily inflows | ≤ 0.25 |
| **Max Gap** | Longest streak without a credit entry | ≤ 3 days |

**Step 3 — Policy Gates (Sequential)**

Gates are checked in order. A failure at any gate has a defined institutional consequence —
gates do not average out or compensate each other.

- **Survival Gate** — DSCR < 1.0 → Auto-Decline. No surplus cash to service debt.
- **Integrity Gate** — GST Variance > ±15% → 50% haircut on all limit calculations. Revenue reliability is in question.
- **Stability Gate** — Bounces > 1 → Auto-Decline. Repeated dishonours signal liquidity crisis.
- **Yield Gate** — Final limit < 50% of request → Refer. The bank cannot profitably serve the ask.

**Step 4 — Limit Waterfall (Min-Cap)**

Three independent limit calculations are computed; the most conservative is recommended:

1. **Turnover Capacity** — Avg monthly credits × 0.85 × Integrity haircut
2. **Serviceability** — Max((Monthly credits × 12% − Existing EMI) × 36, 0)
3. **Policy Floor** — Monthly credits × 0.40 if bounces exist, else × 1.0

The `min()` of these three is the Final Recommended Limit.

**Step 5 — Commercial Structuring**

ROI is base-priced and loaded by risk score. Processing fee rises with concentration risk.
Facility type (revolving OD vs. term loan) is determined by cash-flow volatility — erratic borrowers
get a term structure with fixed repayment, not a revolving line they can over-draw.

---
        """)

        st.markdown("### 📐 Quick Reference — Formula Table")
        st.markdown("""<table class='policy-table'>
            <tr><th>Formula</th><th>Definition</th><th>Threshold</th></tr>
            <tr><td><b>HHI</b></td><td>Σ(payee share)² — Herfindahl concentration index on inflow sources</td><td>≤ 0.15 clean · > 0.40 flag</td></tr>
            <tr><td><b>CRR</b></td><td>Month-3 unique payees ÷ Month-1 unique payees</td><td>≥ 60% healthy</td></tr>
            <tr><td><b>Modified DSCR</b></td><td>Limit Serviceability ÷ Requested Amount</td><td>≥ 1.0 survival gate</td></tr>
            <tr><td><b>GST Variance</b></td><td>(Bank Avg ÷ GST Avg − 1) × 100</td><td>±15% triggers 50% haircut</td></tr>
            <tr><td><b>CV</b></td><td>StdDev(daily credits) ÷ Mean(daily credits)</td><td>≤ 0.25 stable · > 0.60 erratic</td></tr>
            <tr><td><b>Max Gap</b></td><td>Longest day-gap between consecutive credit entries</td><td>> 7 days = operating silence</td></tr>
        </table>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 💰 Limit Waterfall — Formula Reference")
        st.markdown("""<table class='policy-table'>
            <tr><th>Component</th><th>Formula</th><th>Purpose</th></tr>
            <tr><td>Turnover Capacity</td><td>Avg Monthly Credits × 0.85 × Integrity Haircut</td><td>Revenue-based ceiling</td></tr>
            <tr><td>Serviceability (DSCR)</td><td>Max((Monthly Credits × 12% − Existing EMI) × 36, 0)</td><td>Cash-surplus ceiling</td></tr>
            <tr><td>Policy Floor</td><td>Monthly Credits × 0.40 if bounces > 0 else × 1.0</td><td>Stability penalty floor</td></tr>
            <tr><td><b>Final Limit</b></td><td><b>Min(Turnover, Serviceability, Policy)</b></td><td>Most conservative of three</td></tr>
        </table>""", unsafe_allow_html=True)

    render_creator_footer()
    st.markdown("</div>", unsafe_allow_html=True)
