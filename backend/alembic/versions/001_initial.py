"""Create hardware_asset table

Revision ID: 001_initial
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "hardware_asset",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("brand", sa.String(length=100), nullable=False),
        sa.Column("purchase_date", sa.Date(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("assigned_to", sa.String(length=255), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_hardware_asset_name"), "hardware_asset", ["name"], unique=False)
    op.create_index(op.f("ix_hardware_asset_status"), "hardware_asset", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_hardware_asset_status"), table_name="hardware_asset")
    op.drop_index(op.f("ix_hardware_asset_name"), table_name="hardware_asset")
    op.drop_table("hardware_asset")
