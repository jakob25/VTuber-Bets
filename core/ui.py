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
def inject_styles():
    """Inject all global VTuberBets styling."""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800;900&family=JetBrains+Mono:wght@400;500;700&family=DM+Sans:wght@300;400;500;600&display=swap');

    * { box-sizing: border-box; }
    html, body, [data-testid="stAppViewContainer"] {
        background: #05080f !important;
        color: #c8d8f0 !important;
        font-family: 'DM Sans', sans-serif;
    }

    /* Basic clean layout */
    .main .block-container {
        padding-top: 1rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }

    /* Typography */
    h1, h2, h3 { font-family: 'Syne', sans-serif !important; }

    /* Cards */
    .card {
        background: linear-gradient(135deg, #0a0e1c, #080c18);
        border: 1px solid #131d33;
        border-radius: 12px;
        padding: 20px 24px;
        margin-bottom: 14px;
    }

    /* Toasts */
    .notice {
        border-radius: 10px; padding: 14px 18px; margin: 12px 0;
        font-size: 0.88rem; line-height: 1.6;
    }
    .notice-success { background: #001508; border: 1px solid #00ff8833; color: #00dd77; }
    .notice-error   { background: #140005; border: 1px solid #ff335544; color: #ff5577; }
    .notice-warn    { background: #150f00; border: 1px solid #ffdd0033; color: #ddaa00; }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: #060a14 !important;
        border-right: 1px solid #0d1a30 !important;
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
