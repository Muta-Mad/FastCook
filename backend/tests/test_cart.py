import pytest


@pytest.mark.asyncio
async def test_add_to_cart_success(client, auth_headers, recipe):
    r = await client.post(f"/api/recipes/{recipe['id']}/shopping_cart/", headers=auth_headers)
    assert r.status_code == 201
    data = r.json()
    assert data["id"] == recipe["id"]
    assert data["name"] == recipe["name"]
    assert "cooking_time" in data


@pytest.mark.asyncio
async def test_add_to_cart_duplicate(client, auth_headers, recipe):
    await client.post(f"/api/recipes/{recipe['id']}/shopping_cart/", headers=auth_headers)
    r = await client.post(f"/api/recipes/{recipe['id']}/shopping_cart/", headers=auth_headers)
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_add_to_cart_unauthenticated(client, recipe):
    r = await client.post(f"/api/recipes/{recipe['id']}/shopping_cart/")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_add_to_cart_recipe_not_found(client, auth_headers):
    r = await client.post("/api/recipes/99999/shopping_cart/", headers=auth_headers)
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_remove_from_cart_success(client, auth_headers, recipe):
    await client.post(f"/api/recipes/{recipe['id']}/shopping_cart/", headers=auth_headers)
    r = await client.delete(f"/api/recipes/{recipe['id']}/shopping_cart/", headers=auth_headers)
    assert r.status_code == 204


@pytest.mark.asyncio
async def test_remove_from_cart_not_in_cart(client, auth_headers, recipe):
    r = await client.delete(f"/api/recipes/{recipe['id']}/shopping_cart/", headers=auth_headers)
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_remove_from_cart_unauthenticated(client, recipe):
    r = await client.delete(f"/api/recipes/{recipe['id']}/shopping_cart/")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_remove_from_cart_recipe_not_found(client, auth_headers):
    r = await client.delete("/api/recipes/99999/shopping_cart/", headers=auth_headers)
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_cart_reflected_in_recipe_flags(client, auth_headers, recipe):
    await client.post(f"/api/recipes/{recipe['id']}/shopping_cart/", headers=auth_headers)
    r = await client.get(f"/api/recipes/{recipe['id']}/", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["is_in_shopping_cart"] is True


@pytest.mark.asyncio
async def test_cart_removed_from_recipe_flags(client, auth_headers, recipe):
    await client.post(f"/api/recipes/{recipe['id']}/shopping_cart/", headers=auth_headers)
    await client.delete(f"/api/recipes/{recipe['id']}/shopping_cart/", headers=auth_headers)
    r = await client.get(f"/api/recipes/{recipe['id']}/", headers=auth_headers)
    assert r.json()["is_in_shopping_cart"] is False
