import pytest


@pytest.mark.asyncio
async def test_get_tags_empty(client):
    r = await client.get("/api/tags/")
    assert r.status_code == 200
    assert r.json() == []


@pytest.mark.asyncio
async def test_get_tags_list(client, tag):
    r = await client.get("/api/tags/")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 1
    assert data[0]["id"] == tag.id
    assert data[0]["name"] == tag.name
    assert data[0]["slug"] == tag.slug


@pytest.mark.asyncio
async def test_get_tag_by_id(client, tag):
    r = await client.get(f"/api/tags/{tag.id}/")
    assert r.status_code == 200
    data = r.json()
    assert data["id"] == tag.id
    assert data["name"] == tag.name
    assert data["slug"] == tag.slug


@pytest.mark.asyncio
async def test_get_tag_not_found(client):
    r = await client.get("/api/tags/99999/")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_tags_not_require_auth(client, tag):
    r = await client.get("/api/tags/")
    assert r.status_code == 200
