import { useState } from "react";
import { getSuggestions } from "../api.js";

export default function Suggester({ onClose }) {
  const [request, setRequest] = useState("");
  const [useInventory, setUseInventory] = useState(true);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [err, setErr] = useState(null);

  const search = async () => {
    if (!request.trim()) return;
    setLoading(true);
    setErr(null);
    setResult(null);
    try {
      const data = await getSuggestions(request.trim(), useInventory);
      setResult(data);
    } catch (ex) {
      setErr(ex.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="overlay" onClick={onClose}>
      <div className="modal wide" onClick={(e) => e.stopPropagation()}>
        <div className="modal-head">
          <div>
            <h2>💸 Time to lose money on beans</h2>
            <div className="byline">What are Singapore roasters selling right now?</div>
          </div>
          <button className="ghost" onClick={onClose}>✕</button>
        </div>

        <div className="field">
          <label>What are you in the mood for?</label>
          <textarea
            value={request}
            onChange={(e) => setRequest(e.target.value)}
            placeholder="e.g. light-roast fruity naturals, Ethiopian or Kenyan, under $30"
            autoFocus
          />
        </div>
        <label style={{ fontFamily: "var(--body)", fontSize: 13, display: "flex", gap: 8, alignItems: "center" }}>
          <input
            type="checkbox"
            checked={useInventory}
            onChange={(e) => setUseInventory(e.target.checked)}
          />
          Consider what's already on my shelf (suggest things to complement it)
        </label>

        <div className="form-actions">
          <button className="accent" onClick={search} disabled={loading || !request.trim()}>
            {loading ? "Searching the web…" : "💸 Find beans"}
          </button>
        </div>

        {loading && (
          <p className="spinner">Checking live roaster shelves…</p>
        )}
        {err && <div className="error-msg">{err}</div>}

        {result && (
          <div>
            {result.summary && <p className="why" style={{ fontSize: 16 }}>{result.summary}</p>}
            {result.suggestions.length === 0 && !result.summary && (
              <p className="empty" style={{ padding: 30 }}>No suggestions came back — try rephrasing.</p>
            )}
            {result.suggestions.map((s, i) => (
              <div className="suggestion" key={i}>
                <h3>{s.coffee_name}</h3>
                <div className="s-byline">
                  {s.roaster}
                  {s.origin ? ` · ${s.origin}` : ""}
                  {s.process ? ` · ${s.process}` : ""}
                  {s.price ? ` · ${s.price}` : ""}
                </div>
                {s.notes && <div style={{ fontSize: 14 }}>{s.notes}</div>}
                {s.why_it_matches && <p className="why">{s.why_it_matches}</p>}
                {s.url && (
                  <a href={s.url} target="_blank" rel="noreferrer">
                    view at {s.roaster} →
                  </a>
                )}
              </div>
            ))}

            {result.citations?.length > 0 && (
              <div className="citations">
                <div className="k">Sources</div>
                <ul>
                  {result.citations.map((c, i) => (
                    <li key={i}>
                      {c.url ? (
                        <a href={c.url} target="_blank" rel="noreferrer">{c.title || c.url}</a>
                      ) : (
                        c.title
                      )}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
