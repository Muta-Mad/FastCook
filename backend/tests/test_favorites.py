import pytest


@pytest.mark.asyncio
async def test_add_to_favorites_success(client, auth_headers, recipe):
    r = await client.post(f"/api/recipes/{recipe['id']}/favorite/", headers=auth_headers)
    assert r.status_code == 201
    data = r.json()
    assert data["id"] == recipe["id"]
    assert data["name"] == recipe["name"]
    assert "cooking_time" in data


@pytest.mark.asyncio
async def test_add_to_favorites_duplicate(client, auth_headers, recipe):
    await client.post(f"/api/recipes/{recipe['id']}/favorite/", headers=auth_headers)
    r = await client.post(f"/api/recipes/{recipe['id']}/favorite/", headers=auth_headers)
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_add_to_favorites_unauthenticated(client, recipe):
    r = await client.post(f"/api/recipes/{recipe['id']}/favorite/")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_add_to_favorites_recipe_not_found(client, auth_headers):
    r = await client.post("/api/recipes/99999/favorite/", headers=auth_headers)
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_remove_from_favorites_success(client, auth_headers, recipe):
    await client.post(f"/api/recipes/{recipe['id']}/favorite/", headers=auth_headers)
    r = await client.delete(f"/api/recipes/{recipe['id']}/favorite/", headers=auth_headers)
    assert r.status_code == 204


@pytest.mark.asyncio
async def test_remove_from_favorites_not_in_favorites(client, auth_headers, recipe):
    r = await client.delete(f"/api/recipes/{recipe['id']}/favorite/", headers=auth_headers)
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_remove_from_favorites_unauthenticated(client, recipe):
    r = await client.delete(f"/api/recipes/{recipe['id']}/favorite/")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_remove_from_favorites_recipe_not_found(client, auth_headers):
    r = await client.delete("/api/recipes/99999/favorite/", headers=auth_headers)
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_favorite_reflected_in_recipe_flags(client, auth_headers, recipe):
    await client.post(f"/api/recipes/{recipe['id']}/favorite/", headers=auth_headers)
    r = await client.get(f"/api/recipes/{recipe['id']}/", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["is_favorited"] is True


@pytest.mark.asyncio
async def test_favorite_removed_from_recipe_flags(client, auth_headers, recipe):
    await client.post(f"/api/recipes/{recipe['id']}/favorite/", headers=auth_headers)
    await client.delete(f"/api/recipes/{recipe['id']}/favorite/", headers=auth_headers)
    r = await client.get(f"/api/recipes/{recipe['id']}/", headers=auth_headers)
    assert r.json()["is_favorited"] is False
