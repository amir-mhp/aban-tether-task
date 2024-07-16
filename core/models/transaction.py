from sqlalchemy import Table, Column, Integer, ForeignKey, Enum
from sqlalchemy.orm import mapper

from core.entities.transaction import TransactionEntity
from core.models.base import uuid_pk_column, meta, temporal_columns, UUIDField

transactions = Table(
    'transactions', meta,
    uuid_pk_column(),
    Column(
        'user_id',
        UUIDField,
        ForeignKey('users.id'),
        nullable=False
    ),
    Column(
        'currency_id',
        UUIDField,
        ForeignKey('currencies.id'),
        nullable=False
    ),
    Column('count', Integer, nullable=False),
    Column('amount', Integer, nullable=False),
    Column('state', Enum(TransactionEntity.TransactionState), nullable=False),
    *temporal_columns()
)

mapper(
    TransactionEntity,
    transactions,
)
