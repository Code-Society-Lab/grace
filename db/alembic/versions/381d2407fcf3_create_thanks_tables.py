"""Create thanks tables

Revision ID: 381d2407fcf3
Revises: 11f3c9cd0977
Create Date: 2022-12-10 01:52:25.646625

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '381d2407fcf3'
down_revision = '11f3c9cd0977'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('thanks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('member_id', sa.BigInteger(), nullable=False),
        sa.Column('count', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('member_id'),
        if_not_exists=True
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('thanks')
    # ### end Alembic commands ###
