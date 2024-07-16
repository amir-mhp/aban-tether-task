"""add users table

Revision ID: 1ddc08116766
Revises: 
Create Date: 2024-07-15 16:43:42.558484

"""
from alembic import op
import sqlalchemy as sa
from core.models import base

# revision identifiers, used by Alembic.
revision = '1ddc08116766'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'users',
        sa.Column('id', base.UUIDField(as_uuid=True), nullable=False),
        sa.Column('phone', base.PhoneField(length=15), nullable=True),
        sa.Column('password', sa.String(length=255), nullable=False),
        sa.Column('first_name', sa.String(length=32), nullable=True),
        sa.Column('last_name', sa.String(length=32), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_users')),
        sa.UniqueConstraint('phone', name=op.f('uq_users_phone'))
    )


def downgrade():
    op.drop_table('users')
