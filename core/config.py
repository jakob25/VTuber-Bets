"""
core/config.py
Single source of truth for all tunable constants in VTuberBets.
Import this instead of using magic numbers anywhere.
"""

# ── Economy ────────────────────────────────────────────────────────────────
STARTING_COINS: int = 5000
DAILY_BONUS: int = 250
DAILY_COOLDOWN_HOURS: int = 20

# ── Betting ────────────────────────────────────────────────────────────────
HOUSE_CUT: float = 0.05
MIN_VOTES: int = 3
FALLBACK_DAYS: int = 6

# ── Clip Rewards ───────────────────────────────────────────────────────────
CLIP_TOP1_REWARD: int = 1500
CLIP_TOP2_REWARD: int = 750
CLIP_TOP3_REWARD: int = 250

# ── Roles ──────────────────────────────────────────────────────────────────
ROLES: list[str] = ["Viewer", "Streamer", "Clipper"]

# ── Bet Categories ─────────────────────────────────────────────────────────
CATEGORIES: list[str] = [
    "Hidden Gem", "Boss Fight", "Death Count", "Game Completion",
    "Yap Session / Just Chatting", "Tech Scuff", "Karaoke Arc",
    "Follower / Sub Goal", "Raid / Shoutout", "Chaos Moment", "Other"
]

# ── Badge Styles ───────────────────────────────────────────────────────────
BADGE_STYLES: dict[str, str] = {
    "gem_hunter":     "badge-gem",
    "high_roller":    "badge-roller",
    "first_vote":     "badge-vote",
    "indie_scout":    "badge-scout",
    "raid_master":    "badge-raid",
    "clipper_legend": "badge-scout",
}

# ── Role Styling ───────────────────────────────────────────────────────────
ROLE_CSS: dict[str, str] = {
    "Viewer":   "role-watcher",
    "Streamer": "role-streamer",
    "Clipper":  "role-clipper",
}

ROLE_COLOR: dict[str, str] = {
    "Viewer":   "#00aaff",
    "Streamer": "#cc44ff",
    "Clipper":  "#00ee88",
}
