import streamlit as st
import os
import uuid
from datetime import datetime, timedelta
from supabase import create_client, Client

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="VTuberBets",
    page_icon="🎲",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  STYLES
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Syne:wght@700;800&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"] {
    background: #0c0c14 !important;
    color: #ddd8f0 !important;
    font-family: 'DM Sans', sans-serif;
}
[data-testid="stSidebar"] {
    background: #111120 !important;
    border-right: 1px solid #2a2040 !important;
}
h1, h2, h3 { font-family: 'Syne', sans-serif !important; letter-spacing: -0.02em; }

.card {
    background: #16162a;
    border: 1px solid #2a2040;
    border-radius: 16px;
    padding: 20px 22px;
    margin-bottom: 14px;
    transition: border-color 0.2s;
}
.card:hover { border-color: #5b4fcf; }
.card-accent { border-top: 3px solid #5b4fcf; }

.vtag {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #9d8fff;
    margin-bottom: 4px;
}
.bet-title {
    font-size: 1rem;
    font-weight: 600;
    color: #f0ecff;
    margin-bottom: 10px;
    line-height: 1.4;
}

.pill {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 50px;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}
.pill-open   { background: #0d2e1a; color: #4ade80; border: 1px solid #22c55e44; }
.pill-voting { background: #2e2000; color: #fbbf24; border: 1px solid #f59e0b44; }
.pill-closed { background: #1a0d2e; color: #a78bfa; border: 1px solid #7c3aed44; }

.pot { font-size: 0.75rem; color: #9d8fff; font-weight: 600; }

.bar-wrap { margin: 8px 0; }
.bar-label { display: flex; justify-content: space-between; font-size: 0.8rem; margin-bottom: 3px; color: #b0a8cc; }
.bar-bg { background: #1e1e36; border-radius: 4px; height: 8px; overflow: hidden; }
.bar-fill { height: 8px; border-radius: 4px; background: linear-gradient(90deg, #5b4fcf, #9d5fcf); }

.coin-box {
    background: #16162a;
    border: 1px solid #2a2040;
    border-radius: 14px;
    padding: 14px 18px;
    text-align: center;
    margin-bottom: 10px;
}
.coin-amount {
    font-family: 'Syne', sans-serif;
    font-size: 1.8rem;
    font-weight: 800;
    color: #c4b5fd;
}

.lb-row {
    display: flex;
    align-items: center;
    padding: 10px 14px;
    border-radius: 10px;
    margin-bottom: 6px;
    background: #16162a;
    border: 1px solid #2a2040;
    gap: 12px;
}
.lb-rank { font-family:'Syne',sans-serif; font-size:1.1rem; font-weight:800; width:32px; color:#9d8fff; }
.lb-name { flex:1; font-weight:600; font-size:0.9rem; }
.lb-stat { color:#c4b5fd; font-weight:700; font-size:0.85rem; text-align:right; }

.stButton > button {
    background: #5b4fcf !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    transition: background 0.15s !important;
}
.stButton > button:hover { background: #4a3fbf !important; }

.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div {
    background: #16162a !important;
    border: 1px solid #2a2040 !important;
    border-radius: 8px !important;
    color: #ddd8f0 !important;
}

.stTabs [data-baseweb="tab-list"] {
    background: #111120 !important;
    border-radius: 10px;
    gap: 2px;
    padding: 3px;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #6b6490 !important;
    border-radius: 7px !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
}
.stTabs [aria-selected="true"] {
    background: #5b4fcf !important;
    color: white !important;
}

[data-testid="metric-container"] {
    background: #16162a;
    border: 1px solid #2a2040;
    border-radius: 12px;
    padding: 12px 16px;
}

.notice-success {
    background: #0a1f12; border: 1px solid #22c55e44;
    border-radius: 10px; padding: 12px 16px;
    color: #86efac; font-size: 0.88rem; margin: 8px 0;
}
.notice-warn {
    background: #1a1200; border: 1px solid #f59e0b44;
    border-radius: 10px; padding: 12px 16px;
    color: #fcd34d; font-size: 0.88rem; margin: 8px 0;
}
.notice-error {
    background: #1a0a0a; border: 1px solid #f8717144;
    border-radius: 10px; padding: 12px 16px;
    color: #fca5a5; font-size: 0.88rem; margin: 8px 0;
}

.vt-profile {
    background: #16162a; border: 1px solid #2a2040;
    border-radius: 14px; padding: 18px 20px; margin-bottom: 12px;
}
.vt-name { font-family:'Syne',sans-serif; font-size:1.1rem; font-weight:800; color:#f0ecff; }
.vt-handle { font-size:0.78rem; color:#6b6490; margin-bottom:8px; }
.vt-bio { font-size:0.85rem; color:#b0a8cc; line-height:1.5; margin-bottom:10px; }
.tag {
    display: inline-block; background: #1e1e36; border: 1px solid #2a2040;
    border-radius: 6px; padding: 2px 8px; font-size: 0.7rem;
    color: #9d8fff; margin: 2px; font-weight: 500;
}

.hero {
    background: linear-gradient(135deg, #14142a 0%, #1a1030 100%);
    border: 1px solid #2a2040; border-radius: 20px;
    padding: 32px 36px; margin-bottom: 24px;
}

hr { border-color: #2a2040 !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  SUPABASE CLIENT
# ─────────────────────────────────────────────
@st.cache_resource
def get_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

def db() -> Client:
    return get_supabase()

# ─────────────────────────────────────────────
#  CONSTANTS
# ─────────────────────────────────────────────
STARTING_COINS = 5_000
DAILY_BONUS    = 250
HOUSE_CUT      = 0.05
MIN_VOTES      = 8

CATEGORIES = [
    "Boss Fight", "Yap Session", "Tech Scuff", "Death Count",
    "Chaos Moment", "Game Completion", "Karaoke Arc",
    "Follower Goal", "Other"
]

VIBE_TAGS = [
    "cozy", "horror", "variety", "just chatting", "FPS",
    "JRPG", "indie games", "speedrun", "gacha", "minecraft",
    "english", "bilingual", "art stream", "zatsudan"
]

# ─────────────────────────────────────────────
#  DATABASE HELPERS — USERS
# ─────────────────────────────────────────────
def get_user(username: str) -> dict | None:
    r = db().table("users").select("*").eq("username", username).execute()
    return r.data[0] if r.data else None

def create_user(username: str) -> dict:
    user = {
        "username":     username,
        "coins":        STARTING_COINS,
        "joined_at":    datetime.utcnow().isoformat(),
        "last_bonus":   None,
        "total_won":    0,
        "bets_correct": 0,
        "bets_placed":  0,
    }
    r = db().table("users").insert(user).execute()
    return r.data[0]

def get_or_create_user(username: str) -> dict:
    user = get_user(username)
    return user if user else create_user(username)

def update_user(username: str, fields: dict):
    db().table("users").update(fields).eq("username", username).execute()

def claim_daily_bonus(username: str) -> tuple[bool, str]:
    user = get_user(username)
    now  = datetime.utcnow()
    last = user.get("last_bonus")
    if last:
        last_dt = datetime.fromisoformat(last.replace("Z", ""))
        if now - last_dt < timedelta(hours=20):
            rem = timedelta(hours=20) - (now - last_dt)
            h, m = divmod(int(rem.total_seconds() / 60), 60)
            return False, f"Already claimed! Come back in {h}h {m}m"
    update_user(username, {
        "coins":      user["coins"] + DAILY_BONUS,
        "last_bonus": now.isoformat(),
    })
    return True, f"+{DAILY_BONUS} V-Coins added to your wallet!"

# ─────────────────────────────────────────────
#  DATABASE HELPERS — VTUBERS
# ─────────────────────────────────────────────
def get_vtubers(approved_only=True) -> list:
    q = db().table("vtubers").select("*").order("name")
    if approved_only:
        q = q.eq("approved", True)
    return q.execute().data or []

def get_vtuber(vtuber_id: str) -> dict | None:
    r = db().table("vtubers").select("*").eq("id", vtuber_id).execute()
    return r.data[0] if r.data else None

def nominate_vtuber(name, handle, platform, link, bio, tags, nominated_by):
    db().table("vtubers").insert({
        "id":           str(uuid.uuid4()),
        "name":         name,
        "handle":       handle,
        "platform":     platform,
        "link":         link,
        "bio":          bio,
        "tags":         tags,
        "approved":     False,
        "nominated_by": nominated_by,
        "created_at":   datetime.utcnow().isoformat(),
        "spotlight":    False,
    }).execute()

# ─────────────────────────────────────────────
#  DATABASE HELPERS — BETS
# ─────────────────────────────────────────────
def get_bets(status: str | None = None) -> list:
    q = db().table("bets").select("*").order("created_at", desc=True)
    if status:
        q = q.eq("status", status)
    return q.execute().data or []

def get_bet(bet_id: str) -> dict | None:
    r = db().table("bets").select("*").eq("id", bet_id).execute()
    return r.data[0] if r.data else None

def create_bet(vtuber_id, vtuber_name, title, description, options, category, created_by):
    db().table("bets").insert({
        "id":           str(uuid.uuid4()),
        "vtuber_id":    vtuber_id,
        "vtuber_name":  vtuber_name,
        "title":        title,
        "description":  description,
        "options":      options,
        "status":       "open",
        "created_at":   datetime.utcnow().isoformat(),
        "created_by":   created_by,
        "category":     category,
        "result":       None,
    }).execute()

def close_bet_for_voting(bet_id: str):
    db().table("bets").update({"status": "voting"}).eq("id", bet_id).execute()

# ─────────────────────────────────────────────
#  DATABASE HELPERS — BET ENTRIES
# ─────────────────────────────────────────────
def get_entries(bet_id: str) -> list:
    return db().table("bet_entries").select("*").eq("bet_id", bet_id).execute().data or []

def user_entry(bet_id: str, username: str) -> dict | None:
    r = db().table("bet_entries").select("*").eq("bet_id", bet_id).eq("username", username).execute()
    return r.data[0] if r.data else None

def place_bet_entry(bet_id: str, username: str, option: str, amount: int):
    db().table("bet_entries").insert({
        "id":         str(uuid.uuid4()),
        "bet_id":     bet_id,
        "username":   username,
        "option":     option,
        "amount":     amount,
        "created_at": datetime.utcnow().isoformat(),
    }).execute()
    user = get_user(username)
    update_user(username, {
        "coins":       user["coins"] - amount,
        "bets_placed": user["bets_placed"] + 1,
    })

# ─────────────────────────────────────────────
#  DATABASE HELPERS — VOTES
# ─────────────────────────────────────────────
def get_votes(bet_id: str) -> list:
    return db().table("votes").select("*").eq("bet_id", bet_id).execute().data or []

def user_vote(bet_id: str, username: str) -> dict | None:
    r = db().table("votes").select("*").eq("bet_id", bet_id).eq("username", username).execute()
    return r.data[0] if r.data else None

def cast_vote(bet_id: str, username: str, option: str):
    db().table("votes").insert({
        "id":         str(uuid.uuid4()),
        "bet_id":     bet_id,
        "username":   username,
        "option":     option,
        "created_at": datetime.utcnow().isoformat(),
    }).execute()

# ─────────────────────────────────────────────
#  DATABASE HELPERS — RESOLUTION
# ─────────────────────────────────────────────
def resolve_bet(bet_id: str) -> tuple[bool, str]:
    bet     = get_bet(bet_id)
    entries = get_entries(bet_id)
    votes   = get_votes(bet_id)

    if not bet or bet["status"] != "voting":
        return False, "Bet is not in voting phase."

    counts: dict[str, int] = {o: 0 for o in bet["options"]}
    for v in votes:
        counts[v["option"]] = counts.get(v["option"], 0) + 1
    total_v = sum(counts.values())

    if total_v < MIN_VOTES:
        return False, f"Need at least {MIN_VOTES} votes. ({total_v} so far)"

    winner = max(counts, key=counts.get)
    if counts[winner] <= total_v / 2:
        return False, "No clear majority yet."

    pot           = sum(e["amount"] for e in entries)
    distributable = int(pot * (1 - HOUSE_CUT))
    winners       = [e for e in entries if e["option"] == winner]
    winner_stake  = sum(e["amount"] for e in winners)

    for e in winners:
        share = int(distributable * e["amount"] / winner_stake) if winner_stake else 0
        user  = get_user(e["username"])
        if user:
            update_user(e["username"], {
                "coins":        user["coins"] + share,
                "total_won":    user["total_won"] + share,
                "bets_correct": user["bets_correct"] + 1,
            })

    db().table("bets").update({
        "status": "closed",
        "result": winner,
    }).eq("id", bet_id).execute()
    return True, winner

# ─────────────────────────────────────────────
#  DATABASE HELPERS — LEADERBOARD
# ─────────────────────────────────────────────
def get_leaderboard_rich(limit=10) -> list:
    return db().table("users") \
               .select("username,coins,total_won,bets_placed,bets_correct") \
               .order("coins", desc=True).limit(limit).execute().data or []

def get_leaderboard_accurate(limit=10) -> list:
    users = db().table("users") \
                .select("username,coins,bets_placed,bets_correct") \
                .gte("bets_placed", 1).execute().data or []
    for u in users:
        u["pct"] = u["bets_correct"] / u["bets_placed"] if u["bets_placed"] else 0
    return sorted(users, key=lambda x: x["pct"], reverse=True)[:limit]

# ─────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────
for k, v in [("username", None), ("page", "home"),
             ("selected_bet", None), ("selected_vtuber", None), ("toast", None)]:
    if k not in st.session_state:
        st.session_state[k] = v

def nav(page: str, bet_id=None, vtuber_id=None):
    st.session_state.page             = page
    st.session_state.selected_bet     = bet_id
    st.session_state.selected_vtuber  = vtuber_id
    st.rerun()

def toast(kind: str, msg: str):
    st.session_state.toast = (kind, msg)

def show_toast():
    if st.session_state.toast:
        kind, msg = st.session_state.toast
        css  = "notice-success" if kind == "success" else "notice-error"
        icon = "+" if kind == "success" else "!"
        st.markdown(f'<div class="{css}">{icon}  {msg}</div>', unsafe_allow_html=True)
        st.session_state.toast = None

# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
def render_sidebar():
    username = st.session_state.username
    if not username:
        return
    user = get_or_create_user(username)

    with st.sidebar:
        st.markdown("""
        <div style="padding:8px 0 16px;">
            <div style="font-family:'Syne',sans-serif;font-size:1.3rem;
                        font-weight:800;color:#c4b5fd;">VTuberBets</div>
            <div style="font-size:0.72rem;color:#6b6490;margin-top:2px;">
                indie vtuber prediction community
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="coin-box">
            <div style="font-size:0.7rem;color:#6b6490;text-transform:uppercase;
                        letter-spacing:0.08em;margin-bottom:4px;">{username}</div>
            <div class="coin-amount">{user['coins']:,}</div>
            <div style="font-size:0.7rem;color:#6b6490;margin-top:2px;">V-Coins</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Claim Daily Bonus  (+250)", use_container_width=True):
            ok, msg = claim_daily_bonus(username)
            toast("success" if ok else "error", msg)
            st.rerun()

        st.markdown("---")

        for label, key in [
            ("Home",        "home"),
            ("Bets",        "bets"),
            ("Discover",    "discover"),
            ("Create Bet",  "create_bet"),
            ("Nominate",    "nominate"),
            ("Leaderboard", "leaderboard"),
        ]:
            if st.button(label, key=f"nav_{key}", use_container_width=True):
                nav(key)

        st.markdown("---")
        c1, c2 = st.columns(2)
        with c1:
            st.metric("Correct", user.get("bets_correct", 0))
        with c2:
            st.metric("Placed",  user.get("bets_placed",  0))

        if st.button("Log out", use_container_width=True):
            st.session_state.username = None
            st.session_state.page = "home"
            st.rerun()

# ─────────────────────────────────────────────
#  LOGIN PAGE
# ─────────────────────────────────────────────
def page_login():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="text-align:center;padding:48px 0 32px;">
            <div style="font-family:'Syne',sans-serif;font-size:2.8rem;
                        font-weight:800;color:#c4b5fd;margin-bottom:8px;">
                VTuberBets
            </div>
            <div style="color:#6b6490;font-size:0.95rem;line-height:1.6;">
                A community prediction platform for indie VTuber fans.<br>
                Bet virtual V-Coins on stream moments. No real money, ever.
            </div>
        </div>
        """, unsafe_allow_html=True)

        show_toast()

        username = st.text_input("Choose a username to get started:",
                                 placeholder="e.g. StreamGremlin, PredictionKing...")

        if st.button("Enter", use_container_width=True):
            un = username.strip()
            if len(un) < 2:
                toast("error", "Username must be at least 2 characters.")
                st.rerun()
            elif len(un) > 24:
                toast("error", "Username must be 24 characters or fewer.")
                st.rerun()
            else:
                get_or_create_user(un)
                st.session_state.username = un
                nav("home")

        st.markdown("""
        <div style="text-align:center;color:#4a4468;font-size:0.78rem;
                    margin-top:24px;line-height:1.8;">
            New users start with 5,000 V-Coins
            &nbsp;·&nbsp; Earn more by predicting correctly
            &nbsp;·&nbsp; Daily bonus every 20 hours
        </div>
        """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  SHARED COMPONENTS
# ─────────────────────────────────────────────
def pot_total(entries: list) -> int:
    return sum(e["amount"] for e in entries)

def render_bet_card(bet: dict, show_btn=False):
    entries = get_entries(bet["id"])
    pot     = pot_total(entries)

    status_html = {
        "open":   '<span class="pill pill-open">Open</span>',
        "voting": '<span class="pill pill-voting">Voting</span>',
        "closed": '<span class="pill pill-closed">Resolved</span>',
    }.get(bet["status"], "")

    opts_preview = "  vs  ".join(bet["options"][:2])

    st.markdown(f"""
    <div class="card card-accent">
        <div class="vtag">{bet['vtuber_name']}  &middot;  {bet.get('category','')}</div>
        <div class="bet-title">{bet['title']}</div>
        <div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap;">
            {status_html}
            <span class="pot">{pot:,} V-Coins in pot</span>
            <span style="font-size:0.75rem;color:#4a4468;">{opts_preview}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if show_btn:
        if st.button("View", key=f"view_{bet['id']}"):
            nav("bet_detail", bet_id=bet["id"])

def render_vtuber_card(vt: dict, show_btn=True):
    tags_html = "".join(f'<span class="tag">{t}</span>' for t in (vt.get("tags") or []))
    link_html = (f'<a href="{vt["link"]}" target="_blank" '
                 f'style="color:#9d8fff;font-size:0.8rem;text-decoration:none;">'
                 f'Watch on {vt["platform"]} &rarr;</a>') if vt.get("link") else ""

    st.markdown(f"""
    <div class="vt-profile">
        <div class="vt-name">{vt['name']}</div>
        <div class="vt-handle">{vt.get('handle','')}</div>
        <div class="vt-bio">{vt.get('bio','No bio yet.')}</div>
        <div style="margin-bottom:10px;">{tags_html}</div>
        {link_html}
    </div>
    """, unsafe_allow_html=True)

    if show_btn:
        if st.button("View profile", key=f"vt_{vt['id']}"):
            nav("vtuber_profile", vtuber_id=vt["id"])

# ─────────────────────────────────────────────
#  HOME PAGE
# ─────────────────────────────────────────────
def page_home():
    show_toast()
    username = st.session_state.username
    user     = get_or_create_user(username)
    bets     = get_bets()
    vtubers  = get_vtubers()

    st.markdown(f"""
    <div class="hero">
        <div style="font-family:'Syne',sans-serif;font-size:1.8rem;
                    font-weight:800;color:#f0ecff;margin-bottom:6px;">
            Welcome back, {username}
        </div>
        <div style="color:#6b6490;font-size:0.9rem;line-height:1.6;">
            Place your V-Coins on indie VTuber stream moments.<br>
            Help the community discover their next favourite creator.
        </div>
    </div>
    """, unsafe_allow_html=True)

    open_bets   = [b for b in bets if b["status"] == "open"]
    voting_bets = [b for b in bets if b["status"] == "voting"]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Open Bets",    len(open_bets))
    c2.metric("Voting Now",   len(voting_bets))
    c3.metric("VTubers",      len(vtubers))
    c4.metric("Your Balance", f"{user['coins']:,}")

    st.markdown("---")

    # Spotlight
    spotlight = next((v for v in vtubers if v.get("spotlight")), None)
    if spotlight:
        st.markdown("### Spotlight VTuber")
        render_vtuber_card(spotlight)
        st.markdown("---")

    # Open bets
    st.markdown("### Open Bets")
    if not open_bets:
        st.markdown('<div style="color:#6b6490;font-size:0.9rem;margin-bottom:12px;">No open bets right now.</div>',
                    unsafe_allow_html=True)
        if st.button("Create the first one"):
            nav("create_bet")
    else:
        for b in open_bets[:4]:
            render_bet_card(b, show_btn=True)
        if len(open_bets) > 4:
            if st.button("View all open bets"):
                nav("bets")

    # Needs votes
    if voting_bets:
        st.markdown("---")
        st.markdown("### Needs Your Vote")
        for b in voting_bets[:2]:
            render_bet_card(b, show_btn=True)

# ─────────────────────────────────────────────
#  BETS PAGE
# ─────────────────────────────────────────────
def page_bets():
    show_toast()
    bets = get_bets()

    st.markdown("## Bets")

    tab_open, tab_voting, tab_closed = st.tabs(["Open", "Voting", "Resolved"])

    with tab_open:
        ob = [b for b in bets if b["status"] == "open"]
        if not ob:
            st.markdown('<div style="color:#6b6490;">No open bets right now.</div>',
                        unsafe_allow_html=True)
        for b in ob:
            render_bet_card(b, show_btn=True)
        st.markdown("---")
        if st.button("Create a bet", use_container_width=True):
            nav("create_bet")

    with tab_voting:
        vb = [b for b in bets if b["status"] == "voting"]
        if not vb:
            st.markdown('<div style="color:#6b6490;">Nothing in voting phase.</div>',
                        unsafe_allow_html=True)
        for b in vb:
            render_bet_card(b, show_btn=True)

    with tab_closed:
        cb = [b for b in bets if b["status"] == "closed"]
        if not cb:
            st.markdown('<div style="color:#6b6490;">No resolved bets yet.</div>',
                        unsafe_allow_html=True)
        for b in cb:
            render_bet_card(b, show_btn=True)

# ─────────────────────────────────────────────
#  BET DETAIL PAGE
# ─────────────────────────────────────────────
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
    user     = get_or_create_user(username)
    entries  = get_entries(bet_id)
    votes    = get_votes(bet_id)

    if st.button("Back to Bets"):
        nav("bets")

    st.markdown(f"""
    <div class="hero">
        <div class="vtag">{bet['vtuber_name']}  &middot;  {bet.get('category','')}</div>
        <div style="font-family:'Syne',sans-serif;font-size:1.4rem;
                    font-weight:800;color:#f0ecff;margin:6px 0 10px;">{bet['title']}</div>
        <div style="color:#6b6490;font-size:0.88rem;">{bet.get('description','')}</div>
    </div>
    """, unsafe_allow_html=True)

    pot    = pot_total(entries)
    totals = {o: sum(e["amount"] for e in entries if e["option"] == o)
              for o in bet["options"]}

    st.markdown(f"**{pot:,} V-Coins in pot**  &nbsp;·&nbsp;  Created by `{bet['created_by']}`")

    for opt in bet["options"]:
        pct = (totals[opt] / pot * 100) if pot else 0
        st.markdown(f"""
        <div class="bar-wrap">
            <div class="bar-label">
                <span>{opt}</span>
                <span>{totals[opt]:,} ({pct:.0f}%)</span>
            </div>
            <div class="bar-bg">
                <div class="bar-fill" style="width:{pct}%"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    existing = user_entry(bet_id, username)
    if existing:
        st.markdown(f"""
        <div class="notice-success">
            You bet {existing['amount']:,} V-Coins on "{existing['option']}"
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Open
    if bet["status"] == "open":
        st.markdown("### Place Your Bet")
        if existing:
            st.markdown('<div style="color:#6b6490;font-size:0.88rem;">You already have a bet on this one.</div>',
                        unsafe_allow_html=True)
        else:
            col1, col2 = st.columns([2, 1])
            with col1:
                chosen = st.selectbox("Your prediction:", bet["options"])
            with col2:
                amount = st.number_input("V-Coins:", min_value=10,
                                         max_value=min(user["coins"], 99_999),
                                         value=100, step=10)
            st.caption(f"Balance: {user['coins']:,} V-Coins")

            if st.button(f"Place {amount:,} V-Coins on \"{chosen}\"", use_container_width=True):
                if amount > user["coins"]:
                    toast("error", "Not enough V-Coins.")
                else:
                    place_bet_entry(bet_id, username, chosen, amount)
                    toast("success", f"Bet placed — {amount:,} V-Coins on \"{chosen}\"")
                    st.rerun()

        st.markdown("---")
        with st.expander("Stream ended? Close this bet for community voting"):
            st.caption("Move to voting phase once the stream is over.")
            if st.button("Close and start voting"):
                close_bet_for_voting(bet_id)
                toast("success", "Voting phase is now live!")
                st.rerun()

    # Voting
    elif bet["status"] == "voting":
        vote_counts = {o: sum(1 for v in votes if v["option"] == o) for o in bet["options"]}
        total_v     = sum(vote_counts.values())

        st.markdown(f"### Community Vote  ({total_v} / {MIN_VOTES} votes needed)")

        my_vote = user_vote(bet_id, username)
        if my_vote:
            st.markdown(f'<div class="notice-success">You voted: "{my_vote["option"]}"</div>',
                        unsafe_allow_html=True)
        else:
            st.markdown("**What actually happened on stream?**")
            vcols = st.columns(len(bet["options"]))
            for i, opt in enumerate(bet["options"]):
                with vcols[i]:
                    if st.button(f"{opt}  ({vote_counts[opt]})",
                                 key=f"vote_{bet_id}_{i}", use_container_width=True):
                        cast_vote(bet_id, username, opt)
                        toast("success", f"Vote cast for \"{opt}\"")
                        st.rerun()

        for opt in bet["options"]:
            pct = (vote_counts[opt] / total_v * 100) if total_v else 0
            st.markdown(f"""
            <div class="bar-wrap">
                <div class="bar-label">
                    <span>{opt}</span>
                    <span style="color:#fbbf24">{vote_counts[opt]} votes ({pct:.0f}%)</span>
                </div>
                <div class="bar-bg">
                    <div class="bar-fill" style="width:{pct}%;
                         background:linear-gradient(90deg,#b45309,#fbbf24)"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        if total_v >= MIN_VOTES:
            winner_opt = max(vote_counts, key=vote_counts.get)
            if vote_counts[winner_opt] > total_v / 2:
                st.markdown(f'<div class="notice-success">Majority reached — likely winner: "{winner_opt}"</div>',
                            unsafe_allow_html=True)
                if st.button("Resolve and pay out winnings", use_container_width=True):
                    ok, msg = resolve_bet(bet_id)
                    if ok:
                        toast("success", f"Resolved! Winner: \"{msg}\" — V-Coins distributed.")
                    else:
                        toast("error", msg)
                    st.rerun()
        else:
            st.markdown(f'<div style="color:#6b6490;font-size:0.85rem;">Need {MIN_VOTES - total_v} more vote(s).</div>',
                        unsafe_allow_html=True)

    # Closed
    elif bet["status"] == "closed":
        result = bet.get("result")
        st.markdown(f"""
        <div style="background:#0f1a0f;border:1px solid #22c55e44;border-radius:12px;
                    padding:20px 24px;text-align:center;margin:12px 0;">
            <div style="font-size:0.7rem;color:#6b6490;text-transform:uppercase;
                        letter-spacing:0.08em;margin-bottom:6px;">Verified Outcome</div>
            <div style="font-family:'Syne',sans-serif;font-size:1.4rem;
                        font-weight:800;color:#86efac;">{result}</div>
        </div>
        """, unsafe_allow_html=True)

        if existing:
            won = existing["option"] == result
            if won:
                st.markdown('<div class="notice-success">You predicted correctly! Winnings added to your wallet.</div>',
                            unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="notice-error">You bet on "{existing["option"]}" — better luck next time.</div>',
                            unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  CREATE BET PAGE
# ─────────────────────────────────────────────
def page_create_bet():
    show_toast()
    st.markdown("## Create a Bet")
    st.markdown('<div style="color:#6b6490;font-size:0.88rem;margin-bottom:20px;">Submit a prediction for an active or upcoming stream.</div>',
                unsafe_allow_html=True)

    vtubers = get_vtubers()
    if not vtubers:
        st.warning("No approved VTubers listed yet. Nominate one first!")
        if st.button("Nominate a VTuber"):
            nav("nominate")
        return

    vt_names = [f"{v['name']}  ({v['platform']})" for v in vtubers]

    with st.form("create_bet"):
        vt_idx    = st.selectbox("VTuber", range(len(vt_names)),
                                 format_func=lambda i: vt_names[i])
        title     = st.text_input("Bet question",
                                  placeholder="e.g. Will they rage quit before the second boss?")
        desc      = st.text_area("Description (optional)",
                                 placeholder="Add context about what's happening on stream.",
                                 max_chars=280, height=80)
        category  = st.selectbox("Category", CATEGORIES)
        bet_type  = st.radio("Bet type", ["Yes / No", "Over / Under", "Custom"])

        opt1 = opt2 = ""
        if bet_type == "Yes / No":
            opt1, opt2 = "Yes", "No"
            st.info("Options: Yes  and  No")
        elif bet_type == "Over / Under":
            threshold = st.text_input("Threshold", placeholder="e.g. 15 deaths, 20 minutes")
            opt1 = f"Over {threshold}"  if threshold else "Over ?"
            opt2 = f"Under {threshold}" if threshold else "Under ?"
            st.info(f"Options: {opt1}  and  {opt2}")
        else:
            opt1 = st.text_input("Option A", placeholder="e.g. Finishes the game")
            opt2 = st.text_input("Option B", placeholder="e.g. Gets distracted and switches")

        submitted = st.form_submit_button("Submit Bet", use_container_width=True)

        if submitted:
            chosen_vt = vtubers[vt_idx]
            errs = []
            if not title.strip(): errs.append("Bet question is required.")
            if not opt1.strip():  errs.append("Option A is required.")
            if not opt2.strip():  errs.append("Option B is required.")
            if errs:
                for e in errs:
                    toast("error", e)
                st.rerun()
            else:
                create_bet(
                    vtuber_id   = chosen_vt["id"],
                    vtuber_name = chosen_vt["name"],
                    title       = title.strip(),
                    description = desc.strip(),
                    options     = [opt1.strip(), opt2.strip()],
                    category    = category,
                    created_by  = st.session_state.username,
                )
                toast("success", "Bet submitted and now live!")
                nav("bets")

# ─────────────────────────────────────────────
#  DISCOVER PAGE
# ─────────────────────────────────────────────
def page_discover():
    show_toast()
    st.markdown("## Discover VTubers")
    st.markdown('<div style="color:#6b6490;font-size:0.88rem;margin-bottom:20px;">Community-nominated indie creators. Find your next favourite streamer.</div>',
                unsafe_allow_html=True)

    vtubers = get_vtubers()

    if not vtubers:
        st.info("No VTubers listed yet. Be the first to nominate one!")
        if st.button("Nominate a VTuber", use_container_width=True):
            nav("nominate")
        return

    all_tags     = sorted(set(t for v in vtubers for t in (v.get("tags") or [])))
    selected_tag = st.selectbox("Filter by vibe", ["All"] + all_tags)

    filtered = vtubers if selected_tag == "All" else [
        v for v in vtubers if selected_tag in (v.get("tags") or [])
    ]

    bets = get_bets()
    def bet_count(vt):
        return sum(1 for b in bets if b.get("vtuber_id") == vt["id"])

    filtered = sorted(filtered, key=bet_count, reverse=True)

    if not filtered:
        st.markdown('<div style="color:#6b6490;">No VTubers match that tag.</div>',
                    unsafe_allow_html=True)
    else:
        col1, col2 = st.columns(2)
        for i, vt in enumerate(filtered):
            with (col1 if i % 2 == 0 else col2):
                render_vtuber_card(vt)

    st.markdown("---")
    if st.button("Nominate a VTuber not listed here", use_container_width=True):
        nav("nominate")

# ─────────────────────────────────────────────
#  VTUBER PROFILE PAGE
# ─────────────────────────────────────────────
def page_vtuber_profile():
    show_toast()
    vt_id = st.session_state.selected_vtuber
    vt    = get_vtuber(vt_id) if vt_id else None

    if not vt:
        st.error("VTuber not found.")
        if st.button("Back"):
            nav("discover")
        return

    if st.button("Back to Discover"):
        nav("discover")

    tags_html = "".join(f'<span class="tag">{t}</span>' for t in (vt.get("tags") or []))

    st.markdown(f"""
    <div class="hero">
        <div style="font-family:'Syne',sans-serif;font-size:1.8rem;
                    font-weight:800;color:#f0ecff;margin-bottom:4px;">{vt['name']}</div>
        <div style="color:#6b6490;font-size:0.82rem;margin-bottom:12px;">
            {vt.get('handle','')}
        </div>
        <div style="color:#b0a8cc;font-size:0.9rem;line-height:1.6;margin-bottom:12px;">
            {vt.get('bio','No bio yet.')}
        </div>
        <div style="margin-bottom:12px;">{tags_html}</div>
    </div>
    """, unsafe_allow_html=True)

    if vt.get("link"):
        st.markdown(f"[Watch on {vt['platform']} &rarr;]({vt['link']})")

    st.markdown("---")

    all_bets = get_bets()
    related  = [b for b in all_bets if b.get("vtuber_id") == vt_id]
    open_r   = [b for b in related if b["status"] == "open"]
    closed_r = [b for b in related if b["status"] == "closed"]

    st.markdown(f"### Bets featuring {vt['name']}")

    if not related:
        st.markdown('<div style="color:#6b6490;">No bets yet for this VTuber.</div>',
                    unsafe_allow_html=True)
        if st.button("Create the first bet"):
            nav("create_bet")
    else:
        if open_r:
            st.markdown("**Open now:**")
            for b in open_r:
                render_bet_card(b, show_btn=True)
        if closed_r:
            st.markdown("**Past bets:**")
            for b in closed_r[:5]:
                render_bet_card(b, show_btn=True)

# ─────────────────────────────────────────────
#  NOMINATE PAGE
# ─────────────────────────────────────────────
def page_nominate():
    show_toast()
    st.markdown("## Nominate a VTuber")
    st.markdown("""
    <div style="color:#6b6490;font-size:0.88rem;margin-bottom:20px;line-height:1.6;">
        Know a small indie VTuber who deserves more eyes on them?
        Nominate them here and the community can start placing bets on their streams.
        All nominations are reviewed before going live.
    </div>
    """, unsafe_allow_html=True)

    with st.form("nominate"):
        name     = st.text_input("VTuber name *", placeholder="e.g. Chibidoki")
        handle   = st.text_input("Handle / username", placeholder="e.g. @chibidoki")
        platform = st.selectbox("Primary platform", ["Twitch", "YouTube", "Both", "Other"])
        link     = st.text_input("Channel link *", placeholder="https://twitch.tv/...")
        bio      = st.text_area("Short description *",
                                placeholder="What kind of content do they make? What is their vibe?",
                                max_chars=300, height=100)
        tags     = st.multiselect("Vibe tags (pick a few)", VIBE_TAGS)

        submitted = st.form_submit_button("Submit Nomination", use_container_width=True)

        if submitted:
            errs = []
            if not name.strip(): errs.append("Name is required.")
            if not link.strip(): errs.append("Channel link is required.")
            if not bio.strip():  errs.append("Description is required.")
            if errs:
                for e in errs:
                    toast("error", e)
                st.rerun()
            else:
                nominate_vtuber(
                    name         = name.strip(),
                    handle       = handle.strip(),
                    platform     = platform,
                    link         = link.strip(),
                    bio          = bio.strip(),
                    tags         = tags,
                    nominated_by = st.session_state.username,
                )
                toast("success", f"{name} has been nominated! They will appear once approved.")
                nav("discover")

    st.markdown("""
    <div style="color:#4a4468;font-size:0.78rem;margin-top:16px;">
        Guidelines: indie / small VTubers only. No large agency VTubers.
        Please include accurate links and honest descriptions.
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  LEADERBOARD PAGE
# ─────────────────────────────────────────────
def page_leaderboard():
    show_toast()
    st.markdown("## Leaderboard")

    tab_rich, tab_acc = st.tabs(["Most V-Coins", "Most Accurate"])

    with tab_rich:
        st.markdown("### Richest predictors")
        rows = get_leaderboard_rich()
        if not rows:
            st.markdown('<div style="color:#6b6490;">No users yet.</div>', unsafe_allow_html=True)
        for i, u in enumerate(rows):
            rank = f"#{i+1:02d}"
            st.markdown(f"""
            <div class="lb-row">
                <div class="lb-rank">{rank}</div>
                <div class="lb-name">{u['username']}</div>
                <div class="lb-stat">{u['coins']:,} coins</div>
            </div>
            """, unsafe_allow_html=True)

    with tab_acc:
        st.markdown("### Most accurate (min. 1 bet placed)")
        rows = get_leaderboard_accurate()
        if not rows:
            st.markdown('<div style="color:#6b6490;">No data yet.</div>', unsafe_allow_html=True)
        for i, u in enumerate(rows):
            rank = f"#{i+1:02d}"
            pct  = u.get("pct", 0)
            st.markdown(f"""
            <div class="lb-row">
                <div class="lb-rank">{rank}</div>
                <div class="lb-name">{u['username']}</div>
                <div class="lb-stat">
                    {pct*100:.0f}% correct
                    <br><span style="font-size:0.72rem;color:#4a4468;">
                        {u['bets_correct']}/{u['bets_placed']} bets
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("""
    <div style="color:#4a4468;font-size:0.78rem;margin-top:16px;">
        Top 3 earners each week receive a 2,000 V-Coin bonus from the house cut pool.
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  ROUTER
# ─────────────────────────────────────────────
def main():
    if not st.session_state.username:
        page_login()
        return

    render_sidebar()

    p = st.session_state.page
    if   p == "home":           page_home()
    elif p == "bets":           page_bets()
    elif p == "bet_detail":     page_bet_detail()
    elif p == "create_bet":     page_create_bet()
    elif p == "discover":       page_discover()
    elif p == "vtuber_profile": page_vtuber_profile()
    elif p == "nominate":       page_nominate()
    elif p == "leaderboard":    page_leaderboard()
    else:                       page_home()

main()
