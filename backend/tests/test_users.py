import pytest

from tests.conftest import USER_PAYLOAD, USER2_PAYLOAD, TEST_IMAGE


@pytest.mark.asyncio
async def test_register_success(client):
    r = await client.post("/api/users/", json=USER_PAYLOAD)
    assert r.status_code == 201
    data = r.json()
    assert data["email"] == USER_PAYLOAD["email"]
    assert data["username"] == USER_PAYLOAD["username"]
    assert "id" in data
    assert "password" not in data
    assert "hashed_password" not in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client, registered_user):
    payload = {**USER_PAYLOAD, "username": "different_username"}
    r = await client.post("/api/users/", json=payload)
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_register_duplicate_username(client, registered_user):
    payload = {**USER_PAYLOAD, "email": "another@test.com"}
    r = await client.post("/api/users/", json=payload)
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_register_invalid_email(client):
    payload = {**USER_PAYLOAD, "email": "not-an-email"}
    r = await client.post("/api/users/", json=payload)
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_register_invalid_username_pattern(client):
    payload = {**USER_PAYLOAD, "username": "invalid username!"}
    r = await client.post("/api/users/", json=payload)
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_register_missing_fields(client):
    r = await client.post("/api/users/", json={"email": "test@test.com"})
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_get_users_list(client, registered_user):
    r = await client.get("/api/users/")
    assert r.status_code == 200
    data = r.json()
    assert "count" in data
    assert "results" in data
    assert data["count"] >= 1


@pytest.mark.asyncio
async def test_get_users_pagination(client, registered_user, registered_user2):
    r = await client.get("/api/users/?page=1&limit=1")
    assert r.status_code == 200
    data = r.json()
    assert len(data["results"]) == 1
    assert data["next"] is not None


@pytest.mark.asyncio
async def test_get_current_user(client, auth_headers):
    r = await client.get("/api/users/me/", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert data["email"] == USER_PAYLOAD["email"]
    assert data["username"] == USER_PAYLOAD["username"]


@pytest.mark.asyncio
async def test_get_current_user_unauthenticated(client):
    r = await client.get("/api/users/me/")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_get_user_by_id(client, registered_user):
    user_id = registered_user["id"]
    r = await client.get(f"/api/users/{user_id}/")
    assert r.status_code == 200
    assert r.json()["id"] == user_id


@pytest.mark.asyncio
async def test_get_user_not_found(client):
    r = await client.get("/api/users/99999/")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_set_avatar(client, auth_headers):
    r = await client.put(
        "/api/users/me/avatar/",
        json={"avatar": TEST_IMAGE},
        headers=auth_headers,
    )
    assert r.status_code == 200
    assert "avatar" in r.json()


@pytest.mark.asyncio
async def test_delete_avatar(client, auth_headers):
    await client.put(
        "/api/users/me/avatar/",
        json={"avatar": TEST_IMAGE},
        headers=auth_headers,
    )
    r = await client.delete("/api/users/me/avatar/", headers=auth_headers)
    assert r.status_code == 204


@pytest.mark.asyncio
async def test_set_avatar_unauthenticated(client):
    r = await client.put("/api/users/me/avatar/", json={"avatar": TEST_IMAGE})
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_change_password_success(client, auth_headers):
    r = await client.post(
        "/api/users/set_password/",
        json={"current_password": USER_PAYLOAD["password"], "new_password": "newpassword999"},
        headers=auth_headers,
    )
    assert r.status_code == 204


@pytest.mark.asyncio
async def test_change_password_wrong_current(client, auth_headers):
    r = await client.post(
        "/api/users/set_password/",
        json={"current_password": "wrongpassword", "new_password": "newpassword999"},
        headers=auth_headers,
    )
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_change_password_unauthenticated(client):
    r = await client.post(
        "/api/users/set_password/",
        json={"current_password": "any", "new_password": "newpassword999"},
    )
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_subscribe_success(client, auth_headers, registered_user2):
    author_id = registered_user2["id"]
    r = await client.post(f"/api/users/{author_id}/subscribe/", headers=auth_headers)
    assert r.status_code == 201
    data = r.json()
    assert data["id"] == author_id
    assert "recipes_count" in data
    assert "recipes" in data


@pytest.mark.asyncio
async def test_subscribe_to_self(client, auth_headers, registered_user):
    user_id = registered_user["id"]
    r = await client.post(f"/api/users/{user_id}/subscribe/", headers=auth_headers)
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_subscribe_duplicate(client, auth_headers, registered_user2):
    author_id = registered_user2["id"]
    await client.post(f"/api/users/{author_id}/subscribe/", headers=auth_headers)
    r = await client.post(f"/api/users/{author_id}/subscribe/", headers=auth_headers)
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_subscribe_to_nonexistent_user(client, auth_headers):
    r = await client.post("/api/users/99999/subscribe/", headers=auth_headers)
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_subscribe_unauthenticated(client, registered_user2):
    author_id = registered_user2["id"]
    r = await client.post(f"/api/users/{author_id}/subscribe/")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_unsubscribe_success(client, auth_headers, registered_user2):
    author_id = registered_user2["id"]
    await client.post(f"/api/users/{author_id}/subscribe/", headers=auth_headers)
    r = await client.delete(f"/api/users/{author_id}/subscribe/", headers=auth_headers)
    assert r.status_code == 204


@pytest.mark.asyncio
async def test_unsubscribe_not_subscribed(client, auth_headers, registered_user2):
    author_id = registered_user2["id"]
    r = await client.delete(f"/api/users/{author_id}/subscribe/", headers=auth_headers)
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_get_subscriptions_empty(client, auth_headers):
    r = await client.get("/api/users/subscriptions/", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert data["count"] == 0
    assert data["results"] == []


@pytest.mark.asyncio
async def test_get_subscriptions_with_data(client, auth_headers, registered_user2):
    author_id = registered_user2["id"]
    await client.post(f"/api/users/{author_id}/subscribe/", headers=auth_headers)
    r = await client.get("/api/users/subscriptions/", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert data["count"] == 1
    assert data["results"][0]["id"] == author_id


@pytest.mark.asyncio
async def test_get_subscriptions_unauthenticated(client):
    r = await client.get("/api/users/subscriptions/")
    assert r.status_code == 401


# ── is_subscribed correctness ─────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_is_subscribed_false_before_subscribe(client, auth_headers, registered_user2):
    author_id = registered_user2["id"]
    r = await client.get(f"/api/users/{author_id}/", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["is_subscribed"] is False


@pytest.mark.asyncio
async def test_is_subscribed_true_after_subscribe(client, auth_headers, registered_user2):
    author_id = registered_user2["id"]
    await client.post(f"/api/users/{author_id}/subscribe/", headers=auth_headers)
    r = await client.get(f"/api/users/{author_id}/", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["is_subscribed"] is True


@pytest.mark.asyncio
async def test_is_subscribed_false_for_self(client, auth_headers, registered_user):
    r = await client.get(f"/api/users/{registered_user['id']}/", headers=auth_headers)
    assert r.json()["is_subscribed"] is False


@pytest.mark.asyncio
async def test_is_subscribed_false_after_unsubscribe(client, auth_headers, registered_user2):
    author_id = registered_user2["id"]
    await client.post(f"/api/users/{author_id}/subscribe/", headers=auth_headers)
    await client.delete(f"/api/users/{author_id}/subscribe/", headers=auth_headers)
    r = await client.get(f"/api/users/{author_id}/", headers=auth_headers)
    assert r.json()["is_subscribed"] is False


@pytest.mark.asyncio
async def test_is_subscribed_in_users_list(client, auth_headers, registered_user, registered_user2):
    author_id = registered_user2["id"]
    await client.post(f"/api/users/{author_id}/subscribe/", headers=auth_headers)
    r = await client.get("/api/users/", headers=auth_headers)
    assert r.status_code == 200
    users_by_id = {u["id"]: u for u in r.json()["results"]}
    assert users_by_id[registered_user["id"]]["is_subscribed"] is False
    assert users_by_id[author_id]["is_subscribed"] is True


@pytest.mark.asyncio
async def test_is_subscribed_without_auth(client, registered_user2):
    author_id = registered_user2["id"]
    r = await client.get(f"/api/users/{author_id}/")
    assert r.json()["is_subscribed"] is False


# ── rate limiting ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_login_rate_limit_allows_normal_requests(client, registered_user):
    for _ in range(5):
        r = await client.post(
            "/api/auth/token/login/",
            json={"email": USER_PAYLOAD["email"], "password": USER_PAYLOAD["password"]},
        )
        assert r.status_code == 200
