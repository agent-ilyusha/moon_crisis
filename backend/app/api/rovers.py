from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field

from app.api.dependencies import get_db
from app.models.Rover import Rover
from app.models.Station import Station
from app.schemas import (
    RoverBuyRequest,
    RoverCatalogItem,
    RoverCreate,
    RoverRepairResponse,
    RoverResponse,
    RoverUpdate,
)
from app.services.dispatch import (
    calculate_energy_spent,
    calculate_rewards,
    calculate_travel_time_seconds,
    calculate_wear_inflicted,
    find_route_info,
    schedule_rover_arrival,
)

router = APIRouter(prefix="/rovers", tags=["Rovers"])

ROVER_CATALOG: list[RoverCatalogItem] = [
    RoverCatalogItem(
        model="Mule-Mk1",
        name_prefix="Mule",
        price=2500,
        max_payload=500,
        battery_capacity=100,
        base_drain_rate=5,
        armor=50,
        description="Сбалансированный средний транспортёр общего назначения.",
    ),
    RoverCatalogItem(
        model="Speeder-Lite",
        name_prefix="Speeder",
        price=1800,
        max_payload=200,
        battery_capacity=120,
        base_drain_rate=3,
        armor=30,
        description="Быстрый лёгкий разведчик с низким расходом батареи.",
    ),
    RoverCatalogItem(
        model="Titan-Heavy",
        name_prefix="Titan",
        price=6000,
        max_payload=1200,
        battery_capacity=150,
        base_drain_rate=8,
        armor=90,
        description="Тяжёлый бронированный грузовик для опасных зон и массивных грузов.",
    ),
    RoverCatalogItem(
        model="Behemoth-MAX",
        name_prefix="Behemoth",
        price=10000,
        max_payload=2500,
        battery_capacity=200,
        base_drain_rate=12,
        armor=100,
        description="Сверхтяжёлый промышленный флагман лунного флота.",
    ),
]


class RoverDispatch(BaseModel):
    rover_id: UUID
    target_location_id: UUID
    cargo_mass: float = Field(default=0.0, ge=0)


class DispatchResponse(BaseModel):
    status: str
    energy_spent: float
    travel_time_seconds: int
    hazard_risk: int
    wear_inflicted: int
    reward_credits: int
    reward_rep: float
    rover: RoverResponse

    model_config = {"from_attributes": True}


@router.get("/catalog", response_model=List[RoverCatalogItem])
def get_rover_catalog():
    """Каталог доступных моделей роверов для покупки."""
    return ROVER_CATALOG


@router.post("/buy", response_model=RoverResponse)
def buy_rover(payload: RoverBuyRequest, db: Session = Depends(get_db)):
    """
    Покупка нового ровера за кредиты станции.
    """
    catalog_item = next((item for item in ROVER_CATALOG if item.model == payload.model), None)
    if not catalog_item:
        raise HTTPException(status_code=400, detail=f"Модель '{payload.model}' не найдена в каталоге")

    station = db.query(Station).first()
    if not station:
        raise HTTPException(status_code=404, detail="Станция не найдена")

    current_fleet_count = db.query(Rover).filter(Rover.station_id == station.id).count()
    if current_fleet_count >= station.fleet_capacity:
        raise HTTPException(
            status_code=400,
            detail=f"Ангар переполнен! Лимит флота: {station.fleet_capacity} роверов.",
        )

    if station.balance < catalog_item.price:
        raise HTTPException(
            status_code=400,
            detail=f"Недостаточно средств! Требуется {catalog_item.price} CR, доступно {station.balance} CR.",
        )

    station.balance -= catalog_item.price

    rover_name = payload.name or f"{catalog_item.name_prefix}-{current_fleet_count + 1:02d}"

    # Проверяем уникальность имени
    if db.query(Rover).filter(Rover.name == rover_name).first():
        rover_name = f"{rover_name}-{uuid4().hex[:4]}"

    new_rover = Rover(
        id=uuid4(),
        name=rover_name,
        model=catalog_item.model,
        max_payload=catalog_item.max_payload,
        battery_capacity=catalog_item.battery_capacity,
        base_drain_rate=catalog_item.base_drain_rate,
        armor=catalog_item.armor,
        now_battery_capacity=catalog_item.battery_capacity if catalog_item.battery_capacity <= 100 else 100,
        position_x=0.0,
        position_y=0.0,
        status="idle",
        wear=0,
        current_location_id=station.location_id,
        station_id=station.id,
    )
    db.add(new_rover)
    db.commit()
    db.refresh(new_rover)

    return new_rover


@router.post("/{rover_id}/repair", response_model=RoverRepairResponse)
def repair_rover(rover_id: UUID, db: Session = Depends(get_db)):
    """
    Ремонт ровера за кредиты станции (устранение износа и повреждений).
    Стоимость: 10 CR за 1% износа.
    """
    db_rover = db.query(Rover).filter(Rover.id == rover_id).first()
    if not db_rover:
        raise HTTPException(status_code=404, detail="Ровер не найден")

    if db_rover.status == "en_route":
        raise HTTPException(status_code=400, detail="Невозможно ремонтировать ровер в пути")

    if db_rover.wear <= 0:
        raise HTTPException(status_code=400, detail="Ровер не имеет износа и полностью исправен")

    station = None
    if db_rover.station_id:
        station = db.query(Station).filter(Station.id == db_rover.station_id).first()
    if not station:
        station = db.query(Station).first()

    cost_credits = int(db_rover.wear * 10)
    if station and station.balance < cost_credits:
        raise HTTPException(
            status_code=400,
            detail=f"Недостаточно кредитов для ремонта! Требуется {cost_credits} CR, доступно {station.balance} CR",
        )

    if station:
        station.balance -= cost_credits

    repaired_wear = db_rover.wear
    db_rover.wear = 0
    if db_rover.status == "damaged":
        db_rover.status = "idle"

    db.commit()
    db.refresh(db_rover)

    return RoverRepairResponse(
        rover=db_rover,
        cost_credits=cost_credits,
        new_station_balance=station.balance if station else 0,
        repaired_wear=repaired_wear,
    )


@router.get("/", response_model=List[RoverResponse])
def get_rovers(db: Session = Depends(get_db)):
    return db.query(Rover).all()


@router.post("/", response_model=RoverResponse)
def create_rover(rover: RoverCreate, db: Session = Depends(get_db)):
    db_rover = Rover(**rover.model_dump())
    db.add(db_rover)
    db.commit()
    db.refresh(db_rover)
    return db_rover


@router.post("/dispatch", response_model=DispatchResponse)
def dispatch_rover(
    payload: RoverDispatch,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    db_rover = db.query(Rover).filter(Rover.id == payload.rover_id).first()
    if not db_rover:
        raise HTTPException(status_code=404, detail="Ровер не найден")

    if db_rover.status == "damaged":
        raise HTTPException(
            status_code=400,
            detail="Ровер повреждён (критический износ 100%) и требует ремонта перед отправкой!",
        )

    if db_rover.status != "idle":
        raise HTTPException(status_code=400, detail="Ровер недоступен: уже в пути или на обслуживании")

    if not db_rover.current_location_id:
        raise HTTPException(status_code=400, detail="Ровер не привязан к локации")

    if payload.cargo_mass > db_rover.max_payload:
        raise HTTPException(
            status_code=400,
            detail=f"Превышена грузоподъёмность: максимум {db_rover.max_payload} кг",
        )

    if db_rover.now_battery_capacity <= 0:
        raise HTTPException(status_code=400, detail="Ровер разряжен и не может быть отправлен")

    distance_km, avg_hazard_risk, _ = find_route_info(
        db, db_rover.current_location_id, payload.target_location_id
    )

    energy_spent = calculate_energy_spent(
        distance_km=distance_km,
        cargo_mass=payload.cargo_mass,
        max_payload=db_rover.max_payload,
        hazard_risk=avg_hazard_risk,
    )
    travel_time_seconds = calculate_travel_time_seconds(distance_km, avg_hazard_risk)
    wear_inflicted = calculate_wear_inflicted(
        distance_km=distance_km,
        cargo_mass=payload.cargo_mass,
        max_payload=db_rover.max_payload,
        hazard_risk=avg_hazard_risk,
        armor=db_rover.armor,
    )
    reward_credits, reward_rep = calculate_rewards(distance_km, payload.cargo_mass)

    if int(round(energy_spent)) > db_rover.now_battery_capacity:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Недостаточно заряда: требуется {energy_spent}%, "
                f"доступно {db_rover.now_battery_capacity}%"
            ),
        )

    db_rover.now_battery_capacity = max(
        0, int(round(db_rover.now_battery_capacity - energy_spent))
    )
    db_rover.status = "en_route"
    db_rover.current_location_id = payload.target_location_id

    db.commit()
    db.refresh(db_rover)

    background_tasks.add_task(
        schedule_rover_arrival,
        db_rover.id,
        payload.cargo_mass,
        travel_time_seconds,
        wear_inflicted,
        payload.target_location_id,
        distance_km,
    )

    return DispatchResponse(
        status="success",
        energy_spent=energy_spent,
        travel_time_seconds=travel_time_seconds,
        hazard_risk=int(round(avg_hazard_risk)),
        wear_inflicted=wear_inflicted,
        reward_credits=reward_credits,
        reward_rep=reward_rep,
        rover=db_rover,
    )


@router.patch("/{rover_id}", response_model=RoverResponse)
def update_rover_status(rover_id: UUID, rover_update: RoverUpdate, db: Session = Depends(get_db)):
    db_rover = db.query(Rover).filter(Rover.id == rover_id).first()
    if not db_rover:
        raise HTTPException(status_code=404, detail="Ровер не найден")

    update_data = rover_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_rover, key, value)

    db.commit()
    db.refresh(db_rover)
    return db_rover


@router.post("/{rover_id}/charge", response_model=RoverResponse)
def charge_rover(rover_id: UUID, db: Session = Depends(get_db)):
    db_rover = db.query(Rover).filter(Rover.id == rover_id).first()
    if not db_rover:
        raise HTTPException(status_code=404, detail="Ровер не найден")

    if db_rover.status != "idle":
        raise HTTPException(
            status_code=400,
            detail="Зарядка возможна только в состоянии ожидания (idle)"
        )

    if db_rover.now_battery_capacity >= 100.0:
        raise HTTPException(status_code=400, detail="Батарея уже полностью заряжена")

    db_rover.now_battery_capacity = 100.0
    db.commit()
    db.refresh(db_rover)
    return db_rover
