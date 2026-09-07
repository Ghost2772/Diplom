import asyncio
import importlib.util
from decimal import Decimal
from pathlib import Path

from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import select

from app import seed
from app.models.category import Category
from app.models.product import Product

BENELLI = next(item for item in seed.PRODUCTS if item["sku"] == "MF-SMO-0001")
PRESENTATION_FIELDS = ("short_description", "description", "image_url", "attributes")


def test_seeded_product_details_are_available_without_login(api_client, monkeypatch) -> None:
    client, session_factory = api_client
    monkeypatch.setattr(seed, "AsyncSessionLocal", session_factory)
    asyncio.run(seed.seed_demo_data())

    listed = client.get("/products", params={"search": "Benelli M3 Super 90"}).json()
    assert len(listed) == 1
    product_id = listed[0]["id"]
    response = client.get(f"/products/{product_id}")
    assert response.status_code == 200
    product = response.json()
    for field in PRESENTATION_FIELDS:
        assert product[field] == BENELLI[field]

    async def change_commercial_data() -> None:
        async with session_factory.begin() as session:
            item = await session.get(Product, product_id)
            item.price = Decimal("189990.00")
            item.stock = 1

    asyncio.run(change_commercial_data())
    asyncio.run(seed.seed_demo_data())
    updated = client.get(f"/products/{product_id}").json()
    assert Decimal(str(updated["price"])) == Decimal("189990.00")
    assert updated["stock"] == 1
    assert len(client.get("/products").json()) == len(seed.PRODUCTS)
    assert client.get("/products/999999").status_code == 404


def test_migration_updates_existing_benelli_and_preserves_other_data(api_client) -> None:
    client, session_factory = api_client
    migration_path = (
        Path(__file__).resolve().parents[1] / "alembic/versions/0002_benelli_product_details.py"
    )
    spec = importlib.util.spec_from_file_location("benelli_details_migration", migration_path)
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)

    async def create_old_catalog() -> int:
        async with session_factory.begin() as session:
            category = Category(name="Гладкоствольные ружья", slug="smoothbore-shotguns")
            session.add(category)
            await session.flush()
            item = Product(
                name="Benelli M3 Super 90",
                slug="benelli-m3-super-90",
                sku="MF-SMO-0001",
                brand="Benelli",
                category_id=category.id,
                short_description="Демонстрационная карточка гладкоствольной модели.",
                description="Прежнее демонстрационное описание",
                attributes={"Калибр": "12/76", "Тип": "Комбинированная система"},
                price=Decimal("199990.00"),
                old_price=Decimal("239990.00"),
                stock=9,
            )
            session.add(item)
            session.add(
                Product(
                    name="Другая модель",
                    slug="another-model",
                    sku="CUSTOM-1",
                    category_id=category.id,
                    description="Собственное описание",
                    attributes={"Материал": "Дерево"},
                    price=Decimal("15000.00"),
                    stock=2,
                )
            )
            await session.flush()
            return item.id

    product_id = asyncio.run(create_old_catalog())

    async def migrate_existing_catalog() -> None:
        async with session_factory.begin() as session:
            connection = await session.connection()

            def run_migration(sync_connection) -> None:
                with Operations.context(MigrationContext.configure(sync_connection)):
                    migration.upgrade()

            await connection.run_sync(run_migration)
            await connection.run_sync(run_migration)
            other = await session.scalar(select(Product).where(Product.sku == "CUSTOM-1"))
            assert other.description == "Собственное описание"
            assert other.attributes == {"Материал": "Дерево"}

    asyncio.run(migrate_existing_catalog())
    product = client.get(f"/products/{product_id}").json()
    for field in PRESENTATION_FIELDS:
        assert product[field] == BENELLI[field]
    assert Decimal(str(product["price"])) == Decimal("199990.00")
    assert Decimal(str(product["old_price"])) == Decimal("239990.00")
    assert product["stock"] == 9
    assert product["id"] == product_id
    assert len(client.get("/products").json()) == 2
