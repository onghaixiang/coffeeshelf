"""Request/response schemas (separate from the DB table)."""
from datetime import date, datetime

from pydantic import BaseModel


class BeanCreate(BaseModel):
    name: str
    roaster: str
    origin_country: str | None = None
    process: str | None = None
    farm: str | None = None
    roast_date: date | None = None
    weight_left_g: float = 0.0
    reorder_threshold_g: float = 50.0
    price: float | None = None
    category: str | None = None
    rating: int | None = None
    notes: str | None = None


class BeanUpdate(BaseModel):
    """All fields optional -> partial (PATCH) update."""
    name: str | None = None
    roaster: str | None = None
    origin_country: str | None = None
    process: str | None = None
    farm: str | None = None
    roast_date: date | None = None
    weight_left_g: float | None = None
    reorder_threshold_g: float | None = None
    price: float | None = None
    category: str | None = None
    rating: int | None = None
    notes: str | None = None


class BeanRead(BaseModel):
    id: int
    name: str
    roaster: str
    origin_country: str | None
    process: str | None
    farm: str | None
    roast_date: date | None
    weight_left_g: float
    reorder_threshold_g: float
    price: float | None
    category: str | None
    rating: int | None
    notes: str | None
    created_at: datetime
    # derived
    days_since_roast: int | None
    low_stock: bool


# ---- suggestions ----

class SuggestRequest(BaseModel):
    request: str
    use_inventory: bool = True


class Suggestion(BaseModel):
    roaster: str
    coffee_name: str
    origin: str | None = None
    process: str | None = None
    notes: str | None = None
    url: str | None = None
    why_it_matches: str | None = None
    price: str | None = None


class Citation(BaseModel):
    title: str | None = None
    url: str | None = None


class SuggestResponse(BaseModel):
    summary: str
    suggestions: list[Suggestion]
    citations: list[Citation]
