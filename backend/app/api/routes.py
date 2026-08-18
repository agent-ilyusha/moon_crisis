from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.Route import RouteSegment

router = APIRouter(tags=["Routes"])


@router.get("/routes")
def get_all_routes(db: Session = Depends(get_db)):
    """
    Получить список всех соединительных маршрутов между базами.
    """
    routes = db.query(RouteSegment).all()
    return routes
