"""SQLModel table definitions."""
from datetime import date, datetime

from sqlmodel import Field, SQLModel


class CoffeeBean(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    roaster: str
    origin_country: str | None = None
    process: str | None = None          # washed / natural / honey / anaerobic ...
    farm: str | None = None
    roast_date: date | None = None
    weight_left_g: float = 0.0          # grams remaining
    reorder_threshold_g: float = 50.0   # low-stock trigger
    price: float | None = None
    category: str | None = None
    rating: int | None = None           # 1-5 stars; None = unrated
    notes: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
