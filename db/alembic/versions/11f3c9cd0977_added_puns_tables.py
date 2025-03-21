"""Added puns tables

Revision ID: 11f3c9cd0977
Revises: 
Create Date: 2022-11-08 19:39:27.524172

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '11f3c9cd0977'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('puns',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('text', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('text'),
        if_not_exists=True
    )
    op.create_table('pun_words',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('pun_id', sa.Integer(), nullable=True),
        sa.Column('word', sa.String(length=255), nullable=False),
        sa.Column('emoji_code', sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(['pun_id'], ['puns.id'], ),
        sa.PrimaryKeyConstraint('id'),
        if_not_exists=True
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('pun_words')
    op.drop_table('puns')
    # ### end Alembic commands ###
