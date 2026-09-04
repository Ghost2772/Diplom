import asyncio
from decimal import Decimal

from sqlalchemy import select

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
from app.models.category import Category
from app.models.product import Product
from app.models.user import User

CATEGORIES = (
    {
        "name": "Гладкоствольные ружья",
        "slug": "smoothbore-shotguns",
        "description": "Демонстрационный раздел гладкоствольных моделей.",
        "display_order": 10,
    },
    {
        "name": "Нарезные ружья",
        "slug": "rifled-firearms",
        "description": "Демонстрационный раздел нарезных моделей.",
        "display_order": 20,
    },
    {
        "name": "Боеприпасы и амуниция",
        "slug": "ammunition-and-gear",
        "description": "Учебный каталог боеприпасов и охотничьего снаряжения.",
        "display_order": 30,
    },
    {
        "name": "Оптика",
        "slug": "optics",
        "description": "Прицелы, бинокли и аксессуары для наблюдения.",
        "display_order": 40,
    },
    {
        "name": "Тактические модули",
        "slug": "tactical-modules",
        "description": "Фонари, крепления и совместимые модули.",
        "display_order": 50,
    },
    {
        "name": "Прочие товары",
        "slug": "other-products",
        "description": "Кейсы, средства ухода и сопутствующие товары.",
        "display_order": 60,
    },
)


PRODUCTS = (
    {
        "name": "Benelli M3 Super 90",
        "slug": "benelli-m3-super-90",
        "sku": "MF-SMO-0001",
        "brand": "Benelli",
        "category_slug": "smoothbore-shotguns",
        "short_description": "Демонстрационная карточка гладкоствольной модели.",
        "description": (
            "Учебная товарная карточка для демонстрации каталога. "
            "Не является предложением о дистанционной продаже оружия."
        ),
        "price": Decimal("249990.00"),
        "old_price": None,
        "stock": 3,
        "attributes": {"Калибр": "12/76", "Тип": "Комбинированная система"},
        "is_featured": True,
        "is_regulated": True,
    },
    {
        "name": "Tikka T3x Lite",
        "slug": "tikka-t3x-lite",
        "sku": "MF-RIF-0001",
        "brand": "Tikka",
        "category_slug": "rifled-firearms",
        "short_description": "Демонстрационная карточка охотничьего карабина.",
        "description": (
            "Учебная позиция каталога с характеристиками, пригодными для "
            "сравнения и работы ИИ-консультанта."
        ),
        "price": Decimal("219990.00"),
        "old_price": Decimal("229990.00"),
        "stock": 2,
        "attributes": {"Назначение": "Охота", "Материал ложи": "Синтетика"},
        "is_featured": True,
        "is_regulated": True,
    },
    {
        "name": "Учебный комплект патронов 12/70",
        "slug": "training-ammunition-12-70",
        "sku": "MF-AMM-0001",
        "brand": "Muller's Demo",
        "category_slug": "ammunition-and-gear",
        "short_description": "Демонстрационная позиция раздела амуниции.",
        "description": "Позиция предназначена только для демонстрации интерфейса магазина.",
        "price": Decimal("2990.00"),
        "old_price": None,
        "stock": 20,
        "attributes": {"Калибр": "12/70", "Количество": "25 шт."},
        "is_featured": False,
        "is_regulated": True,
    },
    {
        "name": "Vortex Crossfire II",
        "slug": "vortex-crossfire-ii",
        "sku": "MF-OPT-0001",
        "brand": "Vortex",
        "category_slug": "optics",
        "short_description": "Оптический прицел для демонстрационного каталога.",
        "description": "Карточка показывает хранение бренда и технических характеристик.",
        "price": Decimal("32990.00"),
        "old_price": Decimal("35990.00"),
        "stock": 7,
        "attributes": {"Увеличение": "3-9x", "Диаметр объектива": "40 мм"},
        "is_featured": True,
        "is_regulated": False,
    },
    {
        "name": "Streamlight TLR-1 HL",
        "slug": "streamlight-tlr-1-hl",
        "sku": "MF-MOD-0001",
        "brand": "Streamlight",
        "category_slug": "tactical-modules",
        "short_description": "Фонарь с универсальным креплением.",
        "description": "Демонстрационная карточка тактического модуля.",
        "price": Decimal("24990.00"),
        "old_price": None,
        "stock": 8,
        "attributes": {"Световой поток": "1000 лм", "Питание": "CR123A"},
        "is_featured": False,
        "is_regulated": False,
    },
    {
        "name": "Защитный кейс Vault V100",
        "slug": "vault-v100-case",
        "sku": "MF-OTH-0001",
        "brand": "Pelican",
        "category_slug": "other-products",
        "short_description": "Компактный жесткий кейс для оборудования.",
        "description": "Сопутствующий товар демонстрационного интернет-магазина.",
        "price": Decimal("10990.00"),
        "old_price": None,
        "stock": 12,
        "attributes": {"Материал": "Полимер", "Защита": "Пыле- и влагостойкость"},
        "is_featured": False,
        "is_regulated": False,
    },
)


async def seed_demo_data() -> None:
    async with AsyncSessionLocal() as db:
        async with db.begin():
            admin = await db.scalar(select(User).where(User.email == settings.DEMO_ADMIN_EMAIL))
            if admin is None:
                db.add(
                    User(
                        email=settings.DEMO_ADMIN_EMAIL,
                        hashed_password=hash_password(settings.DEMO_ADMIN_PASSWORD),
                        full_name="Demo Administrator",
                        is_active=True,
                        is_admin=True,
                    )
                )
            else:
                admin.is_active = True
                admin.is_admin = True

            category_by_slug: dict[str, Category] = {}
            for category_data in CATEGORIES:
                category = await db.scalar(
                    select(Category).where(Category.slug == category_data["slug"])
                )
                if category is None:
                    category = Category(**category_data)
                    db.add(category)
                category_by_slug[category_data["slug"]] = category

            await db.flush()

            for product_data in PRODUCTS:
                existing_product = await db.scalar(
                    select(Product).where(Product.sku == product_data["sku"])
                )
                if existing_product is not None:
                    continue

                category_slug = product_data["category_slug"]
                product_fields = {
                    key: value for key, value in product_data.items() if key != "category_slug"
                }
                db.add(
                    Product(
                        **product_fields,
                        category_id=category_by_slug[category_slug].id,
                        is_active=True,
                    )
                )

    print(f"Demo data is ready. Admin account: {settings.DEMO_ADMIN_EMAIL}")


if __name__ == "__main__":
    asyncio.run(seed_demo_data())
