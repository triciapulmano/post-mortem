const NICHES = [
    "lifestyle", "fashion", "fitness", "food", "travel",
    "beauty", "tech", "gaming", "finance", "sports",
    "entertainment", "music", "comedy", "education", "wellness",
    "parenting", "pets", "sustainability", "real_estate", "automotive",
    "photography", "art", "dance", "film", "books",
    "coffee", "streetwear", "luxury", "wedding", "architecture",
    "outdoors", "skincare", "haircare", "mensfashion", "plus_size_fashion",
    "vegan", "yoga", "running", "esports", "kpop",
];

interface Props {
  value: string;
  onChange: (v: string) => void;
}

export default function NicheSelect({ value, onChange }: Props) {
  return (
    <select
      value={value}
      onChange={e => onChange(e.target.value)}
      style={{
        background: "var(--surface2)",
        border: "1px solid var(--border)",
        color: "var(--text)",
        padding: "10px 14px",
        borderRadius: "var(--radius)",
        fontSize: 14,
        fontFamily: "inherit",
        outline: "none",
        cursor: "pointer",
      }}
    >
      {NICHES.map(n => (
        <option key={n} value={n}>{n}</option>
      ))}
    </select>
  );
}