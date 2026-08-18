import sys
from pathlib import Path

# Добавляем корень проекта в sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Импортируем Base из общего модуля декларативных моделей
from app.models.general import Base

# Обязательно импортируем все модели, чтобы SQLAlchemy зарегистрировала их таблицы в Base.metadata
from app.models import Faction, Map, RouteSegment, Rover, Station, User
from app.models.Map import LocationType
from app.models.Factions import Factions_relationship, Station_faction_reputation

from app.main import app
from app.api.dependencies import get_db as deps_get_db
from app.database import get_db as db_get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def disable_lifespan_seed(mocker):
    """Отключает сидирование реальной Postgres при старте lifespan в тестах."""
    mocker.patch("app.main.seed_database", return_value=None)


@pytest.fixture(scope="function")
def db_session():
    """Создает таблицы в памяти SQLite для каждого теста."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Тестовый клиент FastAPI с подмененной сессией БД."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[deps_get_db] = override_get_db
    app.dependency_overrides[db_get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def seed_data(db_session):
    faction_a = Faction(id=uuid.uuid4(), name="SpaceX", tag="SPX", description="Test Faction A")
    faction_b = Faction(id=uuid.uuid4(), name="NASA", tag="NAS", description="Test Faction B")
    db_session.add_all([faction_a, faction_b])

    loc_a = Map(
        id=uuid.uuid4(), name="Alpha Base", coord_x=0.0, coord_y=0.0,
        location_type=LocationType.base, controlling_faction_id=faction_a.id, has_charging=True
    )
    loc_b = Map(
        id=uuid.uuid4(), name="Beta Outpost", coord_x=10.0, coord_y=10.0,
        location_type=LocationType.outpost, controlling_faction_id=faction_a.id, has_charging=False
    )
    loc_c = Map(
        id=uuid.uuid4(), name="Gamma Mine", coord_x=20.0, coord_y=20.0,
        location_type=LocationType.mine, controlling_faction_id=faction_b.id, has_charging=False
    )
    db_session.add_all([loc_a, loc_b, loc_c])

    route_ab = RouteSegment(
        id=uuid.uuid4(), from_location_id=loc_a.id, to_location_id=loc_b.id,
        distance_km=10.0, hazard_risk=0, base_energy_cost=5
    )
    db_session.add(route_ab)

    relationship = Factions_relationship(
        id=uuid.uuid4(),
        first_faction_id=faction_a.id,
        second_faction_id=faction_b.id,
        reputation_impact=10.0,
    )
    db_session.add(relationship)

    rover = Rover(
        id=uuid.uuid4(), name="TestRover", model="Mule", max_payload=500,
        battery_capacity=1000, base_drain_rate=1, armor=100,
        now_battery_capacity=100, position_x=0.0, position_y=0.0,
        status="idle", wear=0, current_location_id=loc_a.id
    )
    db_session.add(rover)
    db_session.commit()

    return {
        "faction": faction_a,
        "faction_a": faction_a,
        "faction_b": faction_b,
        "relationship": relationship,
        "loc_a": loc_a,
        "loc_b": loc_b,
        "loc_c": loc_c,
        "rover": rover
    }
