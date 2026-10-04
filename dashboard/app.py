import sys
import os
from pathlib import Path
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
import streamlit as st


ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

# Unified module imports
from scripts.fetch_weather import PAKISTAN_CITIES, fetch_weather
from scripts.wbgt_calculator import add_wbgt_to_df
from scripts.occupation_classifier import (
    OCCUPATION_PROFILES, classify_all_occupations,
    get_work_rest, apply_el_nino_adjustment, EL_NINO_ACTIVE
)
from scripts.guidance_generator import generate_guidance

st.set_page_config(
    page_title="HeatGuard",
    page_icon="🌡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [class*="css"], .stApp {
    font-family: 'Inter', -apple-system, sans-serif;
    background: #0e0e0e;
    color: #f0ece8;
    -webkit-font-smoothing: antialiased;
}

header[data-testid="stHeader"] {
    background: transparent !important;
}

/* Hide footer and default menu items */
#MainMenu, footer, .stDeployButton { 
    display: none !important; 
}
.block-container { padding: 0 !important; max-width: 100% !important; }

/* ── SIDEBAR ─────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background: #141414 !important;
    border-right: 1px solid rgba(255,255,255,0.06) !important;
    width: 280px !important;
}

section[data-testid="stSidebar"] > div {
    padding: 0 !important;
}

.sidebar-logo {
    padding: 28px 24px 20px;
    border-bottom: 1px solid rgba(255,255,255,0.06);
    margin-bottom: 8px;
}

.sidebar-brand {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 6px;
}

.sidebar-icon {
    width: 34px; height: 34px;
    background: linear-gradient(135deg, #f97316, #dc2626);
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
    flex-shrink: 0;
}

.sidebar-title {
    font-size: 15px;
    font-weight: 700;
    color: #f0ece8;
    letter-spacing: -0.02em;
}

.sidebar-sub {
    font-size: 10px;
    color: rgba(240,236,232,0.3);
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: 0.05em;
    margin-left: 44px;
}

.sidebar-section {
    padding: 16px 24px 8px;
    font-size: 9px;
    font-family: 'JetBrains Mono', monospace;
    color: rgba(240,236,232,0.25);
    letter-spacing: 0.15em;
    text-transform: uppercase;
}

.sidebar-link {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 24px;
    font-size: 13px;
    color: rgba(240,236,232,0.55);
    text-decoration: none;
    border-left: 3px solid transparent;
    transition: all 0.15s;
    cursor: pointer;
}

.sidebar-link:hover {
    color: #f0ece8;
    background: rgba(255,255,255,0.04);
    border-left-color: #f97316;
}

.sidebar-link.active {
    color: #f97316;
    background: rgba(249,115,22,0.08);
    border-left-color: #f97316;
}

.sidebar-divider {
    height: 1px;
    background: rgba(255,255,255,0.05);
    margin: 12px 24px;
}

.sidebar-news {
    margin: 8px 16px;
    background: rgba(249,115,22,0.08);
    border: 1px solid rgba(249,115,22,0.2);
    border-radius: 10px;
    padding: 16px;
}

.news-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 8px;
    color: #f97316;
    letter-spacing: 0.15em;
    margin-bottom: 10px;
}

.news-item {
    font-size: 11px;
    color: rgba(240,236,232,0.55);
    line-height: 1.5;
    margin-bottom: 8px;
    padding-bottom: 8px;
    border-bottom: 1px solid rgba(255,255,255,0.05);
}

.news-item:last-child {
    margin-bottom: 0;
    padding-bottom: 0;
    border-bottom: none;
}

.news-link {
    color: #f97316 !important;
    text-decoration: none !important;
    font-size: 10px;
    font-weight: 500;
}

.sidebar-profile {
    position: absolute;
    bottom: 0; left: 0; right: 0;
    padding: 16px 24px;
    border-top: 1px solid rgba(255,255,255,0.06);
    background: #141414;
    display: flex;
    align-items: center;
    gap: 10px;
}

.profile-avatar {
    width: 30px; height: 30px;
    border-radius: 50%;
    background: linear-gradient(135deg, #f97316, #7c3aed);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    flex-shrink: 0;
    color: white;
    font-weight: 600;
}

.profile-name {
    font-size: 12px;
    font-weight: 500;
    color: rgba(240,236,232,0.7);
}

.profile-role {
    font-size: 10px;
    color: rgba(240,236,232,0.3);
}

/* ── TOPBAR ──────────────────────────────────────── */
.topbar {
    height: 56px;
    background: rgba(14,14,14,0.95);
    backdrop-filter: blur(20px);
    border-bottom: 1px solid rgba(255,255,255,0.05);
    display: flex;
    align-items: center;
    padding: 0 32px;
    gap: 16px;
    position: sticky;
    top: 0;
    z-index: 100;
}

.topbar-page {
    font-size: 14px;
    font-weight: 600;
    color: #f0ece8;
    letter-spacing: -0.01em;
}

.topbar-sep { color: rgba(240,236,232,0.2); }

.topbar-sub {
    font-size: 13px;
    color: rgba(240,236,232,0.35);
}

.topbar-right {
    margin-left: auto;
    display: flex;
    align-items: center;
    gap: 8px;
}

.live-chip {
    display: flex;
    align-items: center;
    gap: 6px;
    background: rgba(34,197,94,0.1);
    border: 1px solid rgba(34,197,94,0.2);
    border-radius: 100px;
    padding: 4px 10px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    color: #22c55e;
}

.live-dot {
    width: 5px; height: 5px;
    border-radius: 50%;
    background: #22c55e;
    animation: blink 2s infinite;
}

@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.3} }

/* ── HERO ────────────────────────────────────────── */
.hero {
    padding: 56px 40px 48px;
    background: radial-gradient(ellipse 80% 60% at 70% 0%,
        rgba(220,38,38,0.12) 0%,
        rgba(249,115,22,0.06) 40%,
        transparent 70%),
        #0e0e0e;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    position: relative;
    overflow: hidden;
}

.hero-eyebrow {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    color: #f97316;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    margin-bottom: 18px;
    display: flex;
    align-items: center;
    gap: 10px;
}

.hero-eyebrow::before {
    content:'';
    width: 20px; height: 1px;
    background: #f97316;
}

.hero-h1 {
    font-size: clamp(36px, 5vw, 72px);
    font-weight: 700;
    line-height: 1.0;
    letter-spacing: -0.04em;
    color: #f8f4f0;
    margin-bottom: 16px;
}

.hero-accent {
    background: linear-gradient(90deg, #f97316 0%, #dc2626 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.hero-desc {
    font-size: 14px;
    color: rgba(240,236,232,0.4);
    max-width: 480px;
    line-height: 1.8;
}

.hero-orb {
    position: absolute;
    top: -60px; right: 80px;
    width: 320px; height: 320px;
    background: radial-gradient(circle,
        rgba(220,38,38,0.15) 0%,
        rgba(249,115,22,0.08) 40%,
        transparent 70%);
    border-radius: 50%;
    pointer-events: none;
}

/* ── ALERT STRIP ─────────────────────────────────── */
.alert-strip {
    background: linear-gradient(90deg,
        rgba(220,38,38,0.1) 0%,
        rgba(220,38,38,0.04) 50%,
        transparent 100%);
    border-left: 2px solid #dc2626;
    padding: 14px 40px;
    display: flex;
    align-items: flex-start;
    gap: 12px;
    font-size: 12px;
    color: rgba(240,236,232,0.5);
    line-height: 1.65;
}

/* ── METRICS ROW ─────────────────────────────────── */
.metrics-row {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 1px;
    background: rgba(255,255,255,0.04);
    border-bottom: 1px solid rgba(255,255,255,0.04);
}

.metric-card {
    background: #141414;
    padding: 24px 20px;
    position: relative;
    overflow: hidden;
    transition: background 0.2s;
}

.metric-card:hover { background: #1a1a1a; }

.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: var(--c, rgba(255,255,255,0.07));
}

.metric-glow {
    position: absolute;
    bottom: -20px; right: -20px;
    width: 80px; height: 80px;
    background: radial-gradient(circle, var(--c, transparent) 0%, transparent 70%);
    opacity: 0.15;
    pointer-events: none;
}

.m-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 9px;
    color: rgba(240,236,232,0.28);
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-bottom: 10px;
}

.m-value {
    font-size: 30px;
    font-weight: 700;
    letter-spacing: -0.03em;
    line-height: 1;
    color: var(--c, #f8f4f0);
    margin-bottom: 6px;
}

.m-sub {
    font-size: 11px;
    color: rgba(240,236,232,0.28);
    line-height: 1.4;
}

/* ── RISK BANNER ─────────────────────────────────── */
.risk-banner {
    background: #141414;
    border-bottom: 1px solid rgba(255,255,255,0.04);
    padding: 18px 40px;
    display: flex;
    align-items: center;
    gap: 14px;
    flex-wrap: wrap;
}

.risk-badge {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    font-weight: 500;
    letter-spacing: 0.1em;
    padding: 6px 14px;
    border-radius: 6px;
    border: 1px solid currentColor;
    flex-shrink: 0;
}

.risk-occ-name {
    font-size: 13px;
    color: rgba(240,236,232,0.45);
}

.wr-tag {
    margin-left: auto;
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    color: rgba(240,236,232,0.35);
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.07);
    padding: 6px 14px;
    border-radius: 100px;
    white-space: nowrap;
}

.section-hdr {
    display: flex;
    align-items: baseline;
    gap: 14px;
    margin-bottom: 16px;
    padding-bottom: 12px;
    border-bottom: 1px solid rgba(255,255,255,0.05);
}

.sec-title {
    font-size: 13px;
    font-weight: 600;
    color: rgba(240,236,232,0.65);
    letter-spacing: -0.01em;
}

.sec-cap {
    font-size: 11px;
    color: rgba(240,236,232,0.22);
}

.chart-wrap {
    background: #141414;
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 12px;
    overflow: hidden;
    margin-bottom: 20px;
}

/* ── OCC GRID ────────────────────────────────────── */
.occ-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1px;
    background: rgba(255,255,255,0.04);
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid rgba(255,255,255,0.05);
}

.occ-row {
    background: #141414;
    padding: 13px 16px;
    display: flex;
    align-items: center;
    gap: 10px;
    transition: background 0.15s;
}

.occ-row:hover { background: #1a1a1a; }

.occ-stripe {
    width: 3px; height: 28px;
    border-radius: 2px;
    flex-shrink: 0;
}

.occ-name {
    flex: 1;
    font-size: 12px;
    font-weight: 400;
    color: rgba(240,236,232,0.65);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.occ-wr-txt {
    font-family: 'JetBrains Mono', monospace;
    font-size: 9px;
    color: rgba(240,236,232,0.22);
    white-space: nowrap;
    margin-right: 8px;
}

.occ-pill {
    font-family: 'JetBrains Mono', monospace;
    font-size: 9px;
    font-weight: 500;
    letter-spacing: 0.06em;
    padding: 3px 8px;
    border-radius: 4px;
    flex-shrink: 0;
}

/* ── GUIDANCE ────────────────────────────────────── */
.guidance-pair {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    margin-top: 16px;
}

.g-card {
    background: #141414;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 12px;
    padding: 22px;
    border-top-width: 2px;
    border-top-style: solid;
}

.g-lang {
    font-family: 'JetBrains Mono', monospace;
    font-size: 9px;
    color: rgba(240,236,232,0.25);
    letter-spacing: 0.15em;
    margin-bottom: 14px;
}

.g-text {
    font-size: 13px;
    line-height: 1.9;
    color: rgba(240,236,232,0.65);
    white-space: pre-wrap;
}

/* ── VALIDATION METRICS ──────────────────────────── */
.val-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1px;
    background: rgba(255,255,255,0.04);
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid rgba(255,255,255,0.05);
    margin-top: 16px;
}

.val-card {
    background: #141414;
    padding: 20px;
}

.v-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 9px;
    color: rgba(240,236,232,0.25);
    letter-spacing: 0.12em;
    margin-bottom: 8px;
}

.v-val {
    font-size: 24px;
    font-weight: 700;
    letter-spacing: -0.03em;
    color: #f8f4f0;
}

.v-sub {
    font-size: 10px;
    color: rgba(240,236,232,0.28);
    margin-top: 4px;
}

/* ── FOOTER ──────────────────────────────────────── */
.hg-footer {
    padding: 32px 40px 40px;
    border-top: 1px solid rgba(255,255,255,0.05);
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    flex-wrap: wrap;
    gap: 20px;
    margin-top: 20px;
}

.footer-brand {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: #f97316;
    margin-bottom: 6px;
}

.footer-meta {
    font-size: 12px;
    color: rgba(240,236,232,0.28);
    line-height: 1.8;
}

.footer-meta a {
    color: #f97316 !important;
    text-decoration: none !important;
}

.footer-sources {
    font-family: 'JetBrains Mono', monospace;
    font-size: 9px;
    color: rgba(240,236,232,0.18);
    text-align: right;
    line-height: 2.2;
}

/* ── STREAMLIT OVERRIDES ─────────────────────────── */
div[data-testid="stSelectbox"] > div > div {
    background: #1a1a1a !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 8px !important;
    color: #f0ece8 !important;
    font-size: 13px !important;
}

div[data-testid="stSelectbox"] label {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 9px !important;
    color: rgba(240,236,232,0.3) !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
}

.stButton > button {
    width: 100%;
    background: linear-gradient(135deg, #f97316, #dc2626) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    padding: 13px 20px !important;
    transition: opacity 0.15s !important;
    box-shadow: 0 4px 20px rgba(249,115,22,0.2) !important;
}

.stButton > button:hover { opacity: 0.88 !important; }

div[data-testid="stToggle"] > label {
    font-size: 12px !important;
    color: rgba(240,236,232,0.5) !important;
}

.stSpinner > div { border-top-color: #f97316 !important; }

/* ── MOBILE ──────────────────────────────────────── */
@media (max-width: 768px) {
    .hero { padding: 36px 20px 28px; }
    .metrics-row { grid-template-columns: 1fr 1fr; }
    .occ-grid { grid-template-columns: 1fr; }
    .guidance-pair { grid-template-columns: 1fr; }
    .val-row { grid-template-columns: 1fr 1fr; }
    .risk-banner { padding: 14px 20px; }
    .alert-strip { padding: 12px 20px; }
    .wr-tag { display: none; }
    .hg-footer { padding: 28px 20px; }
}

@media (max-width: 480px) {
    .metrics-row { grid-template-columns: 1fr; }
    .val-row { grid-template-columns: 1fr; }
}
</style>
""", unsafe_allow_html=True)

# ── COLOUR SYSTEM ──────────────────────────────────────────────────────────
RC = {
    'EXTREME': {'hex':'#ef4444','bg':'rgba(239,68,68,0.12)','border':'rgba(239,68,68,0.35)'},
    'HIGH':    {'hex':'#f97316','bg':'rgba(249,115,22,0.12)','border':'rgba(249,115,22,0.35)'},
    'MODERATE':{'hex':'#eab308','bg':'rgba(234,179,8,0.12)', 'border':'rgba(234,179,8,0.35)'},
    'SAFE':    {'hex':'#22c55e','bg':'rgba(34,197,94,0.12)', 'border':'rgba(34,197,94,0.35)'},
}

PT = dict(
    paper_bgcolor='#141414',
    plot_bgcolor='#141414',
    font=dict(family='Inter, sans-serif', color='rgba(240,236,232,0.4)', size=11),
    margin=dict(l=0, r=0, t=16, b=0),
    xaxis=dict(showgrid=False, color='rgba(240,236,232,0.2)',
               linecolor='rgba(255,255,255,0.05)'),
    yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.04)',
               color='rgba(240,236,232,0.35)', linecolor='rgba(255,255,255,0.04)'),
)

# ── DATA ───────────────────────────────────────────────────────────────────
@st.cache_data(ttl=1800)
def load_live(city='Karachi'):
    df = fetch_weather(city=city)
    return add_wbgt_to_df(df)

@st.cache_data
def load_2015():
    df = pd.read_csv('data/karachi_2015_heatwave.csv')
    df['time'] = pd.to_datetime(df['time'])
    return add_wbgt_to_df(df)

# ── SIDEBAR ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
        <div class="sidebar-brand">
            <div class="sidebar-icon">🌡️</div>
            <div class="sidebar-title">HeatGuard</div>
        </div>
            <div class="sidebar-sub">PAKISTAN · WBGT SYSTEM</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section">Controls</div>', unsafe_allow_html=True) 
    city = st.selectbox(
        "CITY",
        list(PAKISTAN_CITIES.keys()),
        index=0
    )

    occ_key = st.selectbox(
        "OCCUPATION",
        list(OCCUPATION_PROFILES.keys()),
        format_func=lambda x: OCCUPATION_PROFILES[x]['label']
    )

    view_mode = st.selectbox(
        "DATASET",
        ["Live Forecast (Today)", "2015 Heatwave Validation"]
    )

    el_nino = st.toggle("El Niño Mode (+1.2°C WBGT)", value=True)

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="sidebar-section">El Niño News</div>
    <div class="sidebar-news">
        <div class="news-label">DAWN · SEPT 2026</div>
        <div class="news-item">
            WHO–WMO declare El Niño a "significant public health threat" : 451,000 additional
            heat deaths projected globally.
            <br><br>
            <a class="news-link" href="https://www.dawn.com/news/2032114" target="_blank">
                Read article →
            </a>
        </div>
        <div class="news-item">
            Climate Impact Lab: 44% more extremely hot days forecast. Pakistan among most
            at-risk nations.
            <br><br>
            <a class="news-link" href="https://www.dawn.com/news/2031860" target="_blank">
                Read article →
            </a>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="sidebar-section">About</div>
    <div class="sidebar-link">
        📄 &nbsp; MUET Conference Paper
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="sidebar-profile">
        <div class="profile-avatar">S</div>
        <div>
            <div class="profile-name">Shiza Shah</div>
            <div class="profile-role">
                <a href="https://www.linkedin.com/in/sshizashah" target="_blank"
                   style="color:#f97316; text-decoration:none; font-size:10px">
                    linkedin.com/in/sshizashah ↗
                </a>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── LOAD DATA ──────────────────────────────────────────────────────────────
with st.spinner(""):
    try:
        if "Live" in view_mode:
            df = load_live(city).copy()
            dlabel = "LIVE"
        else:
            df = load_2015().copy()
            dlabel = "2015 HEATWAVE"

        if el_nino:
            df['WBGT'] = df['WBGT'].apply(apply_el_nino_adjustment)

        df = classify_all_occupations(df)
    except Exception as e:
        st.error(f"Data error: {e}")
        st.stop()

occ_label = OCCUPATION_PROFILES[occ_key]['label']

if "Live" in view_mode:
    nh = datetime.now().hour
    rows = df[df['time'].dt.hour == nh]
    cur = rows.iloc[0] if len(rows) else df.iloc[0]
else:

    cur = df.iloc[df['WBGT'].argmax()]

risk     = cur[f'risk_{occ_key}']
wbgt_val = cur['WBGT']
omgi_val = cur['OMGI']
wm, rm   = get_work_rest(risk, occ_key)
rc       = RC[risk]
ex_count = sum(1 for o in OCCUPATION_PROFILES if cur[f'risk_{o}'] == 'EXTREME')
ex_hrs   = int((df[f'risk_{occ_key}'] == 'EXTREME').sum())

# ── TOPBAR ────────────────────────────────────────────────────────────────
now_str = datetime.now().strftime("%d %b %Y · %H:%M")
st.markdown(f"""
<div class="topbar">
    <div class="topbar-page">Dashboard</div>
    <div class="topbar-sep">/</div>
    <div class="topbar-sub">{city} · {occ_label}</div>
    <div class="topbar-right">
        <div class="live-chip">
            <div class="live-dot"></div>
            {now_str}
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── HERO ──────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="hero">
    <div class="hero-orb"></div>
     <div class="hero-eyebrow">{city.upper()} · {dlabel} · WBGT-BASED HEAT STRESS SYSTEM</div>
    <div class="hero-h1">Who Gets<br><span class="hero-accent">Warned?</span></div>
    <div class="hero-desc">
        Real-time heat stress classification for 24 categories of informal workers
        in {city} : powered by WBGT science, not heat index guesswork.
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div style="padding: 14px 40px; background: rgba(255,255,255,0.02);
     border-bottom: 1px solid rgba(255,255,255,0.04);
     font-size: 12px; color: rgba(240,236,232,0.3); line-height: 1.7">
    <strong style="color:rgba(240,236,232,0.45)">Who is this for?</strong>
    &nbsp; Urban planners, labour welfare officers, public health administrators,
    and NGOs operating in Pakistan — to identify which worker categories need
    intervention, which hours to suspend outdoor work orders, and where to deploy
    cooling stations. Worker-facing guidance is generated below in English and Roman Urdu
    for SMS or community health worker delivery.
</div>
""", unsafe_allow_html=True)

# ── EL NIÑO ALERT ─────────────────────────────────────────────────────────
if el_nino:
    st.markdown("""
    <div class="alert-strip">
        <span style="color:#dc2626; font-size:13px; flex-shrink:0">⚠</span>
        <span>
            <strong style="color:rgba(240,236,232,0.65)">El Niño active.</strong>
            WHO–WMO (Sept 2026): declared a "significant public health threat."
            Climate Impact Lab projects 451,000 additional heat deaths globally through Feb 2027.
            El Niño is a periodic warming of Pacific Ocean temperatures that raises global land temperatures — Pakistan typically sees 1–2°C above normal during active phases.
            WBGT elevated +1.2°C across all classifications on this dashboard.
            &nbsp;<a href="https://www.dawn.com/news/2032114" target="_blank"
            style="color:#f97316; text-decoration:none; font-size:11px">Read →</a>
        </span>
    </div>
    """, unsafe_allow_html=True)

# ── METRICS ───────────────────────────────────────────────────────────────
el_sub = "+1.2°C El Niño applied" if el_nino else "No seasonal adjustment"
wr_str = (f"Max {wm} min work · {rm} min shade rest per hour"
          if risk not in ('SAFE','EXTREME')
          else ("No restriction — stay hydrated" if risk == 'SAFE' else "STOP ALL WORK IMMEDIATELY"))

st.markdown(f"""
<div class="metrics-row">
  <div class="metric-card" style="--c:{rc['hex']}">
    <div class="metric-glow"></div>
    <div class="m-label">Current WBGT</div>
    <div class="m-value">{wbgt_val:.1f}°C</div>
    <div class="m-sub">Wet-Bulb Globe Temperature — combines heat, humidity and sun to measure what the body actually feels. Above 32°C is lethal for heavy outdoor work.</div>
  </div>
  <div class="metric-card" style="--c:#a78bfa">
    <div class="metric-glow"></div>
    <div class="m-label">OMGI Score</div>
    <div class="m-value">{omgi_val:.1f}×</div>
    <div class="m-sub">Occupational Mortality Gap Index — how many times more dangerous this heat is for an outdoor worker vs. an office worker at this exact location right now.</div>
  </div>
  <div class="metric-card" style="--c:{rc['hex']}">
    <div class="metric-glow"></div>
    <div class="m-label">At EXTREME Risk</div>
    <div class="m-value">{ex_count}</div>
    <div class="m-sub">Occupations where WBGT has crossed the lethal threshold — work should stop or be suspended for these categories.</div>
  </div>
  <div class="metric-card" style="--c:#94a3b8">
    <div class="metric-glow"></div>
    <div class="m-label">Air Temperature</div>
    <div class="m-value">{cur['temp_c']:.1f}°C</div>
    <div class="m-sub">{cur['rh_pct']:.0f}% humidity · {cur['wind_ms']:.1f} m/s wind · Source: Open-Meteo API</div>
  </div>
  <div class="metric-card" style="--c:#3b82f6">
    <div class="metric-glow"></div>
    <div class="m-label">EXTREME Hours</div>
    <div class="m-value">{ex_hrs}</div>
    <div class="m-sub">Hours in this dataset where {occ_label[:20]} crossed into lethal WBGT territory.</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── RISK BANNER ───────────────────────────────────────────────────────────
st.markdown(f"""
<div class="risk-banner">
    <div class="risk-badge"
         style="color:{rc['hex']}; border-color:{rc['border']}; background:{rc['bg']}">
        {risk}
    </div>
    <div class="risk-occ-name">{occ_label}</div>
    <div class="wr-tag">{wr_str}</div>
</div>
""", unsafe_allow_html=True)

# ── CHARTS ────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="section-hdr" style="margin-top: 24px;">
    <div class="sec-title">WBGT Timeline</div>
    <div class="sec-cap">Hourly risk classification · {occ_label}</div>
</div>
""", unsafe_allow_html=True)

df['rc'] = df[f'risk_{occ_key}'].map(lambda r: RC[r]['hex'])
thresh = OCCUPATION_PROFILES[occ_key]['thresholds']

fig1 = go.Figure()
fig1.add_trace(go.Bar(
    x=df['time'], y=df['WBGT'],
    marker_color=df['rc'],
    marker_line_width=0,
    hovertemplate='<b>%{x|%d %b %H:%M}</b><br>WBGT: %{y:.1f}°C<extra></extra>'
))

tc = {'moderate':'#eab308','high':'#f97316','extreme':'#ef4444'}
for lvl, val in thresh.items():
    fig1.add_hline(
        y=val, line_dash="dot",
        line_color=tc[lvl], line_width=1, opacity=0.5,
        annotation_text=f"{lvl.upper()} {val}°C",
        annotation_font_size=9,
        annotation_font_color=tc[lvl],
        annotation_position="right"
    )

fig1.update_layout(**PT, height=380, yaxis_title='WBGT °C', showlegend=False)
st.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': False, 'staticPlot': False, 'scrollZoom': False})

# OMGI
st.markdown("""
<div class="section-hdr" style="margin-top:28px">
    <div class="sec-title">Occupational Mortality Gap Index (OMGI)</div>
    <div class="sec-cap">Heat inequality made visible — multiplier vs. office worker</div>
</div>
""", unsafe_allow_html=True)

peak_idx  = df['OMGI'].argmax()
peak_time = df.loc[peak_idx, 'time']
peak_omgi = df['OMGI'].max()

fig2 = go.Figure()
fig2.add_trace(go.Scatter(
    x=df['time'], y=df['OMGI'],
    fill='tozeroy',
    line=dict(color='#a78bfa', width=1.5),
    fillcolor='rgba(167,139,250,0.07)',
    mode='lines',
    hovertemplate='<b>%{x|%d %b %H:%M}</b><br>OMGI: %{y:.1f}×<extra></extra>'
))
fig2.add_hline(y=1.0, line_dash="dot",
               line_color='rgba(255,255,255,0.12)', line_width=1,
               annotation_text="Office worker baseline (1.0×)",
               annotation_font_size=9,
               annotation_font_color='rgba(240,236,232,0.2)')
fig2.add_annotation(
    x=peak_time, y=peak_omgi,
    text=f"Peak {peak_omgi:.1f}×",
    showarrow=True, arrowhead=0, arrowwidth=1,
    arrowcolor='#a78bfa',
    font=dict(color='#c4b5fd', size=10),
    bgcolor='rgba(139,92,246,0.12)',
    bordercolor='rgba(139,92,246,0.3)',
    borderpad=4
)
fig2.update_layout(**PT, height=260, yaxis_title='Multiplier ×', showlegend=False)
st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})

# ── OCCUPATION GRID ────
st.markdown("""
<div class="section-hdr" style="margin-top:28px">
    <div class="sec-title">All 24 Occupations</div>
    <div class="sec-cap">Sorted by current risk severity - highest first</div>
</div>
""", unsafe_allow_html=True)

sorted_occs = sorted(
    OCCUPATION_PROFILES.items(),
    key=lambda x: ['EXTREME','HIGH','MODERATE','SAFE'].index(cur[f'risk_{x[0]}'])
)

occ_html = '<div class="occ-grid">'
for occ, profile in sorted_occs:
    r   = cur[f'risk_{occ}']
    col = RC[r]['hex']
    bg  = RC[r]['bg']
    brd = RC[r]['border']
    w, rest = get_work_rest(r, occ)
    wr_txt = (f"{w}m work / {rest}m rest" if r not in ('SAFE','EXTREME')
              else ("no restriction" if r == 'SAFE' else "STOP WORK"))
    occ_html += f"""
    <div class="occ-row">
        <div class="occ-stripe" style="background:{col}; opacity:0.65"></div>
        <div class="occ-name">{profile['label']}</div>
        <div class="occ-wr-txt">{wr_txt}</div>
        <div class="occ-pill" style="color:{col}; background:{bg}; border:1px solid {brd}">{r}</div>
    </div>"""
occ_html += '</div>'
st.markdown(occ_html, unsafe_allow_html=True)

# ── GUIDANCE ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="section-hdr" style="margin-top:36px">
    <div class="sec-title">Bilingual Safety Guidance</div>
    <div class="sec-cap">English + Roman Urdu · Occupation-specific · 5th-grade literacy</div>
</div>
""", unsafe_allow_html=True)

bc1, bc2 = st.columns([1, 2])
with bc1:
    gen = st.button(f"Generate for {occ_label[:24]}...", type="primary")
with bc2:
    st.markdown(
        "<div style='padding-top:10px; font-size:11px; color:rgba(240,236,232,0.22); line-height:1.75'>"
        "AI-generated guidance calibrated to current WBGT and risk level.<br>"
        "Designed for SMS or community health worker delivery."
        "</div>",
        unsafe_allow_html=True
    )

if gen:
    with st.spinner(""):
        try:
            g = generate_guidance(occ_label, risk, wbgt_val, datetime.now().hour)
            parts = g.split('ROMAN URDU:')
            eng  = parts[0].replace('ENGLISH:', '').strip()
            urdu = parts[1].strip() if len(parts) > 1 else "Urdu output unavailable."
            st.markdown(f"""
            <div class="guidance-pair">
                <div class="g-card" style="border-top-color:#3b82f6">
                    <div class="g-lang">English Guidance</div>
                    <div class="g-text">{eng}</div>
                </div>
                <div class="g-card" style="border-top-color:#22c55e">
                    <div class="g-lang">Roman Urdu — رومن اردو</div>
                    <div class="g-text">{urdu}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        except Exception:
            st.error("API limit reached. Wait a moment and try again.")

# ── 2015 VALIDATION ────────────────────────────────────────────────────────
if "2015" in view_mode:
    st.markdown("""
    <div class="section-hdr" style="margin-top:36px">
        <div class="sec-title">2015 Heatwave — Retrospective Validation</div>
        <div class="sec-cap">Does HeatGuard correctly flag the event that killed 1,228 people?</div>
    </div>
    """, unsafe_allow_html=True)

    D2015 = {
        '2015-06-18': 65,  '2015-06-19': 228, '2015-06-20': 312,
        '2015-06-21': 280, '2015-06-22': 198, '2015-06-23': 89,
        '2015-06-24': 45,  '2015-06-25': 11
    }
    ddf = pd.DataFrame([{'date': pd.to_datetime(d),'deaths': v} for d,v in D2015.items()])
    df['date'] = df['time'].dt.date
    daily = df.groupby('date').agg(
        peak_WBGT=('WBGT','max'),
        ext_hrs=(f'risk_{occ_key}', lambda x: (x=='EXTREME').sum())
    ).reset_index()
    daily['date'] = pd.to_datetime(daily['date'])
    daily = daily.merge(ddf, on='date', how='left')

    fig3 = go.Figure()
    fig3.add_trace(go.Bar(
        x=daily['date'], y=daily['deaths'],
        name='Reported Deaths',
        marker_color='rgba(239,68,68,0.4)',
        marker_line_color='rgba(239,68,68,0.65)',
        marker_line_width=1,
        yaxis='y2',
        hovertemplate='<b>%{x|%d %b}</b><br>Deaths: %{y}<extra></extra>'
    ))
    fig3.add_trace(go.Scatter(
        x=daily['date'], y=daily['peak_WBGT'],
        name='Peak WBGT',
        line=dict(color='#f97316', width=2),
        mode='lines+markers',
        marker=dict(size=5, color='#f97316'),
        hovertemplate='<b>%{x|%d %b}</b><br>WBGT: %{y:.1f}°C<extra></extra>'
    ))
    fig3.update_layout(
        **PT, height=300,
        yaxis=dict(title='Peak WBGT °C', color='#f97316',
                   showgrid=True, gridcolor='rgba(255,255,255,0.03)'),
        yaxis2=dict(title='Deaths', overlaying='y', side='right',
                    color='#ef4444', showgrid=False),
        legend=dict(orientation='h', y=-0.22, font=dict(size=10),
                    bgcolor='rgba(0,0,0,0)')
    )

    st.plotly_chart(fig3, use_container_width=True, config={'displayModeBar': False})

    ext_val = int((df[f'risk_{occ_key}'] == 'EXTREME').sum())
    verdict_col = '#22c55e' if df['WBGT'].max() >= OCCUPATION_PROFILES[occ_key]['thresholds']['extreme'] else '#ef4444'
    verdict_txt = "✓ Correctly classified EXTREME" if df['WBGT'].max() >= OCCUPATION_PROFILES[occ_key]['thresholds']['extreme'] else "✗ Missed"

    st.markdown(f"""
    <div class="val-row">
        <div class="val-card">
            <div class="v-label">Peak WBGT</div>
            <div class="v-val">{df['WBGT'].max():.1f}°C</div>
            <div class="v-sub">June 20, 2015</div>
        </div>
        <div class="val-card">
            <div class="v-label">Total Deaths</div>
            <div class="v-val">1,228</div>
            <div class="v-sub">June 18–25, 2015</div>
        </div>
        <div class="val-card">
            <div class="v-label">Peak OMGI</div>
            <div class="v-val">{df['OMGI'].max():.1f}×</div>
            <div class="v-sub">Mortality gap at peak</div>
        </div>
        <div class="val-card">
            <div class="v-label">Framework Verdict</div>
            <div class="v-val" style="color:{verdict_col}; font-size:14px">{verdict_txt}</div>
            <div class="v-sub">{ext_val} EXTREME hours · {occ_label[:20]}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── FOOTER ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hg-footer">
    <div>
        <div class="footer-brand">HEATGUARD</div>
        <div class="footer-meta">
            Shiza Shah · Dept. of Computer Science · MUET Jamshoro<br>
            <a href="https://www.linkedin.com/in/sshizashah" target="_blank">
                linkedin.com/in/sshizashah ↗
            </a>
            &nbsp;&nbsp;·&nbsp;&nbsp;
            <a href="https://www.dawn.com/news/2032114" target="_blank">
                El Niño Report 1 ↗
            </a>
            &nbsp;&nbsp;·&nbsp;&nbsp;
            <a href="https://www.dawn.com/news/2031860" target="_blank">
                El Niño Report 2 ↗
            </a>
        </div>
    </div>
    <div class="footer-sources">
        WBGT · Stull (2011) formula<br>
        Thresholds · NIOSH / ISO 7933<br>
        El Niño · Climate Impact Lab (2026)<br>
        Weather · Open-Meteo Archive API
    </div>
</div>
""", unsafe_allow_html=True)