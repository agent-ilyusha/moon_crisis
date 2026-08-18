from uuid import uuid4


def test_get_nodes(client, db_session, seed_data):
    response = client.get("/api/nodes")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3


def test_get_maps(client, db_session, seed_data):
    response = client.get("/api/maps")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3


def test_get_map_by_id(client, db_session, seed_data):
    loc_id = seed_data["loc_a"].id
    response = client.get(f"/api/maps/{loc_id}")
    assert response.status_code == 200
    assert response.json()["name"] == seed_data["loc_a"].name


def test_get_map_not_found(client):
    response = client.get(f"/api/maps/{uuid4()}")
    assert response.status_code == 404
