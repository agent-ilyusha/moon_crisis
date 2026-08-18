from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.map import Map
from app.schemas import MapNodeResponse

router = APIRouter(tags=["Maps"])
Session = Annotated[Session, Depends(get_db)]


@router.get("/maps", response_model=list[MapNodeResponse])
def get_all_maps(db: Session):
    """
    Get all maps.

    Args:
        db: Session database.

    Return:
        List of query with maps.
    """
    maps = db.query(Map).all()
    return [MapNodeResponse.from_map(m) for m in maps]


@router.get("/nodes", response_model=list[MapNodeResponse])
def get_all_nodes(db: Session):
    """
    Get all nodes.

    Args:
        db: Session database.

    Return:
        List of all query with maps.
    """
    maps = db.query(Map).all()
    return [MapNodeResponse.from_map(m) for m in maps]


@router.get("/maps/{map_id}", response_model=MapNodeResponse)
def get_map_by_id(map_id: str, db: Session):
    """
    Get map by id.

    Args:
        map_id: Id on maps.
        db: Session database.

    Return:
        Query from id.

    Raises:
        HTTPException: If not location.
    """
    location = db.query(Map).filter(Map.id == map_id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Локация не найдена")
    return MapNodeResponse.from_map(location)
