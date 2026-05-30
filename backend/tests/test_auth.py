import pytest


@pytest.mark.asyncio
async def test_login_success(client, registered_user):
    r = await client.post(
        "/api/auth/token/login/",
        json={"email": "user@test.com", "password": "securepass123"},
    )
    assert r.status_code == 200
    data = r.json()
    assert "auth_token" in data
    assert isinstance(data["auth_token"], str)
    assert len(data["auth_token"]) > 10


@pytest.mark.asyncio
async def test_login_wrong_password(client, registered_user):
    r = await client.post(
        "/api/auth/token/login/",
        json={"email": "user@test.com", "password": "wrongpassword"},
    )
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_login_nonexistent_email(client):
    r = await client.post(
        "/api/auth/token/login/",
        json={"email": "nobody@test.com", "password": "anypassword"},
    )
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_login_missing_fields(client):
    # Custom validation error handler returns 400 (not 422)
    r = await client.post("/api/auth/token/login/", json={})
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_login_invalid_email_format(client):
    # Custom validation error handler returns 400 (not 422)
    r = await client.post(
        "/api/auth/token/login/",
        json={"email": "not-an-email", "password": "securepass123"},
    )
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_logout_success(client, auth_headers):
    r = await client.post("/api/auth/token/logout/", headers=auth_headers)
    assert r.status_code == 204


@pytest.mark.asyncio
async def test_logout_without_token(client):
    r = await client.post("/api/auth/token/logout/")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_token_invalidated_after_logout(client, auth_headers):
    await client.post("/api/auth/token/logout/", headers=auth_headers)
    r = await client.get("/api/users/me/", headers=auth_headers)
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_health_endpoint(client):
    r = await client.get("/health/")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}
