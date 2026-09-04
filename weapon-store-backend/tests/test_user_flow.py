import asyncio
from decimal import Decimal

from app.models.category import Category
from app.models.product import Product


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
