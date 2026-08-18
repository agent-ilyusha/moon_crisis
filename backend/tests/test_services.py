from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.models.rover import Rover
from app.services.dispatch import (
    calculate_energy_spent,
    calculate_rewards,
    calculate_travel_time_seconds,
    calculate_wear_inflicted,
    find_route_distance_km,
    find_route_info,
    schedule_rover_arrival,
)


def test_calculate_energy_spent():
    assert calculate_energy_spent(10.0, 0.0, 500.0, 0.0) == pytest.approx(1.0)
    assert calculate_energy_spent(10.0, 500.0, 500.0, 0.0) == pytest.approx(2.0)
    assert calculate_energy_spent(10.0, 250.0, 500.0, 50.0) == pytest.approx(2.2)  # 1.0 * 1.5 * 1.5 = 2.25 -> 2.2


def test_calculate_travel_time_seconds():
    assert calculate_travel_time_seconds(0.0) == 5  # минимум 5 секунд
    assert calculate_travel_time_seconds(10.0, 0.0) == 15  # 10 * 1.5
    assert calculate_travel_time_seconds(10.0, 50.0) == 30  # 10 * 1.5 * (1 + 50/50) = 30


def test_calculate_wear_inflicted():
    assert calculate_wear_inflicted(100.0, 0.0, 500.0, 0.0, 50) == 2  # (100 * 0.02 + 0) * 1 * 1 = 2
    assert calculate_wear_inflicted(10.0, 0.0, 500.0, 50.0, 50) == 10  # (10 * 0.02 + 50 * 0.2) * 1 * 1 = 10.2 -> 10


def test_calculate_rewards():
    credits, rep = calculate_rewards(100.0, 200.0)
    assert credits == int(100 + 100 * 3.0 + 200 * 1.5)
    assert rep == pytest.approx(5.0 + 200 * 0.02 + 100 * 0.01)

    id1 = uuid4()
    _, rep2 = calculate_rewards(100.0, 200.0, id1, id1)
    assert rep2 == pytest.approx((5.0 + 200 * 0.02 + 100 * 0.01) * 1.5)


def test_find_route_distance_success(db_session, seed_data):
    loc_a_id = seed_data["loc_a"].id
    loc_b_id = seed_data["loc_b"].id

    distance = find_route_distance_km(db_session, loc_a_id, loc_b_id)
    assert distance == 10.0


def test_find_route_info_success(db_session, seed_data):
    loc_a_id = seed_data["loc_a"].id
    loc_b_id = seed_data["loc_b"].id

    dist, hazard, path = find_route_info(db_session, loc_a_id, loc_b_id)
    assert dist == 10.0
    assert hazard == 0.0
    assert len(path) == 2


def test_find_route_distance_same_location(db_session, seed_data):
    loc_a_id = seed_data["loc_a"].id
    assert find_route_distance_km(db_session, loc_a_id, loc_a_id) == 0.0


def test_find_route_distance_unreachable(db_session, seed_data):
    loc_a_id = seed_data["loc_a"].id
    loc_c_id = seed_data["loc_c"].id

    with pytest.raises(HTTPException) as exc:
        find_route_distance_km(db_session, loc_a_id, loc_c_id)
    assert exc.value.status_code == 400
    assert "не найден" in exc.value.detail.lower()


def test_schedule_rover_arrival(db_session, seed_data, mocker):
    mocker.patch("app.services.dispatch.time.sleep", return_value=None)
    mocker.patch("app.services.dispatch.SessionFactory", return_value=db_session)
    mocker.patch.object(db_session, "close", return_value=None)

    rover = seed_data["rover"]
    rover.status = "en_route"
    db_session.commit()

    schedule_rover_arrival(rover.id, 100.0, 15, wear_inflicted=10, target_location_id=seed_data["loc_b"].id, distance_km=10.0)

    updated = db_session.query(Rover).filter(Rover.id == rover.id).one()
    assert updated.status == "idle"
    assert updated.wear == 10
    assert updated.current_location_id == seed_data["loc_b"].id
