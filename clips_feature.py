import streamlit as st
from database import get_clips, award_weekly_clip_rewards, upvote_clip, submit_clip

# ── Clip UI Helpers ─────────────────────────────────────────────────────
def render_clip_card(clip: dict):
    """Single clip card with upvote"""
    st.markdown(f"""
    <div class="card" style="border-left: 3px solid #00d4ff; margin-bottom: 16px;">
        <div class="vtag">{clip['vtuber_name']}</div>
        <div style="font-family:'Syne',sans-serif;font-size:1.05rem;font-weight:800;color:#ddeaff;margin-bottom:8px;">
            {clip['title']}
        </div>
        <div style="color:#4a6a99;font-size:0.85rem;margin-bottom:12px;">{clip.get('description','')}</div>
        <a href="{clip['clip_url']}" target="_blank" style="color:#00d4ff;">▶ Watch Clip</a>
        
        <div style="margin-top:12px;">
            <button 
                onclick="this.innerText = 'Upvoted!'; this.disabled=true;"
                style="background:#00ff88;color:#000;border:none;padding:6px 16px;border-radius:9999px;font-size:0.85rem;cursor:pointer;">
                👍 {clip.get('upvotes', 0)}
            </button>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_clip_submit_form():
    """Clip submission form"""
    with st.form("clip_submit_form"):
        st.markdown("### Submit a new clip")
        clip_url = st.text_input("Clip URL (Twitch / YouTube)")
        vtuber = st.text_input("VTuber name")
        title = st.text_input("Clip title")
        desc = st.text_area("Description (optional)", height=80)
        tags = st.multiselect("Tags", ["Funny", "Chaos", "Wholesome", "Rage", "Skill", "Fail", "Cute"])
        bet_id = st.number_input("Linked Bet ID (optional)", min_value=0, value=0)
        
        submitted = st.form_submit_button("Submit Clip")
        if submitted:
            if not clip_url or not vtuber or not title:
                st.error("Clip URL, VTuber name, and title are required.")
            else:
                submit_clip(clip_url, vtuber, title, desc or "", tags, st.session_state.username, bet_id)
                st.success("Clip submitted! Thank you, scout.")
                st.rerun()

# ── Main Clips Page ─────────────────────────────────────────────────────
def page_clips():
    """Full Clips page"""
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
            st.success(f"Awarded V-Coins to top {count} clips!")
            st.rerun()

    clips = get_clips(sort=sort_param)
    if not clips:
        st.info("No clips submitted yet. Be the first!")
    else:
        for clip in clips:
            render_clip_card(clip)

    st.markdown("---")
    render_clip_submit_form()
