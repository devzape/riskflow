def test_register_and_login(client):
    response = client.post("/auth/register", json={"email": "nuevo@test.com", "password": "1234567"})
    assert response.status_code == 200
    assert response.json()["email"] == "nuevo@test.com"

    response = client.post(
        "/auth/login",
        data={"username": "nuevo@test.com", "password": "1234567"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_with_wrong_password_fails(client):
    client.post("/auth/register", json={"email": "otro@test.com", "password": "1234567"})

    response = client.post(
        "/auth/login",
        data={"username": "otro@test.com", "password": "mal"},
    )
    assert response.status_code == 401