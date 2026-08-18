def test_get_all_routes(client, db_session, seed_data):
    response = client.get("/api/routes")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
