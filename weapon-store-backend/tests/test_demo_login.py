import asyncio
import importlib.util
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

import pytest
from alembic.migration import MigrationContext
from alembic.operations import Operations
from jose import jwt
from sqlalchemy import func, select

from app.core.config import settings
from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.category import Category
from app.models.chat_message import ChatMessage
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product
from app.models.user import User


@pytest.fixture
def demo_client(api_client, monkeypatch):
    client, sessions = api_client
    monkeypatch.setattr(settings, "DEMO_LOGIN_ENABLED", True)
    monkeypatch.setattr(settings, "DEMO_SESSION_MINUTES", 60)
    monkeypatch.setattr(settings, "DEMO_MAX_SESSIONS", 100)

    async def prepare_catalog():
        async with sessions() as db:
            category = Category(name="Демо-категория", slug="demo-category")
            hidden = Category(name="Скрытая категория", slug="hidden", is_active=False)
            db.add_all([category, hidden])
            await db.flush()
            for index, (active, stock, category_id) in enumerate(
                (
                    (False, 5, category.id),
                    (True, 0, category.id),
                    (True, 5, hidden.id),
                    (True, 3, category.id),
                    (True, 2, category.id),
                )
            ):
                db.add(
                    Product(
                        name=f"Товар {index}",
                        sku=f"DEMO-TEST-{index}",
                        slug=f"demo-test-{index}",
                        category_id=category_id,
                        price=Decimal("1250.50"),
                        stock=stock,
                        is_active=active,
                    )
                )
            await db.commit()

    asyncio.run(prepare_catalog())
    return client, sessions


def start_demo(client):
    response = client.post("/auth/demo", json={"is_admin": True, "email": "admin@example.com"})
    assert response.status_code == 200, response.text
    assert response.headers["cache-control"] == "no-store"
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_demo_has_profile_cart_orders_and_can_checkout(demo_client):
    client, _ = demo_client
    assert client.get("/auth/demo").json() == {"enabled": True, "session_minutes": 60}
    headers = start_demo(client)
    profile = client.get("/users/me", headers=headers).json()
    assert profile["is_demo"] and not profile["is_admin"]
    assert profile["full_name"] == "Демо-посетитель"
    assert profile["email"].endswith("@demo.mullers.local")
    expiry = datetime.fromisoformat(profile["demo_expires_at"]).replace(tzinfo=UTC)
    assert 3500 < (expiry - datetime.now(UTC)).total_seconds() <= 3600
    token = headers["Authorization"].removeprefix("Bearer ")
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert payload["exp"] == int(expiry.timestamp())

    cart = client.get("/cart", headers=headers).json()
    assert len(cart["items"]) == 1 and cart["total_amount"] == 1250.5
    assert cart["items"][0]["product_name"] == "Товар 3"
    orders = client.get("/orders/my", headers=headers).json()
    assert len(orders) == 2
    assert {order["status"] for order in orders} == {"completed", "confirmed"}
    assert all(order["total_amount"] == order["items"][0]["total_price"] for order in orders)

    product_id = cart["items"][0]["product_id"]
    created = client.post("/orders/create-from-cart", headers=headers)
    assert created.status_code == 200
    assert created.json()["status"] == "created"
    assert client.get("/cart", headers=headers).json()["items"] == []
    assert len(client.get("/orders/my", headers=headers).json()) == 3
    # Demo visitors exercise checkout without consuming the shared sample catalog.
    assert client.get(f"/products/{product_id}").json()["stock"] == 3


def test_demo_sessions_are_private_and_never_grant_admin_access(demo_client):
    client, sessions = demo_client
    first, second = start_demo(client), start_demo(client)
    first_profile = client.get("/users/me", headers=first).json()
    second_profile = client.get("/users/me", headers=second).json()
    assert first_profile["id"] != second_profile["id"]
    first_order = client.get("/orders/my", headers=first).json()[0]
    assert client.get(f"/orders/{first_order['id']}", headers=second).status_code == 403
    first_item = client.get("/cart", headers=first).json()["items"][0]
    assert client.delete(f"/cart/items/{first_item['id']}", headers=second).status_code == 404
    assert client.delete("/cart", headers=first).status_code == 200
    assert len(client.get("/cart", headers=second).json()["items"]) == 1

    async def add_first_history():
        async with sessions() as db:
            db.add(ChatMessage(user_id=first_profile["id"], role="user", content="Первый диалог"))
            await db.commit()

    asyncio.run(add_first_history())
    assert client.get("/ai/history", headers=second).json() == []
    assert client.delete("/ai/history", headers=second).status_code == 204
    assert len(client.get("/ai/history", headers=first).json()) == 1
    assert client.get("/users", headers=first).status_code == 403
    assert client.get("/orders", headers=first).status_code == 403
    assert (
        client.patch(
            f"/orders/{first_order['id']}/status", headers=first, json={"status": "completed"}
        ).status_code
        == 403
    )
    assert client.delete(f"/orders/{first_order['id']}", headers=first).status_code == 403
    assert (
        client.post(
            "/products/images", headers=first, files={"file": ("demo.png", b"invalid", "image/png")}
        ).status_code
        == 403
    )
    # No shared password or magic login path can authenticate a temporary account.
    assert (
        client.post(
            "/auth/login", data={"username": first_profile["email"], "password": "!"}
        ).status_code
        == 401
    )


def test_demo_expiry_cleanup_preserves_regular_and_other_active_accounts(demo_client):
    client, sessions = demo_client
    regular = client.post(
        "/auth/register",
        json={
            "email": "real@example.com",
            "password": "RegularPassword123",
            "is_admin": True,
            "demo_expires_at": "2000-01-01T00:00:00Z",
        },
    )
    assert regular.status_code == 200
    assert not regular.json()["is_demo"] and not regular.json()["is_admin"]
    regular_token = client.post(
        "/auth/login", data={"username": "real@example.com", "password": "RegularPassword123"}
    ).json()
    regular_headers = {"Authorization": f"Bearer {regular_token['access_token']}"}
    first, active = start_demo(client), start_demo(client)
    expired_id = client.get("/users/me", headers=first).json()["id"]
    active_id = client.get("/users/me", headers=active).json()["id"]
    product_id = client.get("/cart", headers=active).json()["items"][0]["product_id"]
    client.post(
        "/cart/items", headers=regular_headers, json={"product_id": product_id, "quantity": 1}
    )
    regular_order = client.post("/orders/create-from-cart", headers=regular_headers).json()

    async def expire_first():
        async with sessions() as db:
            user = await db.get(User, expired_id)
            user.demo_expires_at = datetime.now(UTC) - timedelta(minutes=6)
            db.add(ChatMessage(user_id=expired_id, role="user", content="Удалить вместе с демо"))
            await db.commit()

    asyncio.run(expire_first())
    # The DB deadline also revokes a token whose signature/exp are still valid.
    assert client.get("/users/me", headers=first).status_code == 401
    start_demo(client)
    assert client.get("/users/me", headers=active).json()["id"] == active_id
    assert client.get("/users/me", headers=regular_headers).status_code == 200
    assert client.get("/orders/my", headers=regular_headers).json()[0]["id"] == regular_order["id"]

    async def check_deleted():
        async with sessions() as db:
            assert await db.get(User, expired_id) is None
            assert await db.scalar(select(func.count()).select_from(ChatMessage)) == 0
            assert await db.scalar(select(func.count()).select_from(Order)) == 5
            assert await db.scalar(select(func.count()).select_from(OrderItem)) == 5
            assert await db.scalar(select(func.count()).select_from(Cart)) == 3
            assert await db.scalar(select(func.count()).select_from(CartItem)) == 2
            assert await db.scalar(select(func.count()).select_from(Product)) == 5

    asyncio.run(check_deleted())


def test_demo_is_hidden_from_admin_lists(demo_client):
    client, sessions = demo_client
    start_demo(client)
    registration = client.post(
        "/auth/register",
        json={
            "email": "owner@example.com",
            "password": "OwnerPassword123",
        },
    ).json()

    async def promote_owner():
        async with sessions() as db:
            owner = await db.get(User, registration["id"])
            owner.is_admin = True
            await db.commit()

    asyncio.run(promote_owner())
    token = client.post(
        "/auth/login", data={"username": "owner@example.com", "password": "OwnerPassword123"}
    ).json()
    headers = {"Authorization": f"Bearer {token['access_token']}"}
    users = client.get("/users", headers=headers).json()
    assert len(users) == 1 and users[0]["email"] == "owner@example.com"
    assert client.get("/orders", headers=headers).json() == []


def test_disabling_demo_revokes_existing_demo_and_prevents_creation(demo_client, monkeypatch):
    client, _ = demo_client
    headers = start_demo(client)
    monkeypatch.setattr(settings, "DEMO_LOGIN_ENABLED", False)
    assert client.get("/auth/demo").json()["enabled"] is False
    assert client.post("/auth/demo").status_code == 404
    assert client.get("/users/me", headers=headers).status_code == 401


def test_demo_capacity_is_limited_without_disturbing_existing_session(demo_client, monkeypatch):
    client, _ = demo_client
    monkeypatch.setattr(settings, "DEMO_MAX_SESSIONS", 1)
    headers = start_demo(client)
    response = client.post("/auth/demo")
    assert response.status_code == 429
    assert response.headers["retry-after"] == "300"
    assert client.get("/users/me", headers=headers).status_code == 200
    assert len(client.get("/orders/my", headers=headers).json()) == 2


def test_empty_catalog_does_not_leave_partial_demo_accounts(api_client, monkeypatch):
    client, sessions = api_client
    monkeypatch.setattr(settings, "DEMO_LOGIN_ENABLED", True)
    assert client.post("/auth/demo").status_code == 503

    async def check_empty():
        async with sessions() as db:
            for model in (User, Cart, Order, OrderItem):
                assert await db.scalar(select(func.count()).select_from(model)) == 0

    asyncio.run(check_empty())


def test_demo_migration_roundtrip_preserves_regular_accounts_and_orders(demo_client):
    client, sessions = demo_client
    demo_headers = start_demo(client)
    client.post(
        "/auth/register",
        json={
            "email": "migration@example.com",
            "password": "MigrationPassword123",
        },
    )
    token = client.post(
        "/auth/login",
        data={
            "username": "migration@example.com",
            "password": "MigrationPassword123",
        },
    ).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    product_id = client.get("/cart", headers=demo_headers).json()["items"][0]["product_id"]
    client.post("/cart/items", json={"product_id": product_id, "quantity": 1}, headers=headers)
    order = client.post("/orders/create-from-cart", headers=headers).json()

    async def migrate():
        path = Path(__file__).resolve().parents[1] / "alembic/versions/0004_demo_sessions.py"
        spec = importlib.util.spec_from_file_location("demo_migration", path)
        migration = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(migration)
        async with sessions.begin() as db:
            connection = await db.connection()

            def roundtrip(sync_connection):
                sync_connection.exec_driver_sql("PRAGMA foreign_keys=ON")
                assert sync_connection.exec_driver_sql("PRAGMA foreign_keys").scalar() == 1
                with Operations.context(MigrationContext.configure(sync_connection)):
                    migration.downgrade()
                    migration.upgrade()

            await connection.run_sync(roundtrip)

    asyncio.run(migrate())
    assert client.get("/users/me", headers=demo_headers).status_code == 401
    assert client.get("/users/me", headers=headers).json()["is_demo"] is False
    assert client.get("/orders/my", headers=headers).json()[0]["id"] == order["id"]
    assert client.get(f"/products/{product_id}").status_code == 200
    # The re-applied migration supports creating new demos again.
    start_demo(client)
