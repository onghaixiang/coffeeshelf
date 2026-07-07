import { useEffect, useMemo, useState } from "react";
import { createBean, deleteBean, listBeans, updateBean } from "./api.js";
import Filters from "./components/Filters.jsx";
import Zine from "./components/Zine.jsx";
import BeanDetail from "./components/BeanDetail.jsx";
import BeanForm from "./components/BeanForm.jsx";
import Suggester from "./components/Suggester.jsx";

const DEFAULT_PARAMS = { q: "", process: "", origin_country: "", category: "", sort: "roast_date", order: "asc" };

export default function App() {
  const [params, setParams] = useState(DEFAULT_PARAMS);
  const [beans, setBeans] = useState([]);
  const [allBeans, setAllBeans] = useState([]); // for filter option lists
  const [loadErr, setLoadErr] = useState(null);

  const [detail, setDetail] = useState(null);   // bean being viewed
  const [formBean, setFormBean] = useState(undefined); // undefined=closed, null=new, obj=edit
  const [suggestOpen, setSuggestOpen] = useState(false);

  const load = async (p = params) => {
    try {
      const [filtered, all] = await Promise.all([listBeans(p), listBeans({})]);
      setBeans(filtered);
      setAllBeans(all);
      setLoadErr(null);
    } catch (ex) {
      setLoadErr(ex.message);
    }
  };

  // Debounce param changes (search box) into the fetch.
  useEffect(() => {
    const t = setTimeout(() => load(params), 200);
    return () => clearTimeout(t);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [params]);

  const options = useMemo(() => {
    const uniq = (key) =>
      [...new Set(allBeans.map((b) => b[key]).filter(Boolean))].sort();
    return {
      process: uniq("process"),
      origin_country: uniq("origin_country"),
      category: uniq("category"),
    };
  }, [allBeans]);

  // keep the open detail view in sync with fresh data
  const syncDetail = (list) => {
    if (detail) {
      const fresh = list.find((b) => b.id === detail.id);
      setDetail(fresh || null);
    }
  };

  const afterMutation = async () => {
    const [filtered, all] = await Promise.all([listBeans(params), listBeans({})]);
    setBeans(filtered);
    setAllBeans(all);
    syncDetail(all);
  };

  const handlePatch = async (id, data) => {
    await updateBean(id, data);
    await afterMutation();
  };
  const handleDelete = async (id) => {
    await deleteBean(id);
    setDetail(null);
    await afterMutation();
  };
  const handleSaveForm = async (data) => {
    if (formBean && formBean.id) await updateBean(formBean.id, data);
    else await createBean(data);
    setFormBean(undefined);
    await afterMutation();
  };

  return (
    <>
      <header className="masthead">
        <div>
          <h1>The Daily Grind</h1>
          <div className="dek">a coffee bean zine · singapore edition</div>
        </div>
        <div className="masthead-right">
          <button onClick={() => setFormBean(null)}>+ Add bean</button>
          <button
            className="accent money-btn"
            onClick={() => setSuggestOpen(true)}
            title="Find beans to buy from Singapore roasters"
          >
            💸<span className="label">buy more</span>
          </button>
        </div>
      </header>

      <Filters params={params} setParams={setParams} options={options} />

      {loadErr && (
        <div className="toolbar">
          <div className="error-msg">Could not reach the backend: {loadErr}</div>
        </div>
      )}

      <Zine beans={beans} onOpen={setDetail} />

      {detail && (
        <BeanDetail
          bean={detail}
          onPatch={handlePatch}
          onDelete={handleDelete}
          onEdit={(b) => { setDetail(null); setFormBean(b); }}
          onClose={() => setDetail(null)}
        />
      )}

      {formBean !== undefined && (
        <BeanForm
          initial={formBean}
          onSave={handleSaveForm}
          onClose={() => setFormBean(undefined)}
        />
      )}

      {suggestOpen && <Suggester onClose={() => setSuggestOpen(false)} />}
    </>
  );
}
