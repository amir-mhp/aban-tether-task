"""add wallet column

Revision ID: c9a9ab3ea9ed
Revises: 635b8cd0a9c6
Create Date: 2024-07-15 21:58:42.666362

"""
from alembic import op
import sqlalchemy as sa
from core.models import base

# revision identifiers, used by Alembic.
revision = 'c9a9ab3ea9ed'
down_revision = '635b8cd0a9c6'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'users',
        sa.Column(
            'wallet',
            sa.FLOAT(),
            nullable=False,
            server_default='0',
            default='0',
        )
    )


def downgrade():
    op.drop_column('users', 'wallet')
