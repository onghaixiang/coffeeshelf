import { useState } from "react";

const BLANK = {
  name: "",
  roaster: "",
  origin_country: "",
  process: "",
  farm: "",
  roast_date: "",
  weight_left_g: 250,
  reorder_threshold_g: 50,
  price: "",
  category: "",
  notes: "",
};

// Convert form strings into the JSON the API expects (numbers, nulls).
function clean(form) {
  const out = { ...form };
  ["origin_country", "process", "farm", "category", "notes"].forEach((k) => {
    if (out[k] === "") out[k] = null;
  });
  out.roast_date = out.roast_date || null;
  out.price = out.price === "" || out.price === null ? null : Number(out.price);
  out.weight_left_g = Number(out.weight_left_g) || 0;
  out.reorder_threshold_g = Number(out.reorder_threshold_g) || 0;
  return out;
}

export default function BeanForm({ initial, onSave, onClose }) {
  const editing = Boolean(initial?.id);
  const [form, setForm] = useState(() => ({ ...BLANK, ...(initial || {}) ,
    // date inputs need YYYY-MM-DD strings, not null
    roast_date: initial?.roast_date || "",
    price: initial?.price ?? "",
  }));
  const [err, setErr] = useState(null);
  const set = (k, v) => setForm((f) => ({ ...f, [k]: v }));

  const submit = async (e) => {
    e.preventDefault();
    if (!form.name.trim() || !form.roaster.trim()) {
      setErr("Name and roaster are required.");
      return;
    }
    try {
      await onSave(clean(form));
    } catch (ex) {
      setErr(ex.message);
    }
  };

  return (
    <div className="overlay" onClick={onClose}>
      <form className="modal" onClick={(e) => e.stopPropagation()} onSubmit={submit}>
        <div className="modal-head">
          <h2>{editing ? "Edit bean" : "New bean"}</h2>
          <button type="button" className="ghost" onClick={onClose}>✕</button>
        </div>

        <div className="grid-2">
          <div className="field"><label>Name *</label>
            <input value={form.name} onChange={(e) => set("name", e.target.value)} autoFocus /></div>
          <div className="field"><label>Roaster *</label>
            <input value={form.roaster} onChange={(e) => set("roaster", e.target.value)} /></div>
          <div className="field"><label>Origin country</label>
            <input value={form.origin_country ?? ""} onChange={(e) => set("origin_country", e.target.value)} /></div>
          <div className="field"><label>Process</label>
            <input value={form.process ?? ""} onChange={(e) => set("process", e.target.value)} placeholder="washed / natural / honey" /></div>
          <div className="field"><label>Farm / producer</label>
            <input value={form.farm ?? ""} onChange={(e) => set("farm", e.target.value)} /></div>
          <div className="field"><label>Category</label>
            <input value={form.category ?? ""} onChange={(e) => set("category", e.target.value)} placeholder="single origin / blend" /></div>
          <div className="field"><label>Roast date</label>
            <input type="date" value={form.roast_date} onChange={(e) => set("roast_date", e.target.value)} /></div>
          <div className="field"><label>Price (SGD)</label>
            <input type="number" step="0.01" value={form.price} onChange={(e) => set("price", e.target.value)} /></div>
          <div className="field"><label>Weight left (g)</label>
            <input type="number" step="1" value={form.weight_left_g} onChange={(e) => set("weight_left_g", e.target.value)} /></div>
          <div className="field"><label>Reorder threshold (g)</label>
            <input type="number" step="1" value={form.reorder_threshold_g} onChange={(e) => set("reorder_threshold_g", e.target.value)} /></div>
        </div>

        <div className="field"><label>Notes</label>
          <textarea value={form.notes ?? ""} onChange={(e) => set("notes", e.target.value)} /></div>

        {err && <div className="error-msg">{err}</div>}

        <div className="form-actions">
          <button type="button" className="ghost" onClick={onClose}>Cancel</button>
          <button type="submit" className="accent">{editing ? "Save" : "Add bean"}</button>
        </div>
      </form>
    </div>
  );
}
