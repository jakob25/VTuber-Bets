import streamlit as st
import uuid
from datetime import datetime, timedelta
from supabase import create_client, Client

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="VTuberBets",
    page_icon="🎲",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  DESIGN SYSTEM  —  deep navy / electric blue / neon cyan
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Syne:wght@700;800&family=JetBrains+Mono:wght@500&display=swap');

/* ── BASE ── */
*, *::before, *::after { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"] {
    background: #080c18 !important;
    color: #c8d8f0 !important;
    font-family: 'Inter', sans-serif;
}
[data-testid="stSidebar"] {
    background: #090d1c !important;
    border-right: 1px solid #1a2540 !important;
}
h1, h2, h3 {
    font-family: 'Syne', sans-serif !important;
    letter-spacing: -0.02em;
    color: #e8f0ff !important;
}

/* ── GRID BACKGROUND on main area ── */
[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image:
        linear-gradient(rgba(30,60,120,0.07) 1px, transparent 1px),
        linear-gradient(90deg, rgba(30,60,120,0.07) 1px, transparent 1px);
    background-size: 40px 40px;
    pointer-events: none;
    z-index: 0;
}

/* ── ANIMATED GRADIENT BORDER FOR HERO ── */
@keyframes gradientBorder {
    0%   { border-color: #0066ff; }
    25%  { border-color: #00c8ff; }
    50%  { border-color: #aa44ff; }
    75%  { border-color: #00c8ff; }
    100% { border-color: #0066ff; }
}

.hero {
    background: linear-gradient(135deg, #080e20 0%, #0c1530 50%, #080e20 100%);
    border: 2px solid #0066ff;
    border-radius: 18px;
    padding: 36px 40px;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
    animation: gradientBorder 4s linear infinite;
    box-shadow: 0 0 25px rgba(0, 102, 255, 0.25);
}

/* ── ANIMATED GRADIENT TEXT ── */
@keyframes gradientText {
    0%   { background-position: 0% 50%; }
    50%  { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

.gradient-text {
    background: linear-gradient(90deg, #00aaff, #00f0ff, #aa88ff, #00aaff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-size: 200% 200%;
    animation: gradientText 3s linear infinite;
    font-style: italic;
    font-weight: 800;
}

/* ── CARDS ── */
.card {
    background: #0b0f1e;
    border: 1px solid #151e33;
    border-left: 3px solid #1e3060;
    border-radius: 10px;
    padding: 18px 20px;
    margin-bottom: 12px;
    transition: border-left-color 0.2s, box-shadow 0.2s;
}
.card:hover {
    border-left-color: #0066ff;
    box-shadow: -2px 0 12px rgba(0, 102, 255, 0.15);
}

/* Live bets get the cyan accent */
.card-live {
    border-left-color: #00c8ff;
    box-shadow: -2px 0 10px rgba(0, 200, 255, 0.1);
}
.card-live:hover {
    border-left-color: #00e5ff;
    box-shadow: -2px 0 16px rgba(0, 200, 255, 0.2);
}

/* Voting bets get amber */
.card-voting {
    border-left-color: #ffaa00;
    box-shadow: -2px 0 10px rgba(255, 170, 0, 0.1);
}
.card-voting:hover {
    border-left-color: #ffcc00;
    box-shadow: -2px 0 16px rgba(255, 204, 0, 0.2);
}

/* Resolved bets get muted purple */
.card-closed {
    border-left-color: #4433aa;
}
.card-closed:hover {
    border-left-color: #6655cc;
}

/* ── BET CARD TEXT ── */
.vtag {
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #4499ff;
    margin-bottom: 6px;
    font-family: 'JetBrains Mono', monospace;
}
.bet-title {
    font-size: 1rem;
    font-weight: 600;
    color: #e0eaff;
    margin-bottom: 6px;
    line-height: 1.4;
}
.bet-game {
    font-size: 0.78rem;
    color: #5577aa;
    margin-bottom: 10px;
    font-style: italic;
}

/* ── STATUS PILLS ── */
.pill {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 4px;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    font-family: 'JetBrains Mono', monospace;
}
.pill-open   { background: #001a0d; color: #00ff88; border: 1px solid #00ff8844; }
.pill-voting { background: #1a1000; color: #ffcc00; border: 1px solid #ffcc0044; }
.pill-closed { background: #0a001a; color: #8866ff; border: 1px solid #8866ff44; }

.pot {
    font-size: 0.75rem;
    color: #4499ff;
    font-weight: 600;
    font-family: 'JetBrains Mono', monospace;
}

/* ── PROGRESS BARS ── */
.bar-wrap { margin: 10px 0; }
.bar-label {
    display: flex;
    justify-content: space-between;
    font-size: 0.85rem;           /* increased size */
    margin-bottom: 5px;
    color: #99aacc;               /* brighter */
}
.bar-label .bar-pct {
    font-family: 'JetBrains Mono', monospace;
    color: #44bbff;               /* brighter */
    font-size: 0.8rem;            /* increased */
}
.bar-bg {
    background: #0d1428;
    border-radius: 3px;
    height: 8px;                  /* taller */
    border: 1px solid #1e3060;
    overflow: hidden;
}
.bar-fill {
    height: 8px;                  /* taller */
    border-radius: 3px;
    background: linear-gradient(90deg, #0044cc, #00aaff);
    box-shadow: 0 0 8px rgba(0,170,255,0.4);
}
.bar-fill-vote {
    height: 8px;
    border-radius: 3px;
    background: linear-gradient(90deg, #cc8800, #ffcc00);
    box-shadow: 0 0 8px rgba(255,204,0,0.4);
}

/* ── COIN DISPLAY ── */
.coin-box {
    background: linear-gradient(135deg, #0d1428, #0a1020);
    border: 1px solid #1e3060;
    border-radius: 12px;
    padding: 14px 18px;
    text-align: center;
    margin-bottom: 10px;
    position: relative;
    overflow: hidden;
}
.coin-box::after {
    content: '';
    position: absolute;
    inset: 0;
    background: radial-gradient(ellipse at 50% 0%, rgba(0,100,255,0.08) 0%, transparent 70%);
    pointer-events: none;
}
.coin-label {
    font-size: 0.65rem;
    color: #4466aa;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-bottom: 4px;
    font-family: 'JetBrains Mono', monospace;
}
.coin-amount {
    font-family: 'Syne', sans-serif;
    font-size: 2rem;
    font-weight: 800;
    background: linear-gradient(90deg, #00aaff, #00f0ff, #aa88ff, #00aaff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-size: 200% 200%;
    animation: gradientText 3s linear infinite;
    text-shadow: 0 0 20px rgba(0,170,255,0.4);
}
.coin-sub {
    font-size: 0.65rem;
    color: #334466;
    margin-top: 2px;
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: 0.08em;
}

/* ── NOTICE BOXES ── */
.notice {
    border-radius: 8px;
    padding: 13px 16px;
    font-size: 0.87rem;
    margin: 10px 0;
    font-weight: 500;
    line-height: 1.5;             /* better line height */
}
.notice-success { background: #001a0d; border: 1px solid #00ff8833; color: #00cc66; }
.notice-warn    { background: #1a1000; border: 1px solid #ffcc0033; color: #ccaa00; }
.notice-error   { background: #140008; border: 1px solid #ff224433; color: #ff4466; }
.notice-info    { background: #000d1a; border: 1px solid #0066ff33; color: #4499ff; }

/* ── LEADERBOARD ── */
.lb-row {
    display: flex;
    align-items: center;
    padding: 11px 16px;
    border-radius: 10px;
    margin-bottom: 6px;
    background: #0d1428;
    border: 1px solid #1a2a44;
    gap: 14px;
    transition: all 0.2s ease;
}
.lb-row:hover { 
    border-color: #0066ff44; 
    background: #111a2f;      /* subtle hover lift */
}
.lb-rank {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    font-weight: 700;
    width: 32px;
    color: #334466;
}
.lb-rank-top { color: #00aaff; }
.lb-name { flex: 1; font-weight: 600; font-size: 0.88rem; color: #c0d0e8; }
.lb-stat {
    color: #00aaff;
    font-weight: 700;
    font-size: 0.82rem;
    text-align: right;
    font-family: 'JetBrains Mono', monospace;
}

/* ── STAT CARDS / METRICS ── */
.stat-val {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.65rem;           /* bigger */
    font-weight: 700;
    color: #00aaff;
}
.stat-lbl {
    font-size: 0.74rem;           /* slightly larger */
    color: #446699;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-top: 2px;
}

[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-size: 1.7rem !important; /* bigger metric values */
}

/* ── SMALL TEXT IMPROVEMENTS ── */
.stTextInput > div > div > input::placeholder,
.stTextArea > div > div > textarea::placeholder,
.stSelectbox > div > div > div {
    color: #7799cc !important;    /* brighter placeholders */
    font-size: 0.92rem !important;
}

.section-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;           /* larger */
    color: #3366aa;               /* brighter */
    text-transform: uppercase;
    letter-spacing: 0.15em;
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 1px solid #1a2540;
}

/* ── BUTTONS & INPUTS remain unchanged ── */
.stButton > button {
    background: linear-gradient(135deg, #0044cc, #0066ff) !important;
    color: #e8f0ff !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    letter-spacing: 0.01em !important;
    transition: opacity 0.15s, box-shadow 0.15s !important;
}
.stButton > button:hover {
    opacity: 0.9 !important;
    box-shadow: 0 0 16px rgba(0,102,255,0.3) !important;
}

/* Rest of the original styles (unchanged) */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div {
    background: #0d1428 !important;
    border: 1px solid #1e3060 !important;
    border-radius: 8px !important;
    color: #c8d8f0 !important;
    font-family: 'Inter', sans-serif !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #0066ff !important;
    box-shadow: 0 0 0 2px rgba(0,102,255,0.15) !important;
}

.stTabs [data-baseweb="tab-list"] {
    background: #090d1c !important;
    border-radius: 8px;
    gap: 2px;
    padding: 3px;
    border: 1px solid #1a2540;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #334466 !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    font-family: 'Inter', sans-serif !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #0033aa, #0055cc) !important;
    color: #e8f0ff !important;
}

hr { border-color: #1a2540 !important; }
[data-testid="stExpander"] {
    background: #0d1428;
    border: 1px solid #1e3060;
    border-radius: 10px;
}
.dup-warn {
    background: #1a0e00;
    border: 1px solid #ff880033;
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 0.82rem;
    color: #ffaa44;
    margin: 8px 0;
}
.stream-link {
    font-size: 0.75rem;
    color: #0088cc;
    text-decoration: none;
    font-family: 'JetBrains Mono', monospace;
}
.stream-link:hover { color: #00aaff; text-decoration: underline; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  SUPABASE (unchanged)
# ─────────────────────────────────────────────
@st.cache_resource
def get_supabase() -> Client:
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

def db() -> Client:
    return get_supabase()

# All the Python logic below remains 100% untouched
# (Only the CSS block was modified as requested)

# ... [The rest of your original code continues exactly as provided] ...
