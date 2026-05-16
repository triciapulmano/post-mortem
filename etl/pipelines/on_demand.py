import os
import sys
from dotenv import load_dotenv

load_dotenv()

from etl.extractors.instagram import get_post_data, get_account_history
from etl.transformers.normalize import normalize_post, normalize_account, compute_account_averages, normalize_post as normalize_history_post
from etl.loaders.db import upsert_account, upsert_post, upsert_posts_bulk, get_account_posts, get_benchmark, save_analysis
from ai.analyzer import analyze_post

def run(url: str, niche: str = "lifestyle") -> dict:
    print(f"\n[1/6] Detecting platform...")
    platform = _detect_platform(url)
    print(f"      Platform: {platform}")

    print(f"\n[2/6] Fetching post data...")
    raw_post = get_post_data(url)
    post = normalize_post(raw_post)
    account = normalize_account(raw_post)
    print(f"      Post by @{account['handle']} — {post['content_type']} — {post['engagement_rate']}% eng.")

    print(f"\n[3/6] Saving account + post to database...")
    account_id = upsert_account(account)
    post_id = upsert_post(post, account_id)
    print(f"      account_id: {account_id}")
    print(f"      post_id:    {post_id}")

    print(f"\n[4/6] Fetching account history...")
    cached_posts = get_account_posts(account_id, limit=50)

    if len(cached_posts) < 10:
        print(f"      Only {len(cached_posts)} posts cached — fetching from Instagram...")
        raw_history = get_account_history(account["handle"], limit=50)
        history_posts = [normalize_post(p) for p in raw_history]
        upsert_posts_bulk(history_posts, account_id)
        cached_posts = get_account_posts(account_id, limit=50)

    print(f"      Using {len(cached_posts)} posts for account averages")

    print(f"\n[5/6] Computing averages + fetching benchmark...")
    account_averages = compute_account_averages(cached_posts)
    benchmark = get_benchmark(platform, niche, post["content_type"])

    if not benchmark:
        print(f"      No benchmark found for {platform}/{niche}/{post['content_type']} — using empty benchmark")
    else:
        print(f"      Benchmark: median eng. rate {benchmark.get('median_engagement_rate')}%")

    print(f"\n[6/6] Running AI analysis...")
    result = analyze_post(post, account_averages, benchmark)
    analysis_id = save_analysis(post_id, result["scores"], result["brief"])
    print(f"      analysis_id: {analysis_id}")
    print(f"      Overall score: {result['scores'].get('overall', 'N/A')}")

    return {
        "analysis_id": analysis_id,
        "post_id": post_id,
        "account_id": account_id,
        "handle": account["handle"],
        "post": post,
        "account_averages": account_averages,
        "benchmark": benchmark,
        "scores": result["scores"],
        "brief": result["brief"],
    }

def _detect_platform(url: str) -> str:
    if "instagram.com" in url:
        return "instagram"
    if "x.com" in url or "twitter.com" in url:
        return "x"
    raise ValueError(f"Unsupported platform for URL: {url}")