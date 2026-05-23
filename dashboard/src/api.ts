import axios from "axios";

const BASE = process.env.REACT_APP_API_URL || "http://localhost:8000";

export interface Analysis {
  analysis_id: string;
  handle: string;
  platform: string;
  overall_score: number;
  score_timing: number;
  score_format: number;
  score_hook: number;
  score_topic: number;
  score_velocity: number;
  ai_explanation: string;
  created_at: string;
  post_url: string;
  caption: string;
  content_type: string;
  likes: number;
  comments: number;
  engagement_rate: number;
  posted_at: string;
  account_averages?: {
    avg_engagement_rate: number;
    avg_likes: number;
    best_days: string[];
    best_hours: number[];
    top_content_type: string;
    recent_themes: string[];
  };
  benchmark?: {
    median_engagement_rate: number;
    p75_engagement_rate: number;
  };
  scores?: {
    timing: number;
    format: number;
    hook: number;
    topic: number;
    velocity: number;
    overall: number;
  };
  brief?: string;
}

export const analyzePost = async (url: string, niche: string) => {
  const res = await axios.post(`${BASE}/analyze`, { url, niche });
  return res.data;
};

export const getAnalyses = async (): Promise<Analysis[]> => {
  const res = await axios.get(`${BASE}/analyses`);
  return res.data;
};

export const getAnalysis = async (id: string): Promise<Analysis> => {
  const res = await axios.get(`${BASE}/analyses/${id}`);
  return res.data;
};