import { useEffect, useState } from "react";
import { useParams, useLocation, useNavigate } from "react-router-dom";
import { getAnalysis, Analysis } from "../api";
import ScoreBar from "../components/ScoreBar";

export default function AnalysisPage() {
  const { id } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const [data, setData] = useState<Analysis | null>(location.state || null);

  useEffect(() => {
    if (!data && id) getAnalysis(id).then(setData);
  }, [id]);

  if (!data) return (
    <div style={{ padding: 60, textAlign: "center", color: "var(--muted)" }}>Loading...</div>
  );

  const scores = data.scores || {
    timing: data.score_timing,
    format: data.score_format,
    hook: data.score_hook,
    topic: data.score_topic,
    velocity: data.score_velocity,
    overall: data.overall_score,
  };

  const brief = data.brief || data.ai_explanation;
  const scoreColor = (s: number) => s >= 75 ? "#c8f566" : s >= 50 ? "#f5a623" : "#ff5c5c";
  const vsAvg = data.account_averages
    ? ((data.engagement_rate - data.account_averages.avg_engagement_rate) / data.account_averages.avg_engagement_rate * 100).toFixed(0)
    : null;

  return (
    <div style={{ maxWidth: 720, margin: "0 auto", padding: "60px 24px" }}>
      <button
        onClick={() => navigate("/")}
        style={{ background: "none", border: "none", color: "var(--muted)", fontSize: 13, marginBottom: 32, padding: 0, display: "flex", alignItems: "center", gap: 6 }}
      >
        ← back
      </button>

      <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", marginBottom: 32 }}>
        <div>
          <p style={{ fontFamily: "'DM Mono', monospace", fontSize: 11, color: "var(--accent)", letterSpacing: 2, textTransform: "uppercase", marginBottom: 8 }}>
            {data.platform} · {data.content_type}
          </p>
          <h2 style={{ fontFamily: "'Instrument Serif', serif", fontSize: 28, fontWeight: 400, marginBottom: 4 }}>
            @{data.handle}
          </h2>
          <a href={data.post_url} target="_blank" rel="noreferrer" style={{ fontSize: 12, color: "var(--muted)", textDecoration: "underline" }}>
            view original post ↗
          </a>
        </div>
        <div style={{ textAlign: "right" }}>
          <p style={{ fontFamily: "'DM Mono', monospace", fontSize: 52, fontWeight: 500, lineHeight: 1, color: scoreColor(scores.overall) }}>
            {Math.round(scores.overall)}
          </p>
          <p style={{ fontSize: 12, color: "var(--muted)" }}>overall score</p>
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 10, marginBottom: 24 }}>
        {[
          { label: "Likes", value: data.likes.toLocaleString() },
          { label: "Eng. rate", value: `${data.engagement_rate.toFixed(2)}%` },
          { label: "vs account avg", value: vsAvg ? `${Number(vsAvg) > 0 ? "+" : ""}${vsAvg}%` : "N/A", color: vsAvg ? (Number(vsAvg) > 0 ? "#c8f566" : "#ff5c5c") : "var(--muted)" },
        ].map(({ label, value, color }) => (
          <div key={label} style={{ background: "var(--surface)", border: "1px solid var(--border)", borderRadius: "var(--radius)", padding: "14px 16px" }}>
            <p style={{ fontSize: 11, color: "var(--muted)", textTransform: "uppercase", letterSpacing: 1, marginBottom: 6 }}>{label}</p>
            <p style={{ fontFamily: "'DM Mono', monospace", fontSize: 20, fontWeight: 500, color: color || "var(--text)" }}>{value}</p>
          </div>
        ))}
      </div>

      <div style={{ background: "var(--surface)", border: "1px solid var(--border)", borderRadius: "var(--radius)", padding: 24, marginBottom: 16 }}>
        <p style={{ fontSize: 12, color: "var(--muted)", textTransform: "uppercase", letterSpacing: 1.5, fontFamily: "'DM Mono', monospace", marginBottom: 20 }}>
          Score breakdown
        </p>
        {Object.entries(scores).filter(([k]) => k !== "overall").map(([k, v]) => (
          <ScoreBar key={k} label={k} score={v as number} />
        ))}
      </div>

      <div style={{ background: "var(--surface)", border: "1px solid var(--border)", borderRadius: "var(--radius)", padding: 24, marginBottom: 16 }}>
        <p style={{ fontSize: 12, color: "var(--muted)", textTransform: "uppercase", letterSpacing: 1.5, fontFamily: "'DM Mono', monospace", marginBottom: 14 }}>
          AI brief
        </p>
        <p style={{ fontSize: 15, lineHeight: 1.7, color: "var(--text)" }}>{brief}</p>
      </div>

      {data.account_averages && (
        <div style={{ background: "var(--surface)", border: "1px solid var(--border)", borderRadius: "var(--radius)", padding: 24 }}>
          <p style={{ fontSize: 12, color: "var(--muted)", textTransform: "uppercase", letterSpacing: 1.5, fontFamily: "'DM Mono', monospace", marginBottom: 16 }}>
            Account context
          </p>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, fontSize: 13 }}>
            <div>
              <p style={{ color: "var(--muted)", marginBottom: 2 }}>Avg engagement rate</p>
              <p style={{ fontFamily: "'DM Mono', monospace" }}>{data.account_averages.avg_engagement_rate.toFixed(2)}%</p>
            </div>
            <div>
              <p style={{ color: "var(--muted)", marginBottom: 2 }}>Top content type</p>
              <p style={{ fontFamily: "'DM Mono', monospace" }}>{data.account_averages.top_content_type}</p>
            </div>
            <div>
              <p style={{ color: "var(--muted)", marginBottom: 2 }}>Best days</p>
              <p style={{ fontFamily: "'DM Mono', monospace" }}>{data.account_averages.best_days.join(", ")}</p>
            </div>
            <div>
              <p style={{ color: "var(--muted)", marginBottom: 2 }}>Best hours</p>
              <p style={{ fontFamily: "'DM Mono', monospace" }}>{data.account_averages.best_hours.map(h => `${h}:00`).join(", ")}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}