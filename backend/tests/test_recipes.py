import pytest

from tests.conftest import TEST_IMAGE


@pytest.mark.asyncio
async def test_create_recipe_success(client, auth_headers, recipe_payload):
    r = await client.post("/api/recipes/", json=recipe_payload, headers=auth_headers)
    assert r.status_code == 201
    data = r.json()
    assert data["name"] == recipe_payload["name"]
    assert data["text"] == recipe_payload["text"]
    assert data["cooking_time"] == recipe_payload["cooking_time"]
    assert len(data["tags"]) == 1
    assert len(data["ingredients"]) == 1
    assert data["is_favorited"] is False
    assert data["is_in_shopping_cart"] is False
    assert "author" in data


@pytest.mark.asyncio
async def test_create_recipe_unauthenticated(client, recipe_payload):
    r = await client.post("/api/recipes/", json=recipe_payload)
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_create_recipe_invalid_ingredient(client, auth_headers, recipe_payload):
    payload = {**recipe_payload, "ingredients": [{"id": 99999, "amount": 1}]}
    r = await client.post("/api/recipes/", json=payload, headers=auth_headers)
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_create_recipe_invalid_tag(client, auth_headers, recipe_payload):
    payload = {**recipe_payload, "tags": [99999]}
    r = await client.post("/api/recipes/", json=payload, headers=auth_headers)
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_create_recipe_zero_cooking_time(client, auth_headers, recipe_payload):
    payload = {**recipe_payload, "cooking_time": 0}
    r = await client.post("/api/recipes/", json=payload, headers=auth_headers)
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_create_recipe_zero_ingredient_amount(client, auth_headers, recipe_payload):
    payload = {
        **recipe_payload,
        "ingredients": [{"id": recipe_payload["ingredients"][0]["id"], "amount": 0}],
    }
    r = await client.post("/api/recipes/", json=payload, headers=auth_headers)
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_create_recipe_missing_ingredients(client, auth_headers, recipe_payload):
    payload = {k: v for k, v in recipe_payload.items() if k != "ingredients"}
    r = await client.post("/api/recipes/", json=payload, headers=auth_headers)
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_get_recipes_list(client, recipe):
    r = await client.get("/api/recipes/")
    assert r.status_code == 200
    data = r.json()
    assert "count" in data
    assert "results" in data
    assert data["count"] >= 1
    assert data["results"][0]["id"] == recipe["id"]


@pytest.mark.asyncio
async def test_get_recipes_list_unauthenticated(client, recipe):
    r = await client.get("/api/recipes/")
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_get_recipes_pagination(client, auth_headers, recipe_payload, recipe):
    await client.post("/api/recipes/", json={**recipe_payload, "name": "Второй рецепт"}, headers=auth_headers)
    r = await client.get("/api/recipes/?page=1&limit=1")
    assert r.status_code == 200
    data = r.json()
    assert len(data["results"]) == 1
    assert data["count"] == 2
    assert data["next"] is not None


@pytest.mark.asyncio
async def test_get_recipe_by_id(client, recipe):
    r = await client.get(f"/api/recipes/{recipe['id']}/")
    assert r.status_code == 200
    data = r.json()
    assert data["id"] == recipe["id"]
    assert data["name"] == recipe["name"]


@pytest.mark.asyncio
async def test_get_recipe_not_found(client):
    r = await client.get("/api/recipes/99999/")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_get_recipe_flags_when_authenticated(client, auth_headers, recipe):
    r = await client.get(f"/api/recipes/{recipe['id']}/", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert "is_favorited" in data
    assert "is_in_shopping_cart" in data


@pytest.mark.asyncio
async def test_update_recipe_success(client, auth_headers, recipe):
    r = await client.patch(
        f"/api/recipes/{recipe['id']}/",
        json={"name": "Обновлённое название"},
        headers=auth_headers,
    )
    assert r.status_code == 200
    assert r.json()["name"] == "Обновлённое название"


@pytest.mark.asyncio
async def test_update_recipe_partial(client, auth_headers, recipe):
    r = await client.patch(
        f"/api/recipes/{recipe['id']}/",
        json={"cooking_time": 15},
        headers=auth_headers,
    )
    assert r.status_code == 200
    assert r.json()["cooking_time"] == 15
    assert r.json()["name"] == recipe["name"]


@pytest.mark.asyncio
async def test_update_recipe_not_owner(client, auth_headers2, recipe, registered_user2):
    r = await client.patch(
        f"/api/recipes/{recipe['id']}/",
        json={"name": "Попытка изменить"},
        headers=auth_headers2,
    )
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_update_recipe_unauthenticated(client, recipe):
    r = await client.patch(
        f"/api/recipes/{recipe['id']}/",
        json={"name": "Попытка изменить"},
    )
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_update_recipe_not_found(client, auth_headers):
    r = await client.patch(
        "/api/recipes/99999/",
        json={"name": "Не существует"},
        headers=auth_headers,
    )
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_delete_recipe_success(client, auth_headers, recipe):
    r = await client.delete(f"/api/recipes/{recipe['id']}/", headers=auth_headers)
    assert r.status_code == 204
    r2 = await client.get(f"/api/recipes/{recipe['id']}/")
    assert r2.status_code == 404


@pytest.mark.asyncio
async def test_delete_recipe_not_owner(client, auth_headers2, recipe, registered_user2):
    r = await client.delete(f"/api/recipes/{recipe['id']}/", headers=auth_headers2)
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_delete_recipe_unauthenticated(client, recipe):
    r = await client.delete(f"/api/recipes/{recipe['id']}/")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_delete_recipe_not_found(client, auth_headers):
    r = await client.delete("/api/recipes/99999/", headers=auth_headers)
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_filter_recipes_by_author(client, auth_headers, recipe, registered_user):
    author_id = registered_user["id"]
    r = await client.get(f"/api/recipes/?author={author_id}")
    assert r.status_code == 200
    data = r.json()
    assert data["count"] >= 1
    for item in data["results"]:
        assert item["author"]["id"] == author_id


@pytest.mark.asyncio
async def test_filter_recipes_by_tags(client, recipe, tag):
    r = await client.get(f"/api/recipes/?tags={tag.slug}")
    assert r.status_code == 200
    data = r.json()
    assert data["count"] >= 1


@pytest.mark.asyncio
async def test_filter_recipes_by_unknown_tag(client, recipe):
    r = await client.get("/api/recipes/?tags=nonexistent-slug")
    assert r.status_code == 200
    assert r.json()["count"] == 0


@pytest.mark.asyncio
async def test_filter_favorited_unauthenticated(client, recipe):
    # Without auth, is_favorited filter is ignored — all recipes are returned
    r = await client.get("/api/recipes/?is_favorited=true")
    assert r.status_code == 200
    assert r.json()["count"] >= 1


@pytest.mark.asyncio
async def test_filter_favorited_authenticated(client, auth_headers, recipe):
    await client.post(f"/api/recipes/{recipe['id']}/favorite/", headers=auth_headers)
    r = await client.get("/api/recipes/?is_favorited=true", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["count"] == 1


@pytest.mark.asyncio
async def test_filter_in_shopping_cart(client, auth_headers, recipe):
    await client.post(f"/api/recipes/{recipe['id']}/shopping_cart/", headers=auth_headers)
    r = await client.get("/api/recipes/?is_in_shopping_cart=true", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["count"] == 1


@pytest.mark.asyncio
async def test_get_short_link(client, recipe):
    r = await client.get(f"/api/recipes/{recipe['id']}/get-link/")
    assert r.status_code == 200
    data = r.json()
    assert "short-link" in data
    assert str(recipe["id"]) in data["short-link"]


@pytest.mark.asyncio
async def test_get_short_link_not_found(client):
    r = await client.get("/api/recipes/99999/get-link/")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_download_shopping_cart_empty(client, auth_headers):
    r = await client.get("/api/recipes/download_shopping_cart/", headers=auth_headers)
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/plain")


@pytest.mark.asyncio
async def test_download_shopping_cart_with_items(client, auth_headers, recipe):
    await client.post(f"/api/recipes/{recipe['id']}/shopping_cart/", headers=auth_headers)
    r = await client.get("/api/recipes/download_shopping_cart/", headers=auth_headers)
    assert r.status_code == 200
    assert "Яйцо" in r.text


@pytest.mark.asyncio
async def test_download_shopping_cart_unauthenticated(client):
    r = await client.get("/api/recipes/download_shopping_cart/")
    assert r.status_code == 401
