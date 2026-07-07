import { useEffect, useState } from "react";
import Stars from "./Stars.jsx";

export default function BeanDetail({ bean, onPatch, onDelete, onEdit, onClose }) {
  const [rating, setRating] = useState(bean.rating);
  const [notes, setNotes] = useState(bean.notes || "");
  const [brew, setBrew] = useState("");
  const [saving, setSaving] = useState(false);
  const [err, setErr] = useState(null);

  useEffect(() => {
    setRating(bean.rating);
    setNotes(bean.notes || "");
  }, [bean.id]);

  const dirty = rating !== bean.rating || (notes || "") !== (bean.notes || "");

  const save = async () => {
    setSaving(true);
    setErr(null);
    try {
      await onPatch(bean.id, { rating, notes: notes || null });
    } catch (ex) {
      setErr(ex.message);
    } finally {
      setSaving(false);
    }
  };

  const logBrew = async () => {
    const g = Number(brew);
    if (!g || g <= 0) return;
    const left = Math.max(0, bean.weight_left_g - g);
    setErr(null);
    try {
      await onPatch(bean.id, { weight_left_g: left });
      setBrew("");
    } catch (ex) {
      setErr(ex.message);
    }
  };

  const meta = [
    bean.origin_country,
    bean.process,
    bean.farm,
    bean.category,
  ].filter(Boolean).join(" · ");

  return (
    <div className="overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-head">
          <div>
            <h2>{bean.name}</h2>
            <div className="byline">{bean.roaster}</div>
          </div>
          <button className="ghost" onClick={onClose}>✕</button>
        </div>

        <p className="detail-meta">
          {meta || "—"}
          <br />
          roast date: {bean.roast_date || "—"}
          {bean.days_since_roast != null && ` (${bean.days_since_roast}d ago)`}
          {" · "}
          {bean.weight_left_g}g left{" "}
          {bean.low_stock && <span className="badge-low">Low</span>}
          {bean.price != null && ` · $${bean.price}`}
        </p>

        <div className="detail-block">
          <div className="k">Your rating</div>
          <Stars value={rating} onChange={setRating} size="big" />
        </div>

        <div className="detail-block">
          <div className="k">Your notes</div>
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Tasting notes, brew recipe, what you'd change…"
            style={{ width: "100%", minHeight: 100 }}
            className="detail-notes"
          />
        </div>

        <div className="detail-block">
          <div className="k">Just brewed?</div>
          <div className="brew-row">
            <input
              type="number"
              value={brew}
              onChange={(e) => setBrew(e.target.value)}
              placeholder="grams"
            />
            <button className="ghost" onClick={logBrew}>− subtract from bag</button>
          </div>
        </div>

        {err && <div className="error-msg">{err}</div>}

        <div className="form-actions" style={{ justifyContent: "space-between" }}>
          <span style={{ display: "flex", gap: 10 }}>
            <button className="ghost" onClick={() => onEdit(bean)}>Edit details</button>
            <button
              className="ghost"
              onClick={() => { if (confirm(`Delete “${bean.name}”?`)) onDelete(bean.id); }}
              style={{ color: "var(--cherry-deep)" }}
            >
              Delete
            </button>
          </span>
          <button className="accent" onClick={save} disabled={!dirty || saving}>
            {saving ? "Saving…" : "Save rating + notes"}
          </button>
        </div>
      </div>
    </div>
  );
}
