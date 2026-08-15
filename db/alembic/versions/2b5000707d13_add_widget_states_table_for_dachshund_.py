"""Add widget_states table for dachshund persistence

Revision ID: 2b5000707d13
Revises: b7c695397ab2
Create Date: 2026-08-15 02:29:13.300732

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "2b5000707d13"
down_revision = "b7c695397ab2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "widget_states",
        sa.Column("key", sa.String(255), nullable=False),
        sa.Column("value", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("key"),
    )


def downgrade() -> None:
    op.drop_table("widget_states")
