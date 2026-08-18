import uuid

from app.models.Factions import Factions_relationship


def test_get_factions(client, seed_data):
    response = client.get("/api/factions")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    names = {f["name"] for f in data}
    assert names == {"SpaceX", "NASA"}


def test_get_faction_by_id(client, seed_data):
    faction = seed_data["faction_a"]
    response = client.get(f"/api/factions/{faction.id}")
    assert response.status_code == 200
    assert response.json()["tag"] == "SPX"


def test_get_faction_not_found(client):
    response = client.get(f"/api/factions/{uuid.uuid4()}")
    assert response.status_code == 404


def test_create_faction_relationship(client, seed_data):
    faction_a = seed_data["faction_a"]
    faction_b = seed_data["faction_b"]

    payload = {
        "first_faction_id": str(faction_a.id),
        "second_faction_id": str(faction_b.id),
        "reputation_impact": 25.0,
    }
    response = client.post("/api/factions/relationships", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["reputation_impact"] == 25.0


def test_update_faction_relationship(client, seed_data):
    relationship = seed_data["relationship"]

    response = client.patch(
        f"/api/factions/relationships/{relationship.id}",
        json={"reputation_impact": -10.0},
    )
    assert response.status_code == 200
    assert response.json()["reputation_impact"] == -10.0


def test_upsert_faction_relationship(client, seed_data):
    faction_a = seed_data["faction_a"]
    faction_b = seed_data["faction_b"]

    payload = {
        "first_faction_id": str(faction_b.id),
        "second_faction_id": str(faction_a.id),
        "reputation_impact": 50.0,
    }
    response = client.post("/api/factions/relationships", json=payload)
    assert response.status_code == 200
    assert response.json()["reputation_impact"] == 50.0

    listed = client.get("/api/factions/relationships").json()
    assert len(listed) == 1


def test_get_faction_relationships(client, seed_data):
    faction_a = seed_data["faction_a"]
    response = client.get(f"/api/factions/{faction_a.id}/relationships")
    assert response.status_code == 200
    assert len(response.json()) == 1
