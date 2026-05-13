"""
vtuber_profiles_db.py
──────────────────────────────────────────────────────────────────────
All database functions for VTuber profiles.

ADD THIS BLOCK to your existing database.py (paste at the bottom),
or keep as a separate module and import with:
  from vtuber_profiles_db import *

Every discovery feature — Constellation Map, Find My Oshi, future
games — calls get_profiles_for_discovery(). Adding a profile
automatically feeds all of them.
──────────────────────────────────────────────────────────────────────
"""

import re
import uuid
from datetime import datetime

# ── Slug helper ────────────────────────────────────────────────────────────

def slugify(name: str) -> str:
    """Turn 'Chibi Doki!!' into 'chibidoki'."""
    s = name.lower().strip()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s_-]+", "-", s)
    s = re.sub(r"^-+|-+$", "", s)
    return s


def unique_slug(display_name: str) -> str:
    """Generate a slug that doesn't already exist in the DB."""
    base = slugify(display_name)
    slug = base
    suffix = 2
    while True:
        existing = db().table("vtuber_profiles").select("id").eq("slug", slug).execute()
        if not existing.data:
            return slug
        slug = f"{base}-{suffix}"
        suffix += 1


# ── Canonical tags ─────────────────────────────────────────────────────────

def get_canonical_tags(category: str | None = None) -> list:
    """Return canonical tag definitions. category = 'vibe' | 'content' | 'cluster'"""
    q = db().table("canonical_tags").select("*").order("sort_order")
    if category:
        q = q.eq("category", category)
    return q.execute().data or []


# ── Create / Update ────────────────────────────────────────────────────────

def create_vtuber_profile(
    display_name: str,
    created_by: str,
    twitch_url: str = "",
    youtube_url: str = "",
    twitter_url: str = "",
    tiktok_url: str = "",
    other_links: list = None,
    avatar_url: str = "",
    short_bio: str = "",
    full_bio: str = "",
    lore: str = "",
    vibe_tags: list = None,
    content_tags: list = None,
    interest_tags: list = None,
    primary_cluster: str = "",
    timezone: str = "",
    typical_schedule: str = "",
    avg_stream_length: str = "",
    language: str = "English",
    energy_level: int = 3,
    chat_interaction: int = 3,
    lore_depth: int = 1,
    adult_content: bool = False,
    approx_size: str = "Under 100",
    is_indie: bool = True,
) -> tuple[bool, str]:
    """
    Create a new VTuber profile.
    Returns (success, profile_id_or_error_message).
    """
    if not display_name.strip():
        return False, "Display name is required."

    slug = unique_slug(display_name)

    profile_id = str(uuid.uuid4())

    db().table("vtuber_profiles").insert({
        "id":               profile_id,
        "display_name":     display_name.strip(),
        "slug":             slug,
        "created_by":       created_by,
        "claimed_by":       None,
        "is_claimed":       False,

        "twitch_url":       twitch_url.strip(),
        "youtube_url":      youtube_url.strip(),
        "twitter_url":      twitter_url.strip(),
        "tiktok_url":       tiktok_url.strip(),
        "other_links":      other_links or [],

        "avatar_url":       avatar_url.strip(),
        "banner_url":       "",
        "short_bio":        short_bio.strip(),
        "full_bio":         full_bio.strip(),
        "lore":             lore.strip(),

        # ── Discovery fields ──────────────────────────────────────────
        "vibe_tags":        vibe_tags or [],
        "content_tags":     content_tags or [],
        "interest_tags":    interest_tags or [],
        "primary_cluster":  primary_cluster.strip(),

        "timezone":         timezone,
        "typical_schedule": typical_schedule.strip(),
        "avg_stream_length":avg_stream_length,
        "language":         language,

        # ── Personality axes ──────────────────────────────────────────
        "energy_level":     energy_level,
        "chat_interaction": chat_interaction,
        "lore_depth":       lore_depth,
        "adult_content":    adult_content,

        "approx_size":      approx_size,
        "is_indie":         is_indie,
        "is_active":        True,

        "upvote_count":     0,
        "clip_count":       0,
        "bet_count":        0,
        "map_x":            None,
        "map_y":            None,

        "created_at":       datetime.utcnow().isoformat(),
        "updated_at":       datetime.utcnow().isoformat(),
    }).execute()

    return True, profile_id


def update_vtuber_profile(profile_id: str, fields: dict) -> bool:
    """Update any fields on an existing profile."""
    fields["updated_at"] = datetime.utcnow().isoformat()
    result = db().table("vtuber_profiles").update(fields).eq("id", profile_id).execute()
    return bool(result.data)


# ── Read ───────────────────────────────────────────────────────────────────

def get_profile_by_id(profile_id: str) -> dict | None:
    r = db().table("vtuber_profiles").select("*").eq("id", profile_id).execute()
    return r.data[0] if r.data else None


def get_profile_by_slug(slug: str) -> dict | None:
    r = db().table("vtuber_profiles").select("*").eq("slug", slug).execute()
    return r.data[0] if r.data else None


def get_profiles_by_user(username: str) -> list:
    """All profiles submitted by this user."""
    return db().table("vtuber_profiles").select("*") \
               .eq("created_by", username) \
               .order("created_at", desc=True).execute().data or []


def search_profiles(query: str = "", limit: int = 20) -> list:
    """Text search on display_name and short_bio."""
    if not query.strip():
        return get_profiles_for_discovery(limit=limit)
    return db().table("vtuber_profiles").select("*") \
               .ilike("display_name", f"%{query.strip()}%") \
               .eq("is_active", True) \
               .limit(limit).execute().data or []


# ══════════════════════════════════════════════════════════════════════════════
#  THE CENTRAL DISCOVERY QUERY
#  Every feature — Map, Find My Oshi, games — calls this.
#  Add filters as keyword args; defaults return everything active & indie.
# ══════════════════════════════════════════════════════════════════════════════

def get_profiles_for_discovery(
    cluster: str | None = None,
    vibe_tags: list | None = None,
    content_tags: list | None = None,
    energy_min: int | None = None,
    energy_max: int | None = None,
    approx_size: str | None = None,
    indie_only: bool = True,
    active_only: bool = True,
    limit: int = 200,
) -> list:
    """
    The single query all discovery features use.

    Returns profiles as dicts with all fields populated.
    Each profile is guaranteed to have:
      - id, slug, display_name
      - vibe_tags, content_tags, primary_cluster
      - energy_level, chat_interaction, lore_depth
      - upvote_count, clip_count, bet_count
      - map_x, map_y  (may be None if not yet positioned)
      - all links, bio, lore fields

    Usage examples:
      get_profiles_for_discovery()                      # full map data
      get_profiles_for_discovery(cluster="STEM")        # one cluster
      get_profiles_for_discovery(energy_min=4)          # high energy only
      get_profiles_for_discovery(vibe_tags=["Gremlin Energy"])
    """
    q = db().table("vtuber_profiles").select("*").order("upvote_count", desc=True)

    if active_only:
        q = q.eq("is_active", True)
    if indie_only:
        q = q.eq("is_indie", True)
    if cluster:
        q = q.eq("primary_cluster", cluster)
    if approx_size:
        q = q.eq("approx_size", approx_size)
    if energy_min is not None:
        q = q.gte("energy_level", energy_min)
    if energy_max is not None:
        q = q.lte("energy_level", energy_max)

    profiles = q.limit(limit).execute().data or []

    # Client-side vibe/content tag filtering (Supabase array overlap)
    if vibe_tags:
        profiles = [
            p for p in profiles
            if any(t in (p.get("vibe_tags") or []) for t in vibe_tags)
        ]
    if content_tags:
        profiles = [
            p for p in profiles
            if any(t in (p.get("content_tags") or []) for t in content_tags)
        ]

    return profiles


def get_constellation_data() -> dict:
    """
    Returns everything the Constellation Map needs in one call.
    Structure:
      {
        "profiles": [...],          # all active indie profiles
        "clusters": {               # grouped by primary_cluster
            "Chaos": [...],
            "STEM / Science": [...],
            ...
        },
        "total": int
      }
    """
    profiles = get_profiles_for_discovery(limit=500)
    clusters: dict[str, list] = {}
    for p in profiles:
        c = p.get("primary_cluster") or "Uncategorized"
        clusters.setdefault(c, []).append(p)
    return {
        "profiles": profiles,
        "clusters": clusters,
        "total": len(profiles),
    }


# ── Community: upvotes ─────────────────────────────────────────────────────

def upvote_profile(profile_id: str, username: str) -> tuple[bool, str]:
    """Toggle upvote. Returns (voted, message)."""
    existing = db().table("vtuber_upvotes").select("id") \
                   .eq("profile_id", profile_id).eq("username", username).execute()
    if existing.data:
        # Remove upvote
        db().table("vtuber_upvotes").delete() \
            .eq("profile_id", profile_id).eq("username", username).execute()
        db().table("vtuber_profiles") \
            .update({"upvote_count": max(0, (get_profile_by_id(profile_id) or {}).get("upvote_count", 1) - 1)}) \
            .eq("id", profile_id).execute()
        return False, "Upvote removed."
    else:
        db().table("vtuber_upvotes").insert({
            "id":         str(uuid.uuid4()),
            "profile_id": profile_id,
            "username":   username,
            "voted_at":   datetime.utcnow().isoformat(),
        }).execute()
        profile = get_profile_by_id(profile_id)
        if profile:
            db().table("vtuber_profiles") \
                .update({"upvote_count": (profile.get("upvote_count") or 0) + 1}) \
                .eq("id", profile_id).execute()
        return True, "Profile endorsed!"


def has_upvoted_profile(profile_id: str, username: str) -> bool:
    r = db().table("vtuber_upvotes").select("id") \
            .eq("profile_id", profile_id).eq("username", username).execute()
    return bool(r.data)


# ── Community: tag voting ──────────────────────────────────────────────────

def vote_on_tag(profile_id: str, username: str, tag: str, tag_type: str, vote: int):
    """vote = +1 or -1. Upserts."""
    db().table("vtuber_tag_votes").upsert({
        "id":         str(uuid.uuid4()),
        "profile_id": profile_id,
        "username":   username,
        "tag":        tag,
        "tag_type":   tag_type,
        "vote":       vote,
        "voted_at":   datetime.utcnow().isoformat(),
    }, on_conflict="profile_id,username,tag,tag_type").execute()


def get_tag_scores(profile_id: str) -> dict:
    """Returns {tag: net_score} for all tags on a profile."""
    votes = db().table("vtuber_tag_votes").select("tag,vote") \
                .eq("profile_id", profile_id).execute().data or []
    scores: dict[str, int] = {}
    for v in votes:
        scores[v["tag"]] = scores.get(v["tag"], 0) + v["vote"]
    return scores


# ── Counters (call these from create_bet / submit_clip) ────────────────────

def increment_profile_bet_count(profile_id: str):
    """Call after create_bet() when a bet references a VTuber profile."""
    p = get_profile_by_id(profile_id)
    if p:
        db().table("vtuber_profiles") \
            .update({"bet_count": (p.get("bet_count") or 0) + 1}) \
            .eq("id", profile_id).execute()


def increment_profile_clip_count(profile_id: str):
    """Call after submit_clip() when a clip references a VTuber profile."""
    p = get_profile_by_id(profile_id)
    if p:
        db().table("vtuber_profiles") \
            .update({"clip_count": (p.get("clip_count") or 0) + 1}) \
            .eq("id", profile_id).execute()


# ── Claiming ───────────────────────────────────────────────────────────────

def generate_claim_token(profile_id: str) -> str:
    """Generate a claim token for a VTuber to verify ownership."""
    token = str(uuid.uuid4())[:8].upper()
    db().table("vtuber_profiles").update({"claim_token": token}) \
        .eq("id", profile_id).execute()
    return token


def claim_profile(profile_id: str, username: str, token: str) -> tuple[bool, str]:
    """VTuber claims their profile using the token."""
    profile = get_profile_by_id(profile_id)
    if not profile:
        return False, "Profile not found."
    if profile.get("is_claimed"):
        return False, "Profile already claimed."
    if profile.get("claim_token") != token.upper().strip():
        return False, "Invalid claim token."
    db().table("vtuber_profiles").update({
        "is_claimed": True,
        "claimed_by": username,
        "claim_token": None,
    }).eq("id", profile_id).execute()
    return True, "Profile claimed! You now own this page."
