from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.Map import Map
from app.schemas import MapNodeResponse

router = APIRouter(tags=["Maps"])


@router.get("/maps", response_model=List[MapNodeResponse])
def get_all_maps(db: Session = Depends(get_db)):
    maps = db.query(Map).all()
    return [MapNodeResponse.from_map(m) for m in maps]


@router.get("/nodes", response_model=List[MapNodeResponse])
def get_all_nodes(db: Session = Depends(get_db)):
    maps = db.query(Map).all()
    return [MapNodeResponse.from_map(m) for m in maps]


@router.get("/maps/{map_id}", response_model=MapNodeResponse)
def get_map_by_id(map_id: str, db: Session = Depends(get_db)):
    location = db.query(Map).filter(Map.id == map_id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Локация не найдена")
    return MapNodeResponse.from_map(location)
