from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.route import RouteSegment

router = APIRouter(tags=["Routes"])
Session = Annotated[Session, Depends(get_db)]


@router.get("/routes")
def get_all_routes(db: Session):
    """
    Take list all routes between base.

    Args:
        db: Session database.

    Return:
        Routes.
    """
    routes = db.query(RouteSegment).all()
    return routes
