"""missing_pre_migrations_tables

Revision ID: cc8da39749e7
Revises: f8ac0bbc34ac
Create Date: 2025-09-16 00:17:25.001017

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cc8da39749e7'
down_revision = 'f8ac0bbc34ac'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- extensions table ---
    op.create_table(
        "extensions",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("module_name", sa.String(255), nullable=False, unique=True),
        sa.Column("state", sa.Integer(), nullable=True, server_default="1"),
        if_not_exists=True,
    )

    # --- channels table ---
    op.create_table(
        "channels",
        sa.Column("channel_name", sa.String(255), primary_key=True, nullable=False),
        sa.Column("channel_id", sa.BigInteger(), primary_key=True, nullable=False),
        sa.UniqueConstraint("channel_name", "channel_id", name="uq_id_cn_cid"),
        if_not_exists=True,
    )

    # ensure there’s always a single settings row
    conn = op.get_bind()
    result = conn.execute(sa.text("SELECT id FROM bot_settings WHERE id = 1")).fetchone()
    if not result:
        conn.execute(sa.text("INSERT INTO bot_settings (id) VALUES (1)"))

    # --- answers table ---
    op.create_table(
        "answers",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("answer", sa.String(255), nullable=False),
        if_not_exists=True,
    )

    # --- triggers table ---
    op.create_table(
        "triggers",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("name", sa.String(255), unique=True),
        sa.Column("positive_emoji_code", sa.String(255), nullable=False),
        sa.Column("negative_emoji_code", sa.String(255), nullable=False),
        if_not_exists=True,
    )

    # --- trigger_words table ---
    op.create_table(
        "trigger_words",
        sa.Column("trigger_id", sa.Integer(), sa.ForeignKey("triggers.id"), primary_key=True, nullable=False),
        sa.Column("word", sa.String(255), primary_key=True, nullable=False),
        if_not_exists=True,
    )


def downgrade() -> None:
    # Drop in reverse dependency order

    # --- trigger_words depends on triggers ---
    op.drop_table("trigger_words", if_exists=True)

    # --- triggers ---
    op.drop_table("triggers", if_exists=True)

    # --- answers ---
    op.drop_table("answers", if_exists=True)

    # --- channels ---
    op.drop_table("channels", if_exists=True)

    # --- extensions ---
    op.drop_table("extensions", if_exists=True)
