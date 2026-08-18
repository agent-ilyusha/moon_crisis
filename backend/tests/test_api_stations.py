import pytest
from uuid import uuid4
from app.models.Station import Station


def test_get_stations(client, db_session, seed_data):
    # Создаем тестовую станцию
    station = Station(
        id=uuid4(),
        name="API Test Station",
        balance=1000,
        reputation=50,
        fleet_capacity=3,
        faction_id=seed_data["faction_a"].id
    )
    db_session.add(station)
    db_session.commit()

    response = client.get("/api/stations/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(s["name"] == "API Test Station" for s in data)


def test_get_station_by_id(client, db_session, seed_data):
    station_id = uuid4()
    station = Station(
        id=station_id,
        name="Single Station",
        balance=100,
        faction_id=seed_data["faction_a"].id
    )
    db_session.add(station)
    db_session.commit()

    response = client.get(f"/api/stations/{station_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Single Station"


def test_get_station_not_found(client):
    response = client.get(f"/api/stations/{uuid4()}")
    assert response.status_code == 404


def test_get_station_stats(client, db_session, seed_data):
    # Сначала удалим все станции, чтобы была предсказуемость (или просто возьмем первую)
    db_session.query(Station).delete()
    
    station = Station(
        id=uuid4(),
        name="Stats Station",
        balance=555,
        reputation=120,
        fleet_capacity=10,
        faction_id=seed_data["faction_a"].id
    )
    db_session.add(station)
    db_session.commit()

    response = client.get("/api/stations/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["balance"] == 555
    assert data["reputation"] >= 0
    assert "faction_reputations" in data


def test_reset_game_state(client, db_session, seed_data):
    station = Station(
        id=uuid4(),
        name="Reset Station",
        balance=0,
        reputation=0,
        faction_id=seed_data["faction_a"].id
    )
    db_session.add(station)
    db_session.commit()

    response = client.post("/api/stations/reset")
    assert response.status_code == 200
    
    updated = db_session.query(Station).filter(Station.id == station.id).one()
    assert updated.balance == 5000
    assert updated.reputation == 150
