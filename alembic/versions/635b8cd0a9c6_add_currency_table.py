"""add currency table

Revision ID: 635b8cd0a9c6
Revises: 1ddc08116766
Create Date: 2024-07-15 21:28:52.252725

"""
from alembic import op
import sqlalchemy as sa

import core
from core.models import base

# revision identifiers, used by Alembic.
revision = '635b8cd0a9c6'
down_revision = '1ddc08116766'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'currencies',
        sa.Column('id', base.UUIDField(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('price', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_currencies'))
    )


def downgrade():
    op.drop_table('currencies')
