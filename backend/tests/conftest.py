import os

# Must be set before `main` is imported so the rate-limiter decorator picks it up.
os.environ.setdefault("LOGIN_RATE_LIMIT", "1000/minute")

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from main import app
from api.core.basemodel import Base
from api.core.database import get_db
from api.recipes.models import Ingredient, Tag

TEST_IMAGE = (
    "data:image/png;base64,"
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAC0lEQVQI12NgAAIABQ"
    "AABjkB6QAAAABJRU5ErkJggg=="
)

USER_PAYLOAD = {
    "email": "user@test.com",
    "username": "testuser",
    "first_name": "Test",
    "last_name": "User",
    "password": "securepass123",
}

USER2_PAYLOAD = {
    "email": "user2@test.com",
    "username": "testuser2",
    "first_name": "Test2",
    "last_name": "User2",
    "password": "securepass456",
}


@pytest_asyncio.fixture
async def db_engine():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )

    @event.listens_for(engine.sync_engine, "connect")
    def set_sqlite_pragma(dbapi_conn, _):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def client(db_engine):
    session_factory = async_sessionmaker(
        db_engine, expire_on_commit=False, class_=AsyncSession
    )

    async def override_get_db():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


async def _db_insert(db_engine, *objs):
    factory = async_sessionmaker(db_engine, expire_on_commit=False)
    async with factory() as session:
        for obj in objs:
            session.add(obj)
        await session.commit()
        for obj in objs:
            await session.refresh(obj)


@pytest_asyncio.fixture
async def tag(db_engine):
    t = Tag(name="Завтрак", slug="breakfast")
    await _db_insert(db_engine, t)
    return t


@pytest_asyncio.fixture
async def ingredient(db_engine):
    i = Ingredient(name="Яйцо", measurement_unit="шт")
    await _db_insert(db_engine, i)
    return i


@pytest_asyncio.fixture
async def registered_user(client):
    r = await client.post("/api/users/", json=USER_PAYLOAD)
    assert r.status_code == 201, r.text
    return r.json()


@pytest_asyncio.fixture
async def token(client, registered_user):
    r = await client.post(
        "/api/auth/token/login/",
        json={"email": USER_PAYLOAD["email"], "password": USER_PAYLOAD["password"]},
    )
    assert r.status_code == 200, r.text
    return r.json()["auth_token"]


@pytest_asyncio.fixture
async def auth_headers(token):
    return {"Authorization": f"Token {token}"}


@pytest_asyncio.fixture
async def registered_user2(client):
    r = await client.post("/api/users/", json=USER2_PAYLOAD)
    assert r.status_code == 201, r.text
    return r.json()


@pytest_asyncio.fixture
async def token2(client, registered_user2):
    r = await client.post(
        "/api/auth/token/login/",
        json={"email": USER2_PAYLOAD["email"], "password": USER2_PAYLOAD["password"]},
    )
    assert r.status_code == 200, r.text
    return r.json()["auth_token"]


@pytest_asyncio.fixture
async def auth_headers2(token2):
    return {"Authorization": f"Token {token2}"}


@pytest_asyncio.fixture
async def recipe_payload(tag, ingredient):
    return {
        "name": "Яичница",
        "text": "Разбить яйца на сковороду и пожарить",
        "cooking_time": 5,
        "image": TEST_IMAGE,
        "tags": [tag.id],
        "ingredients": [{"id": ingredient.id, "amount": 2}],
    }


@pytest_asyncio.fixture
async def recipe(client, auth_headers, recipe_payload):
    r = await client.post("/api/recipes/", json=recipe_payload, headers=auth_headers)
    assert r.status_code == 201, r.text
    return r.json()
