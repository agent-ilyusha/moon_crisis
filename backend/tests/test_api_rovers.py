from uuid import uuid4

from app.models.rover import Rover
from app.models.station import Station


def test_get_rovers(client, seed_data):
    response = client.get("/api/rovers/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "TestRover"


def test_create_rover(client):
    payload = {
        "name": "NewRover", "model": "Scout", "max_payload": 200,
        "battery_capacity": 500, "base_drain_rate": 1, "armor": 50,
        "now_battery_capacity": 100, "position_x": 5.0, "position_y": 5.0,
        "status": "idle", "wear": 0
    }
    response = client.post("/api/rovers/", json=payload)
    assert response.status_code == 200
    assert response.json()["name"] == "NewRover"


def test_dispatch_rover_success(client, seed_data):
    rover = seed_data["rover"]
    loc_b = seed_data["loc_b"]

    payload = {
        "rover_id": str(rover.id),
        "target_location_id": str(loc_b.id),
        "cargo_mass": 100.0
    }
    response = client.post("/api/rovers/dispatch", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["energy_spent"] > 0
    assert data["wear_inflicted"] >= 0
    assert data["rover"]["status"] == "en_route"
    assert data["rover"]["current_location_id"] == str(loc_b.id)


def test_dispatch_rover_overweight(client, seed_data):
    rover = seed_data["rover"]
    loc_b = seed_data["loc_b"]

    payload = {
        "rover_id": str(rover.id),
        "target_location_id": str(loc_b.id),
        "cargo_mass": 9999.0  # Больше max_payload (500)
    }
    response = client.post("/api/rovers/dispatch", json=payload)
    assert response.status_code == 400
    assert "Превышена грузоподъёмность" in response.json()["detail"]


def test_dispatch_rover_not_idle(client, db_session, seed_data):
    rover = seed_data["rover"]
    rover.status = "en_route"
    db_session.commit()

    payload = {
        "rover_id": str(rover.id),
        "target_location_id": str(seed_data["loc_b"].id),
        "cargo_mass": 0.0
    }
    response = client.post("/api/rovers/dispatch", json=payload)
    assert response.status_code == 400
    assert "Ровер недоступен" in response.json()["detail"]


def test_charge_rover_success(client, db_session, seed_data):
    rover = seed_data["rover"]
    rover.now_battery_capacity = 20  # Разряжаем ровер
    db_session.commit()

    response = client.post(f"/api/rovers/{rover.id}/charge")
    assert response.status_code == 200
    assert response.json()["now_battery_capacity"] == 100


def test_charge_rover_already_full(client, seed_data):
    rover = seed_data["rover"]

    response = client.post(f"/api/rovers/{rover.id}/charge")
    assert response.status_code == 400
    assert "уже полностью заряжена" in response.json()["detail"]


def test_charge_rover_not_idle(client, db_session, seed_data):
    rover = seed_data["rover"]
    rover.now_battery_capacity = 50
    rover.status = "damaged"
    db_session.commit()

    response = client.post(f"/api/rovers/{rover.id}/charge")
    assert response.status_code == 400
    assert "только в состоянии ожидания" in response.json()["detail"]


def test_buy_and_repair_rover(client, db_session, seed_data):
    station = Station(
        id=uuid4(),
        name="Test Station",
        balance=5000,
        reputation=100,
        fleet_capacity=5,
        location_id=seed_data["loc_a"].id,
        faction_id=seed_data["faction_a"].id
    )
    db_session.add(station)
    db_session.commit()

    buy_response = client.post("/api/rovers/buy", json={"model": "Mule-Mk1"})
    assert buy_response.status_code == 200
    new_rover_data = buy_response.json()
    assert new_rover_data["model"] == "Mule-Mk1"

    updated_station = db_session.query(Station).filter(Station.id == station.id).one()
    assert updated_station.balance == 2500  # 5000 - 2500

    new_rover_id = new_rover_data["id"]
    db_rover = db_session.query(Rover).filter(Rover.id == new_rover_id).one()
    db_rover.wear = 30
    db_session.commit()

    repair_response = client.post(f"/api/rovers/{new_rover_id}/repair")
    assert repair_response.status_code == 200
    repair_data = repair_response.json()
    assert repair_data["cost_credits"] == 300  # 30 * 10
    assert repair_data["rover"]["wear"] == 0
