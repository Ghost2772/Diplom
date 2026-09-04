import asyncio
from decimal import Decimal

from sqlalchemy import select

from app.models.category import Category
from app.models.product import Product
from app.models.user import User


def register_and_login(client) -> dict[str, str]:
    register_response = client.post(
        "/auth/register",
        json={
            "email": "hunter@example.com",
            "password": "SafePassword123",
            "full_name": "Test User",
        },
    )
    assert register_response.status_code == 200

    login_response = client.post(
        "/auth/login",
        data={"username": "hunter@example.com", "password": "SafePassword123"},
    )
    assert login_response.status_code == 200

    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_registration_login_and_profile(api_client) -> None:
    client, _ = api_client
    headers = register_and_login(client)

    response = client.get("/users/me", headers=headers)

    assert response.status_code == 200
    assert response.json()["email"] == "hunter@example.com"
    assert response.json()["full_name"] == "Test User"


def test_cart_to_order_flow(api_client) -> None:
    client, session_factory = api_client

    async def add_catalog_data() -> None:
        async with session_factory() as session:
            category = Category(
                name="Оптика",
                slug="optics",
                description="Test category",
                display_order=10,
                is_active=True,
            )
            session.add(category)
            await session.flush()
            session.add(
                Product(
                    name="Demo Scope",
                    slug="demo-scope",
                    sku="TEST-OPT-1",
                    brand="Demo",
                    description="Test product",
                    price=Decimal("10000.00"),
                    stock=5,
                    category_id=category.id,
                    attributes={"Увеличение": "3x"},
                    is_active=True,
                )
            )
            await session.commit()

    asyncio.run(add_catalog_data())
    headers = register_and_login(client)

    products_response = client.get("/products")
    assert products_response.status_code == 200
    product_id = products_response.json()[0]["id"]

    add_response = client.post(
        "/cart/items",
        json={"product_id": product_id, "quantity": 2},
        headers=headers,
    )
    assert add_response.status_code == 200

    order_response = client.post("/orders/create-from-cart", headers=headers)
    assert order_response.status_code == 200
    order = order_response.json()
    assert order["order_number"].startswith("MF-")
    assert order["total_amount"] == 20000.0
    assert order["items"][0]["product_sku"] == "TEST-OPT-1"

    cart_response = client.get("/cart", headers=headers)
    assert cart_response.status_code == 200
    assert cart_response.json()["items"] == []


def test_admin_can_view_users_and_manage_orders(api_client) -> None:
    client, session_factory = api_client
    user_headers = register_and_login(client)

    async def add_product() -> None:
        async with session_factory() as session:
            category = Category(
                name="Амуниция",
                slug="admin-test-gear",
                description="Admin test category",
                display_order=10,
                is_active=True,
            )
            session.add(category)
            await session.flush()
            session.add(
                Product(
                    name="Admin Demo Product",
                    slug="admin-demo-product",
                    sku="ADMIN-TEST-1",
                    brand="Demo",
                    description="Product for admin flow",
                    price=Decimal("1500.00"),
                    stock=4,
                    category_id=category.id,
                    attributes={},
                    is_active=True,
                )
            )
            await session.commit()

    asyncio.run(add_product())

    product_id = client.get("/products").json()[0]["id"]
    client.post(
        "/cart/items",
        json={"product_id": product_id, "quantity": 1},
        headers=user_headers,
    )
    order_response = client.post("/orders/create-from-cart", headers=user_headers)
    order_id = order_response.json()["id"]

    admin_email = "admin@example.com"
    admin_password = "AdminPassword123"
    client.post(
        "/auth/register",
        json={
            "email": admin_email,
            "password": admin_password,
            "full_name": "Test Administrator",
        },
    )

    async def promote_admin() -> None:
        async with session_factory() as session:
            admin = await session.scalar(select(User).where(User.email == admin_email))
            admin.is_admin = True
            await session.commit()

    asyncio.run(promote_admin())

    admin_login = client.post(
        "/auth/login",
        data={"username": admin_email, "password": admin_password},
    )
    admin_headers = {
        "Authorization": f"Bearer {admin_login.json()['access_token']}"
    }

    forbidden_users = client.get("/users", headers=user_headers)
    assert forbidden_users.status_code == 403

    users_response = client.get("/users", headers=admin_headers)
    assert users_response.status_code == 200
    assert {user["email"] for user in users_response.json()} == {
        "hunter@example.com",
        admin_email,
    }

    orders_response = client.get("/orders", headers=admin_headers)
    assert orders_response.status_code == 200
    assert orders_response.json()[0]["id"] == order_id

    status_response = client.patch(
        f"/orders/{order_id}/status",
        json={"status": "processing"},
        headers=admin_headers,
    )
    assert status_response.status_code == 200
    assert status_response.json()["status"] == "processing"

    forbidden_delete = client.delete(f"/orders/{order_id}", headers=user_headers)
    assert forbidden_delete.status_code == 403

    delete_response = client.delete(f"/orders/{order_id}", headers=admin_headers)
    assert delete_response.status_code == 204

    missing_order = client.get(f"/orders/{order_id}", headers=admin_headers)
    assert missing_order.status_code == 404
