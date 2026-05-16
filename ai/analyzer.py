from google import genai
from google.genai import types
import os
import json
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def analyze_post(post: dict, account_history: dict, benchmark: dict) -> dict:
    prompt = _build_prompt(post, account_history, benchmark)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    raw = response.text.strip()

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        clean = raw.replace("```json", "").replace("```", "").strip()
        result = json.loads(clean)

    scores = result.get("scores", {})
    scores["overall"] = result.get("overall", _compute_overall(scores))

    return {
        "scores": scores,
        "brief": result.get("brief", "")
    }

def _build_prompt(post: dict, account_history: dict, benchmark: dict) -> str:
    return f"""
You are an expert social media analyst. Analyze this post and score it across 5 dimensions.

## Target post
Platform: {post['platform']}
Caption: {post['caption'][:500]}
Content type: {post['content_type']}
Posted at: {post['posted_at']}
Likes: {post['likes']}
Comments: {post['comments']}
Shares: {post['shares']}
Engagement rate: {post['engagement_rate']}%

## Account historical averages (last 50 posts)
Avg engagement rate: {account_history.get('avg_engagement_rate', 'N/A')}%
Avg likes: {account_history.get('avg_likes', 'N/A')}
Best posting days: {account_history.get('best_days', 'N/A')}
Best posting hours: {account_history.get('best_hours', 'N/A')}
Top content type: {account_history.get('top_content_type', 'N/A')}
Recent hashtag themes: {account_history.get('recent_themes', 'N/A')}

## Platform benchmark ({post['platform']} — {benchmark.get('niche', 'general')} niche)
Median engagement rate: {benchmark.get('median_engagement_rate', 'N/A')}%
75th percentile engagement rate: {benchmark.get('p75_engagement_rate', 'N/A')}%

## Instructions
Score this post 0-100 on each dimension. Avoid clustering scores around 70-75 — be precise.
Use the account history and benchmark as reference points, not generic assumptions.
If benchmark data is unavailable, rely on account history only.

Dimensions:
- timing: Did this post go out at a high-engagement window for this account?
- format: Does the content type match what performs best for this account?
- hook: How strong is the opening line or visual hook?
- topic: Does this topic match what this audience responds to? Flag fatigue if themes repeat.
- velocity: How fast did it pick up engagement relative to this account's average?

Respond ONLY in this JSON format with no extra text:
{{
  "scores": {{
    "timing": <int 0-100>,
    "format": <int 0-100>,
    "hook": <int 0-100>,
    "topic": <int 0-100>,
    "velocity": <int 0-100>
  }},
  "overall": <int 0-100>,
  "brief": "<2-3 sentences. Lead with what drove performance. End with one specific actionable recommendation.>"
}}
"""

def _compute_overall(scores: dict) -> int:
    if not scores:
        return 0
    weights = {
        "timing": 0.15,
        "format": 0.20,
        "hook": 0.30,
        "topic": 0.20,
        "velocity": 0.15,
    }
    total = sum(scores.get(k, 0) * w for k, w in weights.items())
    return round(total)