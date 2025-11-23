"""add quantity to products

Revision ID: a1b2c3d4e5f6
Revises: 367ea37ae560
Create Date: 2025-11-17 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "367ea37ae560"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Добавляем новое NOT NULL поле с дефолтом 0
    op.add_column(
        "products",
        sa.Column(
            "quantity_in_stock", sa.Integer(), nullable=False, server_default="0"
        ),
    )
    # После инициализации можно убрать server_default, если нужно
    with op.batch_alter_table("products") as batch_op:
        batch_op.alter_column("quantity_in_stock", server_default=None)


def downgrade() -> None:
    # Удаляем поле при откате
    op.drop_column("products", "quantity_in_stock")
