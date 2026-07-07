"""CRUD + search/filter/sort for coffee beans."""
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlmodel import Session, select

from .db import get_session
from .models import CoffeeBean
from .schemas import BeanCreate, BeanRead, BeanUpdate

router = APIRouter(prefix="/api/beans", tags=["beans"])


def func_lower(col):
    """lower(coalesce(col, '')) — case-insensitive, NULL-safe substring search."""
    return func.lower(func.coalesce(col, ""))

SORT_FIELDS = {
    "name": CoffeeBean.name,
    "roaster": CoffeeBean.roaster,
    "process": CoffeeBean.process,
    "origin_country": CoffeeBean.origin_country,
    "weight_left_g": CoffeeBean.weight_left_g,
    "roast_date": CoffeeBean.roast_date,
    "rating": CoffeeBean.rating,
}


def to_read(bean: CoffeeBean) -> BeanRead:
    """Attach derived fields (days_since_roast, low_stock)."""
    days = None
    if bean.roast_date is not None:
        days = (date.today() - bean.roast_date).days
    low_stock = bean.weight_left_g <= bean.reorder_threshold_g
    return BeanRead(
        **bean.model_dump(),
        days_since_roast=days,
        low_stock=low_stock,
    )


@router.get("", response_model=list[BeanRead])
def list_beans(
    session: Session = Depends(get_session),
    q: str | None = None,
    process: str | None = None,
    origin_country: str | None = None,
    category: str | None = None,
    sort: str = Query("roast_date"),
    order: str = Query("asc", pattern="^(asc|desc)$"),
):
    stmt = select(CoffeeBean)

    if q:
        like = f"%{q.lower()}%"
        stmt = stmt.where(
            func_lower(CoffeeBean.name).like(like)
            | func_lower(CoffeeBean.roaster).like(like)
            | func_lower(CoffeeBean.origin_country).like(like)
            | func_lower(CoffeeBean.notes).like(like)
        )
    if process:
        stmt = stmt.where(CoffeeBean.process == process)
    if origin_country:
        stmt = stmt.where(CoffeeBean.origin_country == origin_country)
    if category:
        stmt = stmt.where(CoffeeBean.category == category)

    col = SORT_FIELDS.get(sort, CoffeeBean.roast_date)
    stmt = stmt.order_by(col.desc() if order == "desc" else col.asc())

    beans = session.exec(stmt).all()
    return [to_read(b) for b in beans]


@router.post("", response_model=BeanRead, status_code=201)
def create_bean(payload: BeanCreate, session: Session = Depends(get_session)):
    bean = CoffeeBean(**payload.model_dump())
    session.add(bean)
    session.commit()
    session.refresh(bean)
    return to_read(bean)


@router.get("/{bean_id}", response_model=BeanRead)
def get_bean(bean_id: int, session: Session = Depends(get_session)):
    bean = session.get(CoffeeBean, bean_id)
    if not bean:
        raise HTTPException(404, "Bean not found")
    return to_read(bean)


@router.patch("/{bean_id}", response_model=BeanRead)
def update_bean(bean_id: int, payload: BeanUpdate, session: Session = Depends(get_session)):
    bean = session.get(CoffeeBean, bean_id)
    if not bean:
        raise HTTPException(404, "Bean not found")
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(bean, key, value)
    session.add(bean)
    session.commit()
    session.refresh(bean)
    return to_read(bean)


@router.delete("/{bean_id}", status_code=204)
def delete_bean(bean_id: int, session: Session = Depends(get_session)):
    bean = session.get(CoffeeBean, bean_id)
    if not bean:
        raise HTTPException(404, "Bean not found")
    session.delete(bean)
    session.commit()
