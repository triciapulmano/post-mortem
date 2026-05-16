import psycopg2
import psycopg2.extras
import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"))

def upsert_account(account: dict) -> str:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO accounts (platform, handle, last_fetched_at)
        VALUES (%s, %s, %s)
        ON CONFLICT (platform, handle)
        DO UPDATE SET last_fetched_at = EXCLUDED.last_fetched_at
        RETURNING id
    """, (
        account["platform"],
        account["handle"],
        datetime.utcnow()
    ))

    account_id = cur.fetchone()[0]

    cur.execute("""
        INSERT INTO account_snapshots (account_id, followers, following, post_count)
        VALUES (%s, %s, %s, %s)
    """, (
        account_id,
        account.get("followers", 0),
        account.get("following", 0),
        account.get("post_count", 0)
    ))

    conn.commit()
    cur.close()
    conn.close()

    return str(account_id)

def upsert_post(post: dict, account_id: str) -> str:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO posts (
            account_id, platform_post_id, post_url, content_type,
            caption, likes, comments, shares, engagement_rate,
            posted_at, raw_data
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (platform_post_id)
        DO UPDATE SET
            likes = EXCLUDED.likes,
            comments = EXCLUDED.comments,
            shares = EXCLUDED.shares,
            engagement_rate = EXCLUDED.engagement_rate
        RETURNING id
    """, (
        account_id,
        post["platform_post_id"],
        post["post_url"],
        post["content_type"],
        post["caption"],
        post["likes"],
        post["comments"],
        post["shares"],
        post["engagement_rate"],
        post["posted_at"],
        json.dumps(post["raw_data"])
    ))

    post_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()

    return str(post_id)

def upsert_posts_bulk(posts: list[dict], account_id: str) -> list[str]:
    conn = get_connection()
    cur = conn.cursor()
    post_ids = []

    for post in posts:
        cur.execute("""
            INSERT INTO posts (
                account_id, platform_post_id, post_url, content_type,
                caption, likes, comments, shares, engagement_rate,
                posted_at, raw_data
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (platform_post_id)
            DO UPDATE SET
                likes = EXCLUDED.likes,
                comments = EXCLUDED.comments,
                shares = EXCLUDED.shares,
                engagement_rate = EXCLUDED.engagement_rate
            RETURNING id
        """, (
            account_id,
            post["platform_post_id"],
            post["post_url"],
            post["content_type"],
            post["caption"],
            post["likes"],
            post["comments"],
            post["shares"],
            post["engagement_rate"],
            post["posted_at"],
            json.dumps(post.get("raw_data", {}))
        ))
        post_ids.append(str(cur.fetchone()[0]))

    conn.commit()
    cur.close()
    conn.close()

    return post_ids

def save_analysis(post_id: str, scores: dict, explanation: str) -> str:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO analyses (
            post_id, score_timing, score_format, score_hook,
            score_topic, score_velocity, overall_score, ai_explanation
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (post_id)
        DO UPDATE SET
            score_timing = EXCLUDED.score_timing,
            score_format = EXCLUDED.score_format,
            score_hook = EXCLUDED.score_hook,
            score_topic = EXCLUDED.score_topic,
            score_velocity = EXCLUDED.score_velocity,
            overall_score = EXCLUDED.overall_score,
            ai_explanation = EXCLUDED.ai_explanation
        RETURNING id
    """, (
        post_id,
        scores.get("timing"),
        scores.get("format"),
        scores.get("hook"),
        scores.get("topic"),
        scores.get("velocity"),
        scores.get("overall"),
        explanation
    ))

    analysis_id = str(cur.fetchone()[0])
    conn.commit()
    cur.close()
    conn.close()

    return analysis_id

def get_account_posts(account_id: str, limit: int = 50) -> list[dict]:
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cur.execute("""
        SELECT * FROM posts
        WHERE account_id = %s
        ORDER BY posted_at DESC
        LIMIT %s
    """, (account_id, limit))

    posts = [dict(row) for row in cur.fetchall()]
    cur.close()
    conn.close()

    return posts

def get_benchmark(platform: str, niche: str, content_type: str) -> dict:
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cur.execute("""
        SELECT * FROM benchmarks
        WHERE platform = %s AND niche = %s AND content_type = %s
        ORDER BY week_of DESC
        LIMIT 1
    """, (platform, niche, content_type))

    row = cur.fetchone()
    cur.close()
    conn.close()

    return dict(row) if row else {}