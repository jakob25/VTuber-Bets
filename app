import streamlit as st
import json
import os
import uuid
from datetime import datetime, timedelta
from pathlib import Path

# ─────────────────────────────────────────────

# CONFIG & PAGE SETUP

# ─────────────────────────────────────────────

st.set_page_config(
page_title=“VTuberBets 🎲✨”,
page_icon=“🎲”,
layout=“wide”,
initial_sidebar_state=“expanded”,
)

# ─────────────────────────────────────────────

# CUSTOM CSS — dark pastel chaotic vibes

# ─────────────────────────────────────────────

st.markdown(”””

<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=Syne:wght@700;800&display=swap');

/* ── RESET & BASE ── */
* { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"] {
    background: #0e0b1a !important;
    color: #e8e0f5 !important;
    font-family: 'Space Grotesk', sans-serif;
}

[data-testid="stSidebar"] {
    background: #160f2e !important;
    border-right: 2px solid #3a2060 !important;
}

/* ── HEADERS ── */
h1, h2, h3 {
    font-family: 'Syne', sans-serif !important;
    letter-spacing: -0.03em;
}

/* ── CARDS ── */
.bet-card {
    background: linear-gradient(135deg, #1a1035 0%, #200d3a 100%);
    border: 1px solid #3a2060;
    border-radius: 18px;
    padding: 20px 22px;
    margin-bottom: 16px;
    transition: transform 0.15s ease, border-color 0.15s ease;
    position: relative;
    overflow: hidden;
}
.bet-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #b06bff, #ff6bca, #6bffd4);
    border-radius: 18px 18px 0 0;
}
.bet-card:hover {
    border-color: #7c3aed;
    transform: translateY(-2px);
}

.vtuber-name {
    font-family: 'Syne', sans-serif;
    font-size: 0.75rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #b06bff;
    margin-bottom: 4px;
}
.bet-title {
    font-size: 1.05rem;
    font-weight: 600;
    color: #f0eaff;
    margin-bottom: 10px;
}
.bet-meta {
    font-size: 0.78rem;
    color: #8b7aaa;
}
.pot-badge {
    background: linear-gradient(90deg, #7c3aed22, #ec4f9922);
    border: 1px solid #7c3aed55;
    border-radius: 50px;
    padding: 3px 12px;
    font-size: 0.75rem;
    font-weight: 600;
    color: #c084fc;
    display: inline-block;
}
.status-open   { color: #4ade80; font-weight: 700; }
.status-voting { color: #fbbf24; font-weight: 700; }
.status-closed { color: #f87171; font-weight: 700; }

/* ── COINS ── */
.coin-display {
    background: linear-gradient(135deg, #1e1040, #2d1060);
    border: 2px solid #7c3aed55;
    border-radius: 16px;
    padding: 16px 20px;
    text-align: center;
    margin-bottom: 12px;
}
.coin-amount {
    font-family: 'Syne', sans-serif;
    font-size: 2rem;
    font-weight: 800;
    background: linear-gradient(90deg, #c084fc, #f472b6, #67e8f9);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* ── LEADERBOARD ── */
.lb-row {
    display: flex;
    align-items: center;
    padding: 10px 14px;
    border-radius: 12px;
    margin-bottom: 8px;
    background: #1a1035;
    border: 1px solid #2d1f50;
}
.lb-rank { font-family:'Syne',sans-serif; font-size:1.2rem; font-weight:800; width:36px; }
.lb-name { flex:1; font-weight:600; }
.lb-coins { color: #c084fc; font-weight:700; }

.rank-1 { border-color:#f59e0b55; background:linear-gradient(135deg,#1a1035,#2a1a05); }
.rank-2 { border-color:#94a3b855; }
.rank-3 { border-color:#cd7c3955; }

/* ── BUTTONS ── */
.stButton > button {
    background: linear-gradient(135deg, #7c3aed, #ec4899) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 700 !important;
    transition: opacity 0.15s !important;
}
.stButton > button:hover { opacity: 0.85 !important; }

/* ── INPUTS ── */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div {
    background: #1a1035 !important;
    border: 1px solid #3a2060 !important;
    border-radius: 10px !important;
    color: #e8e0f5 !important;
}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
    background: #160f2e !important;
    border-radius: 12px;
    gap: 4px;
    padding: 4px;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #8b7aaa !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #7c3aed, #ec4899) !important;
    color: white !important;
}

/* ── DIVIDER ── */
hr { border-color: #2d1f50 !important; }

/* ── METRIC ── */
[data-testid="metric-container"] {
    background: #1a1035;
    border: 1px solid #3a2060;
    border-radius: 14px;
    padding: 12px 16px;
}

/* ── SIDEBAR LINKS ── */
.sidebar-link {
    display:block;
    padding: 10px 14px;
    border-radius: 10px;
    color: #c4b5d8;
    text-decoration: none;
    font-weight: 600;
    margin-bottom: 6px;
    cursor: pointer;
    transition: background 0.15s;
}
.sidebar-link:hover { background: #2d1f50; }
.sidebar-link.active { background: linear-gradient(135deg,#7c3aed33,#ec489933); color:#e8e0f5; border-left:3px solid #b06bff; }

/* ── VOTE OPTION BUTTON ── */
.vote-btn {
    background: #1a1035;
    border: 2px solid #3a2060;
    border-radius: 12px;
    padding: 12px 18px;
    color: #e8e0f5;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.15s;
    text-align:center;
}
.vote-btn:hover { border-color:#7c3aed; background:#2d1f50; }

/* ── TOAST-style info ── */
.toast-success {
    background: linear-gradient(135deg,#0d2e1a,#0a2a18);
    border: 1px solid #22c55e55;
    border-radius: 12px;
    padding: 12px 16px;
    color: #86efac;
    font-weight: 600;
    margin: 8px 0;
}
.toast-error {
    background: linear-gradient(135deg,#2e0d0d,#2a0a0a);
    border: 1px solid #f8717155;
    border-radius: 12px;
    padding: 12px 16px;
    color: #fca5a5;
    font-weight: 600;
    margin: 8px 0;
}

/* ── PROGRESS BAR ── */
.option-bar-wrap { margin-bottom:10px; }
.option-bar-label { display:flex; justify-content:space-between; font-size:0.82rem; margin-bottom:4px; }
.option-bar-bg { background:#1a1035; border-radius:50px; height:12px; border:1px solid #2d1f50; overflow:hidden; }
.option-bar-fill { height:12px; border-radius:50px; background:linear-gradient(90deg,#7c3aed,#ec4899); transition:width 0.4s ease; }

/* ── HERO BANNER ── */
.hero {
    background: linear-gradient(135deg,#1a0533,#0d1a33,#1a0d33);
    border: 1px solid #3a2060;
    border-radius: 24px;
    padding: 32px 36px;
    margin-bottom: 28px;
    position:relative;
    overflow:hidden;
}
.hero::after {
    content:'🎲 💜 ✨ 🎰 🫧 🌸 🎮 💫 👾';
    position:absolute;
    bottom:12px; right:20px;
    font-size:1.2rem;
    opacity:0.3;
    letter-spacing:4px;
}
</style>

“””, unsafe_allow_html=True)

# ─────────────────────────────────────────────

# DATA LAYER  (JSON flat-file persistence)

# ─────────────────────────────────────────────

USERS_FILE = “users.json”
BETS_FILE  = “bets.json”

def _load(path: str, default) -> dict | list:
if os.path.exists(path):
with open(path) as f:
return json.load(f)
return default

def _save(path: str, data) -> None:
with open(path, “w”) as f:
json.dump(data, f, indent=2, default=str)

def load_users() -> dict:
return _load(USERS_FILE, {})

def save_users(u: dict) -> None:
_save(USERS_FILE, u)

def load_bets() -> list:
return _load(BETS_FILE, [])

def save_bets(b: list) -> None:
_save(BETS_FILE, b)

# ─────────────────────────────────────────────

# SEED DATA  (only written if bets.json absent)

# ─────────────────────────────────────────────

SEED_BETS = [
{
“id”: “b001”,
“vtuber”: “Filian 🦊”,
“title”: “Will Filian actually beat the final boss this stream?”,
“description”: “She’s been on this boss for 3 streams. Chat is losing it. Does she finally do it? 👀”,
“options”: [“YES she does it!! 🎉”, “NO she rage quits 💀”],
“status”: “open”,
“created_at”: (datetime.now() - timedelta(hours=2)).isoformat(),
“closes_at”: (datetime.now() + timedelta(hours=10)).isoformat(),
“bets”: {},        # { username: {option: str, amount: int} }
“votes”: {},       # { username: option }
“result”: None,
“created_by”: “system”,
“category”: “Boss Fight”,
},
{
“id”: “b002”,
“vtuber”: “Shylily 🌸”,
“title”: “How long is the yap session before game starts? Over/Under 18 mins”,
“description”: “Shylily opened stream and has been vibing with chat. When does the game actually start??”,
“options”: [“OVER 18 mins 🗣️”, “UNDER 18 mins 🎮”],
“status”: “open”,
“created_at”: (datetime.now() - timedelta(hours=1)).isoformat(),
“closes_at”: (datetime.now() + timedelta(hours=6)).isoformat(),
“bets”: {},
“votes”: {},
“result”: None,
“created_by”: “system”,
“category”: “Yap Session”,
},
{
“id”: “b003”,
“vtuber”: “Chibidoki 🐸”,
“title”: “Will Chibi’s model break at least once this stream?”,
“description”: “Tech scuff % is astronomically high. Will the frog physics malfunction again? 🐸”,
“options”: [“YES model goes brrrr 💥”, “NO flawless model 😇”],
“status”: “open”,
“created_at”: (datetime.now() - timedelta(hours=3)).isoformat(),
“closes_at”: (datetime.now() + timedelta(hours=8)).isoformat(),
“bets”: {},
“votes”: {},
“result”: None,
“created_by”: “system”,
“category”: “Tech Scuff”,
},
{
“id”: “b004”,
“vtuber”: “Limes 🍋”,
“title”: “Deaths before first dungeon clear? Over/Under 12 deaths”,
“description”: “Limes is playing a notoriously unforgiving roguelike. How many L’s before W?”,
“options”: [“OVER 12 deaths 💀💀💀”, “UNDER 12 deaths 🗡️”],
“status”: “voting”,
“created_at”: (datetime.now() - timedelta(hours=14)).isoformat(),
“closes_at”: (datetime.now() - timedelta(hours=2)).isoformat(),
“bets”: {
“GremlinSupporter”: {“option”: “OVER 12 deaths 💀💀💀”, “amount”: 300},
“StreamSniper99”:   {“option”: “UNDER 12 deaths 🗡️”,   “amount”: 150},
“VoidChatEnjoyer”:  {“option”: “OVER 12 deaths 💀💀💀”, “amount”: 500},
},
“votes”: {
“GremlinSupporter”: “OVER 12 deaths 💀💀💀”,
“StreamSniper99”:   “OVER 12 deaths 💀💀💀”,
},
“result”: None,
“created_by”: “system”,
“category”: “Death Count”,
},
{
“id”: “b005”,
“vtuber”: “Nemu 🌙”,
“title”: “Will Nemu randomly start singing mid-stream?”,
“description”: “It happens every time. The question is WHEN not IF. Will the karaoke arc activate?”,
“options”: [“YES sudden karaoke 🎤”, “NO stays focused 🎮”],
“status”: “open”,
“created_at”: (datetime.now() - timedelta(minutes=45)).isoformat(),
“closes_at”: (datetime.now() + timedelta(hours=12)).isoformat(),
“bets”: {},
“votes”: {},
“result”: None,
“created_by”: “system”,
“category”: “Chaos Moment”,
},
{
“id”: “b006”,
“vtuber”: “Meat 🥩”,
“title”: “Will they finish the announced game OR get distracted?”,
“description”: “The schedule said Hollow Knight. But there was a Minecraft tweet earlier… 👀”,
“options”: [“Finishes planned game ✅”, “Gets distracted / switches 🌀”],
“status”: “closed”,
“created_at”: (datetime.now() - timedelta(days=1, hours=3)).isoformat(),
“closes_at”: (datetime.now() - timedelta(hours=20)).isoformat(),
“bets”: {
“ChatGooblin”:     {“option”: “Gets distracted / switches 🌀”, “amount”: 800},
“PredictionKing”:  {“option”: “Finishes planned game ✅”,       “amount”: 200},
“NachtVoider”:     {“option”: “Gets distracted / switches 🌀”, “amount”: 600},
“SkibidiAnalyst”:  {“option”: “Finishes planned game ✅”,       “amount”: 350},
},
“votes”: {
“ChatGooblin”:    “Gets distracted / switches 🌀”,
“PredictionKing”: “Gets distracted / switches 🌀”,
“NachtVoider”:    “Gets distracted / switches 🌀”,
“SkibidiAnalyst”: “Gets distracted / switches 🌀”,
“SupporterGal”:   “Gets distracted / switches 🌀”,
“ChaosBrain”:     “Gets distracted / switches 🌀”,
“LoreCrafter”:    “Gets distracted / switches 🌀”,
“NewbieWatcher”:  “Gets distracted / switches 🌀”,
},
“result”: “Gets distracted / switches 🌀”,
“created_by”: “system”,
“category”: “Game Completion”,
},
]

def ensure_seed_data():
if not os.path.exists(BETS_FILE):
_save(BETS_FILE, SEED_BETS)
if not os.path.exists(USERS_FILE):
_save(USERS_FILE, {})

ensure_seed_data()

# ─────────────────────────────────────────────

# HELPERS

# ─────────────────────────────────────────────

STARTING_COINS   = 5_000
DAILY_BONUS      = 250
HOUSE_CUT        = 0.05
MIN_VOTES_NEEDED = 8

CATEGORY_EMOJI = {
“Boss Fight”:      “⚔️”,
“Yap Session”:     “🗣️”,
“Tech Scuff”:      “💥”,
“Death Count”:     “💀”,
“Chaos Moment”:    “🌀”,
“Game Completion”: “🎮”,
“Other”:           “🎲”,
}

def get_or_create_user(username: str) -> dict:
users = load_users()
if username not in users:
users[username] = {
“username”:    username,
“coins”:       STARTING_COINS,
“joined_at”:   datetime.now().isoformat(),
“last_bonus”:  None,
“total_won”:   0,
“bets_correct”:0,
“bets_placed”: 0,
}
save_users(users)
return users[username]

def update_user(username: str, data: dict):
users = load_users()
users[username].update(data)
save_users(users)

def get_pot_totals(bet: dict) -> dict[str, int]:
totals: dict[str, int] = {opt: 0 for opt in bet[“options”]}
for b in bet[“bets”].values():
totals[b[“option”]] = totals.get(b[“option”], 0) + b[“amount”]
return totals

def total_pot(bet: dict) -> int:
return sum(get_pot_totals(bet).values())

def vote_counts(bet: dict) -> dict[str, int]:
counts: dict[str, int] = {opt: 0 for opt in bet[“options”]}
for v in bet[“votes”].values():
counts[v] = counts.get(v, 0) + 1
return counts

def majority_option(bet: dict) -> str | None:
counts = vote_counts(bet)
total  = sum(counts.values())
if total < MIN_VOTES_NEEDED:
return None
winner = max(counts, key=counts.get)
if counts[winner] > total / 2:
return winner
return None

def resolve_bet(bet_id: str):
“”“Resolve a bet: distribute winnings, mark closed.”””
bets = load_bets()
users = load_users()
bet = next((b for b in bets if b[“id”] == bet_id), None)
if not bet or bet[“status”] != “voting”:
return False, “Bet not in voting phase.”
winner_opt = majority_option(bet)
if not winner_opt:
return False, f”Need at least {MIN_VOTES_NEEDED} votes with a clear majority to resolve.”

```
bet["result"] = winner_opt
bet["status"] = "closed"

pot = total_pot(bet)
house = int(pot * HOUSE_CUT)
distributable = pot - house

winners = {u: d for u, d in bet["bets"].items() if d["option"] == winner_opt}
winner_stake = sum(d["amount"] for d in winners.values())

for uname, d in winners.items():
    if winner_stake > 0:
        share = int(distributable * d["amount"] / winner_stake)
    else:
        share = 0
    if uname in users:
        users[uname]["coins"]       = users[uname].get("coins", 0) + share
        users[uname]["total_won"]   = users[uname].get("total_won", 0) + share
        users[uname]["bets_correct"]= users[uname].get("bets_correct", 0) + 1

# also credit correct voters
for uname, v in bet["votes"].items():
    if v == winner_opt and uname in users:
        users[uname]["bets_correct"] = users[uname].get("bets_correct", 0)  # already counted if they bet

save_bets(bets)
save_users(users)
return True, winner_opt
```

def claim_daily_bonus(username: str) -> tuple[bool, str]:
users = load_users()
user  = users.get(username)
if not user:
return False, “User not found.”
last = user.get(“last_bonus”)
now  = datetime.now()
if last:
last_dt = datetime.fromisoformat(last)
if now - last_dt < timedelta(hours=20):
remaining = timedelta(hours=20) - (now - last_dt)
h, m = divmod(int(remaining.total_seconds() / 60), 60)
return False, f”Already claimed! Come back in {h}h {m}m ⏰”
users[username][“coins”]     = user.get(“coins”, 0) + DAILY_BONUS
users[username][“last_bonus”] = now.isoformat()
save_users(users)
return True, f”+{DAILY_BONUS} V-Coins claimed! 🎉”

# ─────────────────────────────────────────────

# SESSION STATE

# ─────────────────────────────────────────────

if “username” not in st.session_state:
st.session_state.username = None
if “page” not in st.session_state:
st.session_state.page = “home”
if “toast” not in st.session_state:
st.session_state.toast = None   # (type, msg)
if “selected_bet” not in st.session_state:
st.session_state.selected_bet = None

def nav(page: str, bet_id: str | None = None):
st.session_state.page = page
st.session_state.selected_bet = bet_id
st.rerun()

def show_toast():
if st.session_state.toast:
t, msg = st.session_state.toast
if t == “success”:
st.markdown(f’<div class="toast-success">✅ {msg}</div>’, unsafe_allow_html=True)
else:
st.markdown(f’<div class="toast-error">❌ {msg}</div>’, unsafe_allow_html=True)
st.session_state.toast = None

def toast(t: str, msg: str):
st.session_state.toast = (t, msg)

# ─────────────────────────────────────────────

# LOGIN PAGE

# ─────────────────────────────────────────────

def page_login():
st.markdown(”””
<div class="hero" style="text-align:center; padding:48px 36px;">
<div style="font-size:3.5rem; margin-bottom:12px">🎲✨</div>
<h1 style="font-size:2.8rem; margin:0; background:linear-gradient(90deg,#c084fc,#f472b6,#67e8f9);
-webkit-background-clip:text;-webkit-text-fill-color:transparent;">
VTuberBets
</h1>
<p style="color:#8b7aaa; font-size:1.1rem; margin-top:8px;">
The chaotic, wholesome prediction arena for indie VTuber fans 💜
</p>
<p style="color:#6b5a8a; font-size:0.85rem; margin-top:4px;">
✨ Virtual V-Coins only — zero real money, pure vibes ✨
</p>
</div>
“””, unsafe_allow_html=True)

```
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("### 👾 Who are you, little gremlin?")
    username = st.text_input("Pick a username (no password needed fr fr):",
                             placeholder="e.g. ChatGooblin, StreamSniper99...")
    if st.button("🚀 Enter the Chaos Zone", use_container_width=True):
        un = username.strip()
        if len(un) < 2:
            toast("error", "Username must be at least 2 chars bestie!")
            st.rerun()
        elif len(un) > 24:
            toast("error", "Username too long! Max 24 chars.")
            st.rerun()
        else:
            get_or_create_user(un)
            st.session_state.username = un
            toast("success", f"Welcome back, {un}! 🎉 Ready to make unhinged predictions?")
            nav("home")
    show_toast()

    st.markdown("---")
    st.markdown("""
    <div style="text-align:center; color:#6b5a8a; font-size:0.85rem;">
        🌸 VTuberBets is a fan-made, free-to-play prediction community<br>
        💜 No real money. No gambling. Just pure indie VTuber chaos.<br>
        🎮 Start with <strong style="color:#c084fc">5,000 V-Coins</strong> and climb the leaderboard!
    </div>
    """, unsafe_allow_html=True)
```

# ─────────────────────────────────────────────

# SIDEBAR

# ─────────────────────────────────────────────

def render_sidebar():
username = st.session_state.username
if not username:
return
user = get_or_create_user(username)

```
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding:8px 0 16px;">
        <span style="font-size:2rem">🎲</span>
        <div style="font-family:'Syne',sans-serif; font-size:1.4rem; font-weight:800;
                    background:linear-gradient(90deg,#c084fc,#f472b6);
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
            VTuberBets
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="coin-display">
        <div style="font-size:0.75rem; color:#8b7aaa; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:4px;">
            👾 {username}
        </div>
        <div class="coin-amount">🪙 {user['coins']:,}</div>
        <div style="font-size:0.72rem; color:#6b5a8a; margin-top:2px;">V-Coins</div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🎁 Daily Bonus (+250)", use_container_width=True):
        ok, msg = claim_daily_bonus(username)
        toast("success" if ok else "error", msg)
        st.rerun()

    st.markdown("---")
    pages = [
        ("🏠", "Home", "home"),
        ("🎲", "Open Bets", "bets"),
        ("➕", "Create Bet", "create"),
        ("🏆", "Leaderboard", "leaderboard"),
    ]
    current = st.session_state.page
    for icon, label, key in pages:
        active = "active" if current == key else ""
        if st.button(f"{icon} {label}", key=f"nav_{key}", use_container_width=True):
            nav(key)

    st.markdown("---")
    stats_col1, stats_col2 = st.columns(2)
    with stats_col1:
        st.metric("🎯 Correct", user.get("bets_correct", 0))
    with stats_col2:
        st.metric("🎰 Placed", user.get("bets_placed", 0))

    if st.button("🚪 Log Out", use_container_width=True):
        st.session_state.username = None
        st.session_state.page = "home"
        st.rerun()
```

# ─────────────────────────────────────────────

# HOME PAGE

# ─────────────────────────────────────────────

def page_home():
show_toast()
username = st.session_state.username
user = get_or_create_user(username)
bets = load_bets()

```
st.markdown("""
<div class="hero">
    <h1 style="margin:0 0 8px; font-size:2.2rem;
               background:linear-gradient(90deg,#c084fc,#f472b6,#67e8f9);
               -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
        Welcome to the Chaos 🎲✨
    </h1>
    <p style="color:#8b7aaa; margin:0; font-size:1rem;">
        Place your V-Coins on indie VTuber moments. No skill required. Just vibes. 💜
    </p>
</div>
""", unsafe_allow_html=True)

# Stats row
open_bets   = [b for b in bets if b["status"] == "open"]
voting_bets = [b for b in bets if b["status"] == "voting"]
total_pots  = sum(total_pot(b) for b in bets)

c1, c2, c3, c4 = st.columns(4)
c1.metric("🔥 Open Bets",    len(open_bets))
c2.metric("🗳️ Voting Now",   len(voting_bets))
c3.metric("💰 Total Pot",    f"{total_pots:,} 🪙")
c4.metric("🪙 Your Balance", f"{user['coins']:,}")

st.markdown("---")

# Hot bets
st.markdown("### 🔥 Hot Right Now")
hot_bets = sorted([b for b in bets if b["status"] == "open"],
                  key=lambda x: total_pot(x), reverse=True)[:3]
if not hot_bets:
    st.info("No open bets yet! Go create one 👀")
for bet in hot_bets:
    render_bet_card(bet, show_button=True)

st.markdown("---")
col_a, col_b = st.columns(2)
with col_a:
    st.markdown("### 🗳️ Needs Your Vote!")
    vbets = [b for b in bets if b["status"] == "voting"][:2]
    if not vbets:
        st.markdown('<div class="bet-meta">No bets in voting phase rn!</div>', unsafe_allow_html=True)
    for b in vbets:
        render_bet_card(b, show_button=True)

with col_b:
    st.markdown("### ✅ Recently Resolved")
    closed = [b for b in bets if b["status"] == "closed" and b["result"]][:2]
    if not closed:
        st.markdown('<div class="bet-meta">Nothing resolved yet!</div>', unsafe_allow_html=True)
    for b in closed:
        render_bet_card(b, show_button=True)
```

# ─────────────────────────────────────────────

# BET CARD COMPONENT

# ─────────────────────────────────────────────

def render_bet_card(bet: dict, show_button: bool = False):
status_map = {
“open”:   ‘<span class="status-open">🟢 OPEN</span>’,
“voting”: ‘<span class="status-voting">🗳️ VOTING</span>’,
“closed”: ‘<span class="status-closed">🔒 CLOSED</span>’,
}
status_html = status_map.get(bet[“status”], “”)
pot = total_pot(bet)
cat_icon = CATEGORY_EMOJI.get(bet.get(“category”, “Other”), “🎲”)
opts_preview = “ · “.join(bet[“options”][:2])

```
st.markdown(f"""
<div class="bet-card">
    <div class="vtuber-name">{cat_icon} {bet['vtuber']}</div>
    <div class="bet-title">{bet['title']}</div>
    <div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap;">
        {status_html}
        <span class="pot-badge">🪙 {pot:,} V-Coins in pot</span>
        <span class="bet-meta">{opts_preview}</span>
    </div>
</div>
""", unsafe_allow_html=True)

if show_button:
    if st.button(f"👉 View Bet", key=f"view_{bet['id']}"):
        nav("bet_detail", bet["id"])
```

# ─────────────────────────────────────────────

# OPEN BETS PAGE

# ─────────────────────────────────────────────

def page_bets():
show_toast()
bets = load_bets()

```
st.markdown("## 🎲 All Bets")

tab_open, tab_voting, tab_closed = st.tabs(
    ["🟢 Open", "🗳️ Voting Phase", "🔒 Resolved"]
)

with tab_open:
    open_b = [b for b in bets if b["status"] == "open"]
    if not open_b:
        st.info("No open bets right now! Be the first to create one ✨")
    for b in open_b:
        render_bet_card(b, show_button=True)
    if st.button("➕ Create a New Bet", key="create_from_bets"):
        nav("create")

with tab_voting:
    vot_b = [b for b in bets if b["status"] == "voting"]
    if not vot_b:
        st.info("Nothing in voting phase right now!")
    for b in vot_b:
        render_bet_card(b, show_button=True)

with tab_closed:
    clo_b = [b for b in bets if b["status"] == "closed"]
    if not clo_b:
        st.info("No resolved bets yet!")
    for b in clo_b:
        render_bet_card(b, show_button=True)
```

# ─────────────────────────────────────────────

# BET DETAIL PAGE

# ─────────────────────────────────────────────

def page_bet_detail():
show_toast()
bid = st.session_state.selected_bet
bets = load_bets()
bet  = next((b for b in bets if b[“id”] == bid), None)

```
if not bet:
    st.error("Bet not found 👻")
    if st.button("← Back"):
        nav("bets")
    return

username = st.session_state.username
user     = get_or_create_user(username)

if st.button("← Back to Bets"):
    nav("bets")

# Header
cat_icon = CATEGORY_EMOJI.get(bet.get("category", "Other"), "🎲")
st.markdown(f"""
<div class="hero">
    <div class="vtuber-name" style="font-size:0.9rem;">{cat_icon} {bet['vtuber']}</div>
    <h2 style="margin:6px 0 10px;">{bet['title']}</h2>
    <p style="color:#8b7aaa; margin:0;">{bet.get('description','')}</p>
</div>
""", unsafe_allow_html=True)

# Pot breakdown
totals = get_pot_totals(bet)
pot    = total_pot(bet)
st.markdown(f"**🪙 Total Pot: {pot:,} V-Coins**  ·  Created by `{bet['created_by']}`")

for opt in bet["options"]:
    pct = (totals[opt] / pot * 100) if pot > 0 else 0
    st.markdown(f"""
    <div class="option-bar-wrap">
        <div class="option-bar-label">
            <span>{opt}</span>
            <span style="color:#c084fc">{totals[opt]:,} 🪙 ({pct:.0f}%)</span>
        </div>
        <div class="option-bar-bg">
            <div class="option-bar-fill" style="width:{pct}%"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# User's existing bet
user_bet = bet["bets"].get(username)
if user_bet:
    st.markdown(f"""
    <div class="toast-success">
        🎰 You already bet <strong>{user_bet['amount']:,} V-Coins</strong>
        on <strong>{user_bet['option']}</strong> — let's gooo!
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ── PLACE BET (open only) ──
if bet["status"] == "open":
    st.markdown("### 🎰 Place Your Bet")
    if user_bet:
        st.info("You've already placed a bet on this one! One bet per user per prediction. 🙏")
    else:
        col1, col2 = st.columns([2, 1])
        with col1:
            chosen_option = st.selectbox("Choose your prediction:", bet["options"])
        with col2:
            amount = st.number_input(
                "V-Coins to wager:", min_value=10,
                max_value=min(user["coins"], 99_999), value=100, step=10
            )

        st.caption(f"Your balance: 🪙 {user['coins']:,} V-Coins")

        if st.button(f"🚀 Place Bet — {amount:,} V-Coins on '{chosen_option}'",
                     use_container_width=True):
            if amount > user["coins"]:
                toast("error", "Not enough V-Coins! Grind that daily bonus 😭")
            else:
                # Deduct coins
                users = load_users()
                users[username]["coins"]       -= amount
                users[username]["bets_placed"]  = users[username].get("bets_placed", 0) + 1
                save_users(users)
                # Record bet
                bets2 = load_bets()
                b2 = next(b for b in bets2 if b["id"] == bid)
                b2["bets"][username] = {"option": chosen_option, "amount": amount}
                save_bets(bets2)
                toast("success", f"Bet placed! 🎉 {amount:,} V-Coins on '{chosen_option}'")
                st.rerun()

    # Admin: close for voting
    st.markdown("---")
    with st.expander("🔧 Stream ended? Close bet for voting"):
        st.caption("Use this after the stream ends to move it to the community voting phase.")
        if st.button("🗳️ Close Bet & Start Voting Phase"):
            bets2 = load_bets()
            b2 = next(b for b in bets2 if b["id"] == bid)
            b2["status"] = "voting"
            save_bets(bets2)
            toast("success", "Bet closed! Voting phase is now LIVE 🗳️")
            st.rerun()

# ── VOTING PHASE ──
elif bet["status"] == "voting":
    vc = vote_counts(bet)
    total_v = sum(vc.values())
    st.markdown(f"### 🗳️ Community Vote  ({total_v}/{MIN_VOTES_NEEDED} votes needed)")

    user_vote = bet["votes"].get(username)
    if user_vote:
        st.markdown(f"""
        <div class="toast-success">
            ✅ You voted: <strong>{user_vote}</strong> — waiting for more votes!
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("**What actually happened? Vote to resolve the bet!**")
        vote_cols = st.columns(len(bet["options"]))
        for i, opt in enumerate(bet["options"]):
            with vote_cols[i]:
                if st.button(f"✅ {opt}  ({vc[opt]} votes)", key=f"vote_{bid}_{i}",
                             use_container_width=True):
                    bets2 = load_bets()
                    b2 = next(b for b in bets2 if b["id"] == bid)
                    b2["votes"][username] = opt
                    save_bets(bets2)
                    toast("success", f"Vote cast for '{opt}'! 🗳️")
                    st.rerun()

    # Show vote bars
    for opt in bet["options"]:
        pct = (vc[opt] / total_v * 100) if total_v > 0 else 0
        st.markdown(f"""
        <div class="option-bar-wrap">
            <div class="option-bar-label">
                <span>{opt}</span>
                <span style="color:#fbbf24">{vc[opt]} votes ({pct:.0f}%)</span>
            </div>
            <div class="option-bar-bg">
                <div class="option-bar-fill" style="width:{pct}%;background:linear-gradient(90deg,#f59e0b,#fbbf24)"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Try resolve
    winner = majority_option(bet)
    if winner:
        st.markdown(f"""
        <div class="toast-success">
            🏆 Majority reached! Likely winner: <strong>{winner}</strong>
        </div>
        """, unsafe_allow_html=True)
        if st.button("💰 Resolve & Pay Out Winnings!", use_container_width=True):
            ok, msg = resolve_bet(bid)
            if ok:
                toast("success", f"Bet resolved! Winner: '{msg}' — V-Coins distributed 💰🎉")
            else:
                toast("error", msg)
            st.rerun()
    else:
        remaining = MIN_VOTES_NEEDED - total_v
        st.info(f"Need {remaining} more vote(s) to reach the {MIN_VOTES_NEEDED}-vote minimum!")

# ── RESOLVED ──
elif bet["status"] == "closed":
    result = bet.get("result")
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#0d1a2e,#0a1a0d);border:2px solid #22c55e55;
                border-radius:16px;padding:20px 24px;text-align:center;margin:12px 0;">
        <div style="font-size:0.8rem;color:#8b7aaa;text-transform:uppercase;letter-spacing:0.1em;">
            🏆 Verified Outcome
        </div>
        <div style="font-family:'Syne',sans-serif;font-size:1.5rem;font-weight:800;
                    color:#86efac;margin:8px 0;">
            {result}
        </div>
        <div style="color:#6b5a8a;font-size:0.82rem;">
            Winnings distributed · {int(HOUSE_CUT*100)}% house cut went to weekly bonus pool
        </div>
    </div>
    """, unsafe_allow_html=True)

    if username in bet["bets"]:
        user_b = bet["bets"][username]
        won = user_b["option"] == result
        emoji = "🎉" if won else "😭"
        msg   = "YOU WON! V-Coins in your wallet!" if won else "Better luck next time bestie!"
        st.markdown(f"""
        <div class="{'toast-success' if won else 'toast-error'}">
            {emoji} You bet {user_b['amount']:,} V-Coins on '{user_b['option']}' — {msg}
        </div>
        """, unsafe_allow_html=True)
```

# ─────────────────────────────────────────────

# CREATE BET PAGE

# ─────────────────────────────────────────────

def page_create():
show_toast()
st.markdown(”## ➕ Submit a New Bet”)
st.markdown(”””
<div style="color:#8b7aaa;font-size:0.9rem;margin-bottom:20px;">
📝 Know something chaotic is about to happen on stream?
Submit a prediction and let the community bet on it! Keep it fun & stream-related 💜
</div>
“””, unsafe_allow_html=True)

```
with st.form("create_bet_form", clear_on_submit=True):
    vtuber_name = st.text_input("🌟 Indie VTuber Name",
                                placeholder="e.g. Filian, Chibidoki, Your Oshi...")
    title = st.text_input("🎲 Bet Title / Question",
                           placeholder="e.g. Will they rage quit before the second boss?")
    description = st.text_area("📖 Short Description (optional)",
                                placeholder="Add context! What's happening on stream?",
                                max_chars=280, height=80)
    category = st.selectbox("🏷️ Category",
                             list(CATEGORY_EMOJI.keys()))
    bet_type = st.radio("⚙️ Bet Type", ["Yes / No", "Over / Under", "Custom Options"])

    opt1 = opt2 = ""
    if bet_type == "Yes / No":
        opt1, opt2 = "YES 🎉", "NO 💀"
        st.info(f"Options will be: **{opt1}** and **{opt2}**")
    elif bet_type == "Over / Under":
        threshold = st.text_input("Threshold (e.g. '15 deaths', '20 minutes')")
        opt1 = f"OVER {threshold} 📈" if threshold else "OVER ?"
        opt2 = f"UNDER {threshold} 📉" if threshold else "UNDER ?"
        st.info(f"Options will be: **{opt1}** and **{opt2}**")
    else:
        opt1 = st.text_input("🅰️ Option A", placeholder="e.g. Finishes the game ✅")
        opt2 = st.text_input("🅱️ Option B", placeholder="e.g. Gets distracted 🌀")

    submitted = st.form_submit_button("🚀 Submit Bet to the Community!", use_container_width=True)

    if submitted:
        username = st.session_state.username
        errs = []
        if not vtuber_name.strip():
            errs.append("VTuber name can't be empty!")
        if not title.strip():
            errs.append("Bet title can't be empty!")
        if not opt1.strip() or not opt2.strip():
            errs.append("Both options must be filled in!")
        if errs:
            for e in errs:
                toast("error", e)
            st.rerun()
        else:
            new_bet = {
                "id":         str(uuid.uuid4())[:8],
                "vtuber":     vtuber_name.strip(),
                "title":      title.strip(),
                "description": description.strip(),
                "options":    [opt1.strip(), opt2.strip()],
                "status":     "open",
                "created_at": datetime.now().isoformat(),
                "closes_at":  (datetime.now() + timedelta(hours=24)).isoformat(),
                "bets":       {},
                "votes":      {},
                "result":     None,
                "created_by": username,
                "category":   category,
            }
            bets = load_bets()
            bets.append(new_bet)
            save_bets(bets)
            toast("success", f"Bet submitted! ✨ '{title[:40]}...' is now live!")
            nav("bets")
```

# ─────────────────────────────────────────────

# LEADERBOARD PAGE

# ─────────────────────────────────────────────

def page_leaderboard():
show_toast()
st.markdown(”## 🏆 Leaderboard”)
st.markdown(”””
<div style="color:#8b7aaa;font-size:0.9rem;margin-bottom:20px;">
👑 The most filthy rich and most clairvoyant members of the VTuberBets community.
Can you dethrone them? Probably not. But try anyway. 💜
</div>
“””, unsafe_allow_html=True)

```
users = load_users()
if not users:
    st.info("No users yet! Be the first to sign up 🌟")
    return

tab_rich, tab_accurate = st.tabs(["💰 Most V-Coins", "🎯 Most Accurate"])

with tab_rich:
    sorted_rich = sorted(users.values(), key=lambda u: u.get("coins", 0), reverse=True)
    st.markdown("### 💰 Richest Gremlins")
    rank_emojis = ["🥇", "🥈", "🥉"]
    for i, u in enumerate(sorted_rich[:10]):
        rank_e  = rank_emojis[i] if i < 3 else f"#{i+1}"
        rank_cls = f"rank-{i+1}" if i < 3 else ""
        st.markdown(f"""
        <div class="lb-row {rank_cls}">
            <div class="lb-rank">{rank_e}</div>
            <div class="lb-name">👾 {u['username']}</div>
            <div class="lb-coins">🪙 {u.get('coins',0):,}</div>
        </div>
        """, unsafe_allow_html=True)

with tab_accurate:
    sorted_acc = sorted(
        [u for u in users.values() if u.get("bets_placed", 0) >= 1],
        key=lambda u: u.get("bets_correct", 0) / max(u.get("bets_placed", 1), 1),
        reverse=True
    )
    st.markdown("### 🎯 Most Accurate Predictors (min. 1 bet)")
    if not sorted_acc:
        st.info("Nobody's placed a bet yet! Be the legend. 🌟")
    for i, u in enumerate(sorted_acc[:10]):
        placed  = u.get("bets_placed", 0)
        correct = u.get("bets_correct", 0)
        pct     = (correct / placed * 100) if placed else 0
        rank_e  = rank_emojis[i] if i < 3 else f"#{i+1}"
        rank_cls = f"rank-{i+1}" if i < 3 else ""
        st.markdown(f"""
        <div class="lb-row {rank_cls}">
            <div class="lb-rank">{rank_e}</div>
            <div class="lb-name">👾 {u['username']}</div>
            <div class="lb-coins" style="display:flex;flex-direction:column;align-items:flex-end;gap:2px;">
                <span style="color:#67e8f9">{pct:.0f}% correct</span>
                <span style="font-size:0.72rem;color:#6b5a8a">{correct}/{placed} bets</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")
st.markdown("""
<div style="text-align:center;color:#6b5a8a;font-size:0.82rem;padding:12px;">
    🌸 Leaderboard resets every Sunday midnight UTC<br>
    💜 Top 3 earners each week get a 2,000 V-Coin bonus from the house cut pool!<br>
    🎲 Keep predicting. Keep collecting. Keep being an absolute menace in chat.
</div>
""", unsafe_allow_html=True)
```

# ─────────────────────────────────────────────

# ROUTER

# ─────────────────────────────────────────────

def main():
if not st.session_state.username:
page_login()
return

```
render_sidebar()

page = st.session_state.page
if page == "home":
    page_home()
elif page == "bets":
    page_bets()
elif page == "bet_detail":
    page_bet_detail()
elif page == "create":
    page_create()
elif page == "leaderboard":
    page_leaderboard()
else:
    page_home()
```

main()
