"""Added Recurring Thread table

Revision ID: f8ac0bbc34ac
Revises: 614bb9e370d8
Create Date: 2025-03-10 20:34:24.702582

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f8ac0bbc34ac'
down_revision = '614bb9e370d8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'threads',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('recurrence', sa.Integer(), nullable=False, default=0),
        sa.PrimaryKeyConstraint('id'),
        if_not_exists=True
    )


def downgrade() -> None:
    op.drop_table('threads')
