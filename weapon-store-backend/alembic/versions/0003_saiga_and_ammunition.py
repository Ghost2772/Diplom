"""Replace the demo Tikka and 12/70 entries with Saiga and two ammunition packs.

Revision ID: 0003
Revises: 0002

Product identities are not reused. Existing order-item snapshots are retained,
while references to removed products are cleared and their cart items removed.
The frozen values below deliberately do not import the mutable application seed.
Prices and stock are demonstration values, not current market offers.

Saiga 030: https://kalashnikov.market/product/110000900301/sajga-5-45-isp-30-5-45x39-415-mm
Bornaghi: calibre, 50 g shot charge and 10-round pack from the uploaded packaging.
Barnaul: the uploaded 4.2 g / 30-round pack and the manufacturer's catalogue:
https://www.barnaulpatron.ru/ru/catalog/patrony-dlya-nareznogo-oruzhiya/5-45x39/
"""

from collections.abc import Sequence
from decimal import Decimal

import sqlalchemy as sa

from alembic import op

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None

NEW_PRODUCTS = (
    {
        "name": "Сайга 5,45×39",
        "slug": "saiga-545x39",
        "sku": "MF-RIF-0002",
        "brand": "Калашников",
        "category_slug": "rifled-firearms",
        "short_description": "Самозарядный карабин калибра 5,45×39 в исполнении 030",
        "description": "Сайга 5,45×39 — российский самозарядный карабин семейства «Сайга». В "
        "каталоге представлено исполнение 030 со стволом длиной 415 мм.\n"
        "\n"
        "Модель оснащена съёмным коробчатым магазином, прикладом и цевьём из "
        "ударопрочного полимера. Масса этого исполнения составляет 3,6 кг.",
        "image_url": "/images/products/saiga-545x39.webp",
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
        "short_description": "Дробовые патроны Magnum с массой снаряда 50 г в упаковке по 10 штук",
        "description": "Bornaghi Magnum 12/76 — дробовые патроны итальянского бренда Bornaghi. Масса "
        "дробового снаряда составляет 50 г, длина гильзы — 76 мм.\n"
        "\n"
        "В коробке 10 патронов. Номер дроби зависит от варианта патрона и указывается "
        "на его упаковке.",
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
        "short_description": "Оболочечные патроны с пулей 4,2 г и стальной лакированной гильзой",
        "description": "Патроны Барнаульского патронного завода калибра 5,45×39 с оболочечной пулей "
        "FMJ массой 4,2 г. Пуля имеет коническую хвостовую часть.\n"
        "\n"
        "В представленном варианте используются стальная лакированная гильза и "
        "неоржавляющий капсюль. Упаковка содержит 30 патронов.",
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
)

LEGACY_PRODUCTS = (
    ("MF-RIF-0001", "tikka-t3x-lite", "MF-RIF-0002"),
    ("MF-AMM-0001", "training-ammunition-12-70", "MF-AMM-0002"),
)


def upgrade() -> None:
    connection = op.get_bind()
    products = sa.table(
        "products",
        sa.column("id", sa.Integer()),
        sa.column("name", sa.String()),
        sa.column("slug", sa.String()),
        sa.column("sku", sa.String()),
        sa.column("brand", sa.String()),
        sa.column("short_description", sa.String()),
        sa.column("description", sa.Text()),
        sa.column("image_url", sa.String()),
        sa.column("price", sa.Numeric(10, 2)),
        sa.column("old_price", sa.Numeric(10, 2)),
        sa.column("stock", sa.Integer()),
        sa.column("attributes", sa.JSON()),
        sa.column("is_featured", sa.Boolean()),
        sa.column("is_regulated", sa.Boolean()),
        sa.column("is_active", sa.Boolean()),
        sa.column("category_id", sa.Integer()),
    )
    categories = sa.table(
        "categories", sa.column("id", sa.Integer()), sa.column("slug", sa.String())
    )
    cart_items = sa.table("cart_items", sa.column("product_id", sa.Integer()))
    order_items = sa.table("order_items", sa.column("product_id", sa.Integer()))

    # Insert first so even SQLite cannot recycle the identities being retired.
    # On an empty database the regular seed runs after the migrations.
    for data in NEW_PRODUCTS:
        category_id = connection.scalar(
            sa.select(categories.c.id).where(categories.c.slug == data["category_slug"])
        )
        if category_id is None:
            continue
        existing_id = connection.scalar(
            sa.select(products.c.id).where(
                sa.or_(products.c.sku == data["sku"], products.c.slug == data["slug"])
            )
        )
        if existing_id is None:
            fields = {key: value for key, value in data.items() if key != "category_slug"}
            connection.execute(
                products.insert().values(**fields, category_id=category_id, is_active=True)
            )

    for sku, slug, replacement_sku in LEGACY_PRODUCTS:
        replacement_id = connection.scalar(
            sa.select(products.c.id).where(products.c.sku == replacement_sku)
        )
        if replacement_id is None:
            continue
        old_ids = sa.select(products.c.id).where(products.c.sku == sku, products.c.slug == slug)
        connection.execute(
            order_items.update()
            .where(order_items.c.product_id.in_(old_ids))
            .values(product_id=None)
        )
        connection.execute(cart_items.delete().where(cart_items.c.product_id.in_(old_ids)))
        connection.execute(products.delete().where(products.c.id.in_(old_ids)))


def downgrade() -> None:
    # This data-only change intentionally keeps the new catalogue and order
    # history on rollback; deleted cart contents cannot be reconstructed safely.
    pass
