from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.models.factions import Faction, Station_faction_reputation
from app.models.rover import Rover
from app.models.station import Station
from app.schemas import (
    StationCreate,
    StationFactionRepInfo,
    StationResponse,
    StationStatsResponse,
)

router = APIRouter(prefix="/stations", tags=["Stations"])
Session = Annotated[Session, Depends(get_db)]


@router.get("/", response_model=list[StationResponse])
def get_stations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    stations = db.query(Station).offset(skip).limit(limit).all()
    return stations


@router.get("/stats", response_model=StationStatsResponse)
def get_current_station_stats(db: Session):
    """
    Возвращает статус станции игрока: баланс (деньги), суммарную репутацию,
    репутацию с каждой фракцией и проверку условия проигрыша (репутация < 20 с любой фракцией).
    Returns the status of the player's station.

    Args:
        db: Session database.

    Return:
        Balance, total reputation, reputation with each faction, and a check for the loss condition.

    Raises:
        HTTPException: If not station.
    """
    station = db.query(Station).first()
    if not station:
        raise HTTPException(status_code=404, detail="Станция не найдена")

    factions = db.query(Faction).all()
    reputations = (
        db.query(Station_faction_reputation)
        .filter(Station_faction_reputation.station_id == station.id)
        .all()
    )
    rep_map = {r.faction_id: r.reputation for r in reputations}

    faction_rep_infos: list[StationFactionRepInfo] = []
    is_game_over = False
    game_over_reason = None

    for f in factions:
        rep_val = rep_map.get(f.id, 50)
        is_critical = rep_val < 20
        if is_critical:
            is_game_over = True
            game_over_reason = f"КРИТИЧЕСКИЙ ПРОВАЛ: Репутация с фракцией '{f.name}' упала ниже 20 ({rep_val}/100)!"

        faction_rep_infos.append(
            StationFactionRepInfo(
                faction_id=f.id,
                faction_name=f.name,
                faction_tag=f.tag,
                reputation=rep_val,
                is_critical=is_critical,
            )
        )

    rovers_count = db.query(Rover).filter(Rover.station_id == station.id).count()

    return StationStatsResponse(
        id=station.id,
        name=station.name,
        balance=station.balance,
        reputation=station.reputation,
        fleet_capacity=station.fleet_capacity,
        rovers_count=rovers_count,
        is_game_over=is_game_over,
        game_over_reason=game_over_reason,
        faction_reputations=faction_rep_infos,
    )


@router.post("/reset")
def reset_game_state(db: Session):
    """
    Reset game progress.

    Args:
        db: Session database.

    Return:
        Status.

    Raises:
        HTTPException: If not station.
    """
    station = db.query(Station).first()
    if not station:
        raise HTTPException(status_code=404, detail="Станция не найдена")

    station.balance = 5000
    station.reputation = 150

    reputations = (
        db.query(Station_faction_reputation)
        .filter(Station_faction_reputation.station_id == station.id)
        .all()
    )
    for r in reputations:
        r.reputation = 50

    rovers = db.query(Rover).filter(Rover.station_id == station.id).all()
    for rov in rovers:
        rov.now_battery_capacity = min(rov.battery_capacity, 100)
        rov.wear = 0
        rov.status = "idle"
        rov.current_location_id = station.location_id

    db.commit()
    return {"status": "success", "message": "Игра перезапущена!"}


@router.post("/", response_model=StationResponse, status_code=status.HTTP_201_CREATED)
def create_station(station: StationCreate, db: Session):
    """
    Create station.

    Args:
        station: Station data.
        db: Session database.

    Return:
        Station.
    """
    db_station = Station(**station.model_dump())
    db.add(db_station)
    db.commit()
    db.refresh(db_station)
    return db_station


@router.get("/{station_id}", response_model=StationResponse)
def get_station(station_id: UUID, db: Session):
    """
    Get station.

    Args:
        station_id: UUID of station.
        db: Session database.

    Return:
        Station.

    Raises:
        HTTPException: If not station.
    """
    station = db.query(Station).filter(Station.id == station_id).first()
    if not station:
        raise HTTPException(status_code=404, detail="Станция не найдена")
    return station
