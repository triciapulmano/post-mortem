from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import psycopg2.extras
from etl.pipelines.on_demand import run
from etl.loaders.db import get_connection

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    url: str
    niche: str = "lifestyle"

@app.post("/analyze")
def analyze(req: AnalyzeRequest):
    try:
        result = run(req.url, niche=req.niche)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analyses")
def get_analyses():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""
        SELECT
            a.id as analysis_id,
            a.overall_score,
            a.score_timing,
            a.score_format,
            a.score_hook,
            a.score_topic,
            a.score_velocity,
            a.ai_explanation,
            a.created_at,
            p.post_url,
            p.caption,
            p.content_type,
            p.likes,
            p.comments,
            p.engagement_rate,
            p.posted_at,
            ac.handle,
            ac.platform
        FROM analyses a
        JOIN posts p ON a.post_id = p.id
        JOIN accounts ac ON p.account_id = ac.id
        ORDER BY a.created_at DESC
        LIMIT 50
    """)
    rows = [dict(r) for r in cur.fetchall()]
    cur.close()
    conn.close()
    return rows

@app.get("/analyses/{analysis_id}")
def get_analysis(analysis_id: str):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""
        SELECT
            a.id as analysis_id,
            a.overall_score,
            a.score_timing,
            a.score_format,
            a.score_hook,
            a.score_topic,
            a.score_velocity,
            a.ai_explanation,
            a.created_at,
            p.post_url,
            p.caption,
            p.content_type,
            p.likes,
            p.comments,
            p.engagement_rate,
            p.posted_at,
            ac.handle,
            ac.platform
        FROM analyses a
        JOIN posts p ON a.post_id = p.id
        JOIN accounts ac ON p.account_id = ac.id
        WHERE a.id = %s
    """, (analysis_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    result = dict(row)
    account_id = result.pop("account_id")

    # compute account averages from cached posts
    cur.execute("""
        SELECT content_type, engagement_rate, likes, posted_at, raw_data
        FROM posts
        WHERE account_id = %s
        ORDER BY posted_at DESC
        LIMIT 50
    """, (account_id,))

    posts = [dict(r) for r in cur.fetchall()]
    cur.close()
    conn.close()

    if posts:
        from etl.transformers.normalize import compute_account_averages
        result["account_averages"] = compute_account_averages(posts)
    else:
        result["account_averages"] = None

    return result

@app.get("/health")
def health():
    return {"status": "ok"}