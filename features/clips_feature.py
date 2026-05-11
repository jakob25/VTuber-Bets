import streamlit as st
from core.ui import inject_styles, set_toast, show_toast
from core.config import CATEGORIES
from database import get_clips, award_weekly_clip_rewards, upvote_clip, submit_clip


# ── All Clips Feature (exported as one variable) ───────────────────────────
clips = {
    "page": lambda: page_clips(),
}


# ── Internal Functions ─────────────────────────────────────────────────────
def render_clip_card(clip: dict):
    st.markdown(f"""
    <div class="polaroid-card">
        <div class="polaroid-video">
            <iframe width="100%" height="100%" 
                    src="{clip['clip_url']}" 
                    frameborder="0" allowfullscreen></iframe>
        </div>
        <div class="polaroid-caption">
            {clip['vtuber_name']} — {clip['title']}
        </div>
        <div class="polaroid-tags">
            {' '.join([f'#{t}' for t in clip.get('tags', [])])}
        </div>
        <div style="margin-top:8px; font-size:0.85rem; color:#666;">
            👍 {clip.get('upvotes', 0)} • by {clip.get('submitted_by', 'anonymous')}
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_clip_submit_form():
    with st.form("clip_submit_form"):
        st.markdown("### Submit a new clip")
        clip_url = st.text_input("Clip URL (Twitch / YouTube)")
        vtuber = st.text_input("VTuber name")
        title = st.text_input("Clip title")
        desc = st.text_area("Description (optional)", height=80)
        tags = st.multiselect("Tags", CATEGORIES)
        bet_id = st.number_input("Linked Bet ID (optional)", min_value=0, value=0)
        
        submitted = st.form_submit_button("Submit Clip")
        if submitted:
            if not clip_url or not vtuber or not title:
                st.error("Clip URL, VTuber name, and title are required.")
            else:
                submit_clip(clip_url, vtuber, title, desc or "", tags, st.session_state.username, bet_id)
                set_toast("success", "Clip submitted! Thank you, scout.")
                st.rerun()


def page_clips():
    inject_styles()           # ← uses core
    show_toast()

    st.markdown("## Clip Hub")
    st.markdown(
        '<div style="color:#334466;font-size:0.85rem;margin-bottom:20px;">'
        'Community-submitted clips of indie VTubers. Upvote your favorites — top 3 each week win V-Coins.'
        '</div>',
        unsafe_allow_html=True
    )

    col1, col2 = st.columns([3, 1])
    with col1:
        sort_mode = st.radio("Sort", ["Top this week", "Newest"], horizontal=True, key="clip_sort_radio")
        sort_param = "top" if "Top" in sort_mode else "newest"
    
    with col2:
        if st.button("🏆 Award this week's top clips", use_container_width=True):
            count = award_weekly_clip_rewards()
            set_toast("success", f"Awarded V-Coins to top {count} clips!")
            st.rerun()

    clips_data = get_clips(sort=sort_param)
    if not clips_data:
        st.info("No clips submitted yet. Be the first!")
    else:
        for clip in clips_data:
            render_clip_card(clip)

    st.markdown("---")
    render_clip_submit_form()
