"""
database.py
All Supabase connections, constants, and data access functions.
"""
import streamlit as st
import uuid
import bcrypt
from datetime import datetime, timedelta
from supabase import create_client, Client

# ── Constants ──────────────────────────────────────────────────────────────
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

ROLES = ["Viewer", "Streamer", "Clipper"]

BADGE_STYLES = {
    "gem_hunter":     "badge-gem",
    "high_roller":    "badge-roller",
    "first_vote":     "badge-vote",
    "indie_scout":    "badge-scout",
    "raid_master":    "badge-raid",
    "clipper_legend": "badge-scout",
}

# ── Connection ─────────────────────────────────────────────────────────────
@st.cache_resource
def get_supabase() -> Client:
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

def db() -> Client:
    return get_supabase()

# ── Auth ───────────────────────────────────────────────────────────────────
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

# ── Users ──────────────────────────────────────────────────────────────────
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

# ── Bets ───────────────────────────────────────────────────────────────────
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

# ── Entries ────────────────────────────────────────────────────────────────
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

# ── Votes ──────────────────────────────────────────────────────────────────
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

# ── Resolution ─────────────────────────────────────────────────────────────
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

# ── Achievements ───────────────────────────────────────────────────────────
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

# ── Shop ───────────────────────────────────────────────────────────────────
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

# ── Leaderboard ────────────────────────────────────────────────────────────
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
