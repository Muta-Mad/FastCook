import pytest


@pytest.mark.asyncio
async def test_get_ingredients_empty(client):
    r = await client.get("/api/ingredients/")
    assert r.status_code == 200
    assert r.json() == []


@pytest.mark.asyncio
async def test_get_ingredients_list(client, ingredient):
    r = await client.get("/api/ingredients/")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 1
    assert data[0]["id"] == ingredient.id
    assert data[0]["name"] == ingredient.name
    assert data[0]["measurement_unit"] == ingredient.measurement_unit


@pytest.mark.asyncio
async def test_get_ingredient_by_id(client, ingredient):
    r = await client.get(f"/api/ingredients/{ingredient.id}/")
    assert r.status_code == 200
    data = r.json()
    assert data["id"] == ingredient.id
    assert data["name"] == ingredient.name


@pytest.mark.asyncio
async def test_get_ingredient_not_found(client):
    r = await client.get("/api/ingredients/99999/")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_get_ingredients_filter_by_name(client, ingredient):
    r = await client.get(f"/api/ingredients/?name={ingredient.name[:3]}")
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_ingredients_not_require_auth(client, ingredient):
    r = await client.get("/api/ingredients/")
    assert r.status_code == 200
