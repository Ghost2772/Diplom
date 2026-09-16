"""Add expiring portfolio demo accounts.

Revision ID: 0004
Revises: 0003
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0004"
down_revision: str | None = "0003"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("users", sa.Column("demo_expires_at", sa.DateTime(timezone=True), nullable=True))
    op.create_index("ix_users_demo_expires_at", "users", ["demo_expires_at"])


def downgrade() -> None:
    # Temporary accounts must not become ordinary users after removing their marker.
    demo_users = "SELECT id FROM users WHERE demo_expires_at IS NOT NULL"
    demo_orders = f"SELECT id FROM orders WHERE user_id IN ({demo_users})"
    demo_carts = f"SELECT id FROM carts WHERE user_id IN ({demo_users})"
    op.execute(sa.text(f"DELETE FROM order_items WHERE order_id IN ({demo_orders})"))
    op.execute(sa.text(f"DELETE FROM cart_items WHERE cart_id IN ({demo_carts})"))
    for table in ("chat_messages", "orders", "carts"):
        op.execute(sa.text(f"DELETE FROM {table} WHERE user_id IN ({demo_users})"))
    op.execute(sa.text("DELETE FROM users WHERE demo_expires_at IS NOT NULL"))
    op.drop_index("ix_users_demo_expires_at", table_name="users")
    op.drop_column("users", "demo_expires_at")
