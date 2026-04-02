import streamlit as st
import uuid
import bcrypt
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
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Syne:wght@700;800&family=JetBrains+Mono:wght@500&display=swap');

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

/* ── ANIMATIONS ── */
@keyframes gradient-border {
    0%   { background-position: 0% 50%; }
    50%  { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
@keyframes gradient-text {
    0%   { background-position: -4% 50%; }
    100% { background-position: 100% 50%; }
}

/* ── HERO ── */
.hero-wrap {
    padding: 2px;
    border-radius: 18px;
    background: linear-gradient(135deg, #0044ff, #00ccff, #aa00ff, #0044ff);
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
.hero-name {
    font-family: 'Syne', sans-serif;
    font-size: 2rem;
    font-weight: 800;
    font-style: italic;
    background: linear-gradient(45deg, #44ddff, #aa00ff, #00aaff, #0066ff, #00ccff, #44ddff, #aa00ff, #00aaff, #0066ff, #00ccff);
    background-size: 400% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: gradient-text 4.3s linear infinite;
    display: inline;
}
.hero-sub {
    color: #3a5580;
    font-size: 0.88rem;
    line-height: 1.7;
    margin-top: 10px;
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
.card:hover { border-left-color: #0066ff; box-shadow: -2px 0 12px rgba(0,102,255,0.15); }
.card-live   { border-left-color: #00c8ff; box-shadow: -2px 0 10px rgba(0,200,255,0.1); }
.card-live:hover { border-left-color: #00e5ff; box-shadow: -2px 0 16px rgba(0,200,255,0.2); }
.card-voting { border-left-color: #ffaa00; box-shadow: -2px 0 10px rgba(255,170,0,0.1); }
.card-voting:hover { border-left-color: #ffcc00; box-shadow: -2px 0 16px rgba(255,204,0,0.2); }
.card-closed { border-left-color: #4433aa; }
.card-closed:hover { border-left-color: #6655cc; }

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

/* ── PILLS ── */
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

.pot { font-size: 0.78rem; color: #4499ff; font-weight: 600; font-family: 'JetBrains Mono', monospace; }

/* ── BARS ── */
.bar-wrap { margin: 10px 0; }
.bar-label { display: flex; justify-content: space-between; font-size: 0.82rem; margin-bottom: 5px; color: #7a9acc; }
.bar-label .bar-pct { font-family: 'JetBrains Mono', monospace; color: #4499ff; font-size: 0.78rem; }
.bar-bg { background: #0a1020; border-radius: 3px; height: 7px; border: 1px solid #1a2a44; overflow: hidden; }
.bar-fill { height: 7px; border-radius: 3px; background: linear-gradient(90deg, #0044cc, #00aaff); box-shadow: 0 0 10px rgba(0,170,255,0.5); }
.bar-fill-vote { height: 7px; border-radius: 3px; background: linear-gradient(90deg, #aa7700, #ffcc00); box-shadow: 0 0 10px rgba(255,204,0,0.5); }

/* ── COIN BOX ── */
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
.coin-label { font-size: 0.68rem; color: #2a4a7a; text-transform: uppercase; letter-spacing: 0.12em; margin-bottom: 4px; font-family: 'JetBrains Mono', monospace; }
.coin-amount {
    font-family: 'Syne', sans-serif;
    font-size: 2rem;
    font-weight: 800;
    background: linear-gradient(45deg, #44ddff, #aa00ff, #00aaff, #0066ff, #00ccff, #44ddff, #aa00ff, #00aaff, #0066ff, #00ccff);
    background-size: 400% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: gradient-text 4.3s linear infinite;
}
.coin-sub { font-size: 0.68rem; color: #1e3060; margin-top: 2px; font-family: 'JetBrains Mono', monospace; letter-spacing: 0.1em; }

/* ── NOTICES ── */
.notice { border-radius: 8px; padding: 13px 16px; font-size: 0.88rem; margin: 10px 0; font-weight: 500; line-height: 1.5; }
.notice-success { background: #001a0d; border: 1px solid #00ee8844; color: #00cc77; }
.notice-warn    { background: #1a1000; border: 1px solid #ffcc0044; color: #ddaa00; }
.notice-error   { background: #140008; border: 1px solid #ff334455; color: #ff5577; }
.notice-info    { background: #000d1a; border: 1px solid #0066ff44; color: #5599ff; }

/* ── LEADERBOARD ── */
.lb-row {
    display: flex; align-items: center; padding: 12px 16px;
    border-radius: 10px; margin-bottom: 6px; background: #0b1020;
    border: 1px solid #192540; gap: 14px; transition: border-color 0.15s, background 0.15s;
}
.lb-row:hover { border-color: #0066ff55; background: #0d1428; }
.lb-rank { font-family: 'JetBrains Mono', monospace; font-size: 0.82rem; font-weight: 700; width: 32px; color: #2a3a55; }
.lb-rank-top { color: #00aaff; }
.lb-name { flex: 1; font-weight: 600; font-size: 0.9rem; color: #b8ccee; }
.lb-stat { color: #00aaff; font-weight: 700; font-size: 0.85rem; text-align: right; font-family: 'JetBrains Mono', monospace; }
.lb-stat-loss { color: #ff5577; font-weight: 700; font-size: 0.85rem; text-align: right; font-family: 'JetBrains Mono', monospace; }

/* ── BADGE ── */
.badge {
    display: inline-block;
    background: #0d1428;
    border: 1px solid #1e3060;
    border-radius: 6px;
    padding: 4px 10px;
    font-size: 0.72rem;
    font-weight: 600;
    color: #5599ff;
    margin: 3px;
    font-family: 'JetBrains Mono', monospace;
}
.badge-earned {
    background: linear-gradient(135deg, #0a1428, #0d1e3a);
    border-color: #0066ff55;
    color: #44aaff;
}
.badge-gem    { border-color: #00ee8855; color: #00ee88; }
.badge-roller { border-color: #ffcc0055; color: #ffcc00; }
.badge-vote   { border-color: #aa00ff55; color: #cc44ff; }
.badge-scout  { border-color: #00c8ff55; color: #00c8ff; }
.badge-raid   { border-color: #ff558855; color: #ff5588; }

/* ── TITLE PREFIX ── */
.user-title {
    font-size: 0.7rem;
    font-family: 'JetBrains Mono', monospace;
    color: #4499ff;
    letter-spacing: 0.06em;
    margin-bottom: 2px;
}

/* ── PROFILE CARD ── */
.profile-card {
    background: #0b0f1e;
    border: 1px solid #1e3060;
    border-radius: 14px;
    padding: 24px 28px;
    margin-bottom: 16px;
}
.profile-role {
    display: inline-block;
    padding: 3px 12px;
    border-radius: 4px;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    font-family: 'JetBrains Mono', monospace;
    margin-bottom: 10px;
}
.role-watcher  { background: #001a2e; color: #00aaff; border: 1px solid #00aaff44; }
.role-streamer { background: #1a0028; color: #cc44ff; border: 1px solid #cc44ff44; }
.role-clipper  { background: #001a0d; color: #00ee88; border: 1px solid #00ee8844; }

/* ── SHOP ── */
.shop-item {
    background: #0b0f1e;
    border: 1px solid #1e3060;
    border-radius: 10px;
    padding: 16px 18px;
    margin-bottom: 10px;
    transition: border-color 0.2s;
}
.shop-item:hover { border-color: #0066ff55; }
.shop-item-name { font-weight: 700; font-size: 0.95rem; color: #ddeaff; margin-bottom: 4px; }
.shop-item-desc { font-size: 0.8rem; color: #4a6a99; margin-bottom: 10px; }
.shop-item-cost { font-family: 'JetBrains Mono', monospace; font-size: 0.82rem; color: #4499ff; font-weight: 700; }
.shop-owned { border-color: #00ee8844; }

/* ── HOW IT WORKS ── */
.hiw-section {
    background: #0b0f1e;
    border: 1px solid #1e3060;
    border-left: 3px solid #0066ff;
    border-radius: 10px;
    padding: 20px 24px;
    margin-bottom: 14px;
}
.hiw-num {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    color: #0066ff;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-bottom: 6px;
}
.hiw-title { font-family: 'Syne', sans-serif; font-size: 1.1rem; font-weight: 800; color: #e8f0ff; margin-bottom: 8px; }
.hiw-body { font-size: 0.88rem; color: #6a88aa; line-height: 1.7; }

/* ── BUTTONS ── */
.stButton > button {
    background: linear-gradient(135deg, #0044cc, #0077ff) !important;
    color: #e8f4ff !important; border: none !important; border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important; font-weight: 600 !important;
    transition: box-shadow 0.15s !important;
}
.stButton > button:hover { box-shadow: 0 0 20px rgba(0,119,255,0.35) !important; }

/* ── INPUTS ── */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div {
    background: #0b1020 !important; border: 1px solid #1e3060 !important;
    border-radius: 8px !important; color: #c8d8f0 !important;
    font-family: 'Inter', sans-serif !important; font-size: 0.9rem !important;
}
.stTextInput > div > div > input::placeholder,
.stTextArea > div > div > textarea::placeholder { color: #2a4060 !important; }
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #0066ff !important;
    box-shadow: 0 0 0 2px rgba(0,102,255,0.2) !important;
}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
    background: #080d1a !important; border-radius: 8px; gap: 2px;
    padding: 3px; border: 1px solid #182035;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important; color: #2a4060 !important;
    border-radius: 6px !important; font-weight: 600 !important;
    font-size: 0.84rem !important; font-family: 'Inter', sans-serif !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #003399, #0055cc) !important;
    color: #e8f4ff !important;
}

/* ── METRICS ── */
[data-testid="metric-container"] {
    background: #0b1020; border: 1px solid #192035; border-radius: 10px; padding: 12px 16px;
}
[data-testid="metric-container"] label { color: #2a4060 !important; font-size: 0.78rem !important; text-transform: uppercase; letter-spacing: 0.07em; }
[data-testid="metric-container"] [data-testid="stMetricValue"] { color: #00aaff !important; font-family: 'JetBrains Mono', monospace !important; font-size: 1.4rem !important; }

hr { border-color: #192035 !important; }
[data-testid="stExpander"] { background: #0b1020; border: 1px solid #1e3060; border-radius: 10px; }

.dup-warn { background: #160c00; border: 1px solid #ff880044; border-radius: 8px; padding: 12px 16px; font-size: 0.85rem; color: #ffaa44; margin: 8px 0; line-height: 1.5; }
.stream-link { font-size: 0.72rem; color: #2277cc; text-decoration: none; font-family: 'JetBrains Mono', monospace; transition: color 0.15s; }
.stream-link:hover { color: #44aaff; }
.section-label { font-family: 'JetBrains Mono', monospace; font-size: 0.68rem; color: #1e3a66; text-transform: uppercase; letter-spacing: 0.15em; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid #162030; }
.stCaption, [data-testid="stCaptionContainer"] { color: #3a5578 !important; font-size: 0.8rem !important; }
.stRadio label { color: #7a9acc !important; font-size: 0.88rem !important; }
.stTextInput label, .stTextArea label, .stSelectbox label, .stNumberInput label, .stMultiSelect label { color: #5577aa !important; font-size: 0.84rem !important; font-weight: 500 !important; }
p, li, div { line-height: 1.6; }
</style>

/* ── HIDE STREAMLIT HUD ── */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
.stApp header {display: none;}
.stDeployButton {display: none;}

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
MIN_VOTES      = 3
FALLBACK_DAYS  = 6

CATEGORIES = [
    "Hidden Gem", "Boss Fight", "Death Count", "Game Completion",
    "Yap Session / Just Chatting", "Tech Scuff", "Karaoke Arc",
    "Follower / Sub Goal", "Raid / Shoutout", "Chaos Moment", "Other"
]

ROLES = ["Watcher", "Streamer", "Clipper"]

BADGE_STYLES = {
    "gem_hunter":     "badge-gem",
    "high_roller":    "badge-roller",
    "first_vote":     "badge-vote",
    "indie_scout":    "badge-scout",
    "raid_master":    "badge-raid",
    "clipper_legend": "badge-scout",
}

# ─────────────────────────────────────────────
#  AUTH HELPERS
# ─────────────────────────────────────────────
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except Exception:
        return False

def register_user(username: str, password: str) -> tuple[bool, str]:
    existing = db().table("users").select("username").eq("username", username).execute()
    if existing.data:
        return False, "Username already taken."
    pw_hash = hash_password(password)
    db().table("users").insert({
        "username":      username,
        "password_hash": pw_hash,
        "coins":         STARTING_COINS,
        "joined_at":     datetime.utcnow().isoformat(),
        "last_bonus":    None,
        "total_won":     0,
        "total_lost":    0,
        "biggest_win":   0,
        "biggest_loss":  0,
        "bets_correct":  0,
        "bets_placed":   0,
        "role":          None,
        "bio":           "",
        "favorite_vtubers": "",
    }).execute()
    return True, "Account created."

def login_user(username: str, password: str) -> tuple[bool, str]:
    r = db().table("users").select("*").eq("username", username).execute()
    if not r.data:
        return False, "Username not found."
    user = r.data[0]
    if not user.get("password_hash"):
        return False, "This account was created before passwords were added. Please contact support."
    if not verify_password(password, user["password_hash"]):
        return False, "Incorrect password."
    return True, "OK"

# ─────────────────────────────────────────────
#  DB — USERS
# ─────────────────────────────────────────────
def get_user(username: str) -> dict | None:
    r = db().table("users").select("*").eq("username", username).execute()
    return r.data[0] if r.data else None

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
    update_user(username, {
        "coins":      user["coins"] + DAILY_BONUS,
        "last_bonus": now.isoformat(),
    })
    return True, f"+{DAILY_BONUS} V-Coins claimed."

def needs_role_selection(username: str) -> bool:
    user = get_user(username)
    return not user.get("role")

def set_user_role(username: str, role: str):
    update_user(username, {"role": role})

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
    existing = db().table("bets").select("id,title,status") \
                   .eq("status", "open") \
                   .ilike("vtuber_name", f"%{vtuber_name.strip()}%").execute().data or []
    title_lower = title.lower().strip()
    stop = {"the","a","an","is","will","they","on","of","or","and","in","for","their","this","does"}
    dupes = []
    for b in existing:
        b_words = set(b["title"].lower().split()) - stop
        t_words  = set(title_lower.split()) - stop
        if len(b_words & t_words) >= 3:
            dupes.append(b)
    return dupes

def create_bet(vtuber_name, stream_link, game_or_activity,
               title, description, options, category, created_by):
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

def cast_vote(bet_id: str, username: str, option: str) -> bool:
    """Returns True if this vote triggered auto-resolution."""
    db().table("votes").insert({
        "id":         str(uuid.uuid4()),
        "bet_id":     bet_id,
        "username":   username,
        "option":     option,
        "created_at": datetime.utcnow().isoformat(),
    }).execute()
    # Check if this was the deciding vote
    votes   = get_votes(bet_id)
    bet     = get_bet(bet_id)
    counts  = {o: sum(1 for v in votes if v["option"] == o) for o in bet["options"]}
    total_v = sum(counts.values())
    if total_v >= MIN_VOTES:
        winner = max(counts, key=counts.get)
        if counts[winner] > total_v / 2:
            ok, _ = resolve_bet(bet_id)
            if ok:
                # Award First to Vote achievement
                check_and_award_first_vote(username)
                return True
    return False

# ─────────────────────────────────────────────
#  DB — RESOLUTION
# ─────────────────────────────────────────────
def pot_total(entries: list) -> int:
    return sum(e["amount"] for e in entries)

def resolve_bet(bet_id: str) -> tuple[bool, str]:
    bet     = get_bet(bet_id)
    entries = get_entries(bet_id)
    votes   = get_votes(bet_id)

    if not bet or bet["status"] not in ("voting", "open"):
        return False, "Bet cannot be resolved."

    counts  = {o: 0 for o in bet["options"]}
    for v in votes:
        counts[v["option"]] = counts.get(v["option"], 0) + 1
    total_v = sum(counts.values())

    if total_v == 0:
        return False, "No votes cast yet."

    winner = max(counts, key=counts.get)

    # Check majority (unless fallback)
    if counts[winner] <= total_v / 2 and total_v < MIN_VOTES:
        return False, "No clear majority yet."

    pot           = pot_total(entries)
    distributable = int(pot * (1 - HOUSE_CUT))
    winners       = [e for e in entries if e["option"] == winner]
    winner_stake  = sum(e["amount"] for e in winners)

    for e in winners:
        share = int(distributable * e["amount"] / winner_stake) if winner_stake else 0
        user  = get_user(e["username"])
        if user:
            new_total_won = user.get("total_won", 0) + share
            new_biggest   = max(user.get("biggest_win", 0), share)
            update_user(e["username"], {
                "coins":        user["coins"] + share,
                "total_won":    new_total_won,
                "biggest_win":  new_biggest,
                "bets_correct": user.get("bets_correct", 0) + 1,
            })
            # Re-fetch user so achievement checks see updated total_won
            check_and_award_achievements(e["username"], bet, share)

    # Track losses for losing bettors
    for e in entries:
        if e["option"] != winner:
            user = get_user(e["username"])
            if user:
                new_lost     = user.get("total_lost", 0) + e["amount"]
                new_big_loss = max(user.get("biggest_loss", 0), e["amount"])
                update_user(e["username"], {
                    "total_lost":   new_lost,
                    "biggest_loss": new_big_loss,
                })

    db().table("bets").update({
        "status": "closed", "result": winner
    }).eq("id", bet_id).execute()
    return True, winner

def check_fallback_resolutions():
    """Call this on page load to auto-resolve stale voting bets."""
    voting_bets = get_bets("voting")
    now = datetime.utcnow()
    for bet in voting_bets:
        created = datetime.fromisoformat(bet["created_at"].replace("Z",""))
        if now - created > timedelta(days=FALLBACK_DAYS):
            resolve_bet(bet["id"])

# ─────────────────────────────────────────────
#  DB — ACHIEVEMENTS
# ─────────────────────────────────────────────
def get_all_achievements() -> list:
    return db().table("achievements").select("*").execute().data or []

def get_user_badges(username: str) -> list:
    return db().table("user_badges").select("*") \
               .eq("username", username).execute().data or []

def has_badge(username: str, achievement_id: str) -> bool:
    r = db().table("user_badges").select("id") \
            .eq("username", username).eq("achievement_id", achievement_id).execute()
    return bool(r.data)

def award_badge(username: str, achievement_id: str, reward_coins: int = 0):
    if has_badge(username, achievement_id):
        return
    db().table("user_badges").insert({
        "id":             str(uuid.uuid4()),
        "username":       username,
        "achievement_id": achievement_id,
        "earned_at":      datetime.utcnow().isoformat(),
    }).execute()
    if reward_coins > 0:
        user = get_user(username)
        if user:
            update_user(username, {"coins": user["coins"] + reward_coins})

def check_and_award_achievements(username: str, bet: dict, payout: int):
    """
    Called after a bet resolves for a winning bettor.
    bet = the resolved bet dict, payout = coins they received.
    """
    user = get_user(username)
    if not user:
        return

    newly_earned = []

    # ── High Roller — 10,000+ V-Coins won lifetime ──
    if not has_badge(username, "high_roller"):
        if user.get("total_won", 0) >= 10_000:
            award_badge(username, "high_roller", 2000)
            newly_earned.append("High Roller")

    # ── Gem Hunter — 5+ correct Hidden Gem bets ──
    if not has_badge(username, "gem_hunter"):
        if bet.get("category") == "Hidden Gem":
            # Only count closed Hidden Gem bets this user entered correctly
            gem_entries = db().table("bet_entries") \
                              .select("bet_id,option") \
                              .eq("username", username).execute().data or []
            gem_bet_ids = [e["bet_id"] for e in gem_entries]
            if gem_bet_ids:
                gem_bets = db().table("bets") \
                               .select("id,result,category") \
                               .eq("status", "closed") \
                               .eq("category", "Hidden Gem") \
                               .in_("id", gem_bet_ids).execute().data or []
                correct = sum(
                    1 for gb in gem_bets
                    for e in gem_entries
                    if e["bet_id"] == gb["id"] and e["option"] == gb.get("result")
                )
                if correct >= 5:
                    award_badge(username, "gem_hunter", 800)
                    newly_earned.append("Gem Hunter")

    # ── Raid Master — 10+ correct Raid/Shoutout bets ──
    if not has_badge(username, "raid_master"):
        if bet.get("category") == "Raid / Shoutout":
            raid_entries = db().table("bet_entries") \
                               .select("bet_id,option") \
                               .eq("username", username).execute().data or []
            raid_bet_ids = [e["bet_id"] for e in raid_entries]
            if raid_bet_ids:
                raid_bets = db().table("bets") \
                                .select("id,result,category") \
                                .eq("status", "closed") \
                                .eq("category", "Raid / Shoutout") \
                                .in_("id", raid_bet_ids).execute().data or []
                correct = sum(
                    1 for rb in raid_bets
                    for e in raid_entries
                    if e["bet_id"] == rb["id"] and e["option"] == rb.get("result")
                )
                if correct >= 10:
                    award_badge(username, "raid_master", 0)
                    newly_earned.append("Raid Master")

    # ── Indie Scout — bets on 20+ different VTubers ──
    if not has_badge(username, "indie_scout"):
        all_entries = db().table("bet_entries") \
                          .select("bet_id") \
                          .eq("username", username).execute().data or []
        if len(all_entries) >= 20:
            bet_ids = [e["bet_id"] for e in all_entries]
            placed  = db().table("bets") \
                          .select("vtuber_name") \
                          .in_("id", bet_ids).execute().data or []
            unique  = len(set(b["vtuber_name"].lower().strip() for b in placed))
            if unique >= 20:
                award_badge(username, "indie_scout", 0)
                newly_earned.append("Indie Scout")

    return newly_earned

def check_and_award_first_vote(username: str):
    """Called when a user casts the deciding vote."""
    if has_badge(username, "first_vote"):
        return
    # Count how many times this user cast a deciding vote
    # We track this by checking if their vote was the MIN_VOTES-th vote
    # Simple approach: store a counter in user record (we'll use bets_correct proxy)
    # For now we check resolved bets where they voted and were the last vote
    # This is an approximation — good enough for MVP
    user = get_user(username)
    if not user:
        return
    deciding_count = user.get("deciding_votes", 0)
    deciding_count += 1
    update_user(username, {"deciding_votes": deciding_count})
    if deciding_count >= 5:
        award_badge(username, "first_vote", 0)

# ─────────────────────────────────────────────
#  DB — COSMETIC SHOP
# ─────────────────────────────────────────────
def get_shop_items() -> list:
    return db().table("cosmetic_items").select("*").order("cost").execute().data or []

def get_user_cosmetics(username: str) -> list:
    return db().table("user_cosmetics").select("*") \
               .eq("username", username).execute().data or []

def owns_item(username: str, item_id: str) -> bool:
    r = db().table("user_cosmetics").select("id") \
            .eq("username", username).eq("item_id", item_id).execute()
    return bool(r.data)

def purchase_item(username: str, item_id: str, cost: int) -> tuple[bool, str]:
    user = get_user(username)
    if not user:
        return False, "User not found."
    if owns_item(username, item_id):
        return False, "You already own this item."
    if user["coins"] < cost:
        return False, f"Not enough V-Coins. Need {cost:,}, have {user['coins']:,}."
    db().table("user_cosmetics").insert({
        "id":           str(uuid.uuid4()),
        "username":     username,
        "item_id":      item_id,
        "equipped":     False,
        "purchased_at": datetime.utcnow().isoformat(),
    }).execute()
    update_user(username, {"coins": user["coins"] - cost})
    return True, "Purchased!"

def equip_item(username: str, item_id: str, item_type: str):
    # Unequip all of same type first
    owned = get_user_cosmetics(username)
    all_items = get_shop_items()
    same_type_ids = [i["id"] for i in all_items if i["type"] == item_type]
    for uc in owned:
        if uc["item_id"] in same_type_ids:
            db().table("user_cosmetics").update({"equipped": False}) \
                .eq("username", username).eq("item_id", uc["item_id"]).execute()
    db().table("user_cosmetics").update({"equipped": True}) \
        .eq("username", username).eq("item_id", item_id).execute()

def get_equipped(username: str, item_type: str) -> dict | None:
    owned = get_user_cosmetics(username)
    equipped_ids = [uc["item_id"] for uc in owned if uc.get("equipped")]
    if not equipped_ids:
        return None
    items = get_shop_items()
    for item in items:
        if item["id"] in equipped_ids and item["type"] == item_type:
            return item
    return None

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
        r["pct"] = r["bets_correct"] / r["bets_placed"] if r["bets_placed"] else 0
    return sorted(rows, key=lambda x: x["pct"], reverse=True)[:n]

def leaderboard_losers(n=10) -> list:
    return db().table("users") \
               .select("username,total_lost,biggest_loss") \
               .order("total_lost", desc=True).limit(n).execute().data or []

# ─────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────
for k, v in [("username", None), ("page", "home"), ("auth_tab", "login"),
             ("selected_bet", None), ("selected_profile", None), ("toast", None)]:
    if k not in st.session_state:
        st.session_state[k] = v

def nav(page: str, bet_id=None, profile=None):
    st.session_state.page             = page
    st.session_state.selected_bet     = bet_id
    st.session_state.selected_profile = profile
    st.rerun()

def set_toast(kind: str, msg: str):
    st.session_state.toast = (kind, msg)

def show_toast():
    if st.session_state.toast:
        kind, msg = st.session_state.toast
        css = {"success":"notice-success","warn":"notice-warn",
               "error":"notice-error","info":"notice-info"}.get(kind,"notice-info")
        st.markdown(f'<div class="notice {css}">{msg}</div>', unsafe_allow_html=True)
        st.session_state.toast = None

# ─────────────────────────────────────────────
#  SHARED COMPONENTS
# ─────────────────────────────────────────────
def render_badges(username: str, compact=False):
    badges    = get_user_badges(username)
    all_achvs = {a["id"]: a for a in get_all_achievements()}
    if not badges:
        if not compact:
            st.markdown('<div style="color:#2a4060;font-size:0.82rem;">No badges yet.</div>',
                        unsafe_allow_html=True)
        return
    html = ""
    for b in badges:
        achv  = all_achvs.get(b["achievement_id"], {})
        style = BADGE_STYLES.get(b["achievement_id"], "badge-earned")
        html += f'<span class="badge {style}">{achv.get("name","Badge")}</span>'
    st.markdown(html, unsafe_allow_html=True)

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

    link  = bet.get("stream_link","")
    name  = bet.get("vtuber_name","")
    name_html = (f'<a href="{link}" target="_blank" class="stream-link">{name}</a>'
                 if link else f'<span style="color:#4499ff">{name}</span>')

    game      = bet.get("game_or_activity","")
    game_html = f'<div class="bet-game">{game}</div>' if game else ""
    opts_str  = "  /  ".join(bet["options"][:2])

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
#  AUTH PAGE
# ─────────────────────────────────────────────
def page_auth():
    # Full-page centering — hide sidebar on auth page
    st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none !important; }
    [data-testid="collapsedControl"] { display: none !important; }

    /* Auth-specific tab polish */
    .auth-tabs .stTabs [data-baseweb="tab-list"] {
        background: #0b0f1e !important;
        border: 1px solid #1e3060 !important;
        border-radius: 10px;
        padding: 4px;
    }
    .auth-tabs .stTabs [data-baseweb="tab"] {
        font-size: 0.88rem !important;
        padding: 8px 20px !important;
    }

    /* Auth card */
    .auth-card {
        background: #0b0f1e;
        border: 1px solid #1e3060;
        border-radius: 16px;
        padding: 32px 36px;
        margin-top: 8px;
    }

    /* Getting started steps */
    .gs-step {
        display: flex;
        align-items: flex-start;
        gap: 14px;
        padding: 14px 0;
        border-bottom: 1px solid #111a2e;
    }
    .gs-step:last-child { border-bottom: none; }
    .gs-num {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        font-weight: 700;
        color: #0066ff;
        background: #001a44;
        border: 1px solid #0044aa44;
        border-radius: 4px;
        padding: 3px 8px;
        white-space: nowrap;
        margin-top: 2px;
    }
    .gs-text { font-size: 0.85rem; color: #5577aa; line-height: 1.5; }
    .gs-text strong { color: #99bbdd; font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)

    # Outer centering with max-width
    _, col, _ = st.columns([1, 3, 1])
    with col:
        # Logo / header
        st.markdown("""
        <div style="text-align:center;padding:40px 0 28px;">
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

        show_toast()

        # ── Two-column layout: login/register left, getting started right ──
        left, right = st.columns([1, 1], gap="large")

        with left:
            st.markdown('<div class="auth-tabs">', unsafe_allow_html=True)
            tab_login, tab_register = st.tabs(["  Login  ", "  Create Account  "])

            with tab_login:
                st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
                l_user = st.text_input("Username", key="login_user",
                                       placeholder="Enter your username")
                l_pass = st.text_input("Password", key="login_pass",
                                       type="password", placeholder="Enter your password")
                st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

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
                            # Check if role still needs setting
                            if needs_role_selection(l_user.strip()):
                                st.session_state.page = "role_select"
                            else:
                                st.session_state.page = "home"
                            st.rerun()
                        else:
                            set_toast("error", msg)
                            st.rerun()

            with tab_register:
                st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
                r_user  = st.text_input("Username", key="reg_user",
                                        placeholder="2–24 characters, no spaces")
                r_pass  = st.text_input("Password", key="reg_pass",
                                        type="password", placeholder="At least 6 characters")
                r_pass2 = st.text_input("Confirm password", key="reg_pass2",
                                        type="password", placeholder="Repeat your password")
                st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

                if st.button("Create Account", use_container_width=True, key="btn_register"):
                    un = r_user.strip()
                    errs = []
                    if len(un) < 2:
                        errs.append("Username must be at least 2 characters.")
                    elif len(un) > 24:
                        errs.append("Username must be 24 characters or fewer.")
                    elif " " in un:
                        errs.append("Username cannot contain spaces.")
                    if len(r_pass) < 6:
                        errs.append("Password must be at least 6 characters.")
                    elif r_pass != r_pass2:
                        errs.append("Passwords do not match.")
                    if errs:
                        set_toast("error", errs[0])
                        st.rerun()
                    else:
                        ok, msg = register_user(un, r_pass)
                        if ok:
                            st.session_state.username = un
                            st.session_state.page = "role_select"
                            st.rerun()
                        else:
                            set_toast("error", msg)
                            st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)

            # Stats row under the form
            st.markdown("""
            <div style="display:flex;gap:0;margin-top:20px;
                        border:1px solid #1a2a44;border-radius:10px;overflow:hidden;">
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

        with right:
            st.markdown("""
            <div style="padding:4px 0 12px;">
                <div style="font-family:'JetBrains Mono',monospace;font-size:0.62rem;
                            color:#0055cc;letter-spacing:0.15em;text-transform:uppercase;
                            margin-bottom:12px;">Getting Started</div>

                <div class="gs-step">
                    <span class="gs-num">01</span>
                    <div class="gs-text">
                        <strong>Create an account</strong> with just a username and password.
                        No email, no linked accounts needed.
                    </div>
                </div>

                <div class="gs-step">
                    <span class="gs-num">02</span>
                    <div class="gs-text">
                        <strong>Pick your role</strong> — Watcher, Streamer, or Clipper.
                        You start with 5,000 V-Coins instantly.
                    </div>
                </div>

                <div class="gs-step">
                    <span class="gs-num">03</span>
                    <div class="gs-text">
                        <strong>Browse open bets</strong> on indie VTuber stream moments —
                        boss fights, yap sessions, tech scuff, chaos moments.
                    </div>
                </div>

                <div class="gs-step">
                    <span class="gs-num">04</span>
                    <div class="gs-text">
                        <strong>Place your V-Coins</strong> on the outcome you think will happen.
                        Winner takes the pot, split proportionally.
                    </div>
                </div>

                <div class="gs-step">
                    <span class="gs-num">05</span>
                    <div class="gs-text">
                        <strong>Vote after the stream</strong> to confirm what happened.
                        3 votes resolves the bet automatically.
                    </div>
                </div>

                <div class="gs-step">
                    <span class="gs-num">06</span>
                    <div class="gs-text">
                        <strong>Earn achievements</strong> for predicting correctly, discovering
                        hidden gems, and casting deciding votes. Most pay out bonus V-Coins.
                    </div>
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
            ("Watcher",  "role-watcher",  "You watch streams, follow indie VTubers, and bet on the chaos.",           "Bet on streams, vote on outcomes, climb the leaderboard."),
            ("Streamer", "role-streamer", "You are a VTuber or streamer — your community might bet on your streams.", "Get discovered through community bets featuring your content."),
            ("Clipper",  "role-clipper",  "You create clips and highlight reels of indie VTubers.",                   "Compete in Clip Showdown events and earn the Clipper Legend badge."),
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
                set_toast("success", f"Welcome! Your account is ready. You start with 5,000 V-Coins.")
                st.rerun()

        st.markdown("""
        <div style="text-align:center;margin-top:16px;color:#1e3060;font-size:0.75rem;">
            Not sure? Pick Watcher — you can update it later in your profile.
        </div>
        """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
def render_sidebar():
    username = st.session_state.username
    if not username:
        return
    user = get_user(username)
    if not user:
        return

    title_item = get_equipped(username, "title")

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

        title_html = (f'<div class="user-title">{title_item["value"]}</div>'
                      if title_item else "")
        role  = user.get("role","")
        r_css = {"Watcher":"role-watcher","Streamer":"role-streamer",
                 "Clipper":"role-clipper"}.get(role,"role-watcher")

        st.markdown(f"""
        <div class="coin-box">
            {title_html}
            <div class="coin-label">{username}</div>
            <div class="coin-amount">{user['coins']:,}</div>
            <div class="coin-sub">V-COINS</div>
            {f'<span class="profile-role {r_css}" style="margin-top:8px;display:inline-block;">{role}</span>' if role else ''}
        </div>
        """, unsafe_allow_html=True)

        if st.button("Claim Daily Bonus  +250", use_container_width=True):
            ok, msg = claim_daily_bonus(username)
            set_toast("success" if ok else "warn", msg)
            st.rerun()

        st.markdown("---")

        pages = [
            ("Home",          "home"),
            ("All Bets",      "bets"),
            ("Create Bet",    "create_bet"),
            ("Achievements",  "achievements"),
            ("Shop",          "shop"),
            ("Leaderboard",   "leaderboard"),
            ("My Profile",    "my_profile"),
            ("How It Works",  "how_it_works"),
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
# ─────────────────────────────────────────────
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
# ─────────────────────────────────────────────
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
# ─────────────────────────────────────────────
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
# ─────────────────────────────────────────────
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
# ─────────────────────────────────────────────
def page_my_profile():
    show_toast()
    username = st.session_state.username
    user     = get_user(username)

    st.markdown("## My Profile")

    role  = user.get("role","")
    r_css = {"Watcher":"role-watcher","Streamer":"role-streamer",
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
# ─────────────────────────────────────────────
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

# ─────────────────────────────────────────────
#  ROUTER
# ─────────────────────────────────────────────
def main():
    if not st.session_state.username:
        page_auth()
        return

    # Role selection gates — runs before sidebar
    if st.session_state.page == "role_select" or needs_role_selection(st.session_state.username):
        page_role_select()
        return

    render_sidebar()

    p = st.session_state.page
    if   p == "home":         page_home()
    elif p == "bets":         page_bets()
    elif p == "bet_detail":   page_bet_detail()
    elif p == "create_bet":   page_create_bet()
    elif p == "achievements": page_achievements()
    elif p == "shop":         page_shop()
    elif p == "leaderboard":  page_leaderboard()
    elif p == "my_profile":   page_my_profile()
    elif p == "how_it_works": page_how_it_works()
    else:                     page_home()

main()
