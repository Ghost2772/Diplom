"""Fill in the existing demo Benelli card without replacing its commercial data.

Revision ID: 0002
Revises: 0001

Sources: https://benelli.it/en/arma/m3-black and
https://benelli.it/en/arma/m3-tactical
Only shared M3 specifications are included; configuration-specific dimensions,
weight and capacity cannot be established from the uploaded photograph.
"""

import json
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    products = sa.table(
        "products",
        sa.column("sku", sa.String()),
        sa.column("slug", sa.String()),
        sa.column("short_description", sa.String()),
        sa.column("description", sa.Text()),
        sa.column("image_url", sa.String()),
        sa.column("attributes", sa.JSON()),
    )
    op.execute(
        products.update()
        .where(products.c.sku == "MF-SMO-0001", products.c.slug == "benelli-m3-super-90")
        .values(
            short_description=(
                "Гладкоствольное ружьё 12-го калибра с инерционной и помповой "
                "системами перезаряжания"
            ),
            description=(
                "Benelli M3 Super 90 — гладкоствольное ружьё итальянского производителя "
                "Benelli Armi. Главная особенность модели — сочетание инерционной "
                "полуавтоматики и ручного помпового перезаряжания в одной конструкции.\n\n"
                "Ствольная коробка выполнена из алюминиевого сплава Ergal с чёрным "
                "матовым покрытием, приклад и цевьё — из технополимера. Длина ствола, "
                "масса, прицельные приспособления и ёмкость магазина зависят от исполнения."
            ),
            image_url="/images/products/benelli-m3-super-90.png",
            attributes=op.inline_literal(
                json.dumps(
                    {
                        "Калибр": "12",
                        "Патронник": "76 мм (Magnum)",
                        "Система перезаряжания": "Инерционная полуавтоматика / помповая",
                        "Производитель": "Benelli Armi",
                        "Страна": "Италия",
                        "Ствольная коробка": "Алюминиевый сплав Ergal",
                        "Приклад и цевьё": "Технополимер",
                        "Покрытие ствольной коробки": "Чёрное матовое анодирование",
                    },
                    ensure_ascii=False,
                )
            ),
        )
    )


def downgrade() -> None:
    # There is no schema change. Keep the editorial content when rolling back
    # rather than destroying it or restoring generic demo placeholders.
    pass
