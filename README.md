# The Daily Grind — a coffee bean zine ☕

A personal coffee-bean inventory you flip through like a zine. Track the beans you
own, rate them, filter/sort, get low-stock + freshness warnings, and hit the 💸
button to see what Singapore roasters are selling right now — live, keyless.

- **Backend:** FastAPI + SQLite (SQLModel). Data persists in `backend/beans.db`.
- **Frontend:** React + Vite, editorial/magazine design.
- **Live bean search:** public Shopify storefront JSON from real SG roasters —
  no API key, nothing to steal.

## Run it

**1. Backend** (terminal 1) — uses [uv](https://docs.astral.sh/uv/):

```bash
cd backend
uv sync                                    # creates .venv + installs from pyproject.toml/uv.lock
uv run uvicorn app.main:app --reload --port 8000
```

(No manual venv activation needed — `uv run` uses the project's `.venv` automatically.)

API docs at http://localhost:8000/docs

**2. Frontend** (terminal 2):

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

## The 💸 buy-more-beans feature

**No API key needed.** The backend fetches the public `/products.json`
catalogue that every Shopify storefront exposes, from ~10 Singapore specialty
roasters (Nylon, Apartment, Tiong Hoe, Alchemist, PPP, Parchmen, Homeground,
Common Man, Dutch Colony, Bettr). It filters to in-stock whole beans, ranks
them against your request (flavour words, process, origin, "under $30"
budgets), and links straight to the live product pages. Catalogues are cached
server-side for 10 minutes to be polite to the shops.

Because there's no key, there's nothing users of your app can abuse — the
only outbound calls are to public storefront pages anyone can open in a
browser.

## Data & persistence

All beans live in **`backend/beans.db`** (SQLite, on disk). It's created
automatically on first run and survives server restarts, reboots, and browser
sessions. Delete the file to start fresh. It is git-ignored so your data stays
local.

## Using it

- **+ Add bean** — record a bag (roaster, origin, process, roast date, weight…).
- **Click a bean** — opens the focus view to set a **1–5 star rating**, edit
  **notes**, and log a brew (`− subtract from bag`, which updates weight left).
- **Flip pages** — click the far-left / far-right margins of the zine (or use
  ← / → arrow keys). Each page shows several beans.
- **Filter / sort** — search box + process/origin/category filters + sort control.
- **Low stock** — bags at/under their reorder threshold get a red "Low" badge.
