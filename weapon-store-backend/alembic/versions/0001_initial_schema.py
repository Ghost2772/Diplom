"""Create the initial portfolio schema.

Revision ID: 0001
Revises:
Create Date: 2026-09-04
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def timestamp_columns() -> tuple[sa.Column, sa.Column]:
    return (
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
    )


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column("full_name", sa.String(length=120), nullable=True),
        sa.Column("phone", sa.String(length=32), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("is_admin", sa.Boolean(), server_default=sa.false(), nullable=False),
        *timestamp_columns(),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("slug", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("image_url", sa.String(length=500), nullable=True),
        sa.Column("display_order", sa.Integer(), server_default="0", nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
        *timestamp_columns(),
        sa.CheckConstraint(
            "display_order >= 0",
            name="ck_categories_display_order_nonnegative",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_categories_name", "categories", ["name"], unique=True)
    op.create_index("ix_categories_slug", "categories", ["slug"], unique=True)

    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("slug", sa.String(length=180), nullable=False),
        sa.Column("sku", sa.String(length=64), nullable=False),
        sa.Column("brand", sa.String(length=100), nullable=True),
        sa.Column("short_description", sa.String(length=300), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("image_url", sa.String(length=500), nullable=True),
        sa.Column("price", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("old_price", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("stock", sa.Integer(), server_default="0", nullable=False),
        sa.Column("attributes", sa.JSON(), server_default=sa.text("'{}'"), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("is_featured", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("is_regulated", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        *timestamp_columns(),
        sa.CheckConstraint("old_price IS NULL OR old_price > price", name="ck_products_old_price"),
        sa.CheckConstraint("price > 0", name="ck_products_price_positive"),
        sa.CheckConstraint("stock >= 0", name="ck_products_stock_nonnegative"),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_products_name", "products", ["name"], unique=False)
    op.create_index("ix_products_slug", "products", ["slug"], unique=True)
    op.create_index("ix_products_sku", "products", ["sku"], unique=True)
    op.create_index("ix_products_brand", "products", ["brand"], unique=False)
    op.create_index("ix_products_category_id", "products", ["category_id"], unique=False)

    op.create_table(
        "carts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )

    op.create_table(
        "orders",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("order_number", sa.String(length=32), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("total_amount", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("status", sa.String(length=32), server_default="created", nullable=False),
        sa.Column("contact_name", sa.String(length=120), nullable=True),
        sa.Column("contact_phone", sa.String(length=32), nullable=True),
        sa.Column("delivery_address", sa.Text(), nullable=True),
        sa.Column("customer_comment", sa.Text(), nullable=True),
        *timestamp_columns(),
        sa.CheckConstraint("total_amount >= 0", name="ck_orders_total_nonnegative"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_orders_order_number", "orders", ["order_number"], unique=True)
    op.create_index("ix_orders_user_id", "orders", ["user_id"], unique=False)
    op.create_index("ix_orders_status", "orders", ["status"], unique=False)

    op.create_table(
        "chat_messages",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("role", sa.String(length=16), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_chat_messages_user_id", "chat_messages", ["user_id"], unique=False)

    op.create_table(
        "cart_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("cart_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Integer(), server_default="1", nullable=False),
        *timestamp_columns(),
        sa.CheckConstraint("quantity > 0", name="ck_cart_items_quantity_positive"),
        sa.ForeignKeyConstraint(["cart_id"], ["carts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("cart_id", "product_id", name="uq_cart_items_cart_product"),
    )

    op.create_table(
        "order_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("order_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=True),
        sa.Column("product_name", sa.String(length=150), nullable=False),
        sa.Column("product_sku", sa.String(length=64), nullable=True),
        sa.Column("price", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("total_price", sa.Numeric(precision=10, scale=2), nullable=False),
        *timestamp_columns(),
        sa.CheckConstraint("price >= 0", name="ck_order_items_price_nonnegative"),
        sa.CheckConstraint("quantity > 0", name="ck_order_items_quantity_positive"),
        sa.CheckConstraint("total_price >= 0", name="ck_order_items_total_nonnegative"),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("order_items")
    op.drop_table("cart_items")
    op.drop_index("ix_chat_messages_user_id", table_name="chat_messages")
    op.drop_table("chat_messages")
    op.drop_index("ix_orders_status", table_name="orders")
    op.drop_index("ix_orders_user_id", table_name="orders")
    op.drop_index("ix_orders_order_number", table_name="orders")
    op.drop_table("orders")
    op.drop_table("carts")
    op.drop_index("ix_products_category_id", table_name="products")
    op.drop_index("ix_products_brand", table_name="products")
    op.drop_index("ix_products_sku", table_name="products")
    op.drop_index("ix_products_slug", table_name="products")
    op.drop_index("ix_products_name", table_name="products")
    op.drop_table("products")
    op.drop_index("ix_categories_slug", table_name="categories")
    op.drop_index("ix_categories_name", table_name="categories")
    op.drop_table("categories")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
