from datetime import datetime, timezone
import re

def normalize_post(raw: dict) -> dict:
    return {
        "platform": raw["platform"],
        "platform_post_id": raw["platform_post_id"],
        "post_url": raw["post_url"],
        "handle": raw["handle"],
        "content_type": raw["content_type"],
        "caption": _clean_caption(raw.get("caption", "")),
        "likes": raw.get("likes", 0),
        "comments": raw.get("comments", 0),
        "shares": raw.get("shares", 0),
        "engagement_rate": raw.get("engagement_rate", 0.0),
        "posted_at": _normalize_datetime(raw.get("posted_at")),
        "raw_data": raw.get("raw_data", {}),
    }

def normalize_account(raw: dict) -> dict:
    return {
        "platform": raw["platform"],
        "handle": raw["handle"],
        "followers": raw.get("followers", 0),
        "following": raw.get("following", 0),
        "post_count": raw.get("post_count", 0),
    }

def compute_account_averages(posts: list[dict]) -> dict:
    if not posts:
        return {}

    engagement_rates = [p["engagement_rate"] for p in posts if p["engagement_rate"]]
    likes = [p["likes"] for p in posts]
    posted_ats = [p["posted_at"] for p in posts if p["posted_at"]]

    best_days, best_hours = _compute_best_times(posted_ats, engagement_rates, posts)
    top_content_type = _compute_top_content_type(posts)
    recent_themes = _extract_themes(posts)

    return {
        "avg_engagement_rate": round(sum(engagement_rates) / len(engagement_rates), 4) if engagement_rates else 0,
        "avg_likes": round(sum(likes) / len(likes), 1) if likes else 0,
        "best_days": best_days,
        "best_hours": best_hours,
        "top_content_type": top_content_type,
        "recent_themes": recent_themes,
    }

def _clean_caption(caption: str) -> str:
    if not caption:
        return ""
    caption = caption.strip()
    caption = re.sub(r'\s+', ' ', caption)
    return caption[:2000]

def _normalize_datetime(dt) -> datetime:
    if dt is None:
        return None
    if isinstance(dt, datetime):
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt
    return None

def _compute_best_times(posted_ats, engagement_rates, posts):
    if not posted_ats or not engagement_rates:
        return [], []

    day_scores = {}
    hour_scores = {}

    for post in posts:
        dt = post.get("posted_at")
        er = post.get("engagement_rate", 0)
        if not dt or not er:
            continue

        day = dt.strftime("%A")
        hour = dt.hour

        if day not in day_scores:
            day_scores[day] = []
        day_scores[day].append(er)

        if hour not in hour_scores:
            hour_scores[hour] = []
        hour_scores[hour].append(er)

    best_days = sorted(
        day_scores,
        key=lambda d: sum(day_scores[d]) / len(day_scores[d]),
        reverse=True
    )[:3]

    best_hours = sorted(
        hour_scores,
        key=lambda h: sum(hour_scores[h]) / len(hour_scores[h]),
        reverse=True
    )[:3]

    return best_days, best_hours

def _compute_top_content_type(posts: list[dict]) -> str:
    counts = {}
    for post in posts:
        ct = post.get("content_type", "image")
        counts[ct] = counts.get(ct, 0) + 1
    if not counts:
        return "image"
    return max(counts, key=counts.get)

def _extract_themes(posts: list[dict]) -> list[str]:
    all_hashtags = []
    for post in posts:
        raw = post.get("raw_data", {})
        hashtags = raw.get("hashtags", [])
        all_hashtags.extend([h.lower() for h in hashtags])

    counts = {}
    for tag in all_hashtags:
        counts[tag] = counts.get(tag, 0) + 1

    top = sorted(counts, key=counts.get, reverse=True)[:10]
    return top