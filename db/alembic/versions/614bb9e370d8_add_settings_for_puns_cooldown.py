"""Add settings for puns cooldown

Revision ID: 614bb9e370d8
Revises: 381d2407fcf3
Create Date: 2023-05-29 20:55:26.456843

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '614bb9e370d8'
down_revision = '381d2407fcf3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        'bot_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('puns_cooldown', sa.BigInteger(), nullable=False, server_default="60"),
        sa.PrimaryKeyConstraint('id')
    )
    op.add_column('puns', sa.Column('last_invoked', sa.DateTime(), nullable=True))
    op.execute("INSERT INTO bot_settings (id) VALUES (1)")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('puns', 'last_invoked')
    op.drop_table('bot_settings')
    # ### end Alembic commands ###