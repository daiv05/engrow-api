"""add google oauth fields to user

Revision ID: 8a3df4be018b
Revises: a3f8b2c1d4e5
Create Date: 2026-08-03 13:20:56.687537

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8a3df4be018b'
down_revision: Union[str, None] = 'a3f8b2c1d4e5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # SQLite has no native ALTER COLUMN; batch mode recreates the table instead.
    with op.batch_alter_table('users') as batch_op:
        batch_op.add_column(sa.Column('google_sub', sa.String(length=255), nullable=True))
        batch_op.alter_column('password_hash',
                   existing_type=sa.VARCHAR(length=255),
                   nullable=True)
        batch_op.create_index(batch_op.f('ix_users_google_sub'), ['google_sub'], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('users') as batch_op:
        batch_op.drop_index(batch_op.f('ix_users_google_sub'))
        batch_op.alter_column('password_hash',
                   existing_type=sa.VARCHAR(length=255),
                   nullable=False)
        batch_op.drop_column('google_sub')
