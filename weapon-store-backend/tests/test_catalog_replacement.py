import asyncio
import importlib.util
from decimal import Decimal
from pathlib import Path

from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import select

from app import seed
from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.category import Category
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product
from app.models.user import User

NEW_SKUS = {"MF-RIF-0002", "MF-AMM-0002", "MF-AMM-0003"}


async def apply_catalog_migration(session_factory) -> None:
    path = (
        Path(__file__).resolve().parents[1]
        / "alembic/versions/0003_saiga_and_ammunition.py"
    )
    spec = importlib.util.spec_from_file_location("catalog_replacement_migration", path)
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)

    async with session_factory.begin() as session:
        connection = await session.connection()

        def run_migration(sync_connection) -> None:
            with Operations.context(MigrationContext.configure(sync_connection)):
                migration.upgrade()

        await connection.run_sync(run_migration)


def test_fresh_catalog_has_saiga_and_two_ammunition_detail_pages(api_client, monkeypatch):
    client, session_factory = api_client
    monkeypatch.setattr(seed, "AsyncSessionLocal", session_factory)
    asyncio.run(apply_catalog_migration(session_factory))
    asyncio.run(seed.seed_demo_data())

    categories = {item["slug"]: item["id"] for item in client.get("/categories").json()}
    rifles = client.get("/products", params={
        "category_id": categories["rifled-firearms"], "is_active": True,
    }).json()
    ammunition = client.get("/products", params={
        "category_id": categories["ammunition-and-gear"], "is_active": True,
    }).json()
    assert [item["name"] for item in rifles] == ["Сайга 5,45×39"]
    assert {item["name"] for item in ammunition} == {
        "Bornaghi Magnum 12/76", "БПЗ 5,45×39 FMJ",
    }
    assert {item["sku"] for item in rifles + ammunition} == NEW_SKUS

    for listed in rifles + ammunition:
        response = client.get(f"/products/{listed['id']}")
        assert response.status_code == 200
        detail = response.json()
        assert detail["description"] and detail["short_description"]
        assert len(detail["attributes"]) >= 6
        assert detail["image_url"].startswith("/images/products/")
        asset = (
            Path(__file__).resolve().parents[2] / "weapon-store-frontend/public"
            / detail["image_url"].lstrip("/")
        )
        assert asset.is_file()

    by_sku = {item["sku"]: item for item in rifles + ammunition}
    assert by_sku["MF-RIF-0002"]["attributes"]["Исполнение"] == "030"
    assert by_sku["MF-AMM-0002"]["attributes"]["Количество в упаковке"] == "10 шт"
    assert by_sku["MF-AMM-0002"]["attributes"]["Калибр"] == "12/76"
    assert by_sku["MF-AMM-0003"]["attributes"]["Количество в упаковке"] == "30 шт"
    assert by_sku["MF-AMM-0003"]["attributes"]["Масса пули"] == "4,2 г"


def test_replacement_preserves_order_history_and_unrelated_cart_items(api_client, monkeypatch):
    client, session_factory = api_client
    monkeypatch.setattr(seed, "AsyncSessionLocal", session_factory)

    async def create_legacy_data() -> dict:
        async with session_factory.begin() as session:
            rifle_category = Category(name="Нарезные ружья", slug="rifled-firearms")
            ammo_category = Category(name="Боеприпасы и амуниция", slug="ammunition-and-gear")
            user = User(email="history@example.com", hashed_password="unused-in-this-test")
            session.add_all([rifle_category, ammo_category, user])
            await session.flush()
            tikka = Product(
                name="Tikka T3x Lite", slug="tikka-t3x-lite", sku="MF-RIF-0001",
                category_id=rifle_category.id, price=Decimal("219990.00"), stock=2,
            )
            ammo = Product(
                name="Учебный комплект патронов 12/70", slug="training-ammunition-12-70",
                sku="MF-AMM-0001", category_id=ammo_category.id,
                price=Decimal("2990.00"), stock=20,
            )
            keep = Product(
                name="Собственный товар", slug="keep-product", sku="CUSTOM-KEEP",
                category_id=ammo_category.id, price=Decimal("990.00"), stock=17,
                description="Собственное описание", attributes={"Цвет": "Чёрный"},
            )
            cart = Cart(user_id=user.id)
            order = Order(user_id=user.id, total_amount=Decimal("222980.00"))
            session.add_all([tikka, ammo, keep, cart, order])
            await session.flush()
            for product in [tikka, ammo, keep]:
                session.add(CartItem(cart_id=cart.id, product_id=product.id, quantity=1))
            for product in [tikka, ammo]:
                session.add(OrderItem(
                    order_id=order.id, product_id=product.id, product_name=product.name,
                    product_sku=product.sku, price=product.price,
                    quantity=1, total_price=product.price,
                ))
            return {"old_ids": {tikka.id, ammo.id}, "keep_id": keep.id, "order_id": order.id}

    original = asyncio.run(create_legacy_data())
    asyncio.run(apply_catalog_migration(session_factory))
    for product_id in original["old_ids"]:
        assert client.get(f"/products/{product_id}").status_code == 404

    listed = client.get("/products").json()
    new_products = {item["sku"]: item for item in listed if item["sku"] in NEW_SKUS}
    assert set(new_products) == NEW_SKUS
    assert not original["old_ids"] & {item["id"] for item in new_products.values()}
    for source in seed.PRODUCTS:
        if source["sku"] not in NEW_SKUS:
            continue
        for field in ("name", "slug", "brand", "short_description", "description",
                      "image_url", "attributes"):
            assert new_products[source["sku"]][field] == source[field]

    async def customize_new_product() -> None:
        async with session_factory.begin() as session:
            product = await session.scalar(select(Product).where(Product.sku == "MF-RIF-0002"))
            product.price = Decimal("65000.00")
            product.stock = 7

    asyncio.run(customize_new_product())
    asyncio.run(apply_catalog_migration(session_factory))
    asyncio.run(seed.seed_demo_data())

    async def verify_preserved_data() -> None:
        async with session_factory() as session:
            items = (await session.scalars(
                select(OrderItem).where(OrderItem.order_id == original["order_id"])
            )).all()
            assert {item.product_name for item in items} == {
                "Tikka T3x Lite", "Учебный комплект патронов 12/70",
            }
            assert all(item.product_id is None for item in items)
            assert sum(item.total_price for item in items) == Decimal("222980.00")
            order = await session.get(Order, original["order_id"])
            assert order.total_amount == Decimal("222980.00")
            cart_items = (await session.scalars(select(CartItem))).all()
            assert [(item.product_id, item.quantity) for item in cart_items] == [
                (original["keep_id"], 1),
            ]
            keep = await session.get(Product, original["keep_id"])
            assert keep.description == "Собственное описание"
            assert keep.attributes == {"Цвет": "Чёрный"}
            assert keep.price == Decimal("990.00") and keep.stock == 17

    asyncio.run(verify_preserved_data())
    after_restart = client.get("/products").json()
    assert len(after_restart) == len(seed.PRODUCTS) + 1
    assert not {"MF-RIF-0001", "MF-AMM-0001"} & {item["sku"] for item in after_restart}
    saiga = next(item for item in after_restart if item["sku"] == "MF-RIF-0002")
    assert Decimal(str(saiga["price"])) == Decimal("65000.00")
    assert saiga["stock"] == 7
