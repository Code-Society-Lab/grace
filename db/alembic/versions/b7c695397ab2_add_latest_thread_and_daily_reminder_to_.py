"""add_latest_thread_and_daily_reminder_to_threads

Revision ID: b7c695397ab2
Revises: cc8da39749e7
Create Date: 2025-10-15 15:58:03.467659

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b7c695397ab2"
down_revision = "cc8da39749e7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "threads", sa.Column("latest_thread_id", sa.BigInteger(), nullable=True)
    )
    op.add_column("threads", sa.Column("daily_reminder", sa.Boolean()))


def downgrade() -> None:
    op.drop_column("threads", "latest_thread_id")
    op.drop_column("threads", "daily_reminder")
