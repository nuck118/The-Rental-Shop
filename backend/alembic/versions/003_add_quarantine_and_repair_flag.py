"""Add data_quarantine table and repair_flagged column

Revision ID: 003_add_quarantine_and_repair_flag
Revises: 002_add_user_audit
Create Date: 2024-01-20 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "003_add_quarantine_and_repair_flag"
down_revision: Union[str, None] = "002_add_user_audit"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add repair_flagged column to hardware_asset table
    op.add_column("hardware_asset", sa.Column("repair_flagged", sa.Boolean(), nullable=False, server_default="false"))
    
    # Create data_quarantine table
    op.create_table(
        "data_quarantine",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("raw_data", sa.Text(), nullable=False),
        sa.Column("errors", sa.Text(), nullable=False),
        sa.Column("severity", sa.String(length=20), nullable=False, server_default="warning"),
        sa.Column("source", sa.String(length=100), nullable=True),
        sa.Column("resolved", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_data_quarantine_id"), "data_quarantine", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_data_quarantine_id"), table_name="data_quarantine")
    op.drop_table("data_quarantine")
    op.drop_column("hardware_asset", "repair_flagged")