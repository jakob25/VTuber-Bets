"""
ui.py
CSS injection, session state helpers, and shared UI components
(sidebar, bet cards, badges, toasts, onboarding).
"""
import streamlit as st
from database import (
    get_user, get_entries, get_user_badges, get_all_achievements,
    get_equipped, claim_daily_bonus, pot_total, BADGE_STYLES
)

# ── Styles ─────────────────────────────────────────────────────────────────
def inject_styles():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800;900&family=JetBrains+Mono:wght@400;500;700&family=DM+Sans:wght@300;400;500;600&display=swap');

*, *::before, *::after { box-sizing: border-box; }

/* ── LIVING BACKGROUND ── */
html, body, [data-testid="stAppViewContainer"] {
    background: #05080f !important;
    color: #c8d8f0 !important;
    font-family: 'DM Sans', sans-serif;
}

/* Animated mesh gradient background */
[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed;
    inset: 0;
    z-index: 0;
    background:
        radial-gradient(ellipse 80% 50% at 20% 20%, rgba(0,85,255,0.07) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 80% 80%, rgba(136,0,255,0.06) 0%, transparent 60%),
        radial-gradient(ellipse 50% 60% at 50% 50%, rgba(0,212,255,0.04) 0%, transparent 70%);
    animation: mesh-drift 12s ease-in-out infinite alternate;
    pointer-events: none;
}
@keyframes mesh-drift {
    0%   { background-position: 0% 0%, 100% 100%, 50% 50%; opacity: 1; }
    33%  { background-position: 30% 10%, 70% 90%, 60% 40%; }
    66%  { background-position: 10% 40%, 90% 60%, 40% 60%; }
    100% { background-position: 20% 20%, 80% 80%, 50% 50%; opacity: 0.7; }
}

/* Scanline overlay */
[data-testid="stAppViewContainer"]::after {
    content: '';
    position: fixed;
    inset: 0;
    z-index: 1;
    background: repeating-linear-gradient(
        0deg,
        transparent,
        transparent 2px,
        rgba(0,0,0,0.03) 2px,
        rgba(0,0,0,0.03) 4px
    );
    pointer-events: none;
}

[data-testid="stSidebar"] {
    background: #060a14 !important;
    border-right: 1px solid #0d1a30 !important;
}
[data-testid="stSidebar"]::before {
    content: '';
    position: absolute;
    top: 0; right: 0;
    width: 1px; height: 100%;
    background: linear-gradient(180deg, transparent, #0055ff44, #8800ff33, transparent);
}

h1, h2, h3 {
    font-family: 'Syne', sans-serif !important;
    letter-spacing: -0.02em;
    color: #e8f0ff !important;
}

/* ── ANIMATIONS ── */
@keyframes gradient-border {
    0%   { background-position: 0% 50%; }
    50%  { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
@keyframes gradient-text {
    0%   { background-position: 0% 50%; }
    50%  { background-position: 200% 50%; }
    100% { background-position: 0% 50%; }
}
@keyframes pulse-glow {
    0%, 100% { box-shadow: 0 0 20px rgba(0,85,255,0.2), 0 0 40px rgba(0,85,255,0.1); }
    50%       { box-shadow: 0 0 30px rgba(0,212,255,0.3), 0 0 60px rgba(0,212,255,0.15); }
}
@keyframes float {
    0%, 100% { transform: translateY(0px); }
    50%       { transform: translateY(-6px); }
}
@keyframes neon-flicker {
    0%, 95%, 100% { opacity: 1; }
    96% { opacity: 0.7; }
    97% { opacity: 1; }
    98% { opacity: 0.5; }
}

/* ── HERO ── */
.hero-wrap {
    padding: 2px;
    border-radius: 20px;
    background: linear-gradient(135deg, #0055ff, #00d4ff, #8800ff, #00ff88, #0055ff);
    background-size: 400% 400%;
    animation: gradient-border 5s ease infinite;
    margin-bottom: 28px;
    animation: pulse-glow 3s ease-in-out infinite, gradient-border 5s ease infinite;
}
.hero {
    background: linear-gradient(135deg, #070b1a 0%, #050810 100%);
    border-radius: 18px;
    padding: 40px 44px;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute;
    top: -40%; right: -10%;
    width: 600px; height: 600px;
    background: radial-gradient(circle, rgba(0,85,255,0.1) 0%, transparent 65%);
    pointer-events: none;
    animation: float 8s ease-in-out infinite;
}
.hero::after {
    content: '';
    position: absolute;
    bottom: -30%; left: -5%;
    width: 400px; height: 400px;
    background: radial-gradient(circle, rgba(136,0,255,0.07) 0%, transparent 65%);
    pointer-events: none;
    animation: float 10s ease-in-out infinite reverse;
}
.hero-eyebrow {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.25em;
    text-transform: uppercase;
    color: #0066ff;
    margin-bottom: 12px;
    animation: neon-flicker 8s ease-in-out infinite;
}
.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: 2.4rem;
    font-weight: 900;
    color: #c8dcff;
    margin-bottom: 4px;
    line-height: 1.15;
}
.hero-name {
    font-family: 'Syne', sans-serif;
    font-size: 2.4rem;
    font-weight: 900;
    font-style: italic;
    background: linear-gradient(90deg, #44ddff, #8800ff, #00d4ff, #0055ff, #00ff88, #44ddff, #8800ff, #00d4ff, #0055ff, #00ff88);
    background-size: 400% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: gradient-text 16s ease-in-out infinite;
    display: inline;
}
.hero-sub {
    color: #4a6a99;
    font-size: 0.92rem;
    line-height: 1.75;
    margin-top: 12px;
}

/* ── CARDS ── */
.card {
    background: linear-gradient(135deg, #0a0e1c 0%, #080c18 100%);
    border: 1px solid #131d33;
    border-left: 3px solid #1e3060;
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 14px;
    transition: border-left-color 0.25s, box-shadow 0.25s, transform 0.2s;
    position: relative;
    overflow: hidden;
}
.card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(0,85,255,0.3), transparent);
    opacity: 0;
    transition: opacity 0.25s;
}
.card:hover { border-left-color: #0055ff; box-shadow: -3px 0 20px rgba(0,85,255,0.2), 0 4px 30px rgba(0,0,0,0.3); transform: translateX(2px); }
.card:hover::before { opacity: 1; }
.card-live   { border-left-color: #00d4ff; box-shadow: -3px 0 15px rgba(0,212,255,0.15); }
.card-live:hover { border-left-color: #00eeff; box-shadow: -3px 0 25px rgba(0,238,255,0.25); }
.card-voting { border-left-color: #ffaa00; box-shadow: -3px 0 15px rgba(255,170,0,0.12); }
.card-voting:hover { border-left-color: #ffdd00; box-shadow: -3px 0 25px rgba(255,221,0,0.25); }
.card-closed { border-left-color: #5533bb; }
.card-closed:hover { border-left-color: #7755dd; box-shadow: -3px 0 20px rgba(119,85,221,0.2); }

.vtag {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #00d4ff;
    margin-bottom: 8px;
    font-family: 'JetBrains Mono', monospace;
}
.bet-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.05rem;
    font-weight: 800;
    color: #ddeaff;
    margin-bottom: 6px;
    line-height: 1.4;
}
.bet-game {
    font-size: 0.8rem;
    color: #3a5070;
    margin-bottom: 12px;
    font-style: italic;
}

/* ── PILLS ── */
.pill {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 6px;
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    font-family: 'JetBrains Mono', monospace;
}
.pill-open   { background: #001a0d; color: #00ff88; border: 1px solid #00ff8855; box-shadow: 0 0 8px rgba(0,255,136,0.15); }
.pill-voting { background: #1a1000; color: #ffdd00; border: 1px solid #ffdd0055; box-shadow: 0 0 8px rgba(255,221,0,0.15); }
.pill-closed { background: #0a001a; color: #aa88ff; border: 1px solid #aa88ff55; }
.pot { font-size: 0.78rem; color: #00d4ff; font-weight: 700; font-family: 'JetBrains Mono', monospace; }

/* ── BARS ── */
.bar-wrap { margin: 12px 0; }
.bar-label { display: flex; justify-content: space-between; font-size: 0.82rem; margin-bottom: 6px; color: #6a8aaa; }
.bar-label .bar-pct { font-family: 'JetBrains Mono', monospace; color: #00d4ff; font-size: 0.78rem; }
.bar-bg { background: #070b16; border-radius: 4px; height: 8px; border: 1px solid #0d1a30; overflow: hidden; }
.bar-fill { height: 8px; border-radius: 4px; background: linear-gradient(90deg, #0055ff, #00d4ff); box-shadow: 0 0 12px rgba(0,212,255,0.6); }
.bar-fill-vote { height: 8px; border-radius: 4px; background: linear-gradient(90deg, #aa6600, #ffdd00); box-shadow: 0 0 12px rgba(255,221,0,0.6); }

/* ── NOTICES ── */
.notice { border-radius: 10px; padding: 14px 18px; font-size: 0.88rem; margin: 12px 0; font-weight: 500; line-height: 1.6; }
.notice-success { background: #001508; border: 1px solid #00ff8833; color: #00dd77; box-shadow: 0 0 20px rgba(0,255,136,0.05); }
.notice-warn    { background: #150f00; border: 1px solid #ffdd0033; color: #ddaa00; }
.notice-error   { background: #140005; border: 1px solid #ff335544; color: #ff5577; }
.notice-info    { background: #000c1a; border: 1px solid #0055ff33; color: #4499ff; }

/* ── LEADERBOARD ── */
.lb-row {
    display: flex; align-items: center; padding: 14px 20px;
    border-radius: 12px; margin-bottom: 8px;
    background: linear-gradient(135deg, #090d1c, #070a16);
    border: 1px solid #131d33; gap: 16px;
    transition: border-color 0.2s, background 0.2s, transform 0.2s;
}
.lb-row:hover { border-color: #0055ff44; background: linear-gradient(135deg, #0c1228, #09101e); transform: translateX(4px); }
.lb-rank { font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; font-weight: 700; width: 36px; color: #1e3055; }
.lb-rank-top { color: #00d4ff; text-shadow: 0 0 10px rgba(0,212,255,0.5); }
.lb-name { flex: 1; font-weight: 600; font-size: 0.92rem; color: #b8ccee; }
.lb-stat { color: #00d4ff; font-weight: 700; font-size: 0.88rem; text-align: right; font-family: 'JetBrains Mono', monospace; }
.lb-stat-loss { color: #ff5577; font-weight: 700; font-size: 0.88rem; text-align: right; font-family: 'JetBrains Mono', monospace; }

/* ── BADGES ── */
.badge {
    display: inline-block;
    background: #0a0e1c;
    border: 1px solid #1a2a44;
    border-radius: 6px;
    padding: 5px 12px;
    font-size: 0.72rem;
    font-weight: 700;
    color: #4488ff;
    margin: 3px;
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: 0.05em;
}
.badge-earned { background: linear-gradient(135deg, #0a1428, #0d1e3a); border-color: #0055ff44; color: #44aaff; }
.badge-gem    { border-color: #00ff8855; color: #00ff88; box-shadow: 0 0 8px rgba(0,255,136,0.15); }
.badge-roller { border-color: #ffdd0055; color: #ffdd00; box-shadow: 0 0 8px rgba(255,221,0,0.15); }
.badge-vote   { border-color: #8800ff55; color: #cc44ff; box-shadow: 0 0 8px rgba(136,0,255,0.15); }
.badge-scout  { border-color: #00d4ff55; color: #00d4ff; box-shadow: 0 0 8px rgba(0,212,255,0.15); }
.badge-raid   { border-color: #ff557755; color: #ff5577; box-shadow: 0 0 8px rgba(255,85,119,0.15); }

/* ── USER TITLE ── */
.user-title {
    font-size: 0.7rem;
    font-family: 'JetBrains Mono', monospace;
    color: #00d4ff;
    letter-spacing: 0.08em;
    margin-bottom: 3px;
    text-shadow: 0 0 8px rgba(0,212,255,0.5);
}

/* ── PROFILE CARD ── */
.profile-card {
    background: linear-gradient(135deg, #090d1c, #070a16);
    border: 1px solid #131d33;
    border-radius: 16px;
    padding: 28px 32px;
    margin-bottom: 18px;
    position: relative;
    overflow: hidden;
}
.profile-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, #0055ff66, #8800ff44, transparent);
}
.profile-role {
    display: inline-block;
    padding: 4px 14px;
    border-radius: 6px;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    font-family: 'JetBrains Mono', monospace;
    margin-bottom: 10px;
}
.role-watcher  { background: #00142a; color: #00d4ff; border: 1px solid #00d4ff44; box-shadow: 0 0 10px rgba(0,212,255,0.1); }
.role-streamer { background: #160022; color: #cc44ff; border: 1px solid #cc44ff44; box-shadow: 0 0 10px rgba(204,68,255,0.1); }
.role-clipper  { background: #001508; color: #00ff88; border: 1px solid #00ff8844; box-shadow: 0 0 10px rgba(0,255,136,0.1); }

/* ── SHOP ── */
.shop-item {
    background: linear-gradient(135deg, #090d1c, #070a16);
    border: 1px solid #131d33;
    border-radius: 12px;
    padding: 18px 22px;
    margin-bottom: 12px;
    transition: border-color 0.2s, box-shadow 0.2s;
}
.shop-item:hover { border-color: #0055ff44; box-shadow: 0 4px 30px rgba(0,85,255,0.1); }
.shop-item-name { font-family: 'Syne', sans-serif; font-weight: 800; font-size: 1rem; color: #ddeaff; margin-bottom: 4px; }
.shop-item-desc { font-size: 0.82rem; color: #3a5070; margin-bottom: 12px; line-height: 1.6; }
.shop-item-cost { font-family: 'JetBrains Mono', monospace; font-size: 0.82rem; color: #00d4ff; font-weight: 700; }
.shop-owned { border-color: #00ff8833; box-shadow: 0 0 20px rgba(0,255,136,0.05); }

/* ── HOW IT WORKS ── */
.hiw-section {
    background: linear-gradient(135deg, #090d1c, #070a16);
    border: 1px solid #131d33;
    border-left: 3px solid #0055ff;
    border-radius: 12px;
    padding: 22px 28px;
    margin-bottom: 16px;
    transition: border-left-color 0.2s, box-shadow 0.2s;
}
.hiw-section:hover { border-left-color: #00d4ff; box-shadow: -3px 0 20px rgba(0,212,255,0.15); }
.hiw-num { font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; color: #0055ff; letter-spacing: 0.2em; text-transform: uppercase; margin-bottom: 8px; }
.hiw-title { font-family: 'Syne', sans-serif; font-size: 1.15rem; font-weight: 800; color: #e8f0ff; margin-bottom: 10px; }
.hiw-body { font-size: 0.88rem; color: #5a7a99; line-height: 1.75; }

/* ── BUTTONS ── */
.stButton > button {
    background: linear-gradient(135deg, #0033bb, #0055ff, #0077ff) !important;
    background-size: 200% 200% !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    padding: 12px 24px !important;
    letter-spacing: 0.02em !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 15px rgba(0,85,255,0.3), inset 0 1px 0 rgba(255,255,255,0.1) !important;
    text-shadow: 0 1px 2px rgba(0,0,0,0.3) !important;
    min-height: 44px !important;
}
.stButton > button:hover {
    box-shadow: 0 6px 25px rgba(0,119,255,0.5), 0 0 40px rgba(0,212,255,0.2), inset 0 1px 0 rgba(255,255,255,0.15) !important;
    transform: translateY(-1px) !important;
    background-position: right center !important;
}
.stButton > button:active {
    transform: translateY(0px) !important;
    box-shadow: 0 2px 10px rgba(0,85,255,0.3) !important;
}

/* ── INPUTS ── */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div {
    background: #070b16 !important;
    border: 1px solid #131d33 !important;
    border-radius: 10px !important;
    color: #c8d8f0 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.92rem !important;
    padding: 10px 14px !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
.stTextInput > div > div > input::placeholder,
.stTextArea > div > div > textarea::placeholder { color: #1e3055 !important; }
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #0055ff !important;
    box-shadow: 0 0 0 3px rgba(0,85,255,0.15), 0 0 20px rgba(0,85,255,0.1) !important;
    outline: none !important;
}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
    background: #060a14 !important;
    border-radius: 10px;
    gap: 4px;
    padding: 4px;
    border: 1px solid #0d1a2e;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #2a4060 !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.86rem !important;
    font-family: 'DM Sans', sans-serif !important;
    padding: 10px 20px !important;
    transition: all 0.2s !important;
}
.stTabs [data-baseweb="tab"]:hover { background: #0d1a2e !important; color: #5577aa !important; }
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #003399, #0055ff) !important;
    color: #ffffff !important;
    box-shadow: 0 2px 12px rgba(0,85,255,0.4), 0 0 20px rgba(0,212,255,0.1) !important;
}

/* ── METRICS ── */
[data-testid="metric-container"] {
    background: linear-gradient(135deg, #090d1c, #070a16);
    border: 1px solid #131d33;
    border-radius: 12px;
    padding: 16px 20px;
    position: relative;
    overflow: hidden;
}
[data-testid="metric-container"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, #0055ff33, transparent);
}
[data-testid="metric-container"] label {
    color: #1e3055 !important;
    font-size: 0.72rem !important;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-family: 'JetBrains Mono', monospace !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #00d4ff !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 1.5rem !important;
    text-shadow: 0 0 20px rgba(0,212,255,0.4) !important;
}

hr { border-color: #0d1a2e !important; }
[data-testid="stExpander"] {
    background: linear-gradient(135deg, #090d1c, #070a16);
    border: 1px solid #131d33;
    border-radius: 12px;
}

.dup-warn {
    background: #120800;
    border: 1px solid #ff880033;
    border-radius: 10px;
    padding: 14px 18px;
    font-size: 0.85rem;
    color: #ffaa44;
    margin: 10px 0;
    line-height: 1.6;
}
.stream-link {
    font-size: 0.72rem;
    color: #0077cc;
    text-decoration: none;
    font-family: 'JetBrains Mono', monospace;
    transition: color 0.15s, text-shadow 0.15s;
}
.stream-link:hover { color: #00d4ff; text-shadow: 0 0 8px rgba(0,212,255,0.5); }
.section-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    color: #0055ff;
    text-transform: uppercase;
    letter-spacing: 0.2em;
    margin-bottom: 14px;
    padding-bottom: 8px;
    border-bottom: 1px solid #0d1a2e;
}
.stCaption, [data-testid="stCaptionContainer"] { color: #2a4060 !important; font-size: 0.8rem !important; }
.stRadio label { color: #6a8aaa !important; font-size: 0.9rem !important; }
.stTextInput label, .stTextArea label, .stSelectbox label, .stNumberInput label, .stMultiSelect label {
    color: #4466aa !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    margin-bottom: 6px !important;
}
p, li { line-height: 1.7; }

/* ── AUTH CARD ── */
.auth-card {
    background: linear-gradient(135deg, #090d1c, #070a16);
    border: 1px solid #131d33;
    border-radius: 18px;
    padding: 40px 44px;
    max-width: 480px;
    width: 100%;
    margin: 0 auto;
    box-shadow: 0 20px 60px rgba(0,0,0,0.5), 0 0 40px rgba(0,85,255,0.05);
}
.auth-container { display: flex; justify-content: center; }

/* ── ONBOARDING ── */
.onboarding-wrap {
    background: linear-gradient(135deg, #090d1c, #070a16);
    border: 1px solid #131d33;
    border-radius: 18px;
    padding: 32px 36px;
    position: relative;
    overflow: hidden;
}
.onboarding-wrap::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #0055ff, #00d4ff, #8800ff);
}


/* ── MOBILE ────────────────────────────────────────────────────────────── */
@media (max-width: 768px) {

    /* Show the sidebar collapse toggle on mobile */
    [data-testid="collapsedControl"] {
        display: flex !important;
        position: fixed !important;
        top: 12px !important;
        left: 12px !important;
        z-index: 9999 !important;
        background: #090d1c !important;
        border: 1px solid #1a2a44 !important;
        border-radius: 8px !important;
        padding: 6px 10px !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.4) !important;
    }
    [data-testid="collapsedControl"] svg {
        color: #00d4ff !important;
        width: 18px !important;
        height: 18px !important;
    }

    /* Main content padding so it doesn't hide behind the toggle */
    [data-testid="stAppViewContainer"] > section.main {
        padding-top: 56px !important;
        padding-left: 12px !important;
        padding-right: 12px !important;
    }

    /* Sidebar full-width overlay on mobile */
    [data-testid="stSidebar"] {
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        height: 100vh !important;
        z-index: 9998 !important;
        width: 280px !important;
        box-shadow: 4px 0 30px rgba(0,0,0,0.6) !important;
    }

    /* Scale down hero title */
    .hero-title, .hero-name {
        font-size: 1.6rem !important;
    }
    .hero {
        padding: 24px 20px !important;
    }

    /* Metrics stack nicely */
    [data-testid="metric-container"] {
        padding: 12px 14px !important;
    }
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        font-size: 1.2rem !important;
    }

    /* Bet cards already good, just tighten padding */
    .card {
        padding: 16px 16px !important;
        margin-bottom: 10px !important;
    }

    /* Buttons — full height, easier to tap */
    .stButton > button {
        min-height: 48px !important;
        font-size: 0.95rem !important;
        padding: 12px 16px !important;
    }

    /* Tabs — smaller text so they fit */
    .stTabs [data-baseweb="tab"] {
        font-size: 0.78rem !important;
        padding: 8px 12px !important;
    }

    /* Form inputs — bigger touch target */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea > div > div > textarea {
        font-size: 1rem !important;
        padding: 12px 14px !important;
    }

    /* Leaderboard rows */
    .lb-row {
        padding: 10px 14px !important;
        gap: 10px !important;
    }

    /* Onboarding card */
    .onboarding-wrap {
        padding: 22px 20px !important;
    }

    /* Profile card */
    .profile-card {
        padding: 20px 18px !important;
    }
}

/* Tablet */
@media (max-width: 1024px) and (min-width: 769px) {
    .hero-title, .hero-name { font-size: 1.9rem !important; }
    [data-testid="stAppViewContainer"] > section.main {
        padding-left: 20px !important;
        padding-right: 20px !important;
    }
}

/* ── HIDE STREAMLIT HUD ── */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
.stApp header {display: none;}
.stDeployButton {display: none;}
[data-testid="stAppViewContainer"] > div:first-child { padding-top: 0 !important; }
</style>
""", unsafe_allow_html=True)

# ── Session State ──────────────────────────────────────────────────────────
def init_state():
    for k, v in [
        ("username", None), ("page", "home"), ("auth_tab", "login"),
        ("selected_bet", None), ("selected_profile", None),
        ("toast", None), ("show_onboarding", False),
    ]:
        if k not in st.session_state:
            st.session_state[k] = v

def nav(page: str, bet_id=None, profile=None):
    st.session_state.page             = page
    st.session_state.selected_bet     = bet_id
    st.session_state.selected_profile = profile
    st.rerun()

def set_toast(kind: str, msg: str):
    st.session_state.toast = (kind, msg)

def show_toast():
    if st.session_state.toast:
        kind, msg = st.session_state.toast
        css = {"success":"notice-success","warn":"notice-warn",
               "error":"notice-error","info":"notice-info"}.get(kind,"notice-info")
        st.markdown(f'<div class="notice {css}">{msg}</div>', unsafe_allow_html=True)
        st.session_state.toast = None

# ── Shared Components ──────────────────────────────────────────────────────
def render_badges(username: str, compact=False):
    badges    = get_user_badges(username)
    all_achvs = {a["id"]: a for a in get_all_achievements()}
    if not badges:
        if not compact:
            st.markdown('<div style="color:#2a4060;font-size:0.82rem;">No badges yet.</div>',
                        unsafe_allow_html=True)
        return
    html = ""
    for b in badges:
        achv  = all_achvs.get(b["achievement_id"], {})
        style = BADGE_STYLES.get(b["achievement_id"], "badge-earned")
        html += f'<span class="badge {style}">{achv.get("name","Badge")}</span>'
    st.markdown(html, unsafe_allow_html=True)

def render_bet_card(bet: dict, show_btn=False):
    entries = get_entries(bet["id"])
    pot     = pot_total(entries)

    card_class = {
        "open":   "card card-live",
        "voting": "card card-voting",
        "closed": "card card-closed",
    }.get(bet["status"], "card")

    status_html = {
        "open":   '<span class="pill pill-open">Live</span>',
        "voting": '<span class="pill pill-voting">Voting</span>',
        "closed": '<span class="pill pill-closed">Resolved</span>',
    }.get(bet["status"], "")

    link  = bet.get("stream_link","")
    name  = bet.get("vtuber_name","")
    name_html = (f'<a href="{link}" target="_blank" class="stream-link">{name}</a>'
                 if link else f'<span style="color:#4499ff">{name}</span>')

    game      = bet.get("game_or_activity","")
    game_html = f'<div class="bet-game">{game}</div>' if game else ""
    opts_str  = "  /  ".join(bet["options"][:2])

    st.markdown(f"""
    <div class="{card_class}">
        <div class="vtag">{name_html}&nbsp;&nbsp;·&nbsp;&nbsp;{bet.get('category','')}</div>
        <div class="bet-title">{bet['title']}</div>
        {game_html}
        <div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap;margin-top:4px;">
            {status_html}
            <span class="pot">{pot:,} V-Coins</span>
            <span style="font-size:0.73rem;color:#2a3a55;">{opts_str}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if show_btn:
        if st.button("View", key=f"view_{bet['id']}"):
            nav("bet_detail", bet_id=bet["id"])

# ── Onboarding ─────────────────────────────────────────────────────────────
def show_onboarding_popup():
    if not st.session_state.get("show_onboarding"):
        return

    # Use st.dialog-style layout — centered column, no CSS overlay so button is clickable
    st.markdown("""
    <style>
    .onboarding-wrap {
        background: #0b0f1e;
        border: 1px solid #1e3060;
        border-radius: 16px;
        padding: 28px 32px;
        margin: 0 auto 24px auto;
        max-width: 560px;
    }
    </style>
    """, unsafe_allow_html=True)

    _, mid, _ = st.columns([1, 3, 1])
    with mid:
        st.markdown("""
        <div class="onboarding-wrap">
            <div style="text-align:center;margin-bottom:20px;">
                <div style="font-family:'Syne',sans-serif;font-size:1.8rem;font-weight:800;color:#e8f0ff;">
                    Welcome to VTuberBets! 🎲
                </div>
                <div style="color:#00aaff;font-size:0.9rem;margin-top:4px;">Here's how it works</div>
            </div>
            <div style="display:flex;flex-direction:column;gap:14px;margin-bottom:4px;">
                <div style="display:flex;gap:14px;align-items:flex-start;">
                    <span style="font-family:'JetBrains Mono',monospace;background:#001a44;color:#00aaff;padding:2px 10px;border-radius:4px;font-size:0.8rem;font-weight:700;flex-shrink:0;">01</span>
                    <div style="color:#c8d8f0;"><strong>Create account</strong> — username + password only.</div>
                </div>
                <div style="display:flex;gap:14px;align-items:flex-start;">
                    <span style="font-family:'JetBrains Mono',monospace;background:#001a44;color:#00aaff;padding:2px 10px;border-radius:4px;font-size:0.8rem;font-weight:700;flex-shrink:0;">02</span>
                    <div style="color:#c8d8f0;"><strong>Pick your role</strong> — Viewer, Streamer, or Clipper.</div>
                </div>
                <div style="display:flex;gap:14px;align-items:flex-start;">
                    <span style="font-family:'JetBrains Mono',monospace;background:#001a44;color:#00aaff;padding:2px 10px;border-radius:4px;font-size:0.8rem;font-weight:700;flex-shrink:0;">03</span>
                    <div style="color:#c8d8f0;"><strong>Browse open bets</strong> on indie VTuber streams.</div>
                </div>
                <div style="display:flex;gap:14px;align-items:flex-start;">
                    <span style="font-family:'JetBrains Mono',monospace;background:#001a44;color:#00aaff;padding:2px 10px;border-radius:4px;font-size:0.8rem;font-weight:700;flex-shrink:0;">04</span>
                    <div style="color:#c8d8f0;"><strong>Place V-Coins</strong> on what you think will happen.</div>
                </div>
                <div style="display:flex;gap:14px;align-items:flex-start;">
                    <span style="font-family:'JetBrains Mono',monospace;background:#001a44;color:#00aaff;padding:2px 10px;border-radius:4px;font-size:0.8rem;font-weight:700;flex-shrink:0;">05</span>
                    <div style="color:#c8d8f0;"><strong>Vote after the stream</strong> — 3 votes = auto-resolution.</div>
                </div>
                <div style="display:flex;gap:14px;align-items:flex-start;">
                    <span style="font-family:'JetBrains Mono',monospace;background:#001a44;color:#00aaff;padding:2px 10px;border-radius:4px;font-size:0.8rem;font-weight:700;flex-shrink:0;">06</span>
                    <div style="color:#c8d8f0;"><strong>Earn badges &amp; coins</strong> — achievements pay real V-Coins.</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("✅ Got it! Let's go", use_container_width=True, key="dismiss_onboarding"):
            st.session_state.show_onboarding = False
            st.rerun()

        st.markdown("---")
       
# ─────────────────────────────────────────────
#  SIDEBAR

# ── Sidebar ────────────────────────────────────────────────────────────────
def render_sidebar():
    username = st.session_state.username
    if not username:
        return
    user = get_user(username)
    if not user:
        return

    title_item = get_equipped(username, "title")

    with st.sidebar:
        st.markdown("""
        <div style="padding:12px 0 18px;">
            <div style="font-family:'Syne',sans-serif;font-size:1.2rem;
                        font-weight:800;color:#e8f0ff;">VTuberBets</div>
            <div style="font-family:'JetBrains Mono',monospace;font-size:0.6rem;
                        color:#0066ff;letter-spacing:0.1em;margin-top:2px;">
                PREDICTION PLATFORM
            </div>
        </div>
        """, unsafe_allow_html=True)

        title_html = (f'<div class="user-title">{title_item["value"]}</div>'
                      if title_item else "")
        role  = user.get("role","")
        r_css = {"Viewer":"role-watcher","Streamer":"role-streamer",
                 "Clipper":"role-clipper"}.get(role,"role-watcher")
        role_html = (f'<span class="profile-role {r_css}" style="margin-top:8px;display:inline-block;">{role}</span>'
                     if role else "")
        coins_fmt = f"{user['coins']:,}"

        role_color = {"Viewer":"#00aaff","Streamer":"#cc44ff","Clipper":"#00ee88"}.get(role,"#00aaff")
        role_bg    = {"Viewer":"#001a2e","Streamer":"#1a0028","Clipper":"#001a0d"}.get(role,"#001a2e")
        title_part = f'<div style="font-size:0.7rem;color:#4499ff;font-family:JetBrains Mono,monospace;margin-bottom:2px;">{title_item["value"]}</div>' if title_item else ""
        role_part  = f'<div style="margin-top:8px;display:inline-block;background:{role_bg};color:{role_color};border:1px solid {role_color}44;border-radius:4px;padding:2px 10px;font-size:0.7rem;font-weight:700;letter-spacing:0.08em;">{role}</div>' if role else ""
        coins_fmt  = f"{user['coins']:,}"
        st.markdown(
            f'''<div style="background:linear-gradient(160deg,#0c1428,#091020);border:1px solid #1a3060;border-radius:12px;padding:16px 18px;text-align:center;margin-bottom:10px;">
{title_part}
<div style="font-size:0.68rem;color:#2a4a7a;text-transform:uppercase;letter-spacing:0.12em;margin-bottom:4px;font-family:JetBrains Mono,monospace;">{username}</div>
<div style="font-family:Syne,sans-serif;font-size:2rem;font-weight:800;background:linear-gradient(45deg,#44ddff,#aa00ff,#00aaff,#0066ff);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">{coins_fmt}</div>
<div style="font-size:0.68rem;color:#1e3060;margin-top:2px;font-family:JetBrains Mono,monospace;letter-spacing:0.1em;">V-COINS</div>
{role_part}
</div>''',
            unsafe_allow_html=True
        )

        if st.button("Claim Daily Bonus  +250", use_container_width=True):
            ok, msg = claim_daily_bonus(username)
            set_toast("success" if ok else "warn", msg)
            st.rerun()

        st.markdown("---")

        pages = [
            ("Home",          "home"),
            ("All Bets",      "bets"),
            ("Create Bet",    "create_bet"),
            ("Achievements",  "achievements"),
            ("Shop",          "shop"),
            ("Leaderboard",   "leaderboard"),
            ("My Profile",    "my_profile"),
            ("How It Works",  "how_it_works"),
        ]
        for label, key in pages:
            if st.button(label, key=f"nav_{key}", use_container_width=True):
                nav(key)

        st.markdown("---")
        c1, c2 = st.columns(2)
        with c1:
            st.metric("Correct", user.get("bets_correct", 0))
        with c2:
            st.metric("Placed",  user.get("bets_placed",  0))

        st.markdown("---")
        if st.button("Log out", use_container_width=True):
            st.session_state.username = None
            st.session_state.page     = "home"
            st.rerun()

# ─────────────────────────────────────────────
#  HOME PAGE
