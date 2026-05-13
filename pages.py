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
# COSMETIC SHOP PAGE
# ── Shop ───────────────────────────────────────────────────────────────────
def page_shop():
    show_toast()
    username = st.session_state.username
    user = get_user(username)
    items = get_shop_items()
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
            owned = owns_item(username, item["id"])
            equipped = get_equipped(username, t)
            is_equip = equipped and equipped["id"] == item["id"]
            border = "#00ee8844" if owned else "#1e3060"
            bg = "#001a0d" if owned else "#0b0f1e"
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
                        {' &nbsp;&nbsp; <span style="color:#00ee88">OWNED</span>' if owned else ''}
                        {' &nbsp;&nbsp; <span style="color:#ffcc00">EQUIPPED</span>' if is_equip else ''}
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
# LEADERBOARD PAGE
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
            top = i < 3
            rank = f"#{i+1:02d}"
            style = "lb-rank lb-rank-top" if top else "lb-rank"
            st.markdown(f"""
            <div class="lb-row">
                <div class="{style}">{rank}</div>
                <div class="lb-name">{u['username']}</div>
                <div class="lb-stat">{u['coins']:,}</div>
            </div>
            """, unsafe_allow_html=True)
    with tab_acc:
        st.markdown("### Most Accurate (min. 3 bets)")
        rows = leaderboard_accurate()
        if not rows:
            st.markdown('<div style="color:#334466;padding:12px 0;">Not enough data yet.</div>', unsafe_allow_html=True)
        for i, u in enumerate(rows):
            top = i < 3
            rank = f"#{i+1:02d}"
            style = "lb-rank lb-rank-top" if top else "lb-rank"
            pct = u.get("pct", 0)
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
            top = i < 3
            rank = f"#{i+1:02d}"
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
# MY PROFILE PAGE
# ── My Profile ─────────────────────────────────────────────────────────────
def page_my_profile():
    show_toast()
    username = st.session_state.username
    user = get_user(username)
    st.markdown("## My Profile")
    role = user.get("role","")
    r_css = {"Viewer":"role-watcher","Streamer":"role-streamer",
             "Clipper":"role-clipper"}.get(role,"role-watcher")
    title_item = get_equipped(username, "title")
    title_str = f' — {title_item["value"]}' if title_item else ""
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
    c1.metric("V-Coins", f"{user['coins']:,}")
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
            won = b.get("status") == "closed" and e["option"] == b.get("result")
            lost = b.get("status") == "closed" and e["option"] != b.get("result")
            color = "#00cc77" if won else ("#ff5577" if lost else "#4499ff")
            outcome = "Won" if won else ("Lost" if lost else "Pending")
            st.markdown(f"""
            <div style="background:#0b0f1e;border:1px solid #1a2540;border-radius:8px;
                        padding:12px 16px;margin-bottom:8px;display:flex;
                        justify-content:space-between;align-items:center;">
                <div>
                    <div style="font-size:0.85rem;color:#c8d8f0;font-weight:600;">{b['title'][:60]}</div>
                    <div style="font-size:0.75rem;color:#334466;margin-top:2px;">{b['vtuber_name']}  {e['option']}</div>
                </div>
                <div style="text-align:right;">
                    <div style="font-family:'JetBrains Mono',monospace;font-size:0.82rem;color:{color};">{outcome}</div>
                    <div style="font-family:'JetBrains Mono',monospace;font-size:0.75rem;color:#334466;">{e['amount']:,} V-C</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
# ─────────────────────────────────────────────
# HOW IT WORKS PAGE
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
    
# ── CLIPS PAGE ─────────────────────────────────────────────────────────────
def page_clips():
    show_toast()
    st.markdown("## Clip Hub")
    st.markdown('<div style="color:#334466;font-size:0.85rem;margin-bottom:20px;">Community-submitted clips of indie VTubers. Upvote your favorites — top 3 each week win V-Coins.</div>',
                unsafe_allow_html=True)
    col1, col2 = st.columns([3,1])
    with col1:
        sort_mode = st.radio("Sort", ["Top this week", "Newest"], horizontal=True, key="clip_sort_radio")
        sort_param = "top" if "Top" in sort_mode else "newest"
    with col2:
        if st.button("🏆 Award this week’s top clips", use_container_width=True):
            count = award_weekly_clip_rewards()
            set_toast("success", f"Awarded V-Coins to top {count} clips!")
            st.rerun()
    clips = get_clips(sort=sort_param)
    if not clips:
        st.markdown('<div style="color:#334466;padding:12px 0;">No clips submitted yet. Be the first!</div>', unsafe_allow_html=True)
    else:
        for clip in clips:
            render_clip_card(clip)
    st.markdown("---")
    render_clip_submit_form()
