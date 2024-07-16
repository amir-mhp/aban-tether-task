"""add transaction table

Revision ID: 1a26c0968dd2
Revises: c9a9ab3ea9ed
Create Date: 2024-07-15 22:36:53.235803

"""
from alembic import op
import sqlalchemy as sa
from core.models import base

# revision identifiers, used by Alembic.
revision = '1a26c0968dd2'
down_revision = 'c9a9ab3ea9ed'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'transactions',
        sa.Column('id', base.UUIDField(as_uuid=True), nullable=False),
        sa.Column('user_id', base.UUIDField(as_uuid=True), nullable=False),
        sa.Column('currency_id', base.UUIDField(as_uuid=True), nullable=False),
        sa.Column('count', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Integer(), nullable=False),
        sa.Column(
            'state',
            sa.Enum('SUBMITTED', 'SETTLING', 'SETTLED', name='transactionstate'),
            nullable=False,
        ),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['currency_id'], ['currencies.id'],
                                name=op.f('fk_transactions_currency_id_currencies')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_transactions_user_id_users')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_transactions'))
    )


def downgrade():
    op.drop_table('transactions')
