interface Props {
  label: string;
  score: number;
  avg?: number;
}

const color = (s: number) =>
  s >= 75 ? "#c8f566" : s >= 50 ? "#f5a623" : "#ff5c5c";

export default function ScoreBar({ label, score, avg }: Props) {
  return (
    <div style={{ marginBottom: 14 }}>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 6 }}>
        <span style={{ fontSize: 13, color: "var(--muted)", textTransform: "capitalize" }}>{label}</span>
        <span style={{ fontSize: 13, fontFamily: "'DM Mono', monospace", color: color(score) }}>{score}</span>
      </div>
      <div style={{ height: 4, background: "var(--border)", borderRadius: 99, position: "relative" }}>
        <div style={{
          height: "100%",
          width: `${score}%`,
          background: color(score),
          borderRadius: 99,
          transition: "width 0.8s cubic-bezier(0.16,1,0.3,1)"
        }} />
        {avg !== undefined && (
          <div style={{
            position: "absolute",
            top: -3,
            left: `${avg}%`,
            width: 2,
            height: 10,
            background: "var(--muted)",
            borderRadius: 1,
          }} />
        )}
      </div>
    </div>
  );
}