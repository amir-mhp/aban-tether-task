from sqlalchemy import Table, Column, String, Integer
from sqlalchemy.orm import mapper

from core.entities.currency import CurrencyEntity
from core.models.base import uuid_pk_column, meta, temporal_columns

currencies = Table(
    'currencies', meta,
    uuid_pk_column(),
    Column('title', String(255), nullable=False),
    Column('price', Integer, nullable=True, default=None),
    *temporal_columns()
)

mapper(
    CurrencyEntity,
    currencies,
)
