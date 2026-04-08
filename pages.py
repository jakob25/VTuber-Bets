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
    CATEGORIES, MIN_VOTES
)
from ui import nav, set_toast, show_toast, render_badges, render_bet_card

# ── Auth ───────────────────────────────────────────────────────────────────
def page_auth():
    # Hide sidebar on auth page
    st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none !important; }
    [data-testid="collapsedControl"] { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

    _, col, _ = st.columns([1, 2, 1])
    with col:
        # Show toast if one exists
        if st.session_state.toast:
            show_toast()

        # Logo / header
        st.markdown("""
        <div style="text-align:center;padding:32px 0 28px;">
            <div style="font-family:'JetBrains Mono',monospace;font-size:0.62rem;
                        color:#1e3a6e;letter-spacing:0.25em;text-transform:uppercase;
                        margin-bottom:14px;">PREDICTION PLATFORM</div>
            <div style="font-family:'Syne',sans-serif;font-size:3.2rem;font-weight:800;
                        color:#e8f0ff;line-height:1;margin-bottom:12px;">VTuberBets</div>
            <div style="font-family:'JetBrains Mono',monospace;font-size:0.7rem;
                        color:#0055cc;letter-spacing:0.12em;">
                INDIE VTUBER &nbsp;·&nbsp; COMMUNITY PREDICTIONS &nbsp;·&nbsp; FAKE MONEY ONLY
            </div>
        </div>
        """, unsafe_allow_html=True)

        tab_login, tab_register = st.tabs([" Login ", " Create Account "])

        with tab_login:
            st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
            l_user = st.text_input("Username", key="login_user", placeholder="Enter your username")
            l_pass = st.text_input("Password", key="login_pass", type="password", placeholder="Enter your password")
            if st.button("Login", use_container_width=True, key="btn_login"):
                if not l_user.strip():
                    set_toast("error", "Please enter your username.")
                    st.rerun()
                elif not l_pass:
                    set_toast("error", "Please enter your password.")
                    st.rerun()
                else:
                    ok, msg = login_user(l_user.strip(), l_pass)
                    if ok:
                        st.session_state.username = l_user.strip()
                        if needs_role_selection(l_user.strip()):
                            st.session_state.page = "role_select"
                        else:
                            st.session_state.page = "home"
                        st.rerun()
                    else:
                        set_toast("error", msg)
                        st.rerun()

        with tab_register:
            st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
            r_user = st.text_input("Username", key="reg_user", placeholder="2\u201324 characters, no spaces")
            r_pass = st.text_input("Password", key="reg_pass", type="password", placeholder="At least 6 characters")
            r_pass2 = st.text_input("Confirm password", key="reg_pass2", type="password", placeholder="Repeat your password")
            if st.button("Create Account", use_container_width=True, key="btn_register"):
                un = r_user.strip()
                errs = []
                if len(un) < 2: errs.append("Username must be at least 2 characters.")
                elif len(un) > 24: errs.append("Username must be 24 characters or fewer.")
                elif " " in un: errs.append("Username cannot contain spaces.")
                if len(r_pass) < 6: errs.append("Password must be at least 6 characters.")
                elif r_pass != r_pass2: errs.append("Passwords do not match.")
                if errs:
                    set_toast("error", errs[0])
                    st.rerun()
                else:
                    ok, msg = register_user(un, r_pass)
                    if ok:
                        st.session_state.username = un
                        st.session_state.page = "role_select"
                        st.session_state.show_onboarding = True
                        st.rerun()
                    else:
                        set_toast("error", msg)
                        st.rerun()

        # Stats row
        st.markdown("""
        <div style="display:flex;gap:0;margin-top:24px;
                    border:1px solid #1a2a44;border-radius:12px;overflow:hidden;">
            <div style="flex:1;padding:14px;text-align:center;border-right:1px solid #1a2a44;">
                <div style="font-family:'JetBrains Mono',monospace;font-size:1.2rem;
                            font-weight:700;color:#00aaff;">5,000</div>
                <div style="font-size:0.65rem;color:#1e3060;text-transform:uppercase;
                            letter-spacing:0.08em;margin-top:2px;">Starting Coins</div>
            </div>
            <div style="flex:1;padding:14px;text-align:center;border-right:1px solid #1a2a44;">
                <div style="font-family:'JetBrains Mono',monospace;font-size:1.2rem;
                            font-weight:700;color:#00aaff;">+250</div>
                <div style="font-size:0.65rem;color:#1e3060;text-transform:uppercase;
                            letter-spacing:0.08em;margin-top:2px;">Daily Bonus</div>
            </div>
            <div style="flex:1;padding:14px;text-align:center;">
                <div style="font-family:'JetBrains Mono',monospace;font-size:1.2rem;
                            font-weight:700;color:#00ee88;">$0</div>
                <div style="font-size:0.65rem;color:#1e3060;text-transform:uppercase;
                            letter-spacing:0.08em;margin-top:2px;">Real Money</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  ROLE SELECTION PAGE
# ─────────────────────────────────────────────
def page_role_select():
    # Also hide sidebar on role select
    st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none !important; }
    [data-testid="collapsedControl"] { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

    _, col, _ = st.columns([1, 2, 1])
    with col:
        show_toast()
        st.markdown(f"""
        <div style="text-align:center;padding:40px 0 28px;">
            <div style="font-family:'JetBrains Mono',monospace;font-size:0.62rem;
                        color:#0055cc;letter-spacing:0.2em;text-transform:uppercase;
                        margin-bottom:12px;">ALMOST READY</div>
            <div style="font-family:'Syne',sans-serif;font-size:2rem;font-weight:800;
                        color:#e8f0ff;margin-bottom:8px;">One last thing</div>
            <div style="color:#3a5580;font-size:0.9rem;line-height:1.6;">
                How do you primarily engage with indie VTubers?<br>
                <span style="color:#2a4060;font-size:0.82rem;">
                    This personalises your experience. You can change it in your profile later.
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        roles = [
            ("Viewer",   "role-watcher",   "You watch streams, follow indie VTubers, and bet on the chaos.",           "Bet on streams, vote on outcomes, climb the leaderboard."),
            ("Streamer", "role-streamer",  "You are a VTuber or streamer — your community might bet on your streams.", "Get discovered through community bets featuring your content."),
            ("Clipper",  "role-clipper",   "You create clips and highlight reels of indie VTubers.",                   "Compete in Clip Showdown events and earn the Clipper Legend badge."),
        ]

        for role, css, short_desc, detail in roles:
            st.markdown(f"""
            <div style="background:#0b0f1e;border:1px solid #1e3060;border-radius:12px;
                        padding:18px 22px;margin-bottom:4px;">
                <div style="display:flex;align-items:center;gap:12px;margin-bottom:8px;">
                    <span class="profile-role {css}">{role}</span>
                </div>
                <div style="color:#6a88aa;font-size:0.85rem;margin-bottom:4px;">{short_desc}</div>
                <div style="color:#2a4060;font-size:0.78rem;">{detail}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"I am a {role}", key=f"role_{role}", use_container_width=True):
                set_user_role(st.session_state.username, role)
                st.session_state.page = "home"
                st.session_state.show_onboarding = True
                set_toast("success", f"Welcome! Your account is ready. You start with 5,000 V-Coins.")
                st.rerun()

        st.markdown("""
        <div style="text-align:center;margin-top:16px;color:#1e3060;font-size:0.75rem;">
            Not sure? Pick Viewer — you can update it later in your profile.
        </div>
        """, unsafe_allow_html=True)
# ─────────────────────────────────────────────
# ONBOARDING PAGE

# ── Home ───────────────────────────────────────────────────────────────────
def page_home():
    check_fallback_resolutions()
    show_toast()
    username = st.session_state.username
    user     = get_user(username)
    bets     = get_bets()
    open_bets   = [b for b in bets if b["status"] == "open"]
    voting_bets = [b for b in bets if b["status"] == "voting"]

    st.markdown(f"""
    <div class="hero-wrap">
        <div class="hero">
            <div class="hero-eyebrow">Prediction Platform &nbsp;·&nbsp; Indie VTubers</div>
            <div class="hero-title">Welcome back, <span class="hero-name">{username}</span></div>
            <div class="hero-sub">
                Place V-Coins on indie VTuber stream moments.<br>
                Community-voted outcomes. No real money. Just predictions.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Open Bets",    len(open_bets))
    c2.metric("Voting Now",   len(voting_bets))
    c3.metric("Your Balance", f"{user['coins']:,}")
    c4.metric("Total Bets",   len(bets))

    st.markdown("---")

    if open_bets:
        st.markdown("### Open Bets")
        for b in open_bets[:5]:
            render_bet_card(b, show_btn=True)
        if len(open_bets) > 5:
            if st.button("View all open bets"):
                nav("bets")
    else:
        st.markdown('<div class="notice notice-info">No open bets right now. Be the first to create one.</div>',
                    unsafe_allow_html=True)
        if st.button("Create a bet"):
            nav("create_bet")

    if voting_bets:
        st.markdown("---")
        st.markdown("### Needs Your Vote")
        st.markdown('<div style="color:#334466;font-size:0.82rem;margin-bottom:12px;">These streams have ended. Vote on the real outcome to resolve the pot.</div>',
                    unsafe_allow_html=True)
        for b in voting_bets[:3]:
            render_bet_card(b, show_btn=True)

# ─────────────────────────────────────────────
#  ALL BETS PAGE

# ── All Bets ───────────────────────────────────────────────────────────────
def page_bets():
    show_toast()
    bets = get_bets()
    st.markdown("## All Bets")

    tab_open, tab_voting, tab_closed = st.tabs(["Open", "Voting", "Resolved"])

    with tab_open:
        ob = [b for b in bets if b["status"] == "open"]
        if not ob:
            st.markdown('<div style="color:#334466;padding:12px 0;">No open bets right now.</div>',
                        unsafe_allow_html=True)
        for b in ob:
            render_bet_card(b, show_btn=True)
        if st.button("Create a new bet", use_container_width=True):
            nav("create_bet")

    with tab_voting:
        vb = [b for b in bets if b["status"] == "voting"]
        if not vb:
            st.markdown('<div style="color:#334466;padding:12px 0;">Nothing in voting phase right now.</div>',
                        unsafe_allow_html=True)
        for b in vb:
            render_bet_card(b, show_btn=True)

    with tab_closed:
        cb = [b for b in bets if b["status"] == "closed"]
        if not cb:
            st.markdown('<div style="color:#334466;padding:12px 0;">No resolved bets yet.</div>',
                        unsafe_allow_html=True)
        for b in cb:
            render_bet_card(b, show_btn=True)

# ─────────────────────────────────────────────
#  BET DETAIL PAGE

# ── Bet Detail ─────────────────────────────────────────────────────────────
def page_bet_detail():
    show_toast()
    bet_id = st.session_state.selected_bet
    bet    = get_bet(bet_id) if bet_id else None

    if not bet:
        st.error("Bet not found.")
        if st.button("Back"):
            nav("bets")
        return

    username = st.session_state.username
    user     = get_user(username)
    entries  = get_entries(bet_id)
    votes    = get_votes(bet_id)

    if st.button("Back to Bets"):
        nav("bets")

    link = bet.get("stream_link","")
    name = bet.get("vtuber_name","")
    name_html = (f'<a href="{link}" target="_blank" style="color:#4499ff;'
                 f'text-decoration:none;font-weight:700;">{name}</a>'
                 if link else f'<span style="color:#4499ff;font-weight:700;">{name}</span>')
    game = bet.get("game_or_activity","")

    st.markdown(f"""
    <div class="hero-wrap">
        <div class="hero">
            <div class="vtag" style="margin-bottom:8px;">
                {name_html} &nbsp;·&nbsp; {bet.get('category','')}
            </div>
            <div style="font-family:'Syne',sans-serif;font-size:1.5rem;
                        font-weight:800;color:#ddeaff;margin-bottom:6px;line-height:1.3;">
                {bet['title']}
            </div>
            {f'<div style="font-size:0.85rem;color:#3a5a88;font-style:italic;margin-bottom:8px;">{game}</div>' if game else ''}
            <div style="color:#2a4466;font-size:0.85rem;line-height:1.6;">{bet.get('description','')}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    pot    = pot_total(entries)
    totals = {o: sum(e["amount"] for e in entries if e["option"] == o)
              for o in bet["options"]}

    st.markdown(f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:0.8rem;'
                f'color:#4499ff;margin-bottom:12px;">{pot:,} V-Coins in pot</div>',
                unsafe_allow_html=True)

    for opt in bet["options"]:
        pct = (totals[opt] / pot * 100) if pot else 0
        st.markdown(f"""
        <div class="bar-wrap">
            <div class="bar-label">
                <span>{opt}</span>
                <span class="bar-pct">{totals[opt]:,}  ({pct:.0f}%)</span>
            </div>
            <div class="bar-bg"><div class="bar-fill" style="width:{pct}%"></div></div>
        </div>
        """, unsafe_allow_html=True)

    existing = user_entry(bet_id, username)
    if existing:
        st.markdown(f'<div class="notice notice-success">You have {existing["amount"]:,} V-Coins on "{existing["option"]}"</div>',
                    unsafe_allow_html=True)

    st.markdown("---")

    # Open
    if bet["status"] == "open":
        st.markdown("### Place Your Bet")
        if existing:
            st.markdown('<div style="color:#334466;font-size:0.85rem;">You already have a bet on this one.</div>',
                        unsafe_allow_html=True)
        else:
            col1, col2 = st.columns([2,1])
            with col1:
                chosen = st.selectbox("Your prediction:", bet["options"])
            with col2:
                amount = st.number_input("V-Coins:", min_value=10,
                                         max_value=min(user["coins"], 99_999),
                                         value=100, step=10)
            st.caption(f"Balance: {user['coins']:,} V-Coins")
            if st.button(f"Place {amount:,} V-Coins on \"{chosen}\"", use_container_width=True):
                if amount > user["coins"]:
                    set_toast("error", "Insufficient V-Coins.")
                else:
                    place_entry(bet_id, username, chosen, amount)
                    set_toast("success", f"Bet placed — {amount:,} V-Coins on \"{chosen}\"")
                    st.rerun()
        st.markdown("---")
        with st.expander("Stream ended? Close this bet for community voting."):
            st.caption("Move to voting phase once the stream is over.")
            if st.button("Close and start voting"):
                close_bet_for_voting(bet_id)
                set_toast("success", "Voting phase is now open.")
                st.rerun()

    # Voting
    elif bet["status"] == "voting":
        vc      = {o: sum(1 for v in votes if v["option"] == o) for o in bet["options"]}
        total_v = sum(vc.values())

        st.markdown("### Community Vote")
        st.markdown(f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:0.75rem;'
                    f'color:#334466;margin-bottom:14px;">{total_v} votes cast · resolves at {MIN_VOTES} with majority</div>',
                    unsafe_allow_html=True)

        my_vote = user_vote(bet_id, username)
        if my_vote:
            st.markdown(f'<div class="notice notice-success">You voted: "{my_vote["option"]}"</div>',
                        unsafe_allow_html=True)
        else:
            st.markdown("**What actually happened on stream?**")
            vcols = st.columns(len(bet["options"]))
            for i, opt in enumerate(bet["options"]):
                with vcols[i]:
                    if st.button(f"{opt}  ({vc[opt]})",
                                 key=f"v_{bet_id}_{i}", use_container_width=True):
                        resolved = cast_vote(bet_id, username, opt)
                        if resolved:
                            set_toast("success", f"Vote cast — bet resolved automatically!")
                        else:
                            set_toast("success", f"Vote cast for \"{opt}\"")
                        st.rerun()

        for opt in bet["options"]:
            pct = (vc[opt] / total_v * 100) if total_v else 0
            st.markdown(f"""
            <div class="bar-wrap">
                <div class="bar-label">
                    <span>{opt}</span>
                    <span class="bar-pct" style="color:#ffcc00;">{vc[opt]} votes  ({pct:.0f}%)</span>
                </div>
                <div class="bar-bg"><div class="bar-fill-vote" style="width:{pct}%"></div></div>
            </div>
            """, unsafe_allow_html=True)

        # Manual resolve button if majority reached
        if total_v >= MIN_VOTES:
            winner_opt = max(vc, key=vc.get)
            if vc[winner_opt] > total_v / 2:
                st.markdown(f'<div class="notice notice-success">Clear majority — "{winner_opt}"</div>',
                            unsafe_allow_html=True)
                if st.button("Resolve and distribute winnings", use_container_width=True):
                    ok, msg = resolve_bet(bet_id)
                    set_toast("success" if ok else "error",
                              f"Resolved: \"{msg}\"" if ok else msg)
                    st.rerun()

    # Closed
    elif bet["status"] == "closed":
        result = bet.get("result","")
        st.markdown(f"""
        <div style="background:#001a0d;border:1px solid #00ff8833;border-radius:12px;
                    padding:20px 24px;text-align:center;margin:12px 0;">
            <div style="font-family:'JetBrains Mono',monospace;font-size:0.65rem;
                        color:#004422;text-transform:uppercase;letter-spacing:0.15em;
                        margin-bottom:8px;">Verified Outcome</div>
            <div style="font-family:'Syne',sans-serif;font-size:1.5rem;
                        font-weight:800;color:#00ff88;">{result}</div>
        </div>
        """, unsafe_allow_html=True)
        if existing:
            won = existing["option"] == result
            if won:
                st.markdown('<div class="notice notice-success">You predicted correctly. Winnings added to your wallet.</div>',
                            unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="notice notice-error">You predicted "{existing["option"]}". Better luck next time.</div>',
                            unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  CREATE BET PAGE

# ── Create Bet ─────────────────────────────────────────────────────────────
def page_create_bet():
    show_toast()
    st.markdown("## Create a Bet")
    st.markdown('<div style="color:#334466;font-size:0.85rem;margin-bottom:20px;">Submit a prediction for a live or upcoming stream.</div>',
                unsafe_allow_html=True)

    with st.form("create_bet", clear_on_submit=True):
        st.markdown('<div class="section-label">VTuber</div>', unsafe_allow_html=True)
        vtuber_name = st.text_input("VTuber name *", placeholder="e.g. Filian, Chibidoki, your oshi...")
        stream_link = st.text_input("Stream link", placeholder="https://twitch.tv/...")

        st.markdown('<div class="section-label" style="margin-top:16px;">Stream Context</div>',
                    unsafe_allow_html=True)
        game_or_activity = st.text_input("Game or activity *",
                                         placeholder="e.g. Elden Ring, Just Chatting, Karaoke...")

        st.markdown('<div class="section-label" style="margin-top:16px;">The Bet</div>',
                    unsafe_allow_html=True)
        title    = st.text_input("Bet question *",
                                 placeholder="e.g. Will they beat the Margit boss fight this stream?")
        desc     = st.text_area("Extra context (optional)",
                                placeholder="Anything the community should know before betting.",
                                max_chars=280, height=80)
        category = st.selectbox("Category", CATEGORIES)

        st.markdown('<div class="section-label" style="margin-top:16px;">Options</div>',
                    unsafe_allow_html=True)
        bet_type = st.radio("Bet type", ["Yes / No", "Over / Under", "Custom"], horizontal=True)

        opt1 = opt2 = ""
        if bet_type == "Yes / No":
            opt1, opt2 = "Yes", "No"
            st.markdown('<div class="notice notice-info" style="margin-top:4px;">Options: Yes  /  No</div>',
                        unsafe_allow_html=True)
        elif bet_type == "Over / Under":
            threshold = st.text_input("Threshold", placeholder="e.g. 15 deaths, 20 minutes")
            opt1 = f"Over {threshold}"  if threshold else "Over ?"
            opt2 = f"Under {threshold}" if threshold else "Under ?"
            st.markdown(f'<div class="notice notice-info">Options: {opt1}  /  {opt2}</div>',
                        unsafe_allow_html=True)
        else:
            c1, c2 = st.columns(2)
            with c1:
                opt1 = st.text_input("Option A *", placeholder="e.g. Finishes the game")
            with c2:
                opt2 = st.text_input("Option B *", placeholder="e.g. Rage quits")

        submitted = st.form_submit_button("Submit Bet", use_container_width=True)

        if submitted:
            errs = []
            if not vtuber_name.strip():      errs.append("VTuber name is required.")
            if not game_or_activity.strip(): errs.append("Game or activity is required.")
            if not title.strip():            errs.append("Bet question is required.")
            if not opt1.strip():             errs.append("Option A is required.")
            if not opt2.strip():             errs.append("Option B is required.")
            if errs:
                set_toast("error", errs[0])
                st.rerun()
            else:
                dupes = check_duplicate(vtuber_name, title)
                if dupes:
                    titles = ", ".join(f'"{d["title"][:50]}"' for d in dupes[:2])
                    st.markdown(f'<div class="dup-warn">Similar bet may already exist: {titles}<br>'
                                f'<span style="font-size:0.75rem;color:#886633;">Check open bets before submitting.</span></div>',
                                unsafe_allow_html=True)
                else:
                    create_bet(vtuber_name, stream_link, game_or_activity,
                               title, desc, [opt1.strip(), opt2.strip()],
                               category, st.session_state.username)
                    set_toast("success", "Bet is now live.")
                    nav("bets")

# ─────────────────────────────────────────────
#  ACHIEVEMENTS PAGE

# ── Achievements ───────────────────────────────────────────────────────────
def page_achievements():
    show_toast()
    username  = st.session_state.username
    all_achvs = get_all_achievements()
    earned    = {b["achievement_id"] for b in get_user_badges(username)}

    st.markdown("## Achievements")
    st.markdown('<div style="color:#334466;font-size:0.85rem;margin-bottom:20px;">Earn badges by hitting milestones. Most come with V-Coin rewards.</div>',
                unsafe_allow_html=True)

    for achv in all_achvs:
        is_earned = achv["id"] in earned
        border    = "#00ee8844" if is_earned else "#1e3060"
        bg        = "#001a0d" if is_earned else "#0b0f1e"
        status    = '<span style="color:#00ee88;font-family:\'JetBrains Mono\',monospace;font-size:0.72rem;">EARNED</span>' \
                    if is_earned else \
                    '<span style="color:#2a4060;font-family:\'JetBrains Mono\',monospace;font-size:0.72rem;">LOCKED</span>'
        reward    = f'+{achv["reward_coins"]:,} V-Coins' if achv.get("reward_coins") else "Badge only"

        st.markdown(f"""
        <div style="background:{bg};border:1px solid {border};border-radius:10px;
                    padding:18px 20px;margin-bottom:10px;">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:6px;">
                <div style="font-family:'Syne',sans-serif;font-weight:800;
                            font-size:1rem;color:#ddeaff;">{achv['name']}</div>
                {status}
            </div>
            <div style="color:#4a6a99;font-size:0.85rem;margin-bottom:8px;">{achv['description']}</div>
            <div style="font-family:'JetBrains Mono',monospace;font-size:0.72rem;color:#4499ff;">
                Reward: {reward}
            </div>
        </div>
        """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  COSMETIC SHOP PAGE

# ── Shop ───────────────────────────────────────────────────────────────────
def page_shop():
    show_toast()
    username = st.session_state.username
    user     = get_user(username)
    items    = get_shop_items()

    st.markdown("## Cosmetic Shop")
    st.markdown('<div style="color:#334466;font-size:0.85rem;margin-bottom:6px;">Spend V-Coins on profile cosmetics. Purely decorative — no gameplay advantage.</div>',
                unsafe_allow_html=True)
    st.markdown(f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:0.82rem;color:#4499ff;margin-bottom:20px;">Your balance: {user["coins"]:,} V-Coins</div>',
                unsafe_allow_html=True)

    types = sorted(set(i["type"] for i in items))
    type_labels = {"title":"Title Prefixes","frame":"Badge Frames","theme":"Profile Themes"}

    for t in types:
        st.markdown(f"### {type_labels.get(t, t.title())}")
        type_items = [i for i in items if i["type"] == t]
        for item in type_items:
            owned    = owns_item(username, item["id"])
            equipped = get_equipped(username, t)
            is_equip = equipped and equipped["id"] == item["id"]
            border   = "#00ee8844" if owned else "#1e3060"
            bg       = "#001a0d" if owned else "#0b0f1e"

            col1, col2 = st.columns([3,1])
            with col1:
                st.markdown(f"""
                <div style="background:{bg};border:1px solid {border};border-radius:10px;
                            padding:14px 18px;">
                    <div style="font-weight:700;font-size:0.95rem;color:#ddeaff;
                                margin-bottom:4px;">{item['name']}</div>
                    <div style="font-size:0.8rem;color:#4a6a99;margin-bottom:6px;">{item['description']}</div>
                    <div style="font-family:'JetBrains Mono',monospace;font-size:0.75rem;color:#4499ff;">
                        {item['cost']:,} V-Coins
                        {' &nbsp;·&nbsp; <span style="color:#00ee88">OWNED</span>' if owned else ''}
                        {' &nbsp;·&nbsp; <span style="color:#ffcc00">EQUIPPED</span>' if is_equip else ''}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
                if owned:
                    if not is_equip:
                        if st.button("Equip", key=f"equip_{item['id']}"):
                            equip_item(username, item["id"], t)
                            set_toast("success", f"Equipped {item['name']}!")
                            st.rerun()
                    else:
                        st.markdown('<div style="color:#ffcc00;font-size:0.75rem;text-align:center;padding-top:8px;">Equipped</div>',
                                    unsafe_allow_html=True)
                else:
                    if st.button("Buy", key=f"buy_{item['id']}"):
                        ok, msg = purchase_item(username, item["id"], item["cost"])
                        set_toast("success" if ok else "error", msg)
                        st.rerun()

# ─────────────────────────────────────────────
#  LEADERBOARD PAGE

# ── Leaderboard ────────────────────────────────────────────────────────────
def page_leaderboard():
    show_toast()
    st.markdown("## Leaderboard")

    tab_rich, tab_acc, tab_loss = st.tabs(["Richest", "Most Accurate", "Biggest Losers"])

    with tab_rich:
        st.markdown("### Richest Predictors")
        rows = leaderboard_rich()
        if not rows:
            st.markdown('<div style="color:#334466;padding:12px 0;">No users yet.</div>', unsafe_allow_html=True)
        for i, u in enumerate(rows):
            top   = i < 3
            rank  = f"#{i+1:02d}"
            style = "lb-rank lb-rank-top" if top else "lb-rank"
            st.markdown(f"""
            <div class="lb-row">
                <div class="{style}">{rank}</div>
                <div class="lb-name">{u['username']}</div>
                <div class="lb-stat">{u['coins']:,}</div>
            </div>
            """, unsafe_allow_html=True)

    with tab_acc:
        st.markdown("### Most Accurate  (min. 3 bets)")
        rows = leaderboard_accurate()
        if not rows:
            st.markdown('<div style="color:#334466;padding:12px 0;">Not enough data yet.</div>', unsafe_allow_html=True)
        for i, u in enumerate(rows):
            top   = i < 3
            rank  = f"#{i+1:02d}"
            style = "lb-rank lb-rank-top" if top else "lb-rank"
            pct   = u.get("pct", 0)
            st.markdown(f"""
            <div class="lb-row">
                <div class="{style}">{rank}</div>
                <div class="lb-name">{u['username']}</div>
                <div class="lb-stat">
                    {pct*100:.0f}%
                    <br><span style="font-size:0.68rem;color:#1e3060;">{u['bets_correct']}/{u['bets_placed']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with tab_loss:
        st.markdown("### Biggest Losers")
        st.markdown('<div style="color:#334466;font-size:0.82rem;margin-bottom:12px;">Most V-Coins lost in total. A badge of honour.</div>',
                    unsafe_allow_html=True)
        rows = leaderboard_losers()
        if not rows:
            st.markdown('<div style="color:#334466;padding:12px 0;">Nobody has lost anything yet.</div>', unsafe_allow_html=True)
        for i, u in enumerate(rows):
            top   = i < 3
            rank  = f"#{i+1:02d}"
            style = "lb-rank lb-rank-top" if top else "lb-rank"
            st.markdown(f"""
            <div class="lb-row">
                <div class="{style}">{rank}</div>
                <div class="lb-name">{u['username']}</div>
                <div class="lb-stat-loss">-{u.get('total_lost',0):,}<br>
                    <span style="font-size:0.68rem;color:#2a1020;">
                        biggest: -{u.get('biggest_loss',0):,}
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  MY PROFILE PAGE

# ── My Profile ─────────────────────────────────────────────────────────────
def page_my_profile():
    show_toast()
    username = st.session_state.username
    user     = get_user(username)

    st.markdown("## My Profile")

    role  = user.get("role","")
    r_css = {"Viewer":"role-watcher","Streamer":"role-streamer",
             "Clipper":"role-clipper"}.get(role,"role-watcher")
    title_item = get_equipped(username, "title")
    title_str  = f' — {title_item["value"]}' if title_item else ""

    st.markdown(f"""
    <div class="profile-card">
        <div style="font-family:'Syne',sans-serif;font-size:1.4rem;
                    font-weight:800;color:#e8f0ff;margin-bottom:4px;">
            {username}{title_str}
        </div>
        <span class="profile-role {r_css}">{role or 'No role set'}</span>
        <div style="color:#4a6a99;font-size:0.85rem;margin-top:10px;line-height:1.6;">
            {user.get('bio','No bio yet.')}
        </div>
        {f'<div style="color:#2a4060;font-size:0.8rem;margin-top:8px;">Favourite VTubers: {user.get("favorite_vtubers","")}</div>' if user.get('favorite_vtubers') else ''}
    </div>
    """, unsafe_allow_html=True)

    # Stats
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("V-Coins",   f"{user['coins']:,}")
    c2.metric("Total Won", f"{user.get('total_won',0):,}")
    c3.metric("Total Lost",f"{user.get('total_lost',0):,}")
    c4.metric("Accuracy",
              f"{(user['bets_correct']/user['bets_placed']*100):.0f}%"
              if user.get('bets_placed',0) >= 1 else "N/A")

    st.markdown("---")

    col_badges, col_edit = st.columns([2,1])

    with col_badges:
        st.markdown("### Badges")
        render_badges(username)

    with col_edit:
        st.markdown("### Edit Profile")
        with st.form("edit_profile"):
            new_bio = st.text_area("Bio", value=user.get("bio",""),
                                   max_chars=200, height=80,
                                   placeholder="Tell the community about yourself...")
            new_fav = st.text_input("Favourite VTubers",
                                    value=user.get("favorite_vtubers",""),
                                    placeholder="e.g. Filian, Chibidoki, Nemu")
            if st.form_submit_button("Save", use_container_width=True):
                update_user(username, {"bio": new_bio, "favorite_vtubers": new_fav})
                set_toast("success", "Profile updated.")
                st.rerun()

    st.markdown("---")
    st.markdown("### Bet History")
    all_entries = db().table("bet_entries").select("*") \
                      .eq("username", username).execute().data or []
    if not all_entries:
        st.markdown('<div style="color:#334466;font-size:0.85rem;">No bets placed yet.</div>',
                    unsafe_allow_html=True)
    else:
        bet_ids = [e["bet_id"] for e in all_entries[:20]]
        bets_map = {}
        for bid in bet_ids:
            b = get_bet(bid)
            if b:
                bets_map[bid] = b
        for e in all_entries[:10]:
            b = bets_map.get(e["bet_id"])
            if not b:
                continue
            won  = b.get("status") == "closed" and e["option"] == b.get("result")
            lost = b.get("status") == "closed" and e["option"] != b.get("result")
            color = "#00cc77" if won else ("#ff5577" if lost else "#4499ff")
            outcome = "Won" if won else ("Lost" if lost else "Pending")
            st.markdown(f"""
            <div style="background:#0b0f1e;border:1px solid #1a2540;border-radius:8px;
                        padding:12px 16px;margin-bottom:8px;display:flex;
                        justify-content:space-between;align-items:center;">
                <div>
                    <div style="font-size:0.85rem;color:#c8d8f0;font-weight:600;">{b['title'][:60]}</div>
                    <div style="font-size:0.75rem;color:#334466;margin-top:2px;">{b['vtuber_name']} · {e['option']}</div>
                </div>
                <div style="text-align:right;">
                    <div style="font-family:'JetBrains Mono',monospace;font-size:0.82rem;color:{color};">{outcome}</div>
                    <div style="font-family:'JetBrains Mono',monospace;font-size:0.75rem;color:#334466;">{e['amount']:,} V-C</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  HOW IT WORKS PAGE

# ── How It Works ───────────────────────────────────────────────────────────
def page_how_it_works():
    st.markdown("## How VTuberBets Works")
    st.markdown('<div style="color:#334466;font-size:0.88rem;margin-bottom:24px;">Everything you need to know to start predicting.</div>',
                unsafe_allow_html=True)

    sections = [
        ("01", "What are V-Coins?",
         "V-Coins are VTuberBets' virtual currency. They are completely fake — no real money, no cash value, ever. Every new account starts with 5,000 V-Coins. You earn more by predicting correctly, claiming your daily bonus (+250 every 20 hours), and completing achievements."),

        ("02", "How do I place a bet?",
         "Browse the open bets on the Home or All Bets page. Click View on any bet that interests you. Choose which outcome you think will happen, decide how many V-Coins to wager, and confirm. You can only place one bet per prediction — make it count."),

        ("03", "How are bets resolved?",
         "After a stream ends, the bet creator closes it and moves it to Voting phase. The community then votes on what actually happened. As soon as 3 votes are cast and one option has a clear majority, the bet resolves automatically. If no majority is reached within 6 days, the option with the most votes wins by default."),

        ("04", "How do payouts work?",
         "Winners split the entire pot proportionally based on how much they wagered. If you bet more than others on the winning side, you earn a larger share. A 5% house cut is taken from each pot and goes into the weekly bonus pool — the top 3 richest players each week receive a 2,000 V-Coin bonus from this pool."),

        ("05", "What are Achievements?",
         "Achievements are badges earned by hitting milestones — correctly predicting Hidden Gem bets, winning large amounts, casting deciding votes, and more. Most achievements come with V-Coin rewards. Check the Achievements page to see what you're working toward."),

        ("06", "What is the Cosmetic Shop?",
         "Spend V-Coins on purely decorative profile customizations — title prefixes, badge frames, and profile themes. These have no effect on gameplay. They exist as a fun way to spend excess coins and show off your style."),

        ("07", "What counts as an indie VTuber?",
         "VTuberBets is exclusively for small, independent VTubers — not large agency talents. If you're creating a bet, the VTuber should be a genuine small creator. This is the whole point: helping people discover and engage with creators who don't already have massive audiences."),

        ("08", "What are the bet categories?",
         "Hidden Gem bets spotlight unknown or underrated VTubers specifically. Boss Fight, Death Count, and Game Completion are for gameplay moments. Yap Session / Just Chatting covers pre-game or off-topic tangents. Raid / Shoutout covers end-of-stream moments. Tech Scuff, Karaoke Arc, and Chaos Moment cover the unpredictable stuff that makes indie streams great."),
    ]

    for num, title, body in sections:
        st.markdown(f"""
        <div class="hiw-section">
            <div class="hiw-num">Step {num}</div>
            <div class="hiw-title">{title}</div>
            <div class="hiw-body">{body}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div style="background:#0b0f1e;border:1px solid #00ee8844;border-radius:10px;
                padding:20px 24px;margin-top:8px;text-align:center;">
        <div style="font-family:'Syne',sans-serif;font-size:1rem;font-weight:800;
                    color:#00ee88;margin-bottom:6px;">Ready to play?</div>
        <div style="color:#334466;font-size:0.85rem;">
            Head to the Home page and place your first bet.<br>
            No real money. No downloads. Just predictions and bragging rights.
        </div>
    </div>
    """, unsafe_allow_html=True)


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

    # ── CLIP FUNCTIONS (defined directly here to fix NameError) ────────────────
def render_clip_card(clip: dict):
    st.markdown(f"""
    <div class="card" style="border-left: 3px solid #00d4ff;">
        <div class="vtag">{clip['vtuber_name']}</div>
        <div style="font-family:'Syne',sans-serif;font-size:1rem;font-weight:800;color:#ddeaff;margin-bottom:6px;">
            {clip['title']}
        </div>
        <div style="color:#4a6a99;font-size:0.85rem;margin-bottom:12px;">{clip.get('description','')}</div>
        <a href="{clip['clip_url']}" target="_blank" style="color:#00d4ff;font-family:'JetBrains Mono',monospace;font-size:0.8rem;">
            ▶️ Watch Clip
        </a>
        <div style="display:flex;gap:8px;margin-top:12px;flex-wrap:wrap;">
            {' '.join(f'<span class="pill" style="background:#001a2e;color:#00d4ff;font-size:0.65rem;">{tag}</span>' for tag in clip.get('tags',[]))}
        </div>
        <div style="margin-top:12px;font-family:'JetBrains Mono',monospace;font-size:0.75rem;color:#00d4ff;">
            ↑ {clip['upvotes']} upvotes • by {clip['submitter']}
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("👍 Upvote", key=f"up_{clip['id']}", use_container_width=True):
        from database import upvote_clip
        if upvote_clip(clip['id'], st.session_state.username):
            set_toast("success", "+1 upvote!")
            st.rerun()

def render_clip_submit_form(bet_id=None, prefill_vtuber=""):
    with st.form("clip_submit", clear_on_submit=True):
        st.markdown("### Submit a new clip")
        vtuber = st.text_input("VTuber name *", value=prefill_vtuber)
        clip_url = st.text_input("Clip link *", placeholder="https://twitch.tv/clip/...")
        title = st.text_input("Clip title *", placeholder="That insane clutch moment")
        desc = st.text_area("Short description", max_chars=140, height=80)
        tags = st.multiselect("Tags (choose 1-3)", 
                              ["Boss Fight", "Death Count", "Chaos Moment", "Karaoke Arc", 
                               "Raid / Shoutout", "Tech Scuff", "Hidden Gem", "Other"],
                              default=[])
        
        submitted = st.form_submit_button("Submit Clip", use_container_width=True)
        if submitted:
            if not vtuber or not clip_url or not title:
                set_toast("error", "VTuber, clip link, and title required.")
                return
            from database import submit_clip
            submit_clip(clip_url, vtuber, title, desc or "", tags, 
                        st.session_state.username, bet_id)
            set_toast("success", "Clip submitted! Thank you, scout.")
            st.rerun()
