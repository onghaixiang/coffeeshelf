// Read-only or interactive 1-5 star rating (the zine's recurring motif).
export default function Stars({ value, onChange, size = "" }) {
  const v = value || 0;
  const interactive = typeof onChange === "function";
  return (
    <span className={`stars ${interactive ? "input" : ""} ${size}`.trim()} aria-label={`${v} of 5`}>
      {[1, 2, 3, 4, 5].map((n) => (
        <span
          key={n}
          className={`star ${n <= v ? "on" : "off"}`}
          role={interactive ? "button" : undefined}
          onClick={interactive ? (e) => { e.stopPropagation(); onChange(n === v ? null : n); } : undefined}
          title={interactive ? `${n} star${n > 1 ? "s" : ""}` : undefined}
        >
          {n <= v ? "★" : "☆"}
        </span>
      ))}
    </span>
  );
}
