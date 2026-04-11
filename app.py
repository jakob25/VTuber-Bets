"""
app.py
Entry point — only routing + config. Clean and tiny.
"""
import streamlit as st
from database import needs_role_selection
from pages import(
    page_auth, page_role_select,
    page_home, page_bets, page_bet_detail, page_create_bet,
    page_achievements, page_shop, page_leaderboard,
    page_my_profile, page_how_it_works,
    inject_styles, init_state, render_sidebar, show_onboarding_popup
)

st.set_page_config(
    page_title="VTuberBets",
    page_icon="🎲",
    layout="wide",
    initial_sidebar_state="expanded"
)

inject_styles()
init_state()

def main():
    if not st.session_state.username:
        page_auth()
        return

    if st.session_state.page == "role_select" or needs_role_selection(st.session_state.username):
        page_role_select()
        return

    render_sidebar()
    show_onboarding_popup()

    routes = {
        "home":         page_home,
        "bets":         page_bets,
        "clips":        page_clips,
        "bet_detail":   page_bet_detail,
        "create_bet":   page_create_bet,
        "achievements": page_achievements,
        "shop":         page_shop,
        "leaderboard":  page_leaderboard,
        "my_profile":   page_my_profile,
        "how_it_works": page_how_it_works,
    }
    routes.get(st.session_state.page, page_home)()

main()
