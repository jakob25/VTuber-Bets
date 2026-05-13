"""
vtuber_profile_pages.py
──────────────────────────────────────────────────────────────────────
VTuber profile creation form + profile view page.

Add to pages.py imports and wire into your routes dict:
  from vtuber_profile_pages import page_create_vtuber_profile, page_vtuber_profile

routes = {
    ...
    "create_vtuber_profile": page_create_vtuber_profile,
    "vtuber_profile":        page_vtuber_profile,
    ...
}
──────────────────────────────────────────────────────────────────────
"""
import streamlit as st
from database import get_user, db
from vtuber_profiles_db import (
    create_vtuber_profile, get_profile_by_id, get_profile_by_slug,
    get_profiles_by_user, get_canonical_tags,
    upvote_profile, has_upvoted_profile, get_tag_scores,
    update_vtuber_profile, generate_claim_token, claim_profile,
)

# ── Helpers ────────────────────────────────────────────────────────────────

def _nav(page, **kwargs):
    st.session_state.page = page
    for k, v in kwargs.items():
        st.session_state[k] = v
    st.rerun()

def _toast(kind, msg):
    st.session_state.toast = (kind, msg)

def _show_toast():
    if not st.session_state.get("toast"):
        return
    kind, msg = st.session_state.toast
    css = {"success": "notice-success", "error": "notice-error", "warn": "notice-warn"}.get(kind, "")
    st.markdown(f'<div class="notice {css}">{msg}</div>', unsafe_allow_html=True)
    st.session_state.toast = None

# Size ordering for display
SIZE_OPTIONS = ["Under 100", "100–500", "500–2K", "2K–10K", "10K+"]
STREAM_LENGTH_OPTIONS = ["Under 1 hour", "1–2 hours", "2–4 hours", "4+ hours", "Varies"]
TIMEZONE_OPTIONS = [
    "US/Eastern", "US/Central", "US/Mountain", "US/Pacific",
    "Europe/London", "Europe/Central", "Asia/Tokyo", "Asia/Seoul",
    "Australia/Sydney", "Other / Irregular",
]

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: CREATE VTUBER PROFILE
# ══════════════════════════════════════════════════════════════════════════════

def page_create_vtuber_profile():
    _show_toast()
    username = st.session_state.username

    st.markdown("""
    <div style="margin-bottom:8px;">
        <div style="font-family:'Space Mono',monospace;font-size:0.6rem;
                    letter-spacing:0.25em;text-transform:uppercase;color:#7a6028;
                    margin-bottom:6px;">VTVault // New Entry</div>
        <div style="font-family:'Bebas Neue',sans-serif;font-size:2.6rem;
                    color:#c8a84b;letter-spacing:0.03em;line-height:1;">
            Add a VTuber to the Vault
        </div>
        <div style="font-size:0.9rem;color:#6a7a9a;font-style:italic;
                    margin-top:8px;max-width:560px;line-height:1.6;">
            Anyone can submit a profile for an indie VTuber they love.
            The more detail you add, the better the discovery features work —
            map placement, Find My Oshi, everything.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Load canonical tags ────────────────────────────────────────────────
    all_vibe_tags    = [t["tag"] for t in get_canonical_tags("vibe")]
    all_content_tags = [t["tag"] for t in get_canonical_tags("content")]
    all_clusters     = [t["tag"] for t in get_canonical_tags("cluster")]

    # ── FORM ──────────────────────────────────────────────────────────────
    with st.form("create_vtuber_profile_form", clear_on_submit=False):

        # ── Section 1: Identity ───────────────────────────────────────────
        st.markdown(_section_header("01", "Identity", "Who is this VTuber?"))

        col_a, col_b = st.columns([2, 1])
        with col_a:
            display_name = st.text_input(
                "Display Name *",
                placeholder="e.g. Chibidoki, Filian, NemuVT",
                help="Their VTuber name as they go by it."
            )
        with col_b:
            language = st.selectbox("Primary Language", ["English", "Japanese", "Korean",
                                                          "Spanish", "Portuguese", "Other"])

        short_bio = st.text_input(
            "One-liner bio *",
            placeholder="e.g. Chaotic gremlin who loses her mind at puzzle games",
            max_chars=120,
            help="This shows on cards and search results. Make it snappy."
        )

        full_bio = st.text_area(
            "Full bio",
            placeholder="Tell the community more about their content, personality, and why you think they deserve to be discovered...",
            max_chars=800,
            height=100,
        )

        lore = st.text_area(
            "Lore / Character backstory",
            placeholder="Optional. Any in-universe lore, character concept, or world-building details.",
            max_chars=500,
            height=80,
        )

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        # ── Section 2: Links ──────────────────────────────────────────────
        st.markdown(_section_header("02", "Links", "Where can people find them?"))

        col1, col2 = st.columns(2)
        with col1:
            twitch_url  = st.text_input("Twitch", placeholder="https://twitch.tv/...")
            youtube_url = st.text_input("YouTube", placeholder="https://youtube.com/@...")
        with col2:
            twitter_url = st.text_input("Twitter / X", placeholder="https://twitter.com/...")
            tiktok_url  = st.text_input("TikTok", placeholder="https://tiktok.com/@...")

        avatar_url = st.text_input(
            "Avatar image URL",
            placeholder="Direct link to a PNG/JPG of their avatar (optional)",
            help="Must be a direct image URL ending in .png/.jpg/.webp"
        )

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        # ── Section 3: Discovery Tags ──────────────────────────────────────
        st.markdown(_section_header("03", "Discovery Tags",
                    "This is what powers the map, Find My Oshi, and future features"))

        st.markdown("""
        <div style="font-size:0.8rem;color:#4a5a7a;font-style:italic;
                    margin-bottom:16px;line-height:1.6;">
            Pick everything that fits. More tags = better discovery matches.
            The community can add/validate tags later too.
        </div>
        """, unsafe_allow_html=True)

        selected_vibe_tags = st.multiselect(
            "Vibe tags — what does watching them FEEL like?",
            options=all_vibe_tags,
            max_selections=6,
            help="Pick up to 6. These drive the constellation clusters."
        )

        selected_content_tags = st.multiselect(
            "Content tags — what do they actually stream?",
            options=all_content_tags,
            max_selections=8,
        )

        selected_interest_tags = st.multiselect(
            "Interested in making — things they've expressed wanting to try",
            options=all_content_tags,
            max_selections=4,
            help="Different from what they currently make. Optional."
        )

        primary_cluster = st.selectbox(
            "Primary constellation cluster *",
            options=[""] + all_clusters,
            help="Their main 'neighborhood' on the constellation map. Pick the best fit."
        )

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        # ── Section 4: Personality Axes ───────────────────────────────────
        st.markdown(_section_header("04", "Personality",
                    "Used by Find My Oshi — rate their streams on these scales"))

        col_e, col_c, col_l = st.columns(3)
        with col_e:
            st.markdown(_axis_label("Energy Level", "1 = ASMR chill", "5 = absolute chaos"))
            energy_level = st.slider("", 1, 5, 3, key="energy_slider",
                                     label_visibility="collapsed")
            st.markdown(_axis_display(energy_level,
                ["💤 Very Chill", "😌 Relaxed", "😄 Medium", "🔥 Energetic", "💥 Pure Chaos"]))

        with col_c:
            st.markdown(_axis_label("Chat Focus", "1 = focused on content", "5 = pure zatsudan"))
            chat_interaction = st.slider("", 1, 5, 3, key="chat_slider",
                                          label_visibility="collapsed")
            st.markdown(_axis_display(chat_interaction,
                ["📺 Content Only", "🎮 Mostly Game", "⚖️ Balanced", "💬 Chat-Heavy", "🗣️ Full Yap"]))

        with col_l:
            st.markdown(_axis_label("Lore Depth", "1 = no lore", "5 = full universe"))
            lore_depth = st.slider("", 1, 5, 1, key="lore_slider",
                                    label_visibility="collapsed")
            st.markdown(_axis_display(lore_depth,
                ["👤 No Lore", "📝 Light Lore", "📖 Some Story", "🏰 Rich Lore", "🌌 Full Universe"]))

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        # ── Section 5: Stream Info ─────────────────────────────────────────
        st.markdown(_section_header("05", "Stream Info", "Helps fans find streams that fit their schedule"))

        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            approx_size = st.selectbox("Approx. audience size",
                                        ["Unknown"] + SIZE_OPTIONS)
        with col_s2:
            avg_stream_length = st.selectbox("Typical stream length",
                                              ["Unknown"] + STREAM_LENGTH_OPTIONS)
        with col_s3:
            timezone = st.selectbox("Timezone (approx.)",
                                     ["Unknown"] + TIMEZONE_OPTIONS)

        typical_schedule = st.text_input(
            "Typical schedule",
            placeholder="e.g. Weekends + random weeknights, sporadic, hiatus-prone...",
            max_chars=120,
        )

        adult_content = st.checkbox("18+ content (mature themes, NSFW-adjacent)")
        is_indie      = st.checkbox("Indie / Independent (not a major agency VTuber)", value=True)

        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

        # ── Submit ────────────────────────────────────────────────────────
        submitted = st.form_submit_button(
            "Add to the Vault",
            use_container_width=True,
        )

        if submitted:
            # Validate
            errors = []
            if not display_name.strip():
                errors.append("Display name is required.")
            if not short_bio.strip():
                errors.append("One-liner bio is required.")
            if not primary_cluster:
                errors.append("Please select a primary constellation cluster.")
            if not selected_vibe_tags:
                errors.append("Select at least one vibe tag.")

            if errors:
                _toast("error", errors[0])
                st.rerun()
            else:
                ok, result = create_vtuber_profile(
                    display_name=display_name,
                    created_by=username,
                    twitch_url=twitch_url,
                    youtube_url=youtube_url,
                    twitter_url=twitter_url,
                    tiktok_url=tiktok_url,
                    avatar_url=avatar_url,
                    short_bio=short_bio,
                    full_bio=full_bio,
                    lore=lore,
                    vibe_tags=selected_vibe_tags,
                    content_tags=selected_content_tags,
                    interest_tags=selected_interest_tags,
                    primary_cluster=primary_cluster,
                    timezone=timezone if timezone != "Unknown" else "",
                    typical_schedule=typical_schedule,
                    avg_stream_length=avg_stream_length if avg_stream_length != "Unknown" else "",
                    language=language,
                    energy_level=energy_level,
                    chat_interaction=chat_interaction,
                    lore_depth=lore_depth,
                    adult_content=adult_content,
                    approx_size=approx_size if approx_size != "Unknown" else "",
                    is_indie=is_indie,
                )
                if ok:
                    st.session_state["new_profile_id"] = result
                    _toast("success", f"'{display_name}' is now in the Vault!")
                    _nav("vtuber_profile", selected_profile_id=result)
                else:
                    _toast("error", result)
                    st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: VIEW VTUBER PROFILE
# ══════════════════════════════════════════════════════════════════════════════

def page_vtuber_profile():
    _show_toast()
    username   = st.session_state.username
    profile_id = st.session_state.get("selected_profile_id")

    profile = get_profile_by_id(profile_id) if profile_id else None
    if not profile:
        st.error("Profile not found.")
        if st.button("Browse profiles"):
            _nav("discover")
        return

    # ── Back button ────────────────────────────────────────────────────────
    if st.button("← Back"):
        _nav("discover")

    # ── Header ────────────────────────────────────────────────────────────
    is_claimed = profile.get("is_claimed", False)
    is_mine    = (profile.get("created_by") == username or
                  profile.get("claimed_by") == username)

    # Avatar
    if profile.get("avatar_url"):
        col_av, col_hd = st.columns([1, 5])
        with col_av:
            st.image(profile["avatar_url"], width=100)
        with col_hd:
            _render_profile_header(profile, is_claimed)
    else:
        _render_profile_header(profile, is_claimed)

    # ── Community upvote + claim strip ────────────────────────────────────
    voted = has_upvoted_profile(profile_id, username)
    col_v, col_c, col_e = st.columns([2, 2, 3])
    with col_v:
        upvote_label = f"{'★ Endorsed' if voted else '☆ Endorse'} ({profile.get('upvote_count', 0)})"
        if st.button(upvote_label, use_container_width=True):
            _, msg = upvote_profile(profile_id, username)
            _toast("success", msg)
            st.rerun()
    with col_c:
        if not is_claimed:
            if st.button("Is this you? Claim this profile", use_container_width=True):
                token = generate_claim_token(profile_id)
                st.info(f"Your claim token: **{token}** — Add this to your Twitter/Twitch bio or stream title, then confirm below.")
                confirm_token = st.text_input("Enter token to confirm claim:")
                if st.button("Confirm Claim"):
                    ok, msg = claim_profile(profile_id, username, confirm_token)
                    _toast("success" if ok else "error", msg)
                    st.rerun()
        else:
            st.markdown(f'<div style="font-family:\'Space Mono\',monospace;font-size:0.6rem;'
                        f'color:#5dbb7a;letter-spacing:0.15em;padding-top:12px;">✓ CLAIMED PROFILE</div>',
                        unsafe_allow_html=True)
    with col_e:
        if is_mine:
            if st.button("Edit Profile", use_container_width=True):
                st.session_state["editing_profile_id"] = profile_id
                _nav("edit_vtuber_profile")

    st.markdown("---")

    # ── Main content ──────────────────────────────────────────────────────
    col_left, col_right = st.columns([3, 2])

    with col_left:
        # Bio
        if profile.get("full_bio"):
            st.markdown("### About")
            st.markdown(f'<div style="font-size:0.95rem;color:#c8d8f0;line-height:1.7;'
                        f'font-style:italic;">{profile["full_bio"]}</div>',
                        unsafe_allow_html=True)
            st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

        # Lore
        if profile.get("lore"):
            with st.expander("📖 Lore & Character"):
                st.markdown(f'<div style="font-size:0.9rem;color:#8899bb;line-height:1.7;">'
                            f'{profile["lore"]}</div>', unsafe_allow_html=True)

        # Discovery tags
        st.markdown("### Vibe Tags")
        _render_tag_cloud(profile.get("vibe_tags") or [], "vibe", "#c8a84b")

        if profile.get("content_tags"):
            st.markdown("### Content")
            _render_tag_cloud(profile.get("content_tags") or [], "content", "#d4762a")

        if profile.get("interest_tags"):
            st.markdown("### Interested in Making")
            _render_tag_cloud(profile.get("interest_tags") or [], "interest", "#5a6a8a")

        # Personality axes
        st.markdown("### Stream Personality")
        _render_personality_bars(profile)

    with col_right:
        # Links
        st.markdown("### Find Them")
        _render_links(profile)

        # Stream info
        st.markdown("### Stream Info")
        info_items = [
            ("Cluster", profile.get("primary_cluster")),
            ("Audience", profile.get("approx_size")),
            ("Typical Length", profile.get("avg_stream_length")),
            ("Schedule", profile.get("typical_schedule")),
            ("Timezone", profile.get("timezone")),
            ("Language", profile.get("language")),
        ]
        for label, val in info_items:
            if val:
                st.markdown(f"""
                <div style="display:flex;justify-content:space-between;
                            border-bottom:1px solid #1a2540;padding:8px 0;
                            font-size:0.85rem;">
                    <span style="color:#334466;font-family:'Space Mono',monospace;
                                 font-size:0.7rem;letter-spacing:0.1em;
                                 text-transform:uppercase;">{label}</span>
                    <span style="color:#c8d8f0;">{val}</span>
                </div>
                """, unsafe_allow_html=True)

        # Stats
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        st.markdown("### Activity")
        c1, c2, c3 = st.columns(3)
        c1.metric("Clips", profile.get("clip_count", 0))
        c2.metric("Bets", profile.get("bet_count", 0))
        c3.metric("Endorsements", profile.get("upvote_count", 0))

        # Submitted by
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="font-family:'Space Mono',monospace;font-size:0.55rem;
                    color:#2a3550;letter-spacing:0.1em;text-transform:uppercase;">
            Submitted by {profile.get("created_by","unknown")}<br>
            {profile.get("created_at","")[:10]}
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: DISCOVER (browse all profiles)
# ══════════════════════════════════════════════════════════════════════════════

def page_discover():
    _show_toast()

    st.markdown("""
    <div style="margin-bottom:24px;">
        <div style="font-family:'Space Mono',monospace;font-size:0.6rem;
                    letter-spacing:0.25em;text-transform:uppercase;color:#7a6028;
                    margin-bottom:6px;">VTVault // Discovery</div>
        <div style="font-family:'Bebas Neue',sans-serif;font-size:2.6rem;
                    color:#c8a84b;letter-spacing:0.03em;line-height:1;">
            The Archive
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Filters ────────────────────────────────────────────────────────────
    all_clusters  = [t["tag"] for t in get_canonical_tags("cluster")]
    all_vibe_tags = [t["tag"] for t in get_canonical_tags("vibe")]

    col_f1, col_f2, col_f3, col_f4 = st.columns([2, 2, 1, 1])
    with col_f1:
        search_q = st.text_input("Search by name", placeholder="Search VTubers...",
                                  label_visibility="collapsed")
    with col_f2:
        filter_cluster = st.selectbox("Cluster", ["All clusters"] + all_clusters,
                                       label_visibility="collapsed")
    with col_f3:
        filter_energy = st.selectbox("Energy", ["Any", "Chill (1-2)", "Medium (3)", "Hype (4-5)"],
                                      label_visibility="collapsed")
    with col_f4:
        if st.button("+ Add VTuber", use_container_width=True):
            _nav("create_vtuber_profile")

    # Build filter params
    from vtuber_profiles_db import get_profiles_for_discovery, search_profiles
    energy_map = {
        "Chill (1-2)": (1, 2),
        "Medium (3)":  (3, 3),
        "Hype (4-5)":  (4, 5),
    }
    e_range = energy_map.get(filter_energy, (None, None))

    if search_q.strip():
        profiles = search_profiles(search_q)
    else:
        profiles = get_profiles_for_discovery(
            cluster=None if filter_cluster == "All clusters" else filter_cluster,
            energy_min=e_range[0],
            energy_max=e_range[1],
        )

    st.markdown(f'<div style="font-family:\'Space Mono\',monospace;font-size:0.65rem;'
                f'color:#2a3550;letter-spacing:0.1em;margin-bottom:20px;">'
                f'{len(profiles)} entries in the vault</div>', unsafe_allow_html=True)

    if not profiles:
        st.markdown("""
        <div style="text-align:center;padding:60px 0;color:#2a3550;">
            <div style="font-family:'Bebas Neue',sans-serif;font-size:2rem;
                        color:#c8a84b;margin-bottom:8px;">The Vault is Empty</div>
            <div style="font-size:0.9rem;font-style:italic;">
                Be the first to add an indie VTuber.
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    # ── Profile grid ──────────────────────────────────────────────────────
    cols = st.columns(3)
    for i, profile in enumerate(profiles):
        with cols[i % 3]:
            _render_profile_card(profile)


# ── Component helpers ──────────────────────────────────────────────────────

def _section_header(num: str, title: str, sub: str) -> str:
    return f"""
    <div style="display:flex;align-items:baseline;gap:16px;
                border-top:1px solid #1a2540;padding-top:20px;
                margin:24px 0 16px;">
        <span style="font-family:'Bebas Neue',sans-serif;font-size:2rem;
                     color:#3a3020;line-height:1;">{num}</span>
        <div>
            <div style="font-family:'Bebas Neue',sans-serif;font-size:1.2rem;
                        color:#c8a84b;letter-spacing:0.04em;">{title}</div>
            <div style="font-size:0.78rem;color:#334466;font-style:italic;">{sub}</div>
        </div>
    </div>
    """

def _axis_label(title: str, low: str, high: str) -> str:
    return f"""
    <div style="margin-bottom:6px;">
        <div style="font-family:'Space Mono',monospace;font-size:0.65rem;
                    color:#c8a84b;letter-spacing:0.15em;text-transform:uppercase;
                    margin-bottom:2px;">{title}</div>
        <div style="display:flex;justify-content:space-between;
                    font-size:0.65rem;color:#334466;font-style:italic;">
            <span>{low}</span><span>{high}</span>
        </div>
    </div>
    """

def _axis_display(value: int, labels: list) -> str:
    label = labels[value - 1] if 1 <= value <= len(labels) else ""
    return f"""
    <div style="font-family:'Space Mono',monospace;font-size:0.65rem;
                color:#e8c96a;text-align:center;margin-top:4px;">{label}</div>
    """

def _render_profile_header(profile: dict, is_claimed: bool):
    claimed_badge = ""
    if is_claimed:
        claimed_badge = '<span style="font-family:\'Space Mono\',monospace;font-size:0.55rem;color:#5dbb7a;border:1px solid #5dbb7a;padding:2px 8px;margin-left:12px;letter-spacing:0.1em;">CLAIMED</span>'

    cluster = profile.get("primary_cluster", "")
    size    = profile.get("approx_size", "")
    tags_html = ""
    for tag in (profile.get("vibe_tags") or [])[:4]:
        tags_html += f'<span style="font-family:\'Space Mono\',monospace;font-size:0.55rem;color:#7a6028;border:1px solid #3a3020;padding:2px 8px;margin-right:6px;letter-spacing:0.08em;">{tag}</span>'

    st.markdown(f"""
    <div style="margin-bottom:20px;">
        <div style="font-family:'Bebas Neue',sans-serif;font-size:2.4rem;
                    color:#c8a84b;letter-spacing:0.03em;line-height:1.1;">
            {profile['display_name']}{claimed_badge}
        </div>
        <div style="font-size:1rem;color:#8899bb;font-style:italic;
                    margin:6px 0 14px;line-height:1.4;">
            {profile.get('short_bio','')}
        </div>
        <div style="display:flex;flex-wrap:wrap;gap:4px;align-items:center;
                    margin-bottom:8px;">
            {f'<span style="font-family:\'Space Mono\',monospace;font-size:0.55rem;color:#d4762a;border:1px solid #d4762a44;padding:2px 8px;letter-spacing:0.1em;">{cluster}</span>' if cluster else ""}
            {f'<span style="font-family:\'Space Mono\',monospace;font-size:0.55rem;color:#334466;padding:2px 8px;letter-spacing:0.08em;">{size}</span>' if size else ""}
        </div>
        <div>{tags_html}</div>
    </div>
    """, unsafe_allow_html=True)


def _render_tag_cloud(tags: list, tag_type: str, color: str):
    if not tags:
        st.markdown('<div style="color:#2a3550;font-size:0.82rem;font-style:italic;">None listed</div>',
                    unsafe_allow_html=True)
        return
    tags_html = "".join(
        f'<span style="font-family:\'Space Mono\',monospace;font-size:0.65rem;'
        f'color:{color};border:1px solid {color}44;padding:4px 12px;'
        f'margin:3px;display:inline-block;letter-spacing:0.08em;">{t}</span>'
        for t in tags
    )
    st.markdown(f'<div style="margin-bottom:16px;">{tags_html}</div>', unsafe_allow_html=True)


def _render_personality_bars(profile: dict):
    axes = [
        ("Energy",      profile.get("energy_level",     3), "#c8a84b", "Chill", "Chaos"),
        ("Chat Focus",  profile.get("chat_interaction",  3), "#d4762a", "Content", "Zatsudan"),
        ("Lore Depth",  profile.get("lore_depth",        1), "#5a8abc", "None",  "Full Universe"),
    ]
    html = ""
    for label, val, color, low, high in axes:
        pct = (val / 5) * 100
        html += f"""
        <div style="margin-bottom:14px;">
            <div style="display:flex;justify-content:space-between;
                        font-family:'Space Mono',monospace;font-size:0.6rem;
                        color:#334466;margin-bottom:4px;letter-spacing:0.08em;">
                <span>{label.upper()}</span>
                <span style="color:{color};">{val}/5</span>
            </div>
            <div style="height:4px;background:#1a2540;position:relative;">
                <div style="width:{pct}%;height:100%;background:{color};
                            box-shadow:0 0 8px {color}66;"></div>
            </div>
            <div style="display:flex;justify-content:space-between;
                        font-size:0.6rem;color:#1e2a40;margin-top:2px;font-style:italic;">
                <span>{low}</span><span>{high}</span>
            </div>
        </div>
        """
    st.markdown(html, unsafe_allow_html=True)


def _render_links(profile: dict):
    links = [
        ("Twitch",    profile.get("twitch_url"),   "#9146ff"),
        ("YouTube",   profile.get("youtube_url"),  "#ff0000"),
        ("Twitter/X", profile.get("twitter_url"),  "#4499ff"),
        ("TikTok",    profile.get("tiktok_url"),   "#c8a84b"),
    ]
    has_any = False
    for label, url, color in links:
        if url and url.strip():
            has_any = True
            st.markdown(f"""
            <a href="{url}" target="_blank" style="display:block;
               font-family:'Space Mono',monospace;font-size:0.7rem;
               color:{color};text-decoration:none;letter-spacing:0.1em;
               border:1px solid {color}44;padding:8px 14px;margin-bottom:6px;
               transition:background 0.2s;"
               onmouseover="this.style.background='{color}11'"
               onmouseout="this.style.background='transparent'">
                → {label}
            </a>
            """, unsafe_allow_html=True)
    if not has_any:
        st.markdown('<div style="color:#2a3550;font-size:0.82rem;'
                    'font-style:italic;">No links added yet.</div>', unsafe_allow_html=True)


def _render_profile_card(profile: dict):
    """Compact card for grid/browse view."""
    cluster = profile.get("primary_cluster", "")
    tags    = (profile.get("vibe_tags") or [])[:2]
    tags_html = " ".join(
        f'<span style="font-family:\'Space Mono\',monospace;font-size:0.5rem;'
        f'color:#7a6028;border:1px solid #3a3020;padding:1px 6px;">{t}</span>'
        for t in tags
    )
    claimed_dot = '<span style="color:#5dbb7a;margin-left:6px;font-size:0.6rem;">●</span>' \
                  if profile.get("is_claimed") else ""

    # Avatar or placeholder
    if profile.get("avatar_url"):
        avatar_html = f'<img src="{profile["avatar_url"]}" style="width:48px;height:48px;border-radius:50%;border:1px solid #3a3020;object-fit:cover;">'
    else:
        initials = profile["display_name"][0].upper()
        avatar_html = f'<div style="width:48px;height:48px;border-radius:50%;border:1px solid #3a3020;display:flex;align-items:center;justify-content:center;background:#1a1508;font-family:\'Bebas Neue\',sans-serif;font-size:1.2rem;color:#c8a84b;">{initials}</div>'

    st.markdown(f"""
    <div style="background:#0e0b06;border:1px solid #2a2010;padding:18px;
                margin-bottom:10px;cursor:pointer;transition:border-color 0.2s;"
         onmouseover="this.style.borderColor='#c8a84b'"
         onmouseout="this.style.borderColor='#2a2010'">
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:10px;">
            {avatar_html}
            <div>
                <div style="font-family:'Bebas Neue',sans-serif;font-size:1.1rem;
                            color:#c8a84b;line-height:1;">
                    {profile['display_name']}{claimed_dot}
                </div>
                {f'<div style="font-family:\'Space Mono\',monospace;font-size:0.5rem;color:#d4762a;letter-spacing:0.1em;">{cluster}</div>' if cluster else ''}
            </div>
        </div>
        <div style="font-size:0.82rem;color:#6a7a9a;font-style:italic;
                    line-height:1.5;margin-bottom:10px;">
            {(profile.get('short_bio') or '')[:80]}{'...' if len(profile.get('short_bio') or '') > 80 else ''}
        </div>
        <div style="margin-bottom:10px;">{tags_html}</div>
        <div style="display:flex;justify-content:space-between;
                    font-family:'Space Mono',monospace;font-size:0.55rem;
                    color:#2a3040;letter-spacing:0.08em;">
            <span>☆ {profile.get('upvote_count',0)}</span>
            <span>🎬 {profile.get('clip_count',0)} clips</span>
            <span>🎲 {profile.get('bet_count',0)} bets</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("View Profile", key=f"view_{profile['id']}", use_container_width=True):
        _nav("vtuber_profile", selected_profile_id=profile["id"])
