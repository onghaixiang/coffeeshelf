import { useEffect, useRef, useState } from "react";
import BeanCard from "./BeanCard.jsx";

const PER_PAGE = 4; // several beans per spread — never one-per-page

export default function Zine({ beans, onOpen }) {
  const [page, setPage] = useState(0);
  const [dir, setDir] = useState("fwd");
  const pageCount = Math.max(1, Math.ceil(beans.length / PER_PAGE));

  // Clamp when the filtered list shrinks.
  useEffect(() => {
    if (page > pageCount - 1) setPage(pageCount - 1);
  }, [pageCount, page]);

  const flip = (delta) => {
    setPage((p) => {
      const next = Math.min(pageCount - 1, Math.max(0, p + delta));
      if (next !== p) setDir(delta > 0 ? "fwd" : "back");
      return next;
    });
  };

  // Arrow-key parity with the border click zones.
  const ref = useRef(null);
  useEffect(() => {
    const onKey = (e) => {
      if (e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA") return;
      if (e.key === "ArrowRight") flip(1);
      if (e.key === "ArrowLeft") flip(-1);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [pageCount]);

  const start = page * PER_PAGE;
  const slice = beans.slice(start, start + PER_PAGE);

  return (
    <div className="zine" ref={ref}>
      <div className="page-wrap">
        <button
          className="flip-zone left"
          onClick={() => flip(-1)}
          disabled={page === 0}
          aria-label="Previous page"
          title="Previous page"
        >
          ‹
        </button>
        <button
          className="flip-zone right"
          onClick={() => flip(1)}
          disabled={page >= pageCount - 1}
          aria-label="Next page"
          title="Next page"
        >
          ›
        </button>

        {beans.length === 0 ? (
          <div className="empty">
            No beans on the shelf yet — add one, or hit the 💸 to go shopping.
          </div>
        ) : (
          <div className={`page ${dir === "back" ? "back" : ""}`} key={page}>
            <div className="spread">
              {slice.map((b) => (
                <BeanCard key={b.id} bean={b} onOpen={onOpen} />
              ))}
            </div>
          </div>
        )}
      </div>

      <div className="page-footer">
        <button className="ghost" onClick={() => flip(-1)} disabled={page === 0}>
          ‹ prev
        </button>
        <span>
          page {page + 1} / {pageCount} — {beans.length} bean{beans.length === 1 ? "" : "s"}
        </span>
        <button className="ghost" onClick={() => flip(1)} disabled={page >= pageCount - 1}>
          next ›
        </button>
      </div>
    </div>
  );
}
