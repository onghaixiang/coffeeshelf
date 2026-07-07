"""Live purchase-search: what are Singapore roasters selling right now?

Keyless implementation: every Shopify storefront publicly exposes
`/products.json` — real, live product data with no API key. We fetch the
catalogues of a fixed list of Singapore specialty roasters server-side,
filter to actual coffee beans that are in stock, and rank them against the
user's request with plain keyword matching. Nothing here can leak a secret
because there is no secret.
"""
import asyncio
import html
import re
import time

import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from .db import get_session
from .models import CoffeeBean
from .schemas import Citation, SuggestRequest, SuggestResponse, Suggestion

router = APIRouter(prefix="/api/suggestions", tags=["suggestions"])

# Singapore specialty roasters with public Shopify storefront JSON
# (verified: https://<domain>/products.json returns live catalogue data).
ROASTERS = [
    ("Nylon Coffee Roasters", "nylon.coffee"),
    ("Apartment Coffee", "apartmentcoffee.co"),
    ("Tiong Hoe Specialty Coffee", "tionghoe.com"),
    ("Alchemist", "alchemist.com.sg"),
    ("PPP Coffee", "pppcoffee.com"),
    ("Parchmen & Co", "parchmen.co"),
    ("Homeground Coffee Roasters", "homegroundcoffeeroasters.com"),
    ("Common Man Coffee Roasters", "commonmancoffeeroasters.com"),
    ("Dutch Colony Coffee Co", "dutchcolony.sg"),
    ("Bettr Coffee", "bettr.coffee"),
]

CACHE_TTL_SECONDS = 600
FETCH_TIMEOUT_SECONDS = 12
MAX_SUGGESTIONS = 6

# ---- product classification vocab ------------------------------------------

# Anything matching these is gear/merch/consumables that aren't whole beans.
EXCLUDE_TERMS = [
    "grinder", "dripper", "kettle", "server", "scale", "mug", "cup", "glass",
    "carafe", "tumbler", "bottle", "flask", "brewer", "machine", "moka",
    "aeropress", "chemex", "v60 ", "filter paper", "papers", "capsule", "pod",
    "drip bag", "dripbag", "drip coffee bag", "cold brew", "concentrate",
    "ready to drink", "tea", "matcha", "chocolate bar", "cocoa powder",
    "syrup", "granola", "gift card", "giftcard", "voucher", "e-gift",
    "workshop", "class", "course", "masterclass", "subscription", "bundle",
    "tote", "t-shirt", "tee ", "shirt", "cap ", "beanie", "candle", "sticker",
    "book", "apron", "cleaner", "cleaning", "descaler", "detergent", "brush",
    "sampler pack", "merch", "milk", "cascara", "starter kit", "tamper",
    "pitcher", "jug", "spoon", "canister", "training", "wholesale",
    "drinking chocolate", "hot chocolate", "chisel", "wdt",
    "distribution tool", "leveler",
]

EXCLUDE_TYPES = {
    "equipment", "merchandise", "merch", "accessories", "accessory",
    "brewing gear", "gear", "hardware", "drinkware", "apparel", "gift card",
    "workshop", "class", "subscription", "tea", "drip bags", "drip bag",
    "capsules", "ready-to-drink",
}

COUNTRIES = [
    "ethiopia", "kenya", "colombia", "brazil", "guatemala", "honduras",
    "el salvador", "costa rica", "panama", "peru", "bolivia", "ecuador",
    "mexico", "nicaragua", "rwanda", "burundi", "uganda", "tanzania",
    "indonesia", "sumatra", "java", "sulawesi", "india", "yemen",
    "papua new guinea", "china", "yunnan", "thailand", "vietnam", "myanmar",
    "timor", "malawi", "congo", "geisha", "gesha",
]

PROCESSES = [
    "washed", "natural", "honey", "anaerobic", "carbonic maceration",
    "thermal shock", "co-ferment", "coferment", "wet hulled", "wet-hulled",
    "experimental", "yeast",
]

# Signals that a product is actually coffee beans.
COFFEE_TERMS = [
    "coffee", "beans", "espresso", "filter roast", "single origin",
    "omni", "blend", "roast", "decaf",
] + COUNTRIES + PROCESSES

# Small synonym net so "fruity" finds "berry" tasting notes etc.
SYNONYMS = {
    "fruity": ["berry", "berries", "blueberry", "strawberry", "raspberry",
               "cherry", "stonefruit", "stone fruit", "peach", "apricot",
               "tropical", "mango", "pineapple", "juicy", "jammy", "grape",
               "plum", "citrus", "fruit"],
    "chocolatey": ["chocolate", "cocoa", "cacao", "choc", "nutella", "fudge"],
    "chocolate": ["cocoa", "cacao", "choc", "fudge"],
    "nutty": ["almond", "hazelnut", "peanut", "walnut", "nut"],
    "floral": ["jasmine", "florals", "rose", "lavender", "bergamot", "osmanthus"],
    "sweet": ["caramel", "honey", "toffee", "brown sugar", "molasses", "candy"],
    "citrus": ["lemon", "lime", "orange", "grapefruit", "yuzu", "mandarin"],
    "juicy": ["fruity", "berry", "tropical"],
    "funky": ["anaerobic", "fermented", "boozy", "winey", "co-ferment"],
    "bright": ["acidity", "citrus", "sparkling", "vibrant"],
    "clean": ["washed", "crisp", "delicate"],
    "light": ["light roast", "filter", "nordic"],
    "dark": ["dark roast", "bold", "intense"],
    "ethiopian": ["ethiopia"],
    "kenyan": ["kenya"],
    "colombian": ["colombia"],
    "brazilian": ["brazil"],
    "indonesian": ["indonesia", "sumatra", "java", "sulawesi"],
    "espresso": ["blend"],
    "decaf": ["decaffeinated", "sugarcane", "swiss water", "ea decaf"],
}

STOPWORDS = {
    "a", "an", "the", "and", "or", "of", "for", "with", "under", "over",
    "below", "above", "less", "than", "max", "up", "to", "in", "on", "at",
    "i", "im", "me", "my", "want", "like", "looking", "something", "some",
    "beans", "bean", "coffee", "coffees", "roast", "roasts", "please",
    "would", "prefer", "preferably", "ideally", "around", "about", "budget",
    "sgd", "dollars", "bucks",
}

# ---- live catalogue fetching (cached) ---------------------------------------

_cache: dict[str, tuple[float, list[dict]]] = {}
_cache_lock = asyncio.Lock()


async def _fetch_store(client: httpx.AsyncClient, name: str, domain: str) -> list[dict]:
    url = f"https://{domain}/products.json?limit=250"
    resp = await client.get(url)
    resp.raise_for_status()
    products = resp.json().get("products", [])
    for p in products:
        p["_roaster"] = name
        p["_domain"] = domain
    return products


async def _all_products() -> list[dict]:
    async with _cache_lock:
        cached = _cache.get("products")
        if cached and time.monotonic() - cached[0] < CACHE_TTL_SECONDS:
            return cached[1]

        async with httpx.AsyncClient(
            timeout=FETCH_TIMEOUT_SECONDS,
            follow_redirects=True,
            headers={"User-Agent": "daily-grind-zine/1.0 (personal inventory app)"},
        ) as client:
            results = await asyncio.gather(
                *(_fetch_store(client, n, d) for n, d in ROASTERS),
                return_exceptions=True,
            )

        products: list[dict] = []
        ok = 0
        for res in results:
            if isinstance(res, Exception):
                continue  # one store being down shouldn't kill the search
            ok += 1
            products.extend(res)

        if ok == 0:
            raise HTTPException(
                502, "Couldn't reach any roaster storefronts — check your connection and retry."
            )
        _cache["products"] = (time.monotonic(), products)
        return products


# ---- classification & scoring -----------------------------------------------

_TAG_RE = re.compile(r"<[^>]+>")


def _searchable_text(p: dict) -> str:
    body = html.unescape(_TAG_RE.sub(" ", p.get("body_html") or ""))
    tags = p.get("tags") or []
    if isinstance(tags, str):
        tags = [tags]
    return " ".join(
        [p.get("title") or "", p.get("product_type") or "", " ".join(tags), body]
    ).lower()


def _is_coffee_beans(p: dict) -> bool:
    title = (p.get("title") or "").lower()
    ptype = (p.get("product_type") or "").strip().lower()
    text = _searchable_text(p)
    if ptype in EXCLUDE_TYPES:
        return False
    haystack = f"{title} {ptype}"
    if any(term in haystack for term in EXCLUDE_TERMS):
        return False
    return any(term in text for term in COFFEE_TERMS)


def _in_stock_price(p: dict) -> float | None:
    """Lowest price among available variants, or None if sold out."""
    prices = []
    for v in p.get("variants") or []:
        if v.get("available"):
            try:
                prices.append(float(v.get("price")))
            except (TypeError, ValueError):
                continue
    return min(prices) if prices else None


def _extract_budget(request: str) -> float | None:
    m = re.search(
        r"(?:under|below|less than|max|up to|within|<=?)\s*s?\$?\s*(\d+(?:\.\d+)?)",
        request, re.IGNORECASE,
    )
    if not m:
        m = re.search(r"s?\$\s*(\d+(?:\.\d+)?)\s*(?:budget|max)?", request, re.IGNORECASE)
    return float(m.group(1)) if m else None


def _request_terms(request: str) -> list[str]:
    words = re.findall(r"[a-z]+", request.lower())
    terms = []
    for w in words:
        if w in STOPWORDS or len(w) < 3:
            continue
        terms.append(w)
    # multi-word phrases we care about
    low = request.lower()
    for phrase in ("light roast", "dark roast", "medium roast", "single origin",
                   "stone fruit", "brown sugar", "swiss water", "el salvador",
                   "costa rica", "papua new guinea"):
        if phrase in low:
            terms.append(phrase)
    return list(dict.fromkeys(terms))


def _score(p: dict, terms: list[str]) -> tuple[float, list[str]]:
    title = (p.get("title") or "").lower()
    text = _searchable_text(p)
    score = 0.0
    matched: list[str] = []
    for term in terms:
        variants = [term] + SYNONYMS.get(term, [])
        if term.endswith("s"):  # "naturals" should still find "natural"
            singular = term[:-1]
            variants += [singular] + SYNONYMS.get(singular, [])
        heavy = (term in COUNTRIES or term in PROCESSES
                 or term.rstrip("s") in COUNTRIES or term.rstrip("s") in PROCESSES)
        hit = None
        for v in variants:
            if v in title:
                score += 3 if heavy else 2
                hit = v
                break
            if v in text:
                score += 2 if heavy else 1
                hit = v
                break
        if hit:
            matched.append(term if hit == term else f"{term} ({hit})")
    return score, matched


def _find_origin(text: str) -> str | None:
    for c in COUNTRIES:
        if c in ("geisha", "gesha"):
            continue
        if c in text:
            return c.title()
    return None


def _find_process(title: str, text: str) -> str | None:
    # The title is authoritative ("..., Natural, Kenya"); body copy often
    # mentions other processes in passing.
    for haystack in (title, text):
        for proc in PROCESSES:
            if proc in haystack:
                return proc.title()
    return None


def _tasting_notes(p: dict) -> str | None:
    """Best-effort tasting notes: a 'Tasting notes: ...' line in the body, else tags."""
    body = html.unescape(_TAG_RE.sub(" ", p.get("body_html") or ""))
    m = re.search(r"tasting notes?\s*:?\s*([^.\n]{3,120})", body, re.IGNORECASE)
    if m:
        return m.group(1).strip(" -–:;,")
    tags = p.get("tags") or []
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(",")]
    flavourish = [t for t in tags if t and len(t) < 30 and not t.lower().startswith(("sg", "new", "sale"))]
    return ", ".join(flavourish[:6]) or None


def _owned_keys(session: Session) -> set[str]:
    beans = session.exec(select(CoffeeBean)).all()
    return {b.name.strip().lower() for b in beans if b.name}


# ---- route -------------------------------------------------------------------

@router.post("", response_model=SuggestResponse)
async def suggest(payload: SuggestRequest, session: Session = Depends(get_session)):
    products = await _all_products()

    beans = [p for p in products if _is_coffee_beans(p)]
    budget = _extract_budget(payload.request)
    terms = _request_terms(payload.request)
    owned = _owned_keys(session) if payload.use_inventory else set()

    candidates = []
    for p in beans:
        price = _in_stock_price(p)
        if price is None:
            continue  # sold out
        if budget is not None and price > budget:
            continue
        title = (p.get("title") or "").strip()
        if title.lower() in owned or any(o and o in title.lower() for o in owned):
            continue  # already on the shelf
        score, matched = _score(p, terms)
        candidates.append((score, matched, price, p))

    # Require at least a title hit or a strong (origin/process) match — a single
    # incidental word in the body copy isn't a real match.
    scored = [c for c in candidates if c[0] >= 2]
    if scored:
        # Best score first; among equals, newest listing first. Cap picks per
        # roaster so one shop's catalogue doesn't crowd out the rest.
        scored.sort(key=lambda c: c[3].get("published_at") or "", reverse=True)
        scored.sort(key=lambda c: c[0], reverse=True)
        picked, per_roaster = [], {}
        for c in scored:
            roaster = c[3]["_roaster"]
            if per_roaster.get(roaster, 0) >= 2:
                continue
            per_roaster[roaster] = per_roaster.get(roaster, 0) + 1
            picked.append(c)
            if len(picked) >= MAX_SUGGESTIONS:
                break
        summary = (
            f"Found {len(scored)} in-stock matches across {len(ROASTERS)} Singapore "
            f"roasters (live storefront data); showing the top {len(picked)}."
        )
    else:
        # No keyword hits — fall back to the freshest arrivals so the user
        # still gets something real to look at.
        candidates.sort(key=lambda c: c[3].get("published_at") or "", reverse=True)
        picked = candidates[:MAX_SUGGESTIONS]
        summary = (
            "Nothing matched those exact words, so here are the newest in-stock "
            "beans from Singapore roasters instead — try broader terms like "
            "'fruity', 'washed', or an origin country."
        )

    suggestions = []
    used_domains: dict[str, str] = {}
    for score, matched, price, p in picked:
        text = _searchable_text(p)
        title_lower = (p.get("title") or "").lower()
        why = None
        if matched:
            why = "Matches: " + ", ".join(matched) + f" · in stock at S${price:.2f}"
        elif price is not None:
            why = f"Newly listed · in stock at S${price:.2f}"
        suggestions.append(Suggestion(
            roaster=p["_roaster"],
            coffee_name=p.get("title") or "(untitled)",
            origin=_find_origin(text),
            process=_find_process(title_lower, text),
            notes=_tasting_notes(p),
            url=f"https://{p['_domain']}/products/{p.get('handle')}",
            why_it_matches=why,
            price=f"S${price:.2f}",
        ))
        used_domains[p["_roaster"]] = p["_domain"]

    citations = [
        Citation(title=f"{name} — live catalogue", url=f"https://{domain}/collections/all")
        for name, domain in used_domains.items()
    ]

    if not suggestions:
        summary = "No in-stock beans found within those constraints — try relaxing the budget."

    return SuggestResponse(summary=summary, suggestions=suggestions, citations=citations)
