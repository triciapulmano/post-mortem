import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { analyzePost, getAnalyses, Analysis } from "../api";
import NicheSelect from "../components/NicheSelect";

export default function Home() {
  const [url, setUrl] = useState("");
  const [niche, setNiche] = useState("lifestyle");
  const [loading, setLoading] = useState(false);
  const [analyses, setAnalyses] = useState<Analysis[]>([]);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    getAnalyses().then(setAnalyses).catch(() => {});
  }, []);

  const handleAnalyze = async () => {
    if (!url.trim()) return;
    setLoading(true);
    setError("");
    try {
      const result = await analyzePost(url, niche);
      navigate(`/analysis/${result.analysis_id}`, { state: result });
    } catch (e: any) {
      setError(e.response?.data?.detail || "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  const scoreColor = (s: number) =>
    s >= 75 ? "#c8f566" : s >= 50 ? "#f5a623" : "#ff5c5c";

  return (
    <div style={{ maxWidth: 720, margin: "0 auto", padding: "60px 24px" }}>
      <div style={{ marginBottom: 48 }}>
        <p style={{ fontFamily: "'DM Mono', monospace", fontSize: 11, color: "var(--accent)", letterSpacing: 2, textTransform: "uppercase", marginBottom: 12 }}>
          Post-mortem analyzer
        </p>
        <h1 style={{ fontFamily: "'Instrument Serif', serif", fontSize: 48, fontWeight: 400, lineHeight: 1.1, marginBottom: 16 }}>
          Why did that post<br /><em>really</em> perform?
        </h1>
        <p style={{ color: "var(--muted)", fontSize: 15, maxWidth: 480 }}>
          Paste any Instagram or TikTok URL. We analyze the post against account history and platform benchmarks — then score it across 5 dimensions.
        </p>
      </div>

      <div style={{ background: "var(--surface)", border: "1px solid var(--border)", borderRadius: "var(--radius)", padding: 24, marginBottom: 48 }}>
        <div style={{ display: "flex", gap: 10, marginBottom: 12 }}>
          <input
            type="text"
            placeholder="https://www.instagram.com/p/... or https://www.tiktok.com/@..."
            value={url}
            onChange={e => setUrl(e.target.value)}
            onKeyDown={e => e.key === "Enter" && handleAnalyze()}
            style={{
              flex: 1,
              background: "var(--surface2)",
              border: "1px solid var(--border)",
              color: "var(--text)",
              padding: "10px 14px",
              borderRadius: "var(--radius)",
              fontSize: 14,
              fontFamily: "inherit",
              outline: "none",
            }}
          />
          <NicheSelect value={niche} onChange={setNiche} />
        </div>

        <button
          onClick={handleAnalyze}
          disabled={loading}
          style={{
            width: "100%",
            padding: "12px",
            background: loading ? "var(--border)" : "var(--accent)",
            color: loading ? "var(--muted)" : "#0e0e0e",
            border: "none",
            borderRadius: "var(--radius)",
            fontSize: 14,
            fontWeight: 500,
            transition: "opacity 0.2s",
          }}
        >
          {loading ? "Analyzing — this takes ~60s..." : "Analyze post"}
        </button>

        {error && (
          <p style={{ color: "var(--danger)", fontSize: 13, marginTop: 10 }}>{error}</p>
        )}
      </div>

      {analyses.length > 0 && (
        <div>
          <p style={{ fontSize: 12, color: "var(--muted)", textTransform: "uppercase", letterSpacing: 1.5, fontFamily: "'DM Mono', monospace", marginBottom: 16 }}>
            Recent analyses
          </p>
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            {analyses.map(a => (
              <div
                key={a.analysis_id}
                onClick={() => navigate(`/analysis/${a.analysis_id}`)}
                style={{
                  background: "var(--surface)",
                  border: "1px solid var(--border)",
                  borderRadius: "var(--radius)",
                  padding: "16px 20px",
                  cursor: "pointer",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  transition: "border-color 0.2s",
                }}
                onMouseEnter={e => (e.currentTarget.style.borderColor = "var(--accent)")}
                onMouseLeave={e => (e.currentTarget.style.borderColor = "var(--border)")}
              >
                <div>
                  <p style={{ fontSize: 13, fontWeight: 500, marginBottom: 2 }}>@{a.handle}</p>
                  <p style={{ fontSize: 12, color: "var(--muted)", maxWidth: 400, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                    {a.caption}
                  </p>
                </div>
                <div style={{ textAlign: "right", flexShrink: 0, marginLeft: 16 }}>
                  <p style={{ fontFamily: "'DM Mono', monospace", fontSize: 20, fontWeight: 500, color: scoreColor(a.overall_score) }}>
                    {Math.round(a.overall_score)}
                  </p>
                  <p style={{ fontSize: 11, color: "var(--muted)" }}>overall</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}