"""add_activity_tips

Revision ID: a3f8b2c1d4e5
Revises: 7e611872792c
Create Date: 2026-04-30 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a3f8b2c1d4e5'
down_revision: Union[str, None] = '7e611872792c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'activity_tips',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('activity_type', sa.String(length=50), nullable=False),
        sa.Column('how', sa.Text(), nullable=False),
        sa.Column('tips_json', sa.Text(), nullable=False),
        sa.Column('sort_order', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_activity_tips_activity_type'), 'activity_tips', ['activity_type'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_activity_tips_activity_type'), table_name='activity_tips')
    op.drop_table('activity_tips')
