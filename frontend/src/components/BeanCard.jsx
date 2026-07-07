import Stars from "./Stars.jsx";

function freshness(days) {
  if (days === null || days === undefined) return null;
  const cls = days <= 21 ? "fresh" : days <= 45 ? "" : "stale";
  return <span className={`freshness ${cls}`}>{days}d since roast</span>;
}

export default function BeanCard({ bean, onOpen }) {
  const metaBits = [
    bean.origin_country,
    bean.process,
    bean.roast_date,
    `${bean.weight_left_g}g`,
  ].filter(Boolean);

  return (
    <article
      className={`bean ${bean.low_stock ? "low" : ""}`}
      onClick={() => onOpen(bean)}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => { if (e.key === "Enter") onOpen(bean); }}
    >
      <h2 className="bean-name">{bean.name}</h2>
      <div className="byline">{bean.roaster}</div>
      <div className="meta">
        {metaBits.map((b, i) => (
          <span key={i}>
            {i > 0 && <span className="dot">· </span>}
            {b}
          </span>
        ))}
      </div>
      {bean.notes && <p className="bean-notes">“{bean.notes}”</p>}
      <div className="bean-row">
        <Stars value={bean.rating} />
        <span style={{ display: "flex", gap: 10, alignItems: "center" }}>
          {bean.low_stock && <span className="badge-low">Low</span>}
          {freshness(bean.days_since_roast)}
        </span>
      </div>
    </article>
  );
}
