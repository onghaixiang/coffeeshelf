"""Seed sample coffee beans.

Called on startup (see main.py). Only inserts when the table is empty, so it's
safe to run every boot: on Vercel's ephemeral /tmp SQLite this repopulates the
demo after each cold start, and on a persistent DB (DATABASE_URL) it seeds once
and then leaves your data alone.
"""
from datetime import date, timedelta

from sqlmodel import Session, select

from .db import engine
from .models import CoffeeBean


def _days_ago(n: int) -> date:
    return date.today() - timedelta(days=n)


def _sample_beans() -> list[CoffeeBean]:
    return [
        CoffeeBean(
            name="Kirinyaga AA",
            roaster="Sey Coffee",
            origin_country="Kenya",
            process="washed",
            farm="Kiambu Estate",
            roast_date=_days_ago(6),
            weight_left_g=220.0,
            reorder_threshold_g=50.0,
            price=22.0,
            category="single-origin",
            rating=5,
            notes="Blackcurrant, tomato, grapefruit. Juicy and bright.",
        ),
        CoffeeBean(
            name="Gedeb Halo Beriti",
            roaster="Onyx Coffee Lab",
            origin_country="Ethiopia",
            process="natural",
            farm="Halo Beriti washing station",
            roast_date=_days_ago(10),
            weight_left_g=90.0,
            reorder_threshold_g=100.0,
            price=24.5,
            category="single-origin",
            rating=5,
            notes="Blueberry, strawberry jam, floral finish.",
        ),
        CoffeeBean(
            name="Nariño Honey",
            roaster="La Cabra",
            origin_country="Colombia",
            process="honey",
            farm="El Diviso",
            roast_date=_days_ago(14),
            weight_left_g=150.0,
            reorder_threshold_g=50.0,
            price=19.0,
            category="single-origin",
            rating=4,
            notes="Red apple, panela, silky body.",
        ),
        CoffeeBean(
            name="Diablo Blend",
            roaster="Verve Coffee",
            origin_country=None,
            process=None,
            farm=None,
            roast_date=_days_ago(3),
            weight_left_g=340.0,
            reorder_threshold_g=100.0,
            price=17.0,
            category="blend",
            rating=4,
            notes="Dark chocolate, molasses, toasted almond. Espresso-friendly.",
        ),
        CoffeeBean(
            name="Geisha Anaerobic",
            roaster="Proud Mary",
            origin_country="Panama",
            process="anaerobic",
            farm="Hacienda La Esmeralda",
            roast_date=_days_ago(8),
            weight_left_g=45.0,
            reorder_threshold_g=50.0,
            price=48.0,
            category="single-origin",
            rating=5,
            notes="Jasmine, bergamot, tropical fruit. A splurge.",
        ),
        CoffeeBean(
            name="Antigua Bourbon",
            roaster="Intelligentsia",
            origin_country="Guatemala",
            process="washed",
            farm="Finca El Injerto",
            roast_date=_days_ago(21),
            weight_left_g=30.0,
            reorder_threshold_g=50.0,
            price=18.5,
            category="single-origin",
            rating=3,
            notes="Milk chocolate, orange, brown sugar. Getting past its prime.",
        ),
        CoffeeBean(
            name="Decaf Sugarcane",
            roaster="Counter Culture",
            origin_country="Colombia",
            process="washed",
            farm=None,
            roast_date=_days_ago(12),
            weight_left_g=200.0,
            reorder_threshold_g=50.0,
            price=16.0,
            category="decaf",
            rating=4,
            notes="EA sugarcane decaf. Caramel, cherry, clean.",
        ),
    ]


def seed_if_empty() -> int:
    """Insert sample beans if the table has none. Returns rows added."""
    with Session(engine) as session:
        if session.exec(select(CoffeeBean)).first() is not None:
            return 0
        beans = _sample_beans()
        session.add_all(beans)
        session.commit()
        return len(beans)
