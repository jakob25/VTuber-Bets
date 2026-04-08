"""
pages.py
All page render functions — one per route.
"""
import streamlit as st
from database import (
    get_user, update_user, get_bets, get_bet, get_entries, get_votes,
    user_entry, user_vote, place_entry, cast_vote, create_bet,
    close_bet_for_voting, resolve_bet, check_duplicate, check_fallback_resolutions,
    get_all_achievements, get_user_badges, get_shop_items, owns_item,
    get_equipped, purchase_item, equip_item, pot_total,
    leaderboard_rich, leaderboard_accurate, leaderboard_losers,
    login_user, register_user, needs_role_selection, set_user_role,
    CATEGORIES, MIN_VOTES,
    # Clip functions
    get_clips, award_weekly_clip_rewards
)
from ui import nav, set_toast, show_toast, render_badges, render_bet_card, render_clip_card, render_clip_submit_form

# ── CLIPS PAGE (100% separate — no betting integration) ─────────────────────
def page_clips():
    show_toast()
    st.markdown("## Clip Hub")
    st.markdown('<div style="color:#334466;font-size:0.85rem;margin-bottom:20px;">Community-submitted clips of indie VTubers. Upvote your favorites — top 3 each week win V-Coins.</div>',
                unsafe_allow_html=True)

    from database import get_clips, award_weekly_clip_rewards
    clips = get_clips(sort=st.session_state.get("clip_sort", "top"))

    col1, col2 = st.columns([3,1])
    with col1:
        sort_mode = st.radio("Sort", ["Top this week", "Newest"], horizontal=True, key="clip_sort_radio")
        st.session_state.clip_sort = "top" if "Top" in sort_mode else "newest"
    with col2:
        if st.button("🏆 Award this week’s top clips", use_container_width=True):
            count = award_weekly_clip_rewards()
            set_toast("success", f"Awarded V-Coins to top {count} clips!")
            st.rerun()

    for clip in clips:
        render_clip_card(clip)

    st.markdown("---")
    st.markdown("### Submit a new clip")
    render_clip_submit_form()
