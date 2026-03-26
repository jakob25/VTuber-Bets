import streamlit as st
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
#  DESIGN SYSTEM  —  deep navy / electric blue / neon cyan
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Syne:wght@700;800&family=JetBrains+Mono:wght@500&display=swap');

/* ── BASE ── */
*, *::before, *::after { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"] {
    background: #080c18 !important;
    color: #c8d8f0 !important;
    font-family: 'Inter', sans-serif;
}
[data-testid="stSidebar"] {
    background: #090d1c !important;
    border-right: 1px solid #1a2540 !important;
}
h1, h2, h3 {
    font-family: 'Syne', sans-serif !important;
    letter-spacing: -0.02em;
    color: #e8f0ff !important;
}

/* ── GRID BACKGROUND on main area ── */
[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image:
        linear-gradient(rgba(30,60,120,0.07) 1px, transparent 1px),
        linear-gradient(90deg, rgba(30,60,120,0.07) 1px, transparent 1px);
    background-size: 40px 40px;
    pointer-events: none;
    z-index: 0;
}

/* ── CARDS ── */
.card {
    background: #0b0f1e;
    border: 1px solid #151e33;
    border-left: 3px solid #1e3060;
    border-radius: 10px;
    padding: 18px 20px;
    margin-bottom: 12px;
    transition: border-left-color 0.2s, box-shadow 0.2s;
}
.card:hover {
    border-left-color: #0066ff;
    box-shadow: -2px 0 12px rgba(0, 102, 255, 0.15);
}

/* Live bets get the cyan accent */
.card-live {
    border-left-color: #00c8ff;
    box-shadow: -2px 0 10px rgba(0, 200, 255, 0.1);
}
.card-live:hover {
    border-left-color: #00e5ff;
    box-shadow: -2px 0 16px rgba(0, 200, 255, 0.2);
}

/* Voting bets get amber */
.card-voting {
    border-left-color: #ffaa00;
    box-shadow: -2px 0 10px rgba(255, 170, 0, 0.1);
}
.card-voting:hover {
    border-left-color: #ffcc00;
    box-shadow: -2px 0 16px rgba(255, 204, 0, 0.2);
}

/* Resolved bets get muted purple */
.card-closed {
    border-left-color: #4433aa;
}
.card-closed:hover {
    border-left-color: #6655cc;
}

/* ── ANIMATIONS ── */
@keyframes gradient-border {
    0%   { background-position: 0% 50%; }
    50%  { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
@keyframes gradient-text {
    0%   { background-position: 0% 50%; }
    50%  { background-position: 100% 50%; }
   
}
@keyframes pulse-glow {
    0%, 100% { opacity: 0.6; }
    50%       { opacity: 1; }
}

/* ── HERO ── */
.hero-wrap {
    padding: 2px;
    border-radius: 18px;
    background: linear-gradient(135deg, #0044ff, #00ccff, #0044ff, #7700ff);
    background-size: 300% 300%;
    animation: gradient-border 4s ease infinite;
    margin-bottom: 24px;
}
.hero {
    background: #080e20;
    border-radius: 16px;
    padding: 34px 38px;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute;
    top: -60%; right: -15%;
    width: 500px; height: 500px;
    background: radial-gradient(circle, rgba(0,120,255,0.08) 0%, transparent 65%);
    pointer-events: none;
}
.hero::after {
    content: '';
    position: absolute;
    bottom: -40%; left: -10%;
    width: 300px; height: 300px;
    background: radial-gradient(circle, rgba(0,200,255,0.05) 0%, transparent 65%);
    pointer-events: none;
}
.hero-eyebrow {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #1e4080;
    margin-bottom: 10px;
}
.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: 2rem;
    font-weight: 800;
    color: #c8dcff;
    margin-bottom: 4px;
    line-height: 1.2;
}
/* The gradient username — like "Sweet 16" in the reference */
.hero-name {
    font-family: 'Syne', sans-serif;
    font-size: 2rem;
    font-weight: 800;
    font-style: italic;
    background: linear-gradient(45deg, #aa00ff, #00aaff, #44ddff, #0066ff, #00ccff, #aa00ff, #00aaff, #44ddff, #0066ff, #00ccff);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: gradient-text 3s linear infinite;
    display: inline;
}
.hero-sub {
    color: #3a5580;
    font-size: 0.88rem;
    line-height: 1.7;
    margin-top: 10px;
}

/* ── BET CARD TEXT ── */
.vtag {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #4499ff;
    margin-bottom: 6px;
    font-family: 'JetBrains Mono', monospace;
}
.bet-title {
    font-size: 1rem;
    font-weight: 600;
    color: #ddeaff;
    margin-bottom: 6px;
    line-height: 1.45;
}
.bet-game {
    font-size: 0.8rem;
    color: #4a6a99;
    margin-bottom: 10px;
    font-style: italic;
}

/* ── STATUS PILLS ── */
.pill {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 4px;
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    font-family: 'JetBrains Mono', monospace;
}
.pill-open   { background: #001a0d; color: #00ee88; border: 1px solid #00ee8855; }
.pill-voting { background: #1a1000; color: #ffcc00; border: 1px solid #ffcc0055; }
.pill-closed { background: #0a001a; color: #9977ff; border: 1px solid #9977ff55; }

.pot {
    font-size: 0.78rem;
    color: #4499ff;
    font-weight: 600;
    font-family: 'JetBrains Mono', monospace;
}

/* ── PROGRESS BARS ── */
.bar-wrap { margin: 10px 0; }
.bar-label {
    display: flex;
    justify-content: space-between;
    font-size: 0.82rem;
    margin-bottom: 5px;
    color: #7a9acc;
}
.bar-label .bar-pct {
    font-family: 'JetBrains Mono', monospace;
    color: #4499ff;
    font-size: 0.78rem;
}
.bar-bg {
    background: #0a1020;
    border-radius: 3px;
    height: 7px;
    border: 1px solid #1a2a44;
    overflow: hidden;
}
.bar-fill {
    height: 7px;
    border-radius: 3px;
    background: linear-gradient(90deg, #0044cc, #00aaff);
    box-shadow: 0 0 10px rgba(0,170,255,0.5);
}
.bar-fill-vote {
    height: 7px;
    border-radius: 3px;
    background: linear-gradient(90deg, #aa7700, #ffcc00);
    box-shadow: 0 0 10px rgba(255,204,0,0.5);
}

/* ── COIN DISPLAY ── */
.coin-box {
    background: linear-gradient(160deg, #0c1428 0%, #091020 100%);
    border: 1px solid #1a3060;
    border-radius: 12px;
    padding: 16px 18px;
    text-align: center;
    margin-bottom: 10px;
    position: relative;
    overflow: hidden;
}
.coin-box::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, #0066ff66, transparent);
}
.coin-label {
    font-size: 0.68rem;
    color: #2a4a7a;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-bottom: 4px;
    font-family: 'JetBrains Mono', monospace;
}
.coin-amount {
    font-family: 'Syne', sans-serif;
    font-size: 2rem;
    font-weight: 800;
    background: linear-gradient(90deg, #0088ff, #44ccff, #0066ff);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: gradient-text 3s linear infinite;
}
.coin-sub {
    font-size: 0.68rem;
    color: #1e3060;
    margin-top: 2px;
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: 0.1em;
}

/* ── NOTICE BOXES ── */
.notice {
    border-radius: 8px;
    padding: 13px 16px;
    font-size: 0.88rem;
    margin: 10px 0;
    font-weight: 500;
    line-height: 1.5;
}
.notice-success {
    background: #001a0d;
    border: 1px solid #00ee8844;
    color: #00cc77;
}
.notice-warn {
    background: #1a1000;
    border: 1px solid #ffcc0044;
    color: #ddaa00;
}
.notice-error {
    background: #140008;
    border: 1px solid #ff334455;
    color: #ff5577;
}
.notice-info {
    background: #000d1a;
    border: 1px solid #0066ff44;
    color: #5599ff;
}

/* ── LEADERBOARD ── */
.lb-row {
    display: flex;
    align-items: center;
    padding: 12px 16px;
    border-radius: 10px;
    margin-bottom: 6px;
    background: #0b1020;
    border: 1px solid #192540;
    gap: 14px;
    transition: border-color 0.15s, background 0.15s;
}
.lb-row:hover {
    border-color: #0066ff55;
    background: #0d1428;
}
.lb-rank {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.82rem;
    font-weight: 700;
    width: 32px;
    color: #2a3a55;
}
.lb-rank-top { color: #00aaff; }
.lb-name { flex: 1; font-weight: 600; font-size: 0.9rem; color: #b8ccee; }
.lb-stat {
    color: #00aaff;
    font-weight: 700;
    font-size: 0.85rem;
    text-align: right;
    font-family: 'JetBrains Mono', monospace;
}

/* ── STAT CARDS ── */
.stat-card {
    background: #0d1428;
    border: 1px solid #1e3060;
    border-radius: 12px;
    padding: 16px 20px;
}
.stat-val {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.5rem;
    font-weight: 700;
    color: #00aaff;
}
.stat-lbl {
    font-size: 0.75rem;
    color: #2a4060;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-top: 2px;
}

/* ── BUTTONS ── */
.stButton > button {
    background: linear-gradient(135deg, #0044cc, #0077ff) !important;
    color: #e8f4ff !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    transition: box-shadow 0.15s !important;
}
.stButton > button:hover {
    box-shadow: 0 0 20px rgba(0,119,255,0.35) !important;
}

/* ── INPUTS ── */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div {
    background: #0b1020 !important;
    border: 1px solid #1e3060 !important;
    border-radius: 8px !important;
    color: #c8d8f0 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.9rem !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #0066ff !important;
    box-shadow: 0 0 0 2px rgba(0,102,255,0.2) !important;
}
/* make placeholder text visible */
.stTextInput > div > div > input::placeholder,
.stTextArea > div > div > textarea::placeholder {
    color: #2a4060 !important;
}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
    background: #080d1a !important;
    border-radius: 8px;
    gap: 2px;
    padding: 3px;
    border: 1px solid #182035;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #2a4060 !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
    font-size: 0.84rem !important;
    font-family: 'Inter', sans-serif !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #003399, #0055cc) !important;
    color: #e8f4ff !important;
}

/* ── METRIC ── */
[data-testid="metric-container"] {
    background: #0b1020;
    border: 1px solid #192035;
    border-radius: 10px;
    padding: 12px 16px;
}
[data-testid="metric-container"] label {
    color: #2a4060 !important;
    font-size: 0.78rem !important;
    text-transform: uppercase;
    letter-spacing: 0.07em;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #00aaff !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 1.4rem !important;
}

hr { border-color: #192035 !important; }

[data-testid="stExpander"] {
    background: #0b1020;
    border: 1px solid #1e3060;
    border-radius: 10px;
}

/* ── DUPLICATE WARNING ── */
.dup-warn {
    background: #160c00;
    border: 1px solid #ff880044;
    border-radius: 8px;
    padding: 12px 16px;
    font-size: 0.85rem;
    color: #ffaa44;
    margin: 8px 0;
    line-height: 1.5;
}

/* ── STREAM LINK ── */
.stream-link {
    font-size: 0.72rem;
    color: #2277cc;
    text-decoration: none;
    font-family: 'JetBrains Mono', monospace;
    transition: color 0.15s;
}
.stream-link:hover { color: #44aaff; }

/* ── SECTION LABEL ── */
.section-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    color: #1e3a66;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 1px solid #162030;
}

/* ── CAPTION / SMALL TEXT ── */
.stCaption, [data-testid="stCaptionContainer"] {
    color: #3a5578 !important;
    font-size: 0.8rem !important;
}

/* ── RADIO LABELS ── */
.stRadio label { color: #7a9acc !important; font-size: 0.88rem !important; }

/* ── FORM LABELS ── */
.stTextInput label, .stTextArea label, .stSelectbox label,
.stNumberInput label, .stMultiSelect label {
    color: #5577aa !important;
    font-size: 0.84rem !important;
    font-weight: 500 !important;
}

/* ── GENERAL SMALL TEXT fix ── */
p, li, div { line-height: 1.6; }
small, .small { color: #4a6a90 !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  SUPABASE
# ─────────────────────────────────────────────
@st.cache_resource
def get_supabase() -> Client:
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

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
    "Boss Fight", "Death Count", "Game Completion",
    "Yap Session / Just Chatting", "Tech Scuff",
    "Karaoke Arc", "Follower / Sub Goal",
    "Chaos Moment", "Other"
]

# ─────────────────────────────────────────────
#  DB — USERS
# ─────────────────────────────────────────────
def get_user(username: str) -> dict | None:
    r = db().table("users").select("*").eq("username", username).execute()
    return r.data[0] if r.data else None

def get_or_create_user(username: str) -> dict:
    user = get_user(username)
    if user:
        return user
    new = {
        "username":     username,
        "coins":        STARTING_COINS,
        "joined_at":    datetime.utcnow().isoformat(),
        "last_bonus":   None,
        "total_won":    0,
        "bets_correct": 0,
        "bets_placed":  0,
    }
    return db().table("users").insert(new).execute().data[0]

def update_user(username: str, fields: dict):
    db().table("users").update(fields).eq("username", username).execute()

def claim_daily_bonus(username: str) -> tuple[bool, str]:
    user = get_user(username)
    now  = datetime.utcnow()
    last = user.get("last_bonus")
    if last:
        last_dt = datetime.fromisoformat(last.replace("Z", ""))
        if now - last_dt < timedelta(hours=20):
            rem  = timedelta(hours=20) - (now - last_dt)
            h, m = divmod(int(rem.total_seconds() / 60), 60)
            return False, f"Already claimed. Next bonus in {h}h {m}m."
    update_user(username, {"coins": user["coins"] + DAILY_BONUS,
                            "last_bonus": now.isoformat()})
    return True, f"+{DAILY_BONUS} V-Coins claimed."

# ─────────────────────────────────────────────
#  DB — BETS
# ─────────────────────────────────────────────
def get_bets(status: str | None = None) -> list:
    q = db().table("bets").select("*").order("created_at", desc=True)
    if status:
        q = q.eq("status", status)
    return q.execute().data or []

def get_bet(bet_id: str) -> dict | None:
    r = db().table("bets").select("*").eq("id", bet_id).execute()
    return r.data[0] if r.data else None

def check_duplicate(vtuber_name: str, title: str) -> list:
    """Return any open bets for the same VTuber with a similar title."""
    existing = db().table("bets").select("id,title,status") \
                   .eq("status", "open") \
                   .ilike("vtuber_name", f"%{vtuber_name.strip()}%") \
                   .execute().data or []
    title_lower = title.lower().strip()
    dupes = []
    for b in existing:
        b_words = set(b["title"].lower().split())
        t_words  = set(title_lower.split())
        overlap  = b_words & t_words - {"the","a","an","is","will","they","on","of","or","and","in","for"}
        if len(overlap) >= 3:
            dupes.append(b)
    return dupes

def create_bet(vtuber_name: str, stream_link: str, game_or_activity: str,
               title: str, description: str, options: list,
               category: str, created_by: str):
    db().table("bets").insert({
        "id":               str(uuid.uuid4()),
        "vtuber_name":      vtuber_name.strip(),
        "stream_link":      stream_link.strip(),
        "game_or_activity": game_or_activity.strip(),
        "title":            title.strip(),
        "description":      description.strip(),
        "options":          options,
        "status":           "open",
        "created_at":       datetime.utcnow().isoformat(),
        "created_by":       created_by,
        "category":         category,
        "result":           None,
    }).execute()

def close_bet_for_voting(bet_id: str):
    db().table("bets").update({"status": "voting"}).eq("id", bet_id).execute()

# ─────────────────────────────────────────────
#  DB — BET ENTRIES
# ─────────────────────────────────────────────
def get_entries(bet_id: str) -> list:
    return db().table("bet_entries").select("*").eq("bet_id", bet_id).execute().data or []

def user_entry(bet_id: str, username: str) -> dict | None:
    r = db().table("bet_entries").select("*") \
            .eq("bet_id", bet_id).eq("username", username).execute()
    return r.data[0] if r.data else None

def place_entry(bet_id: str, username: str, option: str, amount: int):
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
#  DB — VOTES
# ─────────────────────────────────────────────
def get_votes(bet_id: str) -> list:
    return db().table("votes").select("*").eq("bet_id", bet_id).execute().data or []

def user_vote(bet_id: str, username: str) -> dict | None:
    r = db().table("votes").select("*") \
            .eq("bet_id", bet_id).eq("username", username).execute()
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
#  DB — RESOLUTION
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
        "status": "closed", "result": winner
    }).eq("id", bet_id).execute()
    return True, winner

# ─────────────────────────────────────────────
#  DB — LEADERBOARD
# ─────────────────────────────────────────────
def leaderboard_rich(n=10) -> list:
    return db().table("users") \
               .select("username,coins,total_won,bets_placed,bets_correct") \
               .order("coins", desc=True).limit(n).execute().data or []

def leaderboard_accurate(n=10) -> list:
    rows = db().table("users") \
               .select("username,bets_placed,bets_correct") \
               .gte("bets_placed", 3).execute().data or []
    for r in rows:
        r["pct"] = r["bets_correct"] / r["bets_placed"]
    return sorted(rows, key=lambda x: x["pct"], reverse=True)[:n]

# ─────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────
for k, v in [("username", None), ("page", "home"),
             ("selected_bet", None), ("toast", None)]:
    if k not in st.session_state:
        st.session_state[k] = v

def nav(page: str, bet_id=None):
    st.session_state.page         = page
    st.session_state.selected_bet = bet_id
    st.rerun()

def set_toast(kind: str, msg: str):
    st.session_state.toast = (kind, msg)

def show_toast():
    if st.session_state.toast:
        kind, msg = st.session_state.toast
        css = {"success": "notice-success", "warn": "notice-warn",
               "error": "notice-error", "info": "notice-info"}.get(kind, "notice-info")
        st.markdown(f'<div class="notice {css}">{msg}</div>', unsafe_allow_html=True)
        st.session_state.toast = None

# ─────────────────────────────────────────────
#  SHARED COMPONENTS
# ─────────────────────────────────────────────
def pot_total(entries: list) -> int:
    return sum(e["amount"] for e in entries)

def render_bet_card(bet: dict, show_btn=False):
    entries = get_entries(bet["id"])
    pot     = pot_total(entries)

    card_class = {
        "open":   "card card-live",
        "voting": "card card-voting",
        "closed": "card card-closed",
    }.get(bet["status"], "card")

    status_html = {
        "open":   '<span class="pill pill-open">Live</span>',
        "voting": '<span class="pill pill-voting">Voting</span>',
        "closed": '<span class="pill pill-closed">Resolved</span>',
    }.get(bet["status"], "")

    opts_str = "  /  ".join(bet["options"][:2])

    link = bet.get("stream_link", "")
    name = bet.get("vtuber_name", "")
    name_html = (f'<a href="{link}" target="_blank" class="stream-link">{name}</a>'
                 if link else f'<span style="color:#4499ff">{name}</span>')

    game = bet.get("game_or_activity", "")
    game_html = f'<div class="bet-game">{game}</div>' if game else ""

    st.markdown(f"""
    <div class="{card_class}">
        <div class="vtag">{name_html}&nbsp;&nbsp;·&nbsp;&nbsp;{bet.get('category','')}</div>
        <div class="bet-title">{bet['title']}</div>
        {game_html}
        <div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap;margin-top:4px;">
            {status_html}
            <span class="pot">{pot:,} V-Coins</span>
            <span style="font-size:0.73rem;color:#2a3a55;">{opts_str}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if show_btn:
        if st.button("View", key=f"view_{bet['id']}"):
            nav("bet_detail", bet_id=bet["id"])

# ─────────────────────────────────────────────
#  LOGIN PAGE
# ─────────────────────────────────────────────
def page_login():
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown("""
        <div style="text-align:center;padding:60px 0 40px;">
            <div style="font-family:'JetBrains Mono',monospace;font-size:0.7rem;
                        color:#1e3060;letter-spacing:0.2em;text-transform:uppercase;
                        margin-bottom:16px;">
                PREDICTION PLATFORM
            </div>
            <div style="font-family:'Syne',sans-serif;font-size:3rem;font-weight:800;
                        color:#e8f0ff;line-height:1.1;margin-bottom:12px;">
                VTuberBets
            </div>
            <div style="font-family:'JetBrains Mono',monospace;font-size:0.75rem;
                        color:#0066ff;letter-spacing:0.1em;">
                INDIE VTUBER COMMUNITY PREDICTIONS
            </div>
        </div>
        """, unsafe_allow_html=True)

        show_toast()

        username = st.text_input("", placeholder="Enter a username to get started",
                                 label_visibility="collapsed")

        if st.button("Enter", use_container_width=True):
            un = username.strip()
            if len(un) < 2:
                set_toast("error", "Username must be at least 2 characters.")
                st.rerun()
            elif len(un) > 24:
                set_toast("error", "Username must be 24 characters or fewer.")
                st.rerun()
            else:
                get_or_create_user(un)
                st.session_state.username = un
                nav("home")

        st.markdown("""
        <div style="text-align:center;margin-top:28px;">
            <div style="display:flex;justify-content:center;gap:24px;flex-wrap:wrap;">
                <div style="text-align:center;">
                    <div style="font-family:'JetBrains Mono',monospace;font-size:1.1rem;
                                font-weight:700;color:#00aaff;">5,000</div>
                    <div style="font-size:0.68rem;color:#1e3060;text-transform:uppercase;
                                letter-spacing:0.1em;">Starting V-Coins</div>
                </div>
                <div style="text-align:center;">
                    <div style="font-family:'JetBrains Mono',monospace;font-size:1.1rem;
                                font-weight:700;color:#00aaff;">+250</div>
                    <div style="font-size:0.68rem;color:#1e3060;text-transform:uppercase;
                                letter-spacing:0.1em;">Daily Bonus</div>
                </div>
                <div style="text-align:center;">
                    <div style="font-family:'JetBrains Mono',monospace;font-size:1.1rem;
                                font-weight:700;color:#00aaff;">0</div>
                    <div style="font-size:0.68rem;color:#1e3060;text-transform:uppercase;
                                letter-spacing:0.1em;">Real Money</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
def render_sidebar():
    if not st.session_state.username:
        return
    user = get_or_create_user(st.session_state.username)

    with st.sidebar:
        st.markdown("""
        <div style="padding:12px 0 18px;">
            <div style="font-family:'Syne',sans-serif;font-size:1.2rem;
                        font-weight:800;color:#e8f0ff;">VTuberBets</div>
            <div style="font-family:'JetBrains Mono',monospace;font-size:0.6rem;
                        color:#0066ff;letter-spacing:0.1em;margin-top:2px;">
                PREDICTION PLATFORM
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="coin-box">
            <div class="coin-label">{st.session_state.username}</div>
            <div class="coin-amount">{user['coins']:,}</div>
            <div class="coin-sub">V-COINS</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Claim Daily Bonus  +250", use_container_width=True):
            ok, msg = claim_daily_bonus(st.session_state.username)
            set_toast("success" if ok else "warn", msg)
            st.rerun()

        st.markdown("---")

        pages = [
            ("Home",        "home"),
            ("All Bets",    "bets"),
            ("Create Bet",  "create_bet"),
            ("Leaderboard", "leaderboard"),
        ]
        for label, key in pages:
            if st.button(label, key=f"nav_{key}", use_container_width=True):
                nav(key)

        st.markdown("---")
        c1, c2 = st.columns(2)
        with c1:
            st.metric("Correct", user.get("bets_correct", 0))
        with c2:
            st.metric("Placed",  user.get("bets_placed",  0))

        st.markdown("---")
        if st.button("Log out", use_container_width=True):
            st.session_state.username = None
            st.session_state.page     = "home"
            st.rerun()

# ─────────────────────────────────────────────
#  HOME PAGE
# ─────────────────────────────────────────────
def page_home():
    show_toast()
    user  = get_or_create_user(st.session_state.username)
    bets  = get_bets()
    open_bets   = [b for b in bets if b["status"] == "open"]
    voting_bets = [b for b in bets if b["status"] == "voting"]

    st.markdown(f"""
    <div class="hero-wrap">
        <div class="hero">
            <div class="hero-eyebrow">Prediction Platform &nbsp;·&nbsp; Indie VTubers</div>
            <div class="hero-title">Welcome back, <span class="hero-name">{st.session_state.username}</span></div>
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
        st.markdown("""
        <div class="notice notice-info">
            No open bets right now. Be the first to create one.
        </div>
        """, unsafe_allow_html=True)
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
# ─────────────────────────────────────────────
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

    # Header
    link = bet.get("stream_link", "")
    name = bet.get("vtuber_name", "")
    name_html = (f'<a href="{link}" target="_blank" style="color:#4499ff;'
                 f'text-decoration:none;font-weight:700;">{name}</a>'
                 if link else f'<span style="color:#4499ff;font-weight:700;">{name}</span>')

    game = bet.get("game_or_activity", "")

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

    # Pot bars
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
            <div class="bar-bg">
                <div class="bar-fill" style="width:{pct}%"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    existing = user_entry(bet_id, username)
    if existing:
        st.markdown(f"""
        <div class="notice notice-success">
            You have {existing['amount']:,} V-Coins on "{existing['option']}"
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ── OPEN ──
    if bet["status"] == "open":
        st.markdown("### Place Your Bet")
        if existing:
            st.markdown('<div style="color:#334466;font-size:0.85rem;">You already have a bet on this one.</div>',
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

            if st.button(f"Place {amount:,} on \"{chosen}\"", use_container_width=True):
                if amount > user["coins"]:
                    set_toast("error", "Insufficient V-Coins.")
                else:
                    place_entry(bet_id, username, chosen, amount)
                    set_toast("success", f"Bet placed — {amount:,} V-Coins on \"{chosen}\"")
                    st.rerun()

        st.markdown("---")
        with st.expander("Stream ended? Close this bet for community voting."):
            st.caption("Once the stream is over, move this bet into voting phase so the community can decide the outcome.")
            if st.button("Close and start voting"):
                close_bet_for_voting(bet_id)
                set_toast("success", "Voting phase is now open.")
                st.rerun()

    # ── VOTING ──
    elif bet["status"] == "voting":
        vc      = {o: sum(1 for v in votes if v["option"] == o) for o in bet["options"]}
        total_v = sum(vc.values())

        st.markdown(f"### Community Vote")
        st.markdown(f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:0.75rem;'
                    f'color:#334466;margin-bottom:14px;">{total_v} / {MIN_VOTES} votes to resolve</div>',
                    unsafe_allow_html=True)

        my_vote = user_vote(bet_id, username)
        if my_vote:
            st.markdown(f'<div class="notice notice-success">You voted: "{my_vote["option"]}"</div>',
                        unsafe_allow_html=True)
        else:
            st.markdown("**What actually happened?**")
            vcols = st.columns(len(bet["options"]))
            for i, opt in enumerate(bet["options"]):
                with vcols[i]:
                    if st.button(f"{opt}  ({vc[opt]})",
                                 key=f"v_{bet_id}_{i}", use_container_width=True):
                        cast_vote(bet_id, username, opt)
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
                <div class="bar-bg">
                    <div class="bar-fill-vote" style="width:{pct}%"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        if total_v >= MIN_VOTES:
            winner_opt = max(vc, key=vc.get)
            if vc[winner_opt] > total_v / 2:
                st.markdown(f'<div class="notice notice-success">Clear majority — "{winner_opt}"</div>',
                            unsafe_allow_html=True)
                if st.button("Resolve and distribute winnings", use_container_width=True):
                    ok, msg = resolve_bet(bet_id)
                    set_toast("success" if ok else "error",
                              f"Resolved: \"{msg}\" — winnings distributed." if ok else msg)
                    st.rerun()
        else:
            remain = MIN_VOTES - total_v
            st.markdown(f'<div style="color:#334466;font-size:0.82rem;">Need {remain} more vote(s) to resolve.</div>',
                        unsafe_allow_html=True)

    # ── CLOSED ──
    elif bet["status"] == "closed":
        result = bet.get("result", "")
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
                st.markdown('<div class="notice notice-success">You predicted correctly. Winnings have been added to your wallet.</div>',
                            unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="notice notice-error">You predicted "{existing["option"]}". Better luck next time.</div>',
                            unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  CREATE BET PAGE
# ─────────────────────────────────────────────
def page_create_bet():
    show_toast()
    st.markdown("## Create a Bet")
    st.markdown('<div style="color:#334466;font-size:0.85rem;margin-bottom:20px;">Submit a prediction for a live or upcoming stream. One bet per moment — keep it specific.</div>',
                unsafe_allow_html=True)

    username = st.session_state.username

    with st.form("create_bet", clear_on_submit=True):
        st.markdown('<div class="section-label">VTuber</div>', unsafe_allow_html=True)
        vtuber_name = st.text_input("VTuber name *",
                                    placeholder="e.g. Filian, Chibidoki, your oshi...",
                                    label_visibility="collapsed")
        stream_link = st.text_input("Stream link (Twitch / YouTube / etc.)",
                                    placeholder="https://twitch.tv/...",
                                    label_visibility="visible")

        st.markdown('<div class="section-label" style="margin-top:16px;">Stream Context</div>',
                    unsafe_allow_html=True)
        game_or_activity = st.text_input("Game or activity *",
                                         placeholder="e.g. Elden Ring, Minecraft, Just Chatting, Karaoke...")

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
        bet_type = st.radio("Bet type", ["Yes / No", "Over / Under", "Custom"],
                            horizontal=True)

        opt1 = opt2 = ""
        if bet_type == "Yes / No":
            opt1, opt2 = "Yes", "No"
            st.markdown('<div class="notice notice-info" style="margin-top:4px;">Options: Yes  /  No</div>',
                        unsafe_allow_html=True)
        elif bet_type == "Over / Under":
            threshold = st.text_input("Threshold", placeholder="e.g. 15 deaths, 20 minutes")
            opt1 = f"Over {threshold}"  if threshold else "Over ?"
            opt2 = f"Under {threshold}" if threshold else "Under ?"
            st.markdown(f'<div class="notice notice-info" style="margin-top:4px;">Options: {opt1}  /  {opt2}</div>',
                        unsafe_allow_html=True)
        else:
            col1, col2 = st.columns(2)
            with col1:
                opt1 = st.text_input("Option A *", placeholder="e.g. Finishes the game")
            with col2:
                opt2 = st.text_input("Option B *", placeholder="e.g. Rage quits")

        submitted = st.form_submit_button("Submit Bet", use_container_width=True)

        if submitted:
            errs = []
            if not vtuber_name.strip():     errs.append("VTuber name is required.")
            if not game_or_activity.strip(): errs.append("Game or activity is required.")
            if not title.strip():           errs.append("Bet question is required.")
            if not opt1.strip():            errs.append("Option A is required.")
            if not opt2.strip():            errs.append("Option B is required.")

            if errs:
                for e in errs:
                    set_toast("error", e)
                st.rerun()
            else:
                # Duplicate check
                dupes = check_duplicate(vtuber_name, title)
                if dupes:
                    dupe_titles = ", ".join(f'"{d["title"][:50]}"' for d in dupes[:2])
                    st.markdown(f"""
                    <div class="dup-warn">
                        Similar bet may already exist: {dupe_titles}<br>
                        <span style="font-size:0.75rem;color:#886633;">
                            Check the open bets list before submitting to avoid duplicates.
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    create_bet(
                        vtuber_name      = vtuber_name,
                        stream_link      = stream_link,
                        game_or_activity = game_or_activity,
                        title            = title,
                        description      = desc,
                        options          = [opt1.strip(), opt2.strip()],
                        category         = category,
                        created_by       = username,
                    )
                    set_toast("success", "Bet is now live.")
                    nav("bets")

# ─────────────────────────────────────────────
#  LEADERBOARD PAGE
# ─────────────────────────────────────────────
def page_leaderboard():
    show_toast()
    st.markdown("## Leaderboard")

    tab_rich, tab_acc = st.tabs(["Most V-Coins", "Most Accurate"])

    with tab_rich:
        st.markdown("### Richest Predictors")
        rows = leaderboard_rich()
        if not rows:
            st.markdown('<div style="color:#334466;padding:12px 0;">No users yet.</div>',
                        unsafe_allow_html=True)
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
        st.markdown("### Most Accurate  (min. 3 bets placed)")
        rows = leaderboard_accurate()
        if not rows:
            st.markdown('<div style="color:#334466;padding:12px 0;">Not enough data yet.</div>',
                        unsafe_allow_html=True)
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
                    <br><span style="font-size:0.68rem;color:#1e3060;">
                        {u['bets_correct']}/{u['bets_placed']}
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("""
    <div style="color:#1e3060;font-size:0.75rem;margin-top:16px;
                font-family:'JetBrains Mono',monospace;">
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
    if   p == "home":       page_home()
    elif p == "bets":       page_bets()
    elif p == "bet_detail": page_bet_detail()
    elif p == "create_bet": page_create_bet()
    elif p == "leaderboard": page_leaderboard()
    else:                   page_home()

main()
