from apify_client import ApifyClient
import os
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

client = ApifyClient(os.getenv("APIFY_API_TOKEN"))

def get_post_data(url: str) -> dict:
    run_input = {
        "directUrls": [url],
        "resultsType": "posts",
        "resultsLimit": 1,
    }
    run = client.actor("shu8hvrXbJbY3Eb9W").call(run_input=run_input)
    items = list(client.dataset(run["defaultDatasetId"]).iterate_items())

    if not items:
        raise ValueError(f"No data returned for URL: {url}")

    item = items[0]
    handle = item.get("ownerUsername", "")
    profile = get_profile(handle)

    return _parse_post(item, profile)

def get_account_history(handle: str, limit: int = 50) -> list[dict]:
    profile = get_profile(handle)

    run_input = {
        "directUrls": [f"https://www.instagram.com/{handle}/"],
        "resultsType": "posts",
        "resultsLimit": limit,
    }
    run = client.actor("shu8hvrXbJbY3Eb9W").call(run_input=run_input)
    items = list(client.dataset(run["defaultDatasetId"]).iterate_items())

    return [_parse_post(item, profile) for item in items]

def get_profile(handle: str) -> dict:
    run_input = {
        "usernames": [handle],
    }
    run = client.actor("dSCLg0C3YEZ83HzYX").call(run_input=run_input)
    items = list(client.dataset(run["defaultDatasetId"]).iterate_items())

    if not items:
        return {}

    p = items[0]
    return {
        "followers": p.get("followersCount", 0) or 0,
        "following": p.get("followsCount", 0) or 0,
        "post_count": p.get("postsCount", 0) or 0,
    }

def _parse_post(item: dict, profile: dict) -> dict:
    handle = item.get("ownerUsername", "")
    followers = profile.get("followers", 0) or 1
    likes = item.get("likesCount", 0) or 0
    comments = item.get("commentsCount", 0) or 0
    engagement_rate = round(((likes + comments) / followers * 100), 4)

    timestamp = item.get("timestamp")
    posted_at = datetime.fromisoformat(
        timestamp.replace("Z", "+00:00")
    ) if timestamp else None

    return {
        "platform": "instagram",
        "platform_post_id": item.get("shortCode", ""),
        "post_url": item.get("url", ""),
        "handle": handle,
        "content_type": _get_content_type(item),
        "caption": item.get("caption", "") or "",
        "likes": likes,
        "comments": comments,
        "shares": 0,
        "engagement_rate": engagement_rate,
        "posted_at": posted_at,
        "followers": profile.get("followers", 0),
        "following": profile.get("following", 0),
        "post_count": profile.get("post_count", 0),
        "raw_data": {
            "shortcode": item.get("shortCode", ""),
            "is_video": item.get("isVideo", False),
            "video_view_count": item.get("videoViewCount", 0),
            "location": item.get("locationName"),
            "hashtags": item.get("hashtags", []) or [],
        }
    }

def _get_content_type(item: dict) -> str:
    if item.get("isVideo"):
        return "video"
    if item.get("type") == "Sidecar":
        return "carousel"
    return "image"