"""Add return_record table

Revision ID: 004_add_return_records
Revises: 003_add_quarantine_and_repair_flag
Create Date: 2024-01-21 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "004_add_return_records"
down_revision: Union[str, None] = "003_add_quarantine_and_repair_flag"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create return_record table
    op.create_table(
        "return_record",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("hardware_id", sa.Integer(), nullable=False),
        sa.Column("returned_by", sa.String(length=255), nullable=False),
        sa.Column("return_condition", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("returned_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["hardware_id"], ["hardware_asset.id"], ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_return_record_id"), "return_record", ["id"], unique=False)
    op.create_index(op.f("ix_return_record_hardware_id"), "return_record", ["hardware_id"], unique=False)
    op.create_index(op.f("ix_return_record_returned_by"), "return_record", ["returned_by"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_return_record_returned_by"), table_name="return_record")
    op.drop_index(op.f("ix_return_record_hardware_id"), table_name="return_record")
    op.drop_index(op.f("ix_return_record_id"), table_name="return_record")
    op.drop_table("return_record")
