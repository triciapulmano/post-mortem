import tweepy
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

client = tweepy.Client(bearer_token=os.getenv("X_BEARER_TOKEN"))

def get_post_data(url: str) -> dict:
    tweet_id = _extract_tweet_id(url)

    tweet = client.get_tweet(
        tweet_id,
        tweet_fields=["created_at", "public_metrics", "entities", "attachments"],
        expansions=["author_id", "attachments.media_keys"],
        media_fields=["type", "public_metrics"],
        user_fields=["username", "public_metrics"]
    )

    user = tweet.includes["users"][0]
    metrics = tweet.data.public_metrics
    media = tweet.includes.get("media", [])

    followers = user.public_metrics["followers_count"]
    likes = metrics["like_count"]
    comments = metrics["reply_count"]
    shares = metrics["retweet_count"] + metrics["quote_count"]
    engagement_rate = ((likes + comments + shares) / followers * 100) if followers else 0

    return {
        "platform": "x",
        "platform_post_id": str(tweet_id),
        "post_url": url,
        "handle": user.username,
        "content_type": _get_content_type(tweet.data, media),
        "caption": tweet.data.text,
        "likes": likes,
        "comments": comments,
        "shares": shares,
        "engagement_rate": round(engagement_rate, 4),
        "posted_at": tweet.data.created_at,
        "followers": followers,
        "following": user.public_metrics["following_count"],
        "post_count": user.public_metrics["tweet_count"],
        "raw_data": {
            "tweet_id": str(tweet_id),
            "retweet_count": metrics["retweet_count"],
            "quote_count": metrics["quote_count"],
            "impression_count": metrics.get("impression_count", 0),
            "hashtags": [
                tag["tag"] for tag in
                (tweet.data.entities or {}).get("hashtags", [])
            ],
            "media_types": [m.type for m in media],
        }
    }

def get_account_history(handle: str, limit: int = 50) -> list[dict]:
    user = client.get_user(
        username=handle,
        user_fields=["public_metrics"]
    )
    followers = user.data.public_metrics["followers_count"]
    user_id = user.data.id

    tweets = client.get_users_tweets(
        user_id,
        max_results=min(limit, 100),
        tweet_fields=["created_at", "public_metrics", "attachments"],
        expansions=["attachments.media_keys"],
        media_fields=["type"]
    )

    if not tweets.data:
        return []

    media_map = {
        m.media_key: m
        for m in (tweets.includes or {}).get("media", [])
    }

    posts = []
    for tweet in tweets.data:
        metrics = tweet.public_metrics
        likes = metrics["like_count"]
        comments = metrics["reply_count"]
        shares = metrics["retweet_count"] + metrics["quote_count"]
        engagement_rate = ((likes + comments + shares) / followers * 100) if followers else 0

        media_keys = (tweet.attachments or {}).get("media_keys", [])
        media = [media_map[k] for k in media_keys if k in media_map]

        posts.append({
            "platform_post_id": str(tweet.id),
            "post_url": f"https://x.com/{handle}/status/{tweet.id}",
            "content_type": _get_content_type(tweet, media),
            "caption": tweet.text,
            "likes": likes,
            "comments": comments,
            "shares": shares,
            "engagement_rate": round(engagement_rate, 4),
            "posted_at": tweet.created_at,
        })

    return posts

def _extract_tweet_id(url: str) -> int:
    return int(url.rstrip("/").split("/")[-1])

def _get_content_type(tweet, media: list) -> str:
    if not media:
        return "text"
    types = [m.type for m in media]
    if "video" in types:
        return "video"
    if len(media) > 1:
        return "carousel"
    return "image"