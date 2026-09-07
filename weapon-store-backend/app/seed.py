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
        # Shared M3 specifications; barrel, weight and capacity vary by configuration.
        # https://benelli.it/en/arma/m3-black
        # https://benelli.it/en/arma/m3-tactical
        "short_description": (
            "Гладкоствольное ружьё 12-го калибра с инерционной и помповой "
            "системами перезаряжания"
        ),
        "description": (
            "Benelli M3 Super 90 — гладкоствольное ружьё итальянского производителя "
            "Benelli Armi. Главная особенность модели — сочетание инерционной "
            "полуавтоматики и ручного помпового перезаряжания в одной конструкции.\n\n"
            "Ствольная коробка выполнена из алюминиевого сплава Ergal с чёрным "
            "матовым покрытием, приклад и цевьё — из технополимера. Длина ствола, "
            "масса, прицельные приспособления и ёмкость магазина зависят от исполнения."
        ),
        "image_url": "/images/products/benelli-m3-super-90.png",
        "price": Decimal("249990.00"),
        "old_price": None,
        "stock": 3,
        "attributes": {
            "Калибр": "12",
            "Патронник": "76 мм (Magnum)",
            "Система перезаряжания": "Инерционная полуавтоматика / помповая",
            "Производитель": "Benelli Armi",
            "Страна": "Италия",
            "Ствольная коробка": "Алюминиевый сплав Ergal",
            "Приклад и цевьё": "Технополимер",
            "Покрытие ствольной коробки": "Чёрное матовое анодирование",
        },
        "is_featured": True,
        "is_regulated": True,
    },
    {
        "name": "Сайга 5,45×39",
        "slug": "saiga-545x39",
        "sku": "MF-RIF-0002",
        "brand": "Калашников",
        "category_slug": "rifled-firearms",
        # Configuration 030 is selected explicitly; do not mix its dimensions with 033.
        # https://kalashnikov.market/product/110000900301/sajga-5-45-isp-30-5-45x39-415-mm
        "short_description": "Самозарядный карабин калибра 5,45×39 в исполнении 030",
        "description": (
            "Сайга 5,45×39 — российский самозарядный карабин семейства «Сайга». "
            "В каталоге представлено исполнение 030 со стволом длиной 415 мм.\n\n"
            "Модель оснащена съёмным коробчатым магазином, прикладом и цевьём "
            "из ударопрочного полимера. Масса этого исполнения составляет 3,6 кг."
        ),
        "image_url": "/images/products/saiga-545x39.webp",
        # Prices and stock in the seed are display-only demo values, not market quotes.
        "price": Decimal("79990.00"),
        "old_price": None,
        "stock": 2,
        "attributes": {
            "Калибр": "5,45×39",
            "Исполнение": "030",
            "Длина ствола": "415 мм",
            "Тип": "Самозарядный нарезной карабин",
            "Масса": "3,6 кг",
            "Магазин": "Съёмный коробчатый",
            "Приклад и цевьё": "Ударопрочный полимер",
            "Производитель": "Калашников",
            "Страна": "Россия",
        },
        "is_featured": True,
        "is_regulated": True,
    },
    {
        "name": "Bornaghi Magnum 12/76",
        "slug": "bornaghi-magnum-12-76",
        "sku": "MF-AMM-0002",
        "brand": "Bornaghi",
        "category_slug": "ammunition-and-gear",
        # Calibre, shot charge and pack size follow the user's photographed packaging.
        "short_description": (
            "Дробовые патроны Magnum с массой снаряда 50 г в упаковке по 10 штук"
        ),
        "description": (
            "Bornaghi Magnum 12/76 — дробовые патроны итальянского бренда Bornaghi. "
            "Масса дробового снаряда составляет 50 г, длина гильзы — 76 мм.\n\n"
            "В коробке 10 патронов. Номер дроби зависит от варианта патрона и "
            "указывается на его упаковке."
        ),
        "image_url": "/images/products/bornaghi-magnum-12-76.png",
        "price": Decimal("2990.00"),
        "old_price": None,
        "stock": 20,
        "attributes": {
            "Калибр": "12/76",
            "Масса дробового снаряда": "50 г",
            "Количество в упаковке": "10 шт",
            "Тип": "Дробовой патрон Magnum",
            "Длина гильзы": "76 мм",
            "Гильза": "Пластиковая с металлическим основанием",
            "Бренд": "Bornaghi",
            "Страна": "Италия",
        },
        "is_featured": False,
        "is_regulated": True,
    },
    {
        "name": "БПЗ 5,45×39 FMJ",
        "slug": "barnaul-545x39-fmj",
        "sku": "MF-AMM-0003",
        "brand": "БПЗ / Barnaul",
        "category_slug": "ammunition-and-gear",
        # This is the 4.2 g / 30-round variant shown on the user's packaging.
        # https://www.barnaulpatron.ru/ru/catalog/patrony-dlya-nareznogo-oruzhiya/5-45x39/
        "short_description": (
            "Оболочечные патроны с пулей 4,2 г и стальной лакированной гильзой"
        ),
        "description": (
            "Патроны Барнаульского патронного завода калибра 5,45×39 с оболочечной "
            "пулей FMJ массой 4,2 г. Пуля имеет коническую хвостовую часть.\n\n"
            "В представленном варианте используются стальная лакированная гильза "
            "и неоржавляющий капсюль. Упаковка содержит 30 патронов."
        ),
        "image_url": "/images/products/barnaul-545x39-fmj.webp",
        "price": Decimal("1490.00"),
        "old_price": None,
        "stock": 20,
        "attributes": {
            "Калибр": "5,45×39",
            "Масса пули": "4,2 г",
            "Количество в упаковке": "30 шт",
            "Тип пули": "FMJ, оболочечная с конусом",
            "Гильза": "Стальная лакированная",
            "Капсюль": "Неоржавляющий",
            "Производитель": "АО «Барнаульский патронный завод»",
            "Страна": "Россия",
        },
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
