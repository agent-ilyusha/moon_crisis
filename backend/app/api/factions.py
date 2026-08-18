from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.models.Factions import Faction, Factions_relationship
from app.schemas import (
    FactionRelationshipCreate,
    FactionRelationshipResponse,
    FactionRelationshipUpdate,
    FactionResponse,
)

router = APIRouter(tags=["Factions"])


def _get_faction_or_404(db: Session, faction_id: UUID) -> Faction:
    faction = db.query(Faction).filter(Faction.id == faction_id).first()
    if not faction:
        raise HTTPException(status_code=404, detail="Фракция не найдена")
    return faction


def _find_relationship(
    db: Session, faction_a: UUID, faction_b: UUID
) -> Factions_relationship | None:
    return (
        db.query(Factions_relationship)
        .filter(
            (
                (Factions_relationship.first_faction_id == faction_a)
                & (Factions_relationship.second_faction_id == faction_b)
            )
            | (
                (Factions_relationship.first_faction_id == faction_b)
                & (Factions_relationship.second_faction_id == faction_a)
            )
        )
        .first()
    )


@router.get("/factions", response_model=List[FactionResponse])
def get_all_factions(db: Session = Depends(get_db)):
    factions = db.query(Faction).all()
    from app.models.Station import Station
    from app.models.Factions import Station_faction_reputation

    station = db.query(Station).first()
    rep_map = {}
    if station:
        reps = (
            db.query(Station_faction_reputation)
            .filter(Station_faction_reputation.station_id == station.id)
            .all()
        )
        rep_map = {r.faction_id: r.reputation for r in reps}

    result = []
    for f in factions:
        rep_val = rep_map.get(f.id, 50)
        result.append(
            FactionResponse(
                id=f.id,
                name=f.name,
                tag=f.tag,
                description=f.description,
                reputation=rep_val,
            )
        )
    return result


@router.get("/factions/relationships", response_model=List[FactionRelationshipResponse])
def get_all_faction_relationships(db: Session = Depends(get_db)):
    return db.query(Factions_relationship).all()


@router.post("/factions/relationships", response_model=FactionRelationshipResponse)
def create_or_update_faction_relationship(
    payload: FactionRelationshipCreate,
    db: Session = Depends(get_db),
):
    if payload.first_faction_id == payload.second_faction_id:
        raise HTTPException(
            status_code=400,
            detail="Фракция не может иметь отношение сама с собой",
        )

    _get_faction_or_404(db, payload.first_faction_id)
    _get_faction_or_404(db, payload.second_faction_id)

    existing = _find_relationship(
        db, payload.first_faction_id, payload.second_faction_id
    )
    if existing:
        existing.reputation_impact = payload.reputation_impact
        db.commit()
        db.refresh(existing)
        return existing

    relationship = Factions_relationship(
        first_faction_id=payload.first_faction_id,
        second_faction_id=payload.second_faction_id,
        reputation_impact=payload.reputation_impact,
    )
    db.add(relationship)
    db.commit()
    db.refresh(relationship)
    return relationship


@router.patch(
    "/factions/relationships/{relationship_id}",
    response_model=FactionRelationshipResponse,
)
def update_faction_relationship(
    relationship_id: UUID,
    payload: FactionRelationshipUpdate,
    db: Session = Depends(get_db),
):
    relationship = (
        db.query(Factions_relationship)
        .filter(Factions_relationship.id == relationship_id)
        .first()
    )
    if not relationship:
        raise HTTPException(status_code=404, detail="Отношение между фракциями не найдено")

    relationship.reputation_impact = payload.reputation_impact
    db.commit()
    db.refresh(relationship)
    return relationship


@router.get(
    "/factions/{faction_id}/relationships",
    response_model=List[FactionRelationshipResponse],
)
def get_faction_relationships(faction_id: UUID, db: Session = Depends(get_db)):
    _get_faction_or_404(db, faction_id)
    return (
        db.query(Factions_relationship)
        .filter(
            (Factions_relationship.first_faction_id == faction_id)
            | (Factions_relationship.second_faction_id == faction_id)
        )
        .all()
    )


@router.get("/factions/{faction_id}", response_model=FactionResponse)
def get_faction_by_id(faction_id: UUID, db: Session = Depends(get_db)):
    return _get_faction_or_404(db, faction_id)
