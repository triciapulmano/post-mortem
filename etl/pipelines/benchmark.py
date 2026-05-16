import os
import numpy as np
from datetime import date
from dotenv import load_dotenv

load_dotenv()

from etl.extractors.instagram import get_account_history, get_profile
from etl.transformers.normalize import normalize_post
from etl.loaders.db import get_connection

NICHES = [
    "lifestyle",
    "fashion",
    "fitness",
    "food",
    "travel",
    "beauty",
    "tech",
    "gaming",
    "finance",
    "sports",
]

NICHE_ACCOUNTS = {
    "lifestyle": ["humansofny", "natgeo"],
    "fashion": ["zara", "hm"],
    "fitness": ["nike", "gymshark"],
    "food": ["tasty", "buzzfeedtasty"],
    "travel": ["lonelyplanet", "airbnb"],
    "beauty": ["fentybeauty", "glossier"],
    "tech": ["nasa", "spacex"],
    "gaming": ["playstation", "xbox"],
    "finance": ["nerdwallet", "investopedia"],
    "sports": ["nba", "espn"],
}

def run():
    print(f"\n[benchmark] Starting benchmark pipeline — {date.today()}")
    week_of = date.today()

    for niche, accounts in NICHE_ACCOUNTS.items():
        print(f"\n[benchmark] Niche: {niche}")
        all_posts = []

        for handle in accounts:
            print(f"  Fetching @{handle}...")
            try:
                profile = get_profile(handle)
                raw_posts = get_account_history(handle, limit=25)
                normalized = []

                for raw in raw_posts:
                    raw["handle"] = handle
                    raw["platform"] = "instagram"
                    post = normalize_post(raw)
                    post["followers"] = profile.get("followers", 1)
                    normalized.append(post)

                all_posts.extend(normalized)
                print(f"  Got {len(normalized)} posts from @{handle}")
            except Exception as e:
                print(f"  Skipping @{handle}: {e}")
                continue

        if not all_posts:
            print(f"  No posts collected for {niche}, skipping")
            continue

        _compute_and_store(all_posts, "instagram", niche, week_of)

    print(f"\n[benchmark] Done.")

def _compute_and_store(posts: list, platform: str, niche: str, week_of: date):
    by_content_type = {}
    for post in posts:
        ct = post.get("content_type", "image")
        if ct not in by_content_type:
            by_content_type[ct] = []
        by_content_type[ct].append(post.get("engagement_rate", 0))

    conn = get_connection()
    cur = conn.cursor()

    for content_type, rates in by_content_type.items():
        if not rates:
            continue

        median_er = float(np.median(rates))
        p75_er = float(np.percentile(rates, 75))
        median_likes = float(np.median([
            p.get("likes", 0) for p in posts
            if p.get("content_type") == content_type
        ]))

        print(f"  [{content_type}] median={median_er:.2f}% p75={p75_er:.2f}%")

        cur.execute("""
            INSERT INTO benchmarks (
                platform, niche, content_type,
                median_engagement_rate, median_likes,
                p75_engagement_rate, week_of
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (platform, niche, content_type, week_of)
            DO UPDATE SET
                median_engagement_rate = EXCLUDED.median_engagement_rate,
                median_likes = EXCLUDED.median_likes,
                p75_engagement_rate = EXCLUDED.p75_engagement_rate
        """, (
            platform,
            niche,
            content_type,
            median_er,
            median_likes,
            p75_er,
            week_of,
        ))

    conn.commit()
    cur.close()
    conn.close()