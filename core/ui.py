"""
core/ui.py
Shared UI layer for the entire app.
Import only what you need from here.
"""

import streamlit as st
from core.config import ROLE_CSS, ROLE_COLOR, BADGE_STYLES

# Lazy DB import to avoid circular imports
def _get_db():
    from database import (
        get_user, claim_daily_bonus, get_user_badges,
        get_all_achievements, get_equipped, pot_total
    )
    return get_user, claim_daily_bonus, get_user_badges, get_all_achievements, get_equipped, pot_total


# ══════════════════════════════════════════════════════════════════════════════
# STYLES
# ══════════════════════════════════════════════════════════════════════════════
ddef inject_styles():
    """Inject all global VTuberBets styling - brighter & more neon."""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800;900&family=JetBrains+Mono:wght@400;500;700&family=DM+Sans:wght@300;400;500;600&display=swap');

    *, *::before, *::after { box-sizing: border-box; }

    html, body, [data-testid="stAppViewContainer"] {
        background: #05080f !important;
        color: #e8f0ff !important;
        font-family: 'DM Sans', sans-serif;
    }
    /* Stronger neon background glow */
    [data-testid="stAppViewContainer"]::before {
        content: '';
        position: fixed; inset: 0; z-index: 0;
        background:
            radial-gradient(ellipse 80% 50% at 20% 20%, rgba(0,212,255,0.18) 0%, transparent 60%),
            radial-gradient(ellipse 60% 40% at 80% 80%, rgba(170,0,255,0.15) 0%, transparent 60%);
        animation: mesh-drift 12s ease-in-out infinite alternate;
        pointer-events: none;
    }
    @keyframes mesh-drift {
        0%   { opacity: 1; }
        100% { opacity: 0.75; }
    }
    /* Typography - brighter */
    h1, h2, h3, .landing-logo, .basics-title {
        color: #ffffff !important;
    }
    .landing-tagline {
        color: #c8f0ff !important;
    }
    /* Basics box & cards - much more vibrant */
    .basics-block, .card {
        border-color: #00eeff88 !important;
        box-shadow: 0 0 30px rgba(0, 238, 255, 0.25) !important;
    }
    .basics-label, .stat-val {
        color: #00eeff !important;
    }
    /* Buttons pop more */
    .stButton > button {
        background: linear-gradient(135deg, #00aaff, #00d4ff, #8800ff) !important;
        color: #ffffff !important;
        box-shadow: 0 0 25px rgba(0, 212, 255, 0.6) !important;
    }
    .stButton > button:hover {
        box-shadow: 0 0 40px rgba(0, 212, 255, 0.8) !important;
    }
    /* Pills and accents */
    .pill-open   { color: #00ff99; border-color: #00ff99; }
    .pill-voting { color: #ffdd44; border-color: #ffdd44; }

    /* General brighter links and text */
    a, .stream-link, .basics-body {
        color: #a0e0ff !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════
def init_state():
    defaults = [
        ("username", None),
        ("page", "home"),
        ("selected_bet", None),
        ("toast", None),
        ("show_onboarding", False),
    ]
    for key, default in defaults:
        if key not in st.session_state:
            st.session_state[key] = default


# ══════════════════════════════════════════════════════════════════════════════
# TOASTS
# ══════════════════════════════════════════════════════════════════════════════
def set_toast(kind: str, msg: str):
    st.session_state.toast = (kind, msg)

def show_toast():
    if not st.session_state.toast:
        return
    kind, msg = st.session_state.toast
    css = {"success": "notice-success", "error": "notice-error", "warn": "notice-warn"}.get(kind, "notice")
    st.markdown(f'<div class="notice {css}">{msg}</div>', unsafe_allow_html=True)
    st.session_state.toast = None


# ══════════════════════════════════════════════════════════════════════════════
# NAVIGATION
# ══════════════════════════════════════════════════════════════════════════════
def nav(page: str, bet_id=None):
    st.session_state.page = page
    if bet_id is not None:
        st.session_state.selected_bet = bet_id
    st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR (when logged in)
# ══════════════════════════════════════════════════════════════════════════════
def render_sidebar():
    if not st.session_state.username:
        return

    get_user, claim_daily_bonus, _, _, _, _ = _get_db()
    user = get_user(st.session_state.username)
    if not user:
        return

    with st.sidebar:
        st.markdown(f"""
        <div style="padding:12px 0 20px;">
            <div style="font-family:'Syne',sans-serif;font-size:1.35rem;font-weight:800;color:#e8f0ff;">
                VTuberBets
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Wallet
        st.markdown(f"""
        <div style="background:#0a0f1f;border:1px solid #1a2a44;border-radius:12px;padding:16px;text-align:center;margin-bottom:16px;">
            <div style="font-size:0.75rem;color:#2a4a7a;">{st.session_state.username}</div>
            <div style="font-family:'Syne',sans-serif;font-size:2.1rem;font-weight:800;color:#00d4ff;">
                {user['coins']:,}
            </div>
            <div style="font-size:0.7rem;color:#1e3060;">V-COINS</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Claim Daily Bonus (+250)", use_container_width=True):
            ok, msg = claim_daily_bonus(st.session_state.username)
            set_toast("success" if ok else "warn", msg)
            st.rerun()

        st.markdown("---")

        # Navigation
        pages = [
            ("Home", "home"),
            ("Bets", "bets"),
            ("Create Bet", "create_bet"),
            ("Clip Hub", "clips"),
            ("Achievements", "achievements"),
            ("Shop", "shop"),
            ("Leaderboard", "leaderboard"),
            ("My Profile", "my_profile"),
        ]
        for label, key in pages:
            if st.button(label, key=f"nav_{key}", use_container_width=True):
                nav(key)

        st.markdown("---")

        if st.button("Log out", use_container_width=True):
            st.session_state.username = None
            st.session_state.page = "home"
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# ONBOARDING
# ══════════════════════════════════════════════════════════════════════════════
def show_onboarding_popup():
    if not st.session_state.get("show_onboarding"):
        return

    _, mid, _ = st.columns([1, 3, 1])
    with mid:
        st.markdown("Welcome to VTuberBets!")
        if st.button("Got it! Let's go", use_container_width=True):
            st.session_state.show_onboarding = False
            st.rerun()
