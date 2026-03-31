
import streamlit as st
import uuid
from datetime import datetime, timedelta
from supabase import create_client, Client
import requests
import re
# testing testing 123
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
/* The gradient username */
.hero-name {
    font-family: 'Syne', sans-serif;
    font-size: 2rem;
    font-weight: 800;
    font-style: italic;
    background: linear-gradient(135deg, #aa00ff, #aa00ff, #0066ff, #00aaff, #00ccff);
    background-size: 100% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
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
    margin-bottom: 6px;
    font-size: 0.78rem;
    font-weight: 500;
    color: #aaccff;
}
.bar-pct {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    color: #3366aa;
}
.bar-bg {
    background: #111828;
    border-radius: 6px;
    height: 8px;
    overflow: hidden;
    border: 1px solid #1a2540;
}
.bar-fill {
    background: linear-gradient(90deg, #0066ff, #0088ff);
    height: 100%;
    border-radius: 6px;
    transition: width 0.5s ease;
}
.bar-fill-vote {
    background: linear-gradient(90deg, #ffaa00, #ffcc00);
    height: 100%;
    border-radius: 6px;
    transition: width 0.5s ease;
}

/* ── NOTICES ── */
.notice {
    padding: 10px 14px;
    border-radius: 8px;
    font-size: 0.8rem;
    line-height: 1.5;
    margin: 10px 0;
}
.notice-info {
    background: #001530;
    color: #4499ff;
    border: 1px solid #00337755;
}
.notice-success {
    background: #001a0d;
    color: #00ee88;
    border: 1px solid #00ee8833;
}
.notice-error {
    background: #200008;
    color: #ff4466;
    border: 1px solid #ff446633;
}

/* ── DUPLICATE WARNING ── */
.dup-warn {
    background: #1a1000;
    color: #ffaa00;
    border: 1px solid #ffaa0044;
    border-radius: 8px;
    padding: 12px 16px;
    font-size: 0.82rem;
    line-height: 1.5;
    margin: 12px 0;
}

/* ── LEADERBOARD ── */
.lb-row {
    display: flex;
    align-items: center;
    background: #0a0e1c;
    border: 1px solid #151e33;
    border-radius: 10px;
    padding: 14px 18px;
    margin-bottom: 10px;
    gap: 16px;
}
.lb-rank {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    color: #334466;
    min-width: 40px;
}
.lb-rank-top {
    color: #ffcc00;
    font-weight: 700;
}
.lb-name {
    flex: 1;
    font-size: 0.95rem;
    color: #b8ccee;
}
.lb-stat {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.88rem;
    color: #00ccff;
    font-weight: 600;
    text-align: right;
}

/* ── SECTIONS ── */
.section-label {
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #1e4080;
    margin-bottom: 8px;
    margin-top: 12px;
    font-family: 'JetBrains Mono', monospace;
}

/* ── BUTTONS (Streamlit overrides) ── */
.stButton > button {
    background: linear-gradient(135deg, #0055dd, #0077ff);
    color: white !important;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    font-size: 0.88rem;
    padding: 10px 20px;
    transition: all 0.2s;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #0066ff, #0088ff);
    box-shadow: 0 4px 12px rgba(0, 102, 255, 0.3);
}

/* ── FORMS ── */
.stTextInput input, .stTextArea textarea, .stSelectbox select {
    background: #0a0e1c !important;
    border: 1px solid #1a2540 !important;
    color: #c8d8f0 !important;
    border-radius: 6px;
}
.stTextInput input:focus, .stTextArea textarea:focus, .stSelectbox select:focus {
    border-color: #0066ff !important;
    box-shadow: 0 0 0 1px #0066ff !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  SUPABASE CONNECTION
# ─────────────────────────────────────────────
SUPABASE_URL = st.secrets.get("SUPABASE_URL", "")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "")

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("Missing Supabase credentials in secrets.")
    st.stop()

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ─────────────────────────────────────────────
#  CONSTANTS
# ─────────────────────────────────────────────
STARTING_COINS    = 10000
DEFAULT_BET       = 100
MIN_BET           = 10
HOUSE_CUT         = 0.05
MIN_VOTES         = 3
VOTE_WINDOW_HOURS = 24

CATEGORIES = [
    "Game Mastery",
    "Rage & Tilt",
    "Just Chatting",
    "Singing / Karaoke",
    "Misc",
]

# ─────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────
if "username" not in st.session_state:
    st.session_state.username = None
if "page" not in st.session_state:
    st.session_state.page = "home"
if "bet_id" not in st.session_state:
    st.session_state.bet_id = None
if "toast" not in st.session_state:
    st.session_state.toast = None

def nav(page_name: str, bet_id=None):
    st.session_state.page = page_name
    if bet_id:
        st.session_state.bet_id = bet_id

def set_toast(kind: str, message: str):
    st.session_state.toast = {"kind": kind, "message": message}

def show_toast():
    if st.session_state.toast:
        t = st.session_state.toast
        if t["kind"] == "success":
            st.success(t["message"])
        elif t["kind"] == "error":
            st.error(t["message"])
        elif t["kind"] == "warning":
            st.warning(t["message"])
        else:
            st.info(t["message"])
        st.session_state.toast = None

# ─────────────────────────────────────────────
#  AUTO-PULL FUNCTIONS FOR STREAM LINKS
# ─────────────────────────────────────────────
def extract_twitch_username(url: str) -> str:
    """Extract Twitch username from URL"""
    patterns = [
        r'twitch\.tv/([^/\?\#]+)',
        r'twitch\.tv/videos/\d+\?.*channel=([^&]+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, url, re.IGNORECASE)
        if match:
            return match.group(1)
    return ""

def extract_youtube_channel_id(url: str) -> tuple:
    """Extract YouTube channel ID or handle from URL"""
    # Pattern for @handle
    handle_match = re.search(r'youtube\.com/@([^/\?\#]+)', url, re.IGNORECASE)
    if handle_match:
        return ('handle', handle_match.group(1))
    
    # Pattern for /c/channelname or /channel/channelid
    channel_match = re.search(r'youtube\.com/(?:c|channel)/([^/\?\#]+)', url, re.IGNORECASE)
    if channel_match:
        return ('channel', channel_match.group(1))
    
    return (None, None)

def fetch_twitch_stream_info(username: str) -> dict:
    """
    Fetch Twitch stream info using Twitch API
    Returns dict with 'streamer_name' and 'category'
    """
    try:
        # Note: You'll need to add Twitch Client ID and Secret to Streamlit secrets
        client_id = st.secrets.get("TWITCH_CLIENT_ID", "")
        client_secret = st.secrets.get("TWITCH_CLIENT_SECRET", "")
        
        if not client_id or not client_secret:
            return {"error": "Twitch API credentials not configured"}
        
        # Get OAuth token
        token_response = requests.post(
            "https://id.twitch.tv/oauth2/token",
            params={
                "client_id": client_id,
                "client_secret": client_secret,
                "grant_type": "client_credentials"
            }
        )
        
        if token_response.status_code != 200:
            return {"error": "Failed to get Twitch access token"}
        
        access_token = token_response.json()["access_token"]
        
        # Get user info
        user_response = requests.get(
            "https://api.twitch.tv/helix/users",
            headers={
                "Client-ID": client_id,
                "Authorization": f"Bearer {access_token}"
            },
            params={"login": username}
        )
        
        if user_response.status_code != 200 or not user_response.json()["data"]:
            return {"error": "Twitch user not found"}
        
        user_data = user_response.json()["data"][0]
        user_id = user_data["id"]
        display_name = user_data["display_name"]
        
        # Get current stream info
        stream_response = requests.get(
            "https://api.twitch.tv/helix/streams",
            headers={
                "Client-ID": client_id,
                "Authorization": f"Bearer {access_token}"
            },
            params={"user_id": user_id}
        )
        
        if stream_response.status_code == 200 and stream_response.json()["data"]:
            stream_data = stream_response.json()["data"][0]
            return {
                "streamer_name": display_name,
                "category": stream_data["game_name"] or "Just Chatting"
            }
        else:
            # Stream is offline, just return the display name
            return {
                "streamer_name": display_name,
                "category": ""
            }
            
    except Exception as e:
        return {"error": str(e)}

def fetch_youtube_stream_info(channel_type: str, channel_id: str) -> dict:
    """
    Fetch YouTube channel info using YouTube Data API
    Returns dict with 'streamer_name' and 'category'
    """
    try:
        api_key = st.secrets.get("YOUTUBE_API_KEY", "")
        
        if not api_key:
            return {"error": "YouTube API key not configured"}
        
        # Get channel info
        if channel_type == 'handle':
            # Search by handle
            search_response = requests.get(
                "https://www.googleapis.com/youtube/v3/search",
                params={
                    "part": "snippet",
                    "q": channel_id,
                    "type": "channel",
                    "maxResults": 1,
                    "key": api_key
                }
            )
            
            if search_response.status_code != 200 or not search_response.json().get("items"):
                return {"error": "YouTube channel not found"}
            
            channel_title = search_response.json()["items"][0]["snippet"]["title"]
        else:
            # Get by channel ID
            channel_response = requests.get(
                "https://www.googleapis.com/youtube/v3/channels",
                params={
                    "part": "snippet",
                    "id": channel_id,
                    "key": api_key
                }
            )
            
            if channel_response.status_code != 200 or not channel_response.json().get("items"):
                return {"error": "YouTube channel not found"}
            
            channel_title = channel_response.json()["items"][0]["snippet"]["title"]
        
        return {
            "streamer_name": channel_title,
            "category": ""  # YouTube doesn't provide current game/category easily
        }
            
    except Exception as e:
        return {"error": str(e)}

def auto_pull_stream_info(stream_link: str) -> dict:
    """
    Main function to auto-pull stream info from Twitch or YouTube
    Returns dict with 'streamer_name' and 'category'
    """
    if not stream_link:
        return {}
    
    # Check if it's Twitch
    if 'twitch.tv' in stream_link.lower():
        username = extract_twitch_username(stream_link)
        if username:
            return fetch_twitch_stream_info(username)
    
    # Check if it's YouTube
    elif 'youtube.com' in stream_link.lower():
        channel_type, channel_id = extract_youtube_channel_id(stream_link)
        if channel_type and channel_id:
            return fetch_youtube_stream_info(channel_type, channel_id)
    
    return {}

# ─────────────────────────────────────────────
#  DB HELPERS
# ─────────────────────────────────────────────
def get_or_create_user(username: str) -> dict:
    resp = supabase.table("users").select("*").eq("username", username).execute()
    if resp.data:
        return resp.data[0]
    new_user = {
        "username": username,
        "coins": STARTING_COINS,
        "bets_placed": 0,
        "bets_correct": 0,
    }
    ins = supabase.table("users").insert(new_user).execute()
    return ins.data[0] if ins.data else new_user

def get_user(username: str):
    resp = supabase.table("users").select("*").eq("username", username).execute()
    return resp.data[0] if resp.data else None

def update_user_coins(username: str, delta: int):
    u = get_user(username)
    if not u:
        return
    new_amt = u["coins"] + delta
    supabase.table("users").update({"coins": new_amt}).eq("username", username).execute()

def create_bet(vtuber_name: str, stream_link: str, game_or_activity: str,
               title: str, description: str, options: list, category: str, created_by: str):
    bet_id = str(uuid.uuid4())
    bet_data = {
        "id": bet_id,
        "vtuber_name": vtuber_name,
        "stream_link": stream_link,
        "game_or_activity": game_or_activity,
        "title": title,
        "description": description,
        "options": options,
        "category": category,
        "status": "open",
        "created_by": created_by,
        "created_at": datetime.utcnow().isoformat(),
        "result": None,
    }
    supabase.table("bets").insert(bet_data).execute()

def get_all_bets():
    resp = supabase.table("bets").select("*").order("created_at", desc=True).execute()
    return resp.data if resp.data else []

def get_bet(bet_id: str):
    resp = supabase.table("bets").select("*").eq("id", bet_id).execute()
    return resp.data[0] if resp.data else None

def get_my_entry(bet_id: str, username: str):
    resp = (supabase.table("bet_entries")
            .select("*")
            .eq("bet_id", bet_id)
            .eq("username", username)
            .execute())
    return resp.data[0] if resp.data else None

def place_bet_entry(bet_id: str, username: str, option: str, amount: int):
    u = get_user(username)
    if u["coins"] < amount:
        return False, "Not enough V-Coins."
    update_user_coins(username, -amount)
    entry = {
        "bet_id": bet_id,
        "username": username,
        "option": option,
        "amount": amount,
        "placed_at": datetime.utcnow().isoformat(),
    }
    supabase.table("bet_entries").insert(entry).execute()
    supabase.table("users").update({"bets_placed": u["bets_placed"] + 1}).eq("username", username).execute()
    return True, "Bet placed."

def get_bet_pool(bet_id: str):
    resp = supabase.table("bet_entries").select("*").eq("bet_id", bet_id).execute()
    entries = resp.data if resp.data else []
    option_totals = {}
    for e in entries:
        opt = e["option"]
        option_totals[opt] = option_totals.get(opt, 0) + e["amount"]
    total_pot = sum(option_totals.values())
    return entries, option_totals, total_pot

def move_to_voting(bet_id: str):
    supabase.table("bets").update({
        "status": "voting",
        "voting_opened_at": datetime.utcnow().isoformat()
    }).eq("id", bet_id).execute()

def create_vote(bet_id: str, username: str, chosen_option: str):
    v = {
        "bet_id": bet_id,
        "username": username,
        "chosen_option": chosen_option,
        "voted_at": datetime.utcnow().isoformat(),
    }
    supabase.table("votes").insert(v).execute()

def get_votes(bet_id: str):
    resp = supabase.table("votes").select("*").eq("bet_id", bet_id).execute()
    data = resp.data if resp.data else []
    counts = {}
    for v in data:
        opt = v["chosen_option"]
        counts[opt] = counts.get(opt, 0) + 1
    return data, counts

def has_voted(bet_id: str, username: str) -> bool:
    resp = (supabase.table("votes")
            .select("*")
            .eq("bet_id", bet_id)
            .eq("username", username)
            .execute())
    return bool(resp.data)

def resolve_bet(bet_id: str):
    bet = get_bet(bet_id)
    if not bet or bet["status"] != "voting":
        return False, "Bet not in voting state."
    
    _, vote_counts = get_votes(bet_id)
    if not vote_counts:
        return False, "No votes recorded."
    
    winner_opt = max(vote_counts, key=vote_counts.get)
    entries, option_totals, total_pot = get_bet_pool(bet_id)
    
    house_take = int(total_pot * HOUSE_CUT)
    payout_pool = total_pot - house_take
    
    winning_pool = option_totals.get(winner_opt, 0)
    if winning_pool == 0:
        supabase.table("bets").update({"status": "closed", "result": winner_opt}).eq("id", bet_id).execute()
        return True, winner_opt
    
    for e in entries:
        if e["option"] == winner_opt:
            share = e["amount"] / winning_pool
            payout = int(share * payout_pool)
            update_user_coins(e["username"], payout)
            
            u = get_user(e["username"])
            supabase.table("users").update({
                "bets_correct": u["bets_correct"] + 1
            }).eq("username", e["username"]).execute()
    
    supabase.table("bets").update({"status": "closed", "result": winner_opt}).eq("id", bet_id).execute()
    return True, winner_opt

def check_duplicate(vtuber_name: str, title: str):
    all_bets = get_all_bets()
    dupes = []
    for b in all_bets:
        if b["status"] == "open" and b["vtuber_name"].lower() == vtuber_name.lower():
            if title.lower() in b["title"].lower() or b["title"].lower() in title.lower():
                dupes.append(b)
    return dupes

def leaderboard_rich():
    resp = supabase.table("users").select("*").order("coins", desc=True).limit(10).execute()
    return resp.data if resp.data else []

def leaderboard_accurate():
    resp = supabase.table("users").select("*").gte("bets_placed", 3).execute()
    users = resp.data if resp.data else []
    for u in users:
        u["pct"] = u["bets_correct"] / u["bets_placed"] if u["bets_placed"] else 0
    users.sort(key=lambda x: x["pct"], reverse=True)
    return users[:10]

# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        st.markdown('<div class="hero-eyebrow">VTuber Betting</div>', unsafe_allow_html=True)
        st.markdown('<div class="hero-title" style="font-size:1.6rem;">VTuberBets</div>', unsafe_allow_html=True)
        st.markdown('<div style="color:#1e4080;font-size:0.75rem;margin-bottom:24px;">Community prediction platform</div>',
                    unsafe_allow_html=True)

        u = get_user(st.session_state.username)
        if u:
            st.markdown(f"""
            <div style="background:#0a0e1c;border:1px solid #151e33;border-radius:10px;
                        padding:14px 18px;margin-bottom:20px;">
                <div style="color:#334466;font-size:0.7rem;text-transform:uppercase;
                            letter-spacing:0.1em;margin-bottom:6px;">Your Wallet</div>
                <div style="font-family:'Syne',sans-serif;font-size:1.5rem;
                            font-weight:800;color:#00ccff;">{u['coins']:,}</div>
                <div style="color:#1e4080;font-size:0.72rem;">V-Coins</div>
            </div>
            """, unsafe_allow_html=True)

        if st.button("🏠  Home", use_container_width=True):
            nav("home")
        if st.button("🎲  All Bets", use_container_width=True):
            nav("bets")
        if st.button("➕  Create Bet", use_container_width=True):
            nav("create_bet")
        if st.button("🏆  Leaderboard", use_container_width=True):
            nav("leaderboard")

        st.markdown("---")
        if st.button("Logout"):
            st.session_state.username = None
            st.session_state.page = "home"
            st.rerun()

# ─────────────────────────────────────────────
#  LOGIN PAGE
# ─────────────────────────────────────────────
def page_login():
    st.markdown("""
    <div class="hero-wrap">
        <div class="hero">
            <div class="hero-eyebrow">Welcome to</div>
            <div class="hero-title">VTuberBets</div>
            <div class="hero-sub">
                Predict stream outcomes, climb the leaderboard, and earn V-Coins.
                No real money — just pure prediction skill.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Enter your username to continue")
    username_input = st.text_input("Username", placeholder="Enter a unique username...", label_visibility="collapsed")
    if st.button("Continue", use_container_width=True):
        if username_input.strip():
            get_or_create_user(username_input.strip())
            st.session_state.username = username_input.strip()
            st.rerun()
        else:
            st.error("Please enter a username.")

# ─────────────────────────────────────────────
#  HOME PAGE
# ─────────────────────────────────────────────
def page_home():
    show_toast()
    username = st.session_state.username

    st.markdown(f"""
    <div class="hero-wrap">
        <div class="hero">
            <div class="hero-eyebrow">Powered by Community Votes</div>
            <div class="hero-title">
                Welcome, <span class="hero-name">{username}</span>
            </div>
            <div class="hero-sub">
                Predict VTuber stream outcomes, vote on results, and earn V-Coins for accurate calls.
                Track live bets, climb the leaderboard, and flex your prediction prowess.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("## Active Bets")
    bets = [b for b in get_all_bets() if b["status"] == "open"]
    if not bets:
        st.markdown('<div style="color:#334466;padding:20px 0;">No active bets right now. Create the first one!</div>',
                    unsafe_allow_html=True)
    else:
        for bet in bets[:5]:
            _, option_totals, total_pot = get_bet_pool(bet["id"])
            existing = get_my_entry(bet["id"], username)
            
            card_class = "card card-live"
            st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)
            st.markdown(f'<div class="vtag">{bet["vtuber_name"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="bet-title">{bet["title"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="bet-game">{bet["game_or_activity"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="pot">💰 {total_pot:,} V-Coins in the pot</div>', unsafe_allow_html=True)
            
            if existing:
                st.markdown(f'<div style="color:#00ee88;font-size:0.75rem;margin-top:6px;">✓ You bet {existing["amount"]:,} on "{existing["option"]}"</div>',
                            unsafe_allow_html=True)
            
            if st.button(f"View Bet", key=f"home_bet_{bet['id']}", use_container_width=True):
                nav("bet_detail", bet_id=bet["id"])
            
            st.markdown('</div>', unsafe_allow_html=True)

        if len(bets) > 5:
            st.markdown(f'<div style="color:#334466;font-size:0.8rem;margin-top:12px;">+ {len(bets)-5} more active bets</div>',
                        unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  ALL BETS PAGE
# ─────────────────────────────────────────────
def page_bets():
    show_toast()
    st.markdown("## All Bets")

    tab_open, tab_voting, tab_closed = st.tabs(["Open", "Voting", "Resolved"])

    username = st.session_state.username

    with tab_open:
        bets = [b for b in get_all_bets() if b["status"] == "open"]
        if not bets:
            st.markdown('<div style="color:#334466;padding:12px 0;">No open bets.</div>', unsafe_allow_html=True)
        for bet in bets:
            _, option_totals, total_pot = get_bet_pool(bet["id"])
            existing = get_my_entry(bet["id"], username)
            
            card_class = "card card-live"
            st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)
            st.markdown(f'<div class="vtag">{bet["vtuber_name"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="bet-title">{bet["title"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="bet-game">{bet["game_or_activity"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="pot">💰 {total_pot:,} V-Coins</div>', unsafe_allow_html=True)
            
            if existing:
                st.markdown(f'<div style="color:#00ee88;font-size:0.75rem;margin-top:6px;">✓ You bet {existing["amount"]:,} on "{existing["option"]}"</div>',
                            unsafe_allow_html=True)
            
            if st.button(f"View", key=f"open_{bet['id']}", use_container_width=True):
                nav("bet_detail", bet_id=bet["id"])
            st.markdown('</div>', unsafe_allow_html=True)

    with tab_voting:
        bets = [b for b in get_all_bets() if b["status"] == "voting"]
        if not bets:
            st.markdown('<div style="color:#334466;padding:12px 0;">No bets in voting phase.</div>', unsafe_allow_html=True)
        for bet in bets:
            card_class = "card card-voting"
            st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)
            st.markdown(f'<div class="vtag">{bet["vtuber_name"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="bet-title">{bet["title"]}</div>', unsafe_allow_html=True)
            st.markdown('<span class="pill pill-voting">Voting</span>', unsafe_allow_html=True)
            
            if st.button(f"Vote", key=f"voting_{bet['id']}", use_container_width=True):
                nav("bet_detail", bet_id=bet["id"])
            st.markdown('</div>', unsafe_allow_html=True)

    with tab_closed:
        bets = [b for b in get_all_bets() if b["status"] == "closed"]
        if not bets:
            st.markdown('<div style="color:#334466;padding:12px 0;">No resolved bets yet.</div>', unsafe_allow_html=True)
        for bet in bets:
            card_class = "card card-closed"
            st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)
            st.markdown(f'<div class="vtag">{bet["vtuber_name"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="bet-title">{bet["title"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="color:#9977ff;font-size:0.8rem;margin-top:6px;">Result: {bet.get("result", "N/A")}</div>',
                        unsafe_allow_html=True)
            
            if st.button(f"View", key=f"closed_{bet['id']}", use_container_width=True):
                nav("bet_detail", bet_id=bet["id"])
            st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  BET DETAIL PAGE
# ─────────────────────────────────────────────
def page_bet_detail():
    show_toast()
    bet_id = st.session_state.bet_id
    if not bet_id:
        st.error("No bet selected.")
        return

    bet = get_bet(bet_id)
    if not bet:
        st.error("Bet not found.")
        return

    username = st.session_state.username

    st.markdown(f'<div class="vtag">{bet["vtuber_name"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="bet-title" style="font-size:1.4rem;">{bet["title"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="bet-game" style="margin-bottom:14px;">{bet["game_or_activity"]}</div>', unsafe_allow_html=True)

    if bet["description"]:
        st.markdown(f'<div style="color:#4a6a99;font-size:0.85rem;line-height:1.6;margin-bottom:14px;">{bet["description"]}</div>',
                    unsafe_allow_html=True)

    if bet["stream_link"]:
        st.markdown(f'<div style="margin-bottom:10px;"><a href="{bet["stream_link"]}" target="_blank" style="color:#0088ff;text-decoration:none;">🔗 Stream Link</a></div>',
                    unsafe_allow_html=True)

    status_pill = {
        "open": "pill-open",
        "voting": "pill-voting",
        "closed": "pill-closed",
    }.get(bet["status"], "pill-open")
    st.markdown(f'<span class="pill {status_pill}">{bet["status"].upper()}</span>', unsafe_allow_html=True)

    entries, option_totals, total_pot = get_bet_pool(bet_id)
    existing = get_my_entry(bet_id, username)

    # ── OPEN ──
    if bet["status"] == "open":
        st.markdown(f'<div class="pot" style="margin:12px 0;">💰 Total Pot: {total_pot:,} V-Coins</div>', unsafe_allow_html=True)

        for opt in bet["options"]:
            amt = option_totals.get(opt, 0)
            pct = (amt / total_pot * 100) if total_pot else 0
            st.markdown(f"""
            <div class="bar-wrap">
                <div class="bar-label">
                    <span>{opt}</span>
                    <span class="bar-pct">{amt:,} VC  ({pct:.0f}%)</span>
                </div>
                <div class="bar-bg">
                    <div class="bar-fill" style="width:{pct}%"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        if existing:
            st.markdown(f"""
            <div class="notice notice-info">
                You've already bet {existing['amount']:,} V-Coins on "{existing['option']}".
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("### Place Your Bet")
            with st.form(f"place_bet_{bet_id}"):
                chosen_opt = st.selectbox("Pick an outcome", bet["options"])
                bet_amount = st.number_input("Bet amount (V-Coins)", min_value=MIN_BET, value=DEFAULT_BET, step=10)
                submitted = st.form_submit_button("Place Bet", use_container_width=True)
                if submitted:
                    ok, msg = place_bet_entry(bet_id, username, chosen_opt, bet_amount)
                    set_toast("success" if ok else "error", msg)
                    st.rerun()

        if bet["created_by"] == username:
            st.markdown("---")
            st.markdown("### Creator Controls")
            if st.button("Move to Voting Phase", use_container_width=True):
                move_to_voting(bet_id)
                set_toast("success", "Bet moved to voting. Participants can now vote on the outcome.")
                st.rerun()

    # ── VOTING ──
    elif bet["status"] == "voting":
        _, vote_counts = get_votes(bet_id)
        total_v = sum(vote_counts.values())
        st.markdown(f'<div style="color:#ffaa00;font-size:0.8rem;margin:10px 0;">⏳ Voting phase: {total_v} vote(s) so far</div>',
                    unsafe_allow_html=True)

        already_voted = has_voted(bet_id, username)
        if already_voted:
            st.markdown('<div class="notice notice-info">You have already voted on this bet.</div>',
                        unsafe_allow_html=True)
        else:
            st.markdown("### Cast Your Vote")
            with st.form(f"vote_{bet_id}"):
                vote_opt = st.selectbox("What was the actual outcome?", bet["options"])
                vote_submit = st.form_submit_button("Submit Vote", use_container_width=True)
                if vote_submit:
                    create_vote(bet_id, username, vote_opt)
                    set_toast("success", "Vote recorded.")
                    st.rerun()

        for opt in bet["options"]:
            vc = vote_counts.get(opt, 0)
            pct = (vc / total_v * 100) if total_v else 0
            st.markdown(f"""
            <div class="bar-wrap">
                <div class="bar-label">
                    <span>{opt}</span>
                    <span class="bar-pct" style="color:#ffcc00;">{vc} votes  ({pct:.0f}%)</span>
                </div>
                <div class="bar-bg">
                    <div class="bar-fill-vote" style="width:{pct}%"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        if total_v >= MIN_VOTES:
            winner_opt = max(vote_counts, key=vote_counts.get)
            if vote_counts[winner_opt] > total_v / 2:
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

    # Initialize session state for auto-pulled values
    if "auto_pulled_data" not in st.session_state:
        st.session_state.auto_pulled_data = {}
    
    # Stream link input with auto-pull button
    st.markdown('<div class="section-label">Stream Link (Optional but recommended)</div>', unsafe_allow_html=True)
    col1, col2 = st.columns([4, 1])
    
    with col1:
        stream_link = st.text_input(
            "Stream link (Twitch / YouTube)",
            placeholder="https://twitch.tv/... or https://youtube.com/@...",
            label_visibility="collapsed",
            key="stream_link_input"
        )
    
    with col2:
        if st.button("🔄 Auto-Pull", use_container_width=True):
            if stream_link:
                with st.spinner("Fetching stream info..."):
                    info = auto_pull_stream_info(stream_link)
                    if "error" in info:
                        set_toast("warning", f"Could not auto-pull: {info['error']}")
                    else:
                        st.session_state.auto_pulled_data = info
                        set_toast("success", "Stream info auto-pulled successfully!")
                st.rerun()
            else:
                set_toast("error", "Please enter a stream link first")
                st.rerun()

    # Display auto-pulled notification if data exists
    if st.session_state.auto_pulled_data:
        st.markdown(f"""
        <div class="notice notice-success">
            ✓ Auto-pulled: {st.session_state.auto_pulled_data.get('streamer_name', '')}
            {f" - {st.session_state.auto_pulled_data.get('category', '')}" if st.session_state.auto_pulled_data.get('category') else ''}
        </div>
        """, unsafe_allow_html=True)

    with st.form("create_bet", clear_on_submit=True):
        st.markdown('<div class="section-label">VTuber</div>', unsafe_allow_html=True)
        
        # Pre-fill with auto-pulled data if available
        default_vtuber = st.session_state.auto_pulled_data.get("streamer_name", "")
        default_game = st.session_state.auto_pulled_data.get("category", "")
        
        vtuber_name = st.text_input(
            "VTuber name *",
            placeholder="e.g. Filian, Chibidoki, your oshi...",
            label_visibility="collapsed",
            value=default_vtuber
        )

        st.markdown('<div class="section-label" style="margin-top:16px;">Stream Context</div>',
                    unsafe_allow_html=True)
        game_or_activity = st.text_input(
            "Game or activity *",
            placeholder="e.g. Elden Ring, Minecraft, Just Chatting, Karaoke...",
            value=default_game
        )

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
                    # Clear auto-pulled data after successful submission
                    st.session_state.auto_pulled_data = {}
                    set_toast("success", "Bet is now live.")
                    nav("bets")
                    st.rerun()

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
