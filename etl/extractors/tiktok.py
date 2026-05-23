from apify_client import ApifyClient
import os
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

client = ApifyClient(os.getenv("APIFY_API_TOKEN"))

def get_post_data(url: str) -> dict:
    run_input = {
        "postURLs": [url],
        "maxItems": 1,
    }
    run = client.actor("GdWCkxBtKWOsKjdch").call(run_input=run_input)
    items = list(client.dataset(run["defaultDatasetId"]).iterate_items())

    if not items:
        raise ValueError(f"No data returned for URL: {url}")

    return _parse_post(items[0])

def get_account_history(handle: str, limit: int = 50) -> list[dict]:
    run_input = {
        "profiles": [handle],
        "resultsPerPage": limit,
        "maxItems": limit,
    }
    run = client.actor("GdWCkxBtKWOsKjdch").call(run_input=run_input)
    items = list(client.dataset(run["defaultDatasetId"]).iterate_items())

    return [_parse_post(item) for item in items]

def _parse_post(item: dict) -> dict:
    author = item.get("authorMeta", {})
    fans = author.get("fans", 0) or 1
    likes = item.get("diggCount", 0) or 0
    comments = item.get("commentCount", 0) or 0
    shares = item.get("shareCount", 0) or 0
    plays = item.get("playCount", 0) or 0

    engagement_rate = round(
        ((likes + comments + shares) / fans * 100), 4
    ) if fans else 0

    timestamp = item.get("createTimeISO")
    if timestamp:
        posted_at = datetime.fromisoformat(
            timestamp.replace("Z", "+00:00")
        )
    else:
        posted_at = None

    hashtags = [h.get("name", "") for h in item.get("hashtags", [])]

    return {
        "platform": "tiktok",
        "platform_post_id": item.get("id", ""),
        "post_url": item.get("webVideoUrl", ""),
        "handle": author.get("name", ""),
        "content_type": "slideshow" if item.get("isSlideshow") else "video",
        "caption": item.get("text", "") or "",
        "likes": likes,
        "comments": comments,
        "shares": shares,
        "engagement_rate": engagement_rate,
        "posted_at": posted_at,
        "followers": fans,
        "following": author.get("following", 0),
        "post_count": author.get("video", 0),
        "raw_data": {
            "play_count": plays,
            "collect_count": item.get("collectCount", 0),
            "repost_count": item.get("repostCount", 0),
            "is_ad": item.get("isAd", False),
            "is_pinned": item.get("isPinned", False),
            "hashtags": hashtags,
            "music": item.get("musicMeta", {}).get("musicName", ""),
        }
    }