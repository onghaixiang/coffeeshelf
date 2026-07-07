const SORTS = [
  ["roast_date", "roast date"],
  ["rating", "rating"],
  ["name", "name"],
  ["roaster", "roaster"],
  ["weight_left_g", "weight left"],
  ["process", "process"],
  ["origin_country", "origin"],
];

export default function Filters({ params, setParams, options }) {
  const set = (patch) => setParams((p) => ({ ...p, ...patch }));

  const Select = ({ field, label }) => (
    <>
      <label>{label}</label>
      <select value={params[field] || ""} onChange={(e) => set({ [field]: e.target.value })}>
        <option value="">all</option>
        {(options[field] || []).map((o) => (
          <option key={o} value={o}>{o}</option>
        ))}
      </select>
    </>
  );

  return (
    <div className="toolbar">
      <input
        type="text"
        placeholder="Search name, roaster, origin, notes…"
        value={params.q || ""}
        onChange={(e) => set({ q: e.target.value })}
      />
      <Select field="process" label="process" />
      <Select field="origin_country" label="origin" />
      <Select field="category" label="category" />
      <span className="spacer" />
      <label>sort</label>
      <select value={params.sort} onChange={(e) => set({ sort: e.target.value })}>
        {SORTS.map(([v, l]) => (
          <option key={v} value={v}>{l}</option>
        ))}
      </select>
      <button
        className="ghost"
        title="Toggle order"
        onClick={() => set({ order: params.order === "asc" ? "desc" : "asc" })}
      >
        {params.order === "asc" ? "↑ asc" : "↓ desc"}
      </button>
    </div>
  );
}
