"""
core/ui.py
VTVault — New Cyber/Gold Sci-Fi Aesthetic (matches your reference image)
"""

import streamlit as st

def inject_styles():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Space+Grotesk:wght@500;600&display=swap');

        .stApp {
            background: #0A0F1F;
            background-image: 
                linear-gradient(#1E2937 1px, transparent 1px),
                linear-gradient(90deg, #1E2937 1px, transparent 1px);
            background-size: 40px 40px;
            color: #E2E8F0;
            font-family: 'Inter', sans-serif;
        }

        /* Custom Header Bar - matches your image */
        .vtvault-header-bar {
            background: linear-gradient(90deg, #1E2937, #334155);
            border-bottom: 3px solid #F59E0B;
            padding: 12px 30px;
            margin: -20px -20px 30px -20px;
            display: flex;
            align-items: center;
            box-shadow: 0 4px 20px rgba(245, 158, 11, 0.3);
        }
        .vtvault-logo {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 2.1rem;
            font-weight: 600;
            background: linear-gradient(90deg, #67E8F9, #F59E0B);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: -2px;
        }

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            background: transparent;
            gap: 8px;
        }
        .stTabs [data-baseweb="tab"] {
            background: #1E2937;
            color: #CBD5E1;
            border-radius: 6px;
            padding: 10px 24px;
            font-weight: 600;
        }
        .stTabs [aria-selected="true"] {
            background: #F59E0B !important;
            color: #0F172A !important;
        }

        /* Polaroid Cards - much closer to reference */
        .polaroid-card {
            background: #F8FAFC;
            color: #0F172A;
            padding: 12px;
            margin: 15px 0;
            border: 12px solid #F8FAFC;
            box-shadow: 8px 10px 20px rgba(0,0,0,0.6);
            transform: rotate(-2deg);
            transition: all 0.3s ease;
            position: relative;
        }
        .polaroid-card:hover {
            transform: rotate(1deg) scale(1.03);
        }
        .polaroid-card::before {
            content: '';
            position: absolute;
            top: -8px;
            left: 30%;
            width: 40%;
            height: 20px;
            background: #F59E0B;
            opacity: 0.15;
            transform: rotate(-8deg);
            z-index: 2;
        }
        .polaroid-video {
            width: 100%;
            height: 240px;
            background: #000;
            margin-bottom: 12px;
            border: 4px solid #0F172A;
        }
        .polaroid-caption {
            font-size: 15px;
            font-weight: 600;
            color: #0F172A;
            margin-bottom: 8px;
        }
        .polaroid-tags {
            color: #67E8F9;
            font-size: 13px;
            font-weight: 500;
        }

        /* Buttons */
        .stButton > button {
            background: linear-gradient(90deg, #F59E0B, #FB923C);
            color: #0F172A;
            font-weight: 600;
            border: none;
            border-radius: 6px;
        }
        .stButton > button:hover {
            box-shadow: 0 0 15px #F59E0B;
        }

        /* Notices */
        .notice {
            padding: 16px;
            border-radius: 8px;
            margin: 12px 0;
        }
        .notice-success { background: #052E16; border-left: 6px solid #67E8F9; }
        .notice-error   { background: #3B1F1F; border-left: 6px solid #F87171; }

        /* Sidebar */
        .stSidebar {
            background-color: #1E2937 !important;
            border-right: 3px solid #F59E0B;
        }
    </style>
    """, unsafe_allow_html=True)

# Keep the rest of your helpers (init_state, toast, nav, sidebar, etc.)
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

def set_toast(kind: str, msg: str):
    st.session_state.toast = (kind, msg)

def show_toast():
    if not st.session_state.toast:
        return
    kind, msg = st.session_state.toast
    css = {"success": "notice-success", "error": "notice-error", "warn": "notice"}.get(kind, "notice")
    st.markdown(f'<div class="notice {css}">{msg}</div>', unsafe_allow_html=True)
    st.session_state.toast = None

def nav(page: str, bet_id=None):
    st.session_state.page = page
    if bet_id is not None:
        st.session_state.selected_bet = bet_id
    st.rerun()

def render_sidebar():
    # (keeping your existing sidebar logic — we'll update wallet to "SCRAPS" later)
    from database import get_user, claim_daily_bonus
    if not st.session_state.username:
        return
    user = get_user(st.session_state.username)
    if not user:
        return
    with st.sidebar:
        st.markdown("### ⚙️ VTVault")
        st.markdown(f"""
        <div style="background:#0F172A;border:2px solid #F59E0B;border-radius:8px;padding:16px;text-align:center;margin:20px 0;">
            <div style="color:#67E8F9;">{st.session_state.username}</div>
            <div style="font-size:2.2rem;font-weight:700;color:#F59E0B;">{user['coins']:,}</div>
            <div style="font-size:0.8rem;color:#CBD5E1;">SCRAPS</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Claim Daily Bonus (+250)", use_container_width=True):
            ok, msg = claim_daily_bonus(st.session_state.username)
            set_toast("success" if ok else "warn", msg)
            st.rerun()
        # ... rest of your nav buttons (Home, Bets, etc.)

def show_onboarding_popup():
    if not st.session_state.get("show_onboarding"):
        return
    _, mid, _ = st.columns([1, 3, 1])
    with mid:
        st.markdown("Welcome to **VTVault**!")
        if st.button("Got it! Let's go", use_container_width=True):
            st.session_state.show_onboarding = False
            st.rerun()
